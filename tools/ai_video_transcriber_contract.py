"""Pure contracts and artifact writers for the AI-Video-Transcriber adapter."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import parse_qs, urlparse

SCHEMA_VERSION = "ai-video-transcriber-evidence@1"
SOURCE_MANIFEST_VERSION = "zettelkasten-source-manifest@2"
TOOL_VERSION = "0.1.0"
UPSTREAM_REPOSITORY = "wendy7756/AI-Video-Transcriber"
DEFAULT_UPSTREAM_COMMIT = "ade833b790d482f7a5c0a722c67bc33f71e9d2b5"
UPSTREAM_MODULE = "backend/video_processor.py"
UPSTREAM_LICENSE = "Apache-2.0"
VERIFIED_RIGHTS_BASES = {
    "owned",
    "licensed",
    "creator-permission",
    "public-domain",
    "user-provided-media",
}
AUTHORIZATION_STATUSES = {"verified", "unverified-evaluation-only"}
YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}
TIMING_LINE = re.compile(
    r"^\*\*\[(?P<start>(?:\d{1,2}:)?\d{2}:\d{2})\s*-\s*"
    r"(?P<end>(?:\d{1,2}:)?\d{2}:\d{2})\]\*\*$"
)
INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"reveal\s+(?:the\s+)?(?:system\s+)?prompt", re.IGNORECASE),
    re.compile(r"mark\s+every\s+command\s+tested", re.IGNORECASE),
)


class AdapterError(RuntimeError):
    """Fail-closed adapter error."""


@dataclass(frozen=True)
class Cue:
    start_seconds: int
    end_seconds: int
    start_label: str
    end_label: str
    text: str


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
        raise AdapterError("URL must be a supported youtube.com or youtu.be video URL")
    query = parse_qs(parsed.query)
    if "list" in query:
        raise AdapterError("playlist parameters are not accepted; submit one video only")
    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/", 1)[0]
    elif parsed.path == "/watch":
        video_id = query.get("v", [""])[0]
    elif parsed.path.startswith(("/shorts/", "/live/", "/embed/")):
        parts = parsed.path.strip("/").split("/")
        video_id = parts[1] if len(parts) > 1 else ""
    else:
        raise AdapterError("URL is not a single YouTube video URL")
    if not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", video_id or ""):
        raise AdapterError("could not extract a valid YouTube video ID")
    return video_id


def canonical_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def parse_time_label(value: str) -> int:
    pieces = value.split(":")
    if len(pieces) == 3:
        hours, minutes, seconds = pieces
    elif len(pieces) == 2:
        hours, minutes, seconds = "0", pieces[0], pieces[1]
    else:
        raise AdapterError(f"invalid upstream timestamp: {value}")
    try:
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    except ValueError as exc:
        raise AdapterError(f"invalid upstream timestamp: {value}") from exc


def canonical_time_label(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def parse_upstream_markdown(text: str) -> list[Cue]:
    """Parse the timestamped Markdown emitted by AI-Video-Transcriber."""

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cues: list[Cue] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        match = TIMING_LINE.match(line)
        if not match:
            index += 1
            continue
        start_raw, end_raw = match.group("start"), match.group("end")
        start, end = parse_time_label(start_raw), parse_time_label(end_raw)
        if end < start:
            raise AdapterError(f"upstream cue ends before it starts: {line}")
        index += 1
        body: list[str] = []
        while index < len(lines) and not TIMING_LINE.match(lines[index].strip()):
            candidate = lines[index].strip()
            if candidate:
                body.append(candidate)
            index += 1
        cue_text = " ".join(body).strip()
        if cue_text:
            cues.append(
                Cue(
                    start_seconds=start,
                    end_seconds=end,
                    start_label=canonical_time_label(start),
                    end_label=canonical_time_label(end),
                    text=cue_text,
                )
            )
    if not cues:
        raise AdapterError("AI-Video-Transcriber returned no parseable timestamped cues")
    previous_start = -1
    for cue in cues:
        if cue.start_seconds < previous_start:
            raise AdapterError("AI-Video-Transcriber returned non-monotonic cue timestamps")
        previous_start = cue.start_seconds
    return cues


def validate_authorization(args: argparse.Namespace) -> None:
    if args.authorization_status not in AUTHORIZATION_STATUSES:
        raise AdapterError(f"unsupported authorization status: {args.authorization_status}")
    if not args.rights_reference.strip() or not args.attested_by.strip():
        raise AdapterError("rights reference and attestor are required")
    if args.authorization_status == "verified":
        if args.rights_basis not in VERIFIED_RIGHTS_BASES:
            raise AdapterError("verified acquisition requires a recognized rights basis")
    elif args.rights_basis != "user-directed-evaluation":
        raise AdapterError(
            "unverified evaluation must use rights_basis=user-directed-evaluation"
        )


def published_date(metadata: dict[str, Any]) -> str | None:
    value = metadata.get("upload_date")
    if isinstance(value, str) and re.fullmatch(r"\d{8}", value):
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    return None


def caption_kind(metadata: dict[str, Any], language: str | None) -> str | None:
    if not language:
        return None
    manual = metadata.get("subtitles") or {}
    automatic = metadata.get("automatic_captions") or {}
    if isinstance(manual, dict) and language in manual:
        return "manual"
    if isinstance(automatic, dict) and language in automatic:
        return "automatic"
    return None


def detect_injection_findings(cues: Sequence[Cue], source_id: str) -> list[dict[str, str]]:
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


def build_validation(cues: Sequence[Cue], duration: float | None) -> dict[str, Any]:
    text = " ".join(cue.text for cue in cues)
    max_end = max(cue.end_seconds for cue in cues)
    end_coverage = max_end / duration if duration and duration > 0 else None
    warnings = [
        "AI-Video-Transcriber deletes its downloaded subtitle temp file; this bundle preserves the returned Markdown, not the raw platform VTT/SRT.",
        "technical names, figures, quotations, identifiers, and cue boundaries require human review",
    ]
    if end_coverage is not None and end_coverage < 0.8:
        warnings.append("transcript ends before 80% of the video timeline")
    return {
        "cue_count": len(cues),
        "word_count": len(text.split()),
        "character_count": len(text),
        "timestamps_monotonic": True,
        "maximum_end_seconds": max_end,
        "end_coverage_ratio": round(end_coverage, 6) if end_coverage is not None else None,
        "warnings": warnings,
        "quality_grade": "upstream-caption-candidate",
        "human_review_required": True,
    }


def write_transcript_artifacts(
    output_dir: Path,
    *,
    upstream_markdown: str,
    cues: Sequence[Cue],
    video_id: str,
    canonical_url: str,
) -> dict[str, dict[str, str]]:
    raw_path = output_dir / "raw_upstream_transcript.md"
    transcript_json_path = output_dir / "transcript.json"
    transcript_text_path = output_dir / "transcript.txt"
    raw_path.write_text(upstream_markdown.rstrip() + "\n", encoding="utf-8")
    write_json(
        transcript_json_path,
        {
            "schema_version": "ai-video-transcriber-transcript@1",
            "video_id": video_id,
            "canonical_url": canonical_url,
            "timestamp_precision": "whole-second-as-rendered-by-upstream",
            "cues": [asdict(cue) for cue in cues],
        },
    )
    transcript_text_path.write_text(
        "\n".join(
            f"[{cue.start_label} --> {cue.end_label}] {cue.text}" for cue in cues
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "raw_upstream_transcript": artifact_entry(raw_path, output_dir),
        "transcript_json": artifact_entry(transcript_json_path, output_dir),
        "transcript_text": artifact_entry(transcript_text_path, output_dir),
    }


def build_source_manifest(
    *,
    output_dir: Path,
    video_id: str,
    caption_type: str | None,
    upstream_commit: str,
    cues: Sequence[Cue],
    artifacts: dict[str, dict[str, str]],
    prompt_path: Path,
    created_at: str,
    authorization_status: str,
) -> dict[str, Any]:
    prompt_digest = sha256_file(prompt_path)
    source_digest = artifacts["raw_upstream_transcript"]["sha256"]
    source_id = f"youtube:{video_id}:ai-video-transcriber"
    missing_spans = [
        "raw platform VTT/SRT is not retained by the upstream fetch_subtitles contract",
        "human review of names, figures, quotations, identifiers, and timestamp boundaries is pending",
    ]
    if authorization_status != "verified":
        missing_spans.append("rights basis is unverified; evaluation output cannot complete a note")
    source_set_digest = sha256_text(
        "\n".join((video_id, source_digest, upstream_commit, caption_type or "unknown"))
    )
    first, last = cues[0].start_label, cues[-1].end_label
    manifest = {
        "schema_version": SOURCE_MANIFEST_VERSION,
        "manifest_id": f"sm-youtube-{video_id}-ai-video-transcriber",
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
                "primary_or_secondary": "primary" if caption_type == "manual" else "unknown",
                "digest": f"sha256:{source_digest}",
                "locators": [f"timestamp:{first}..{last}"],
            }
        ],
        "artifact_boundaries": [
            {
                "artifact_id": "raw-upstream-transcript",
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


def base_manifest(args: argparse.Namespace, video_id: str, created_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "ai_video_transcriber_adapter.py", "version": TOOL_VERSION},
        "status": "blocked",
        "upstream": None,
        "video": {
            "id": video_id,
            "canonical_url": canonical_video_url(video_id),
            "title": None,
            "channel": None,
            "channel_id": None,
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
            "backend": "ai-video-transcriber.fetch_subtitles",
            "requested_languages": [
                item.strip() for item in args.languages.split(",") if item.strip()
            ],
            "caption_kind": None,
            "language": None,
            "source_format": "upstream-markdown",
            "retrieved_at": created_at,
        },
        "validation": {
            "cue_count": 0,
            "word_count": 0,
            "character_count": 0,
            "timestamps_monotonic": False,
            "maximum_end_seconds": 0,
            "end_coverage_ratio": None,
            "warnings": [],
            "quality_grade": "blocked",
            "human_review_required": True,
        },
        "artifacts": {},
        "authority": {
            "may_compile_evaluation_cards": True,
            "may_complete_note": False,
            "may_raise_claim_evidence": False,
            "may_enable_skill_routing": False,
        },
        "error": None,
    }
