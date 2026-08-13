#!/usr/bin/env python3
"""Acquire a private review-only caption transcript from youtube-transcript.ai.

This is a third-line transport fallback after the pinned AI-Video-Transcriber path
and a direct no-cookie caption client. It performs one documented HTTPS GET, stores
the exact broker response, binds it to the original YouTube dependency key, and
never treats the broker as an independent corroborating source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import Request, urlopen

SCHEMA_VERSION = "youtube-transcript-ai-evidence@1"
SOURCE_MANIFEST_VERSION = "zettelkasten-source-manifest@2"
TOOL_NAME = "youtube_transcript_ai_adapter.py"
TOOL_VERSION = "0.1.0"
SERVICE_ORIGIN = "https://youtube-transcript.ai"
SERVICE_TERMS = "https://youtube-transcript.ai/terms"
SERVICE_PRIVACY = "https://youtube-transcript.ai/privacy"
YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}
VERIFIED_RIGHTS_BASES = {
    "owned",
    "licensed",
    "creator-permission",
    "public-domain",
    "user-provided-media",
}
AUTHORIZATION_STATUSES = {"verified", "unverified-evaluation-only"}
TIMESTAMP_LINE = re.compile(
    r"^\[(?P<timestamp>(?:\d+:)?\d{1,2}:\d{2})\]\s*(?P<text>.*)$"
)
LANGUAGE_LINE = re.compile(
    r"^Language:\s*(?P<language>[^·]+?)\s*·\s*Duration:\s*(?P<duration>[^·]+?)"
    r"\s*·\s*Words:\s*(?P<words>\d+)\s*$"
)
INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"reveal\s+(?:the\s+)?(?:system\s+)?prompt", re.IGNORECASE),
    re.compile(r"mark\s+every\s+command\s+tested", re.IGNORECASE),
)


class BrokerTranscriptError(RuntimeError):
    """Fail-closed transcript-broker error."""


@dataclass(frozen=True)
class BrokerCue:
    start_seconds: int
    end_seconds: int | None
    start_label: str
    end_label: str | None
    text: str


@dataclass(frozen=True)
class ParsedTranscript:
    title: str
    source_url: str
    language: str
    duration_seconds: int
    declared_word_count: int
    other_languages: str | None
    cues: tuple[BrokerCue, ...]


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact_error(exc: Exception) -> str:
    return re.sub(r"\s+", " ", str(exc)).strip()[:2000]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def youtube_video_id(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower().split(":", 1)[0]
    if host not in YOUTUBE_HOSTS:
        raise BrokerTranscriptError(
            "URL must be a supported youtube.com or youtu.be video URL"
        )
    query = parse_qs(parsed.query)
    if "list" in query:
        raise BrokerTranscriptError(
            "playlist parameters are not accepted; submit one video only"
        )
    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/", 1)[0]
    elif parsed.path == "/watch":
        video_id = query.get("v", [""])[0]
    elif parsed.path.startswith(("/shorts/", "/live/", "/embed/")):
        parts = parsed.path.strip("/").split("/")
        video_id = parts[1] if len(parts) > 1 else ""
    else:
        raise BrokerTranscriptError("URL is not a single YouTube video URL")
    if not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", video_id or ""):
        raise BrokerTranscriptError("could not extract a valid YouTube video ID")
    return video_id


def canonical_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def parse_clock(value: str) -> int:
    pieces = value.strip().split(":")
    if len(pieces) == 2:
        hours, minutes, seconds = 0, int(pieces[0]), int(pieces[1])
    elif len(pieces) == 3:
        hours, minutes, seconds = map(int, pieces)
    else:
        raise BrokerTranscriptError(f"invalid timestamp: {value}")
    if minutes < 0 or seconds < 0 or seconds >= 60:
        raise BrokerTranscriptError(f"invalid timestamp: {value}")
    return hours * 3600 + minutes * 60 + seconds


def format_clock(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def parse_broker_response(text: str, expected_video_id: str) -> ParsedTranscript:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    title: str | None = None
    source_url: str | None = None
    language: str | None = None
    duration_seconds: int | None = None
    declared_word_count: int | None = None
    other_languages: str | None = None
    raw_cues: list[tuple[int, str]] = []
    current_start: int | None = None
    current_body: list[str] = []

    def flush() -> None:
        nonlocal current_start, current_body
        if current_start is None:
            return
        body = " ".join(part.strip() for part in current_body if part.strip()).strip()
        if body:
            raw_cues.append((current_start, body))
        current_start = None
        current_body = []

    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("# Transcript:"):
            title = line.split(":", 1)[1].strip()
            continue
        if line.startswith("Source video:"):
            source_url = line.split(":", 1)[1].strip()
            continue
        language_match = LANGUAGE_LINE.match(line)
        if language_match:
            language = language_match.group("language").strip()
            duration_seconds = parse_clock(language_match.group("duration").strip())
            declared_word_count = int(language_match.group("words"))
            continue
        if line.startswith("Other available languages:"):
            other_languages = line.split(":", 1)[1].strip() or None
            continue
        timestamp_match = TIMESTAMP_LINE.match(line)
        if timestamp_match:
            flush()
            current_start = parse_clock(timestamp_match.group("timestamp"))
            current_body = [timestamp_match.group("text").strip()]
            continue
        if current_start is not None and line:
            current_body.append(line)
    flush()

    if not title or not source_url or not language:
        raise BrokerTranscriptError(
            "broker response is missing the required title, source, or language header"
        )
    if duration_seconds is None or declared_word_count is None:
        raise BrokerTranscriptError(
            "broker response is missing the required duration or word-count header"
        )
    source_video_id = youtube_video_id(source_url)
    if source_video_id != expected_video_id:
        raise BrokerTranscriptError(
            f"broker source mismatch: expected {expected_video_id}, got {source_video_id}"
        )
    if not raw_cues:
        raise BrokerTranscriptError("broker response contains no timestamped transcript cues")

    cues: list[BrokerCue] = []
    previous_start = -1
    for index, (start, body) in enumerate(raw_cues):
        if start < previous_start:
            raise BrokerTranscriptError("broker transcript timestamps are non-monotonic")
        previous_start = start
        next_start = raw_cues[index + 1][0] if index + 1 < len(raw_cues) else None
        end = next_start if next_start is not None else duration_seconds
        if end is not None and end < start:
            raise BrokerTranscriptError("broker transcript cue ends before it starts")
        cues.append(
            BrokerCue(
                start_seconds=start,
                end_seconds=end,
                start_label=format_clock(start),
                end_label=format_clock(end) if end is not None else None,
                text=body,
            )
        )
    return ParsedTranscript(
        title=title,
        source_url=source_url,
        language=language,
        duration_seconds=duration_seconds,
        declared_word_count=declared_word_count,
        other_languages=other_languages,
        cues=tuple(cues),
    )


def validate_authorization(args: argparse.Namespace) -> None:
    if args.authorization_status not in AUTHORIZATION_STATUSES:
        raise BrokerTranscriptError(
            f"unsupported authorization status: {args.authorization_status}"
        )
    if not args.rights_reference.strip() or not args.attested_by.strip():
        raise BrokerTranscriptError("rights reference and attestor are required")
    if args.authorization_status == "verified":
        if args.rights_basis not in VERIFIED_RIGHTS_BASES:
            raise BrokerTranscriptError(
                "verified acquisition requires a recognized rights basis"
            )
    elif args.rights_basis != "user-directed-evaluation":
        raise BrokerTranscriptError(
            "unverified evaluation must use rights_basis=user-directed-evaluation"
        )


def fetch_broker_response(video_id: str, language: str | None) -> tuple[str, str]:
    endpoint = f"{SERVICE_ORIGIN}/transcript/{quote(video_id)}.txt"
    if language:
        endpoint += f"?lang={quote(language)}"
    request = Request(
        endpoint,
        headers={
            "Accept": "text/markdown, text/plain; q=0.9",
            "User-Agent": "ai-content-notes/0.1 single-video-evaluation",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=60) as response:  # noqa: S310 - fixed trusted origin
            payload = response.read(12 * 1024 * 1024 + 1)
            if len(payload) > 12 * 1024 * 1024:
                raise BrokerTranscriptError("broker response exceeds the 12 MiB safety limit")
            charset = response.headers.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="strict"), endpoint
    except HTTPError as exc:
        body = exc.read(2000).decode("utf-8", errors="replace")
        raise BrokerTranscriptError(
            f"broker HTTP {exc.code}: {compact_error(Exception(body))}"
        ) from exc
    except URLError as exc:
        raise BrokerTranscriptError(f"broker request failed: {exc.reason}") from exc


def detect_injection_findings(
    cues: Sequence[BrokerCue], source_id: str
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for cue in cues:
        for pattern in INJECTION_PATTERNS:
            match = pattern.search(cue.text)
            if match:
                findings.append(
                    {
                        "source_id": source_id,
                        "locator": f"timestamp:{cue.start_label}",
                        "text_match": match.group(0),
                        "disposition": "ISOLATED_AS_DATA",
                    }
                )
    return findings


def artifact_entry(path: Path, output_dir: Path) -> dict[str, str]:
    return {
        "path": path.relative_to(output_dir).as_posix(),
        "sha256": sha256_file(path),
    }


def base_manifest(args: argparse.Namespace, video_id: str, created_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "status": "blocked",
        "video": {
            "id": video_id,
            "canonical_url": canonical_video_url(video_id),
            "title": None,
            "duration_seconds": None,
        },
        "authorization": {
            "status": args.authorization_status,
            "rights_basis": args.rights_basis,
            "rights_reference": args.rights_reference,
            "attested_by": args.attested_by,
            "attested_at": created_at,
            "scope": "private-transient-evaluation"
            if args.authorization_status != "verified"
            else "review-candidate-evidence",
        },
        "transport": {
            "service": "youtube-transcript.ai",
            "service_origin": SERVICE_ORIGIN,
            "endpoint": None,
            "terms_url": SERVICE_TERMS,
            "privacy_url": SERVICE_PRIVACY,
            "authentication_used": False,
            "cookies_supplied": False,
            "proxy_supplied": False,
            "audio_requested": False,
            "retrieved_at": created_at,
        },
        "transcript": {
            "language": None,
            "duration_seconds": None,
            "declared_word_count": None,
            "observed_word_count": 0,
            "character_count": 0,
            "cue_count": 0,
            "timestamps_monotonic": False,
            "other_languages": None,
            "human_review_required": True,
            "warnings": [],
        },
        "artifacts": {},
        "authority": {
            "may_compile_evaluation_cards": True,
            "may_complete_note": False,
            "may_raise_claim_evidence": False,
            "may_enable_skill_routing": False,
            "may_count_as_independent_corroboration": False,
        },
        "source_manifest_digest": None,
        "source_manifest_id": None,
        "error": None,
    }


def write_artifacts(
    output_dir: Path,
    video_id: str,
    raw_response: str,
    parsed: ParsedTranscript,
) -> dict[str, dict[str, str]]:
    raw_path = output_dir / "raw_broker_response.md"
    transcript_json_path = output_dir / "transcript.json"
    transcript_text_path = output_dir / "transcript.txt"
    raw_path.write_text(raw_response.rstrip() + "\n", encoding="utf-8")
    write_json(
        transcript_json_path,
        {
            "schema_version": "youtube-transcript-ai-transcript@1",
            "video_id": video_id,
            "canonical_url": canonical_video_url(video_id),
            "transport_service": "youtube-transcript.ai",
            "source_dependency_key": f"youtube-video:{video_id}",
            "title": parsed.title,
            "language": parsed.language,
            "duration_seconds": parsed.duration_seconds,
            "declared_word_count": parsed.declared_word_count,
            "other_languages": parsed.other_languages,
            "cues": [asdict(cue) for cue in parsed.cues],
        },
    )
    transcript_text_path.write_text(
        "\n".join(
            f"[{cue.start_label}] {cue.text}" for cue in parsed.cues
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "raw_broker_response": artifact_entry(raw_path, output_dir),
        "transcript_json": artifact_entry(transcript_json_path, output_dir),
        "transcript_text": artifact_entry(transcript_text_path, output_dir),
    }


def build_source_manifest(
    *,
    output_dir: Path,
    video_id: str,
    parsed: ParsedTranscript,
    artifacts: dict[str, dict[str, str]],
    prompt_path: Path,
    created_at: str,
    authorization_status: str,
) -> dict[str, Any]:
    source_digest = artifacts["raw_broker_response"]["sha256"]
    prompt_digest = sha256_file(prompt_path)
    source_id = f"youtube:{video_id}:youtube-transcript-ai"
    source_set_digest = sha256_text(
        "\n".join((video_id, source_digest, "youtube-transcript.ai", parsed.language))
    )
    missing_spans = [
        "caption track identity and raw YouTube VTT/SRT were not supplied by the broker response",
        "technical names, figures, quotations, identifiers, punctuation, and cue grouping require human review",
    ]
    if authorization_status != "verified":
        missing_spans.append(
            "rights basis is unverified; this private evaluation cannot complete a note"
        )
    manifest = {
        "schema_version": SOURCE_MANIFEST_VERSION,
        "manifest_id": f"sm-youtube-{video_id}-youtube-transcript-ai",
        "content_id": video_id,
        "source_set_digest": f"sha256:{source_set_digest}",
        "locator_policy": "SOURCE_THEN_HEADING_THEN_TEXT_MATCH_THEN_MISSING",
        "completeness": {
            "status": "needs-review",
            "reviewed": False,
            "missing_spans": missing_spans,
        },
        "sources": [
            {
                "source_id": source_id,
                "source_type": "transcript",
                "source_dependency_key": f"youtube-video:{video_id}",
                "primary_or_secondary": "secondary",
                "digest": f"sha256:{source_digest}",
                "locators": [
                    f"timestamp:{parsed.cues[0].start_label}..{parsed.cues[-1].start_label}"
                ],
            }
        ],
        "artifact_boundaries": [
            {
                "artifact_id": "raw-youtube-transcript-ai-response",
                "role": "subject-matter-source",
                "digest": f"sha256:{source_digest}",
            },
            {
                "artifact_id": "card-protocol-v7.1",
                "role": "prompt",
                "digest": f"sha256:{prompt_digest}",
            },
        ],
        "injection_findings": detect_injection_findings(parsed.cues, source_id),
        "created_at": created_at,
    }
    write_json(output_dir / "source-manifest.json", manifest)
    return manifest


def acquire(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    validate_authorization(args)
    video_id = youtube_video_id(args.url)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    created_at = utc_now()
    manifest = base_manifest(args, video_id, created_at)
    manifest_path = output_dir / "manifest.json"
    try:
        if any(output_dir.iterdir()):
            raise BrokerTranscriptError(
                "output directory must be empty for an atomic acquisition"
            )
        prompt_path = Path(args.prompt_path).resolve()
        if not prompt_path.is_file():
            raise BrokerTranscriptError("v7.1 prompt path does not exist")
        raw_response, endpoint = fetch_broker_response(video_id, args.language)
        parsed = parse_broker_response(raw_response, video_id)
        artifacts = write_artifacts(output_dir, video_id, raw_response, parsed)
        source_manifest = build_source_manifest(
            output_dir=output_dir,
            video_id=video_id,
            parsed=parsed,
            artifacts=artifacts,
            prompt_path=prompt_path,
            created_at=created_at,
            authorization_status=args.authorization_status,
        )
        source_manifest_path = output_dir / "source-manifest.json"
        artifacts["source_manifest"] = artifact_entry(
            source_manifest_path, output_dir
        )
        observed_text = " ".join(cue.text for cue in parsed.cues)
        warnings = [
            "transport is a secondary broker; it shares the same youtube-video dependency and is not independent corroboration",
            "raw YouTube caption files and caption-track identity are unavailable",
            "technical names, figures, quotations, identifiers, punctuation, and cue grouping require human review",
        ]
        if args.authorization_status != "verified":
            warnings.append(
                "authorization is unverified-evaluation-only; do not mark the note completed"
            )
        manifest["video"].update(
            {
                "title": parsed.title,
                "duration_seconds": parsed.duration_seconds,
            }
        )
        manifest["transport"]["endpoint"] = endpoint
        manifest["transcript"].update(
            {
                "language": parsed.language,
                "duration_seconds": parsed.duration_seconds,
                "declared_word_count": parsed.declared_word_count,
                "observed_word_count": len(observed_text.split()),
                "character_count": len(observed_text),
                "cue_count": len(parsed.cues),
                "timestamps_monotonic": True,
                "other_languages": parsed.other_languages,
                "warnings": warnings,
            }
        )
        manifest["artifacts"] = artifacts
        manifest["status"] = "needs-review"
        manifest["source_manifest_digest"] = (
            f"sha256:{artifacts['source_manifest']['sha256']}"
        )
        manifest["source_manifest_id"] = source_manifest["manifest_id"]
        write_json(manifest_path, manifest)
        return manifest, 0
    except Exception as exc:  # noqa: BLE001 - convert failures to blocked evidence
        manifest["status"] = "blocked"
        manifest["error"] = {
            "type": type(exc).__name__,
            "message": compact_error(exc),
        }
        manifest["transcript"]["warnings"] = [
            "broker acquisition failed closed; no completed note may be compiled"
        ]
        write_json(manifest_path, manifest)
        return manifest, 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--prompt-path", required=True)
    parser.add_argument("--language")
    parser.add_argument(
        "--authorization-status",
        choices=sorted(AUTHORIZATION_STATUSES),
        required=True,
    )
    parser.add_argument("--rights-basis", required=True)
    parser.add_argument("--rights-reference", required=True)
    parser.add_argument("--attested-by", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _, return_code = acquire(args)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
