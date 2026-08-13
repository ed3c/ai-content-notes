#!/usr/bin/env python3
"""Acquire a private, review-only YouTube caption candidate without cookies or proxies.

This fallback is intentionally separate from AI-Video-Transcriber. It is invoked only
when the pinned upstream caption path fails. The resulting manifest records the
actual backend so an upstream failure can never be presented as upstream success.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import parse_qs, urlparse

SCHEMA_VERSION = "youtube-direct-caption-evidence@1"
SOURCE_MANIFEST_VERSION = "zettelkasten-source-manifest@2"
TOOL_NAME = "youtube_direct_caption_adapter.py"
TOOL_VERSION = "0.1.0"
BACKEND_REPOSITORY = "jdepoix/youtube-transcript-api"
BACKEND_VERSION = "1.2.4"
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
INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"reveal\s+(?:the\s+)?(?:system\s+)?prompt", re.IGNORECASE),
    re.compile(r"mark\s+every\s+command\s+tested", re.IGNORECASE),
)


class DirectCaptionError(RuntimeError):
    """Fail-closed direct-caption error."""


@dataclass(frozen=True)
class CaptionCue:
    start_seconds: float
    duration_seconds: float
    end_seconds: float
    start_label: str
    end_label: str
    text: str


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact_error(exc: Exception) -> str:
    return re.sub(r"\s+", " ", str(exc)).strip()[:2000]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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
        raise DirectCaptionError("URL must be a supported youtube.com or youtu.be video URL")
    query = parse_qs(parsed.query)
    if "list" in query:
        raise DirectCaptionError("playlist parameters are not accepted; submit one video only")
    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/", 1)[0]
    elif parsed.path == "/watch":
        video_id = query.get("v", [""])[0]
    elif parsed.path.startswith(("/shorts/", "/live/", "/embed/")):
        parts = parsed.path.strip("/").split("/")
        video_id = parts[1] if len(parts) > 1 else ""
    else:
        raise DirectCaptionError("URL is not a single YouTube video URL")
    if not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", video_id or ""):
        raise DirectCaptionError("could not extract a valid YouTube video ID")
    return video_id


def canonical_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def format_timestamp(seconds: float) -> str:
    if seconds < 0:
        raise DirectCaptionError("caption timestamp cannot be negative")
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def validate_authorization(args: argparse.Namespace) -> None:
    if args.authorization_status not in AUTHORIZATION_STATUSES:
        raise DirectCaptionError(
            f"unsupported authorization status: {args.authorization_status}"
        )
    if not args.rights_reference.strip() or not args.attested_by.strip():
        raise DirectCaptionError("rights reference and attestor are required")
    if args.authorization_status == "verified":
        if args.rights_basis not in VERIFIED_RIGHTS_BASES:
            raise DirectCaptionError(
                "verified acquisition requires a recognized rights basis"
            )
    elif args.rights_basis != "user-directed-evaluation":
        raise DirectCaptionError(
            "unverified evaluation must use rights_basis=user-directed-evaluation"
        )


def select_transcript(
    transcripts: Iterable[Any], preferred_languages: Sequence[str]
) -> tuple[Any, bool]:
    available = list(transcripts)
    if not available:
        raise DirectCaptionError("YouTube exposed no caption tracks")
    by_code: dict[str, list[Any]] = {}
    for transcript in available:
        by_code.setdefault(str(transcript.language_code), []).append(transcript)
    for generated in (False, True):
        for language in preferred_languages:
            for transcript in by_code.get(language, []):
                if bool(transcript.is_generated) is generated:
                    return transcript, False
    for generated in (False, True):
        for transcript in available:
            if bool(transcript.is_generated) is generated:
                return transcript, True
    raise DirectCaptionError("caption tracks were listed but none could be selected")


def build_cues(snippets: Iterable[Any]) -> list[CaptionCue]:
    cues: list[CaptionCue] = []
    previous_start = -1.0
    for snippet in snippets:
        start = float(snippet.start)
        duration = max(float(snippet.duration), 0.0)
        end = start + duration
        text = html.unescape(str(snippet.text)).replace("\u200b", "").strip()
        if not text:
            continue
        if start < previous_start:
            raise DirectCaptionError("direct caption backend returned non-monotonic timestamps")
        previous_start = start
        cues.append(
            CaptionCue(
                start_seconds=round(start, 3),
                duration_seconds=round(duration, 3),
                end_seconds=round(end, 3),
                start_label=format_timestamp(start),
                end_label=format_timestamp(end),
                text=text,
            )
        )
    if not cues:
        raise DirectCaptionError("direct caption backend returned no non-empty cues")
    return cues


def detect_injection_findings(
    cues: Sequence[CaptionCue], source_id: str
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
            "channel": None,
            "duration_seconds": None,
            "published_at": None,
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
        "acquisition": {
            "backend": "youtube-transcript-api",
            "backend_repository": BACKEND_REPOSITORY,
            "backend_version": BACKEND_VERSION,
            "requested_languages": [
                item.strip() for item in args.languages.split(",") if item.strip()
            ],
            "language": None,
            "language_name": None,
            "caption_kind": None,
            "selection_outside_preference": False,
            "retrieved_at": created_at,
            "cookies_used": False,
            "proxy_used": False,
            "audio_used": False,
        },
        "validation": {
            "cue_count": 0,
            "word_count": 0,
            "character_count": 0,
            "timestamps_monotonic": False,
            "maximum_end_seconds": 0,
            "warnings": [],
            "human_review_required": True,
        },
        "artifacts": {},
        "authority": {
            "may_compile_evaluation_cards": True,
            "may_complete_note": False,
            "may_raise_claim_evidence": False,
            "may_enable_skill_routing": False,
        },
        "source_manifest_digest": None,
        "source_manifest_id": None,
        "error": None,
    }


def write_transcript_artifacts(
    output_dir: Path,
    video_id: str,
    canonical_url: str,
    transcript: Any,
    cues: Sequence[CaptionCue],
) -> dict[str, dict[str, str]]:
    transcript_json = output_dir / "transcript.json"
    transcript_text = output_dir / "transcript.txt"
    write_json(
        transcript_json,
        {
            "schema_version": "youtube-direct-caption-transcript@1",
            "video_id": video_id,
            "canonical_url": canonical_url,
            "backend_repository": BACKEND_REPOSITORY,
            "backend_version": BACKEND_VERSION,
            "language": str(transcript.language),
            "language_code": str(transcript.language_code),
            "is_generated": bool(transcript.is_generated),
            "timestamp_precision": "milliseconds-from-caption-api",
            "cues": [asdict(cue) for cue in cues],
        },
    )
    transcript_text.write_text(
        "\n".join(
            f"[{cue.start_label} --> {cue.end_label}] {cue.text}" for cue in cues
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "transcript_json": artifact_entry(transcript_json, output_dir),
        "transcript_text": artifact_entry(transcript_text, output_dir),
    }


def build_source_manifest(
    *,
    output_dir: Path,
    video_id: str,
    transcript: Any,
    cues: Sequence[CaptionCue],
    artifacts: dict[str, dict[str, str]],
    prompt_path: Path,
    created_at: str,
    authorization_status: str,
) -> dict[str, Any]:
    source_digest = artifacts["transcript_json"]["sha256"]
    prompt_digest = sha256_file(prompt_path)
    source_id = f"youtube:{video_id}:youtube-transcript-api"
    dependency_key = f"youtube-video:{video_id}"
    source_set_digest = sha256_text(
        "\n".join(
            (
                video_id,
                source_digest,
                BACKEND_REPOSITORY,
                BACKEND_VERSION,
                str(transcript.language_code),
                "generated" if transcript.is_generated else "manual",
            )
        )
    )
    missing_spans = [
        "video title, channel, publication date, and duration were not supplied by the caption endpoint",
        "human review of names, figures, quotations, identifiers, and caption boundaries is pending",
    ]
    if authorization_status != "verified":
        missing_spans.append(
            "rights basis is unverified; evaluation output cannot complete a note"
        )
    manifest = {
        "schema_version": SOURCE_MANIFEST_VERSION,
        "manifest_id": f"sm-youtube-{video_id}-youtube-transcript-api",
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
                "source_dependency_key": dependency_key,
                "primary_or_secondary": "unknown"
                if transcript.is_generated
                else "primary",
                "digest": f"sha256:{source_digest}",
                "locators": [
                    f"timestamp:{cues[0].start_label}..{cues[-1].end_label}"
                ],
            }
        ],
        "artifact_boundaries": [
            {
                "artifact_id": "direct-caption-transcript-json",
                "role": "subject-matter-source",
                "digest": f"sha256:{source_digest}",
            },
            {
                "artifact_id": "card-protocol-v7.1",
                "role": "prompt",
                "digest": f"sha256:{prompt_digest}",
            },
        ],
        "injection_findings": detect_injection_findings(cues, source_id),
        "created_at": created_at,
    }
    write_json(output_dir / "source-manifest.json", manifest)
    return manifest


def acquire(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    validate_authorization(args)
    video_id = youtube_video_id(args.url)
    canonical_url = canonical_video_url(video_id)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    created_at = utc_now()
    manifest = base_manifest(args, video_id, created_at)
    manifest_path = output_dir / "manifest.json"
    try:
        if any(output_dir.iterdir()):
            raise DirectCaptionError(
                "output directory must be empty for an atomic acquisition"
            )
        prompt_path = Path(args.prompt_path).resolve()
        if not prompt_path.is_file():
            raise DirectCaptionError("v7.1 prompt path does not exist")
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError as exc:
            raise DirectCaptionError(
                "runtime requires requirements-youtube-direct-caption.txt"
            ) from exc

        api = YouTubeTranscriptApi()
        preferred = manifest["acquisition"]["requested_languages"]
        selected, outside_preference = select_transcript(
            api.list(video_id), preferred
        )
        fetched = selected.fetch()
        cues = build_cues(fetched)
        artifacts = write_transcript_artifacts(
            output_dir,
            video_id,
            canonical_url,
            selected,
            cues,
        )
        source_manifest = build_source_manifest(
            output_dir=output_dir,
            video_id=video_id,
            transcript=selected,
            cues=cues,
            artifacts=artifacts,
            prompt_path=prompt_path,
            created_at=created_at,
            authorization_status=args.authorization_status,
        )
        source_manifest_path = output_dir / "source-manifest.json"
        artifacts["source_manifest"] = artifact_entry(
            source_manifest_path, output_dir
        )
        text = " ".join(cue.text for cue in cues)
        warnings = [
            "technical names, figures, quotations, identifiers, and caption boundaries require human review"
        ]
        if outside_preference:
            warnings.append(
                "no preferred-language caption existed; the first available track was selected"
            )
        if args.authorization_status != "verified":
            warnings.append(
                "authorization is unverified-evaluation-only; do not mark the note completed"
            )
        manifest["acquisition"].update(
            {
                "language": str(selected.language_code),
                "language_name": str(selected.language),
                "caption_kind": "automatic"
                if selected.is_generated
                else "manual",
                "selection_outside_preference": outside_preference,
            }
        )
        manifest["validation"] = {
            "cue_count": len(cues),
            "word_count": len(text.split()),
            "character_count": len(text),
            "timestamps_monotonic": True,
            "maximum_end_seconds": cues[-1].end_seconds,
            "warnings": warnings,
            "human_review_required": True,
        }
        manifest["artifacts"] = artifacts
        manifest["status"] = "needs-review"
        manifest["source_manifest_digest"] = (
            f"sha256:{artifacts['source_manifest']['sha256']}"
        )
        manifest["source_manifest_id"] = source_manifest["manifest_id"]
        write_json(manifest_path, manifest)
        return manifest, 0
    except Exception as exc:  # noqa: BLE001 - convert all failures to a blocked manifest
        manifest["status"] = "blocked"
        manifest["error"] = {
            "type": type(exc).__name__,
            "message": compact_error(exc),
        }
        manifest["validation"]["warnings"] = [
            "direct caption acquisition failed closed; no completed note may be compiled"
        ]
        write_json(manifest_path, manifest)
        return manifest, 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--prompt-path", required=True)
    parser.add_argument("--languages", default="en,zh-Hant,zh-TW,zh,ja")
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
