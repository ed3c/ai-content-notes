#!/usr/bin/env python3
"""Acquire a reviewable YouTube transcript under an explicit rights attestation.

The tool is deliberately fail-closed:

* it never uses cookies, proxies, PO-token providers, or browser impersonation flags;
* it handles exactly one video and refuses playlists;
* captions are preferred over audio download;
* ASR is an explicit mode and deletes downloaded audio by default;
* output is a candidate evidence bundle, never an automatically completed note.

Runtime dependencies are imported lazily so contract tests do not need yt-dlp,
faster-whisper, CUDA, or network access.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import parse_qs, urlparse

SCHEMA_VERSION = "youtube-transcript-manifest@1"
TOOL_VERSION = "0.1.0"
DEFAULT_ASR_MODEL_REVISION = "edaa852ec7e145841d8ffdb056a99866b5f0a478"
ALLOWED_RIGHTS_BASES = {
    "owned",
    "licensed",
    "creator-permission",
    "public-domain",
    "user-provided-media",
}
ALLOWED_MODES = {"captions", "asr", "auto"}
YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
TIMESTAMP_RE = re.compile(
    r"^(?P<start>(?:\d{1,2}:)?\d{2}:\d{2}[.,]\d{3})\s+-->\s+"
    r"(?P<end>(?:\d{1,2}:)?\d{2}:\d{2}[.,]\d{3})(?:\s+.*)?$"
)


class TranscriptError(RuntimeError):
    """A fail-closed acquisition or validation failure."""


@dataclass(frozen=True)
class Cue:
    start: float
    end: float
    text: str
    normalized_text: str


@dataclass(frozen=True)
class Word:
    start: float | None
    end: float | None
    word: str
    probability: float | None


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def normalize_text(value: str) -> str:
    value = html.unescape(TAG_RE.sub("", value))
    value = value.replace("\u200b", "").replace("\ufeff", "")
    return SPACE_RE.sub(" ", value).strip()


def parse_timestamp(value: str) -> float:
    pieces = value.replace(",", ".").split(":")
    if len(pieces) == 3:
        hours, minutes, seconds = pieces
    elif len(pieces) == 2:
        hours, minutes, seconds = "0", pieces[0], pieces[1]
    else:
        raise TranscriptError(f"invalid timestamp: {value}")
    try:
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except ValueError as exc:
        raise TranscriptError(f"invalid timestamp: {value}") from exc


def parse_webvtt(text: str) -> list[Cue]:
    """Parse WebVTT while preserving cue timing and removing markup.

    Raw VTT remains a separate artifact. This parser intentionally ignores NOTE,
    STYLE, REGION, cue identifiers, and blank blocks.
    """

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    cues: list[Cue] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip().lstrip("\ufeff")
        if not line or line == "WEBVTT":
            index += 1
            continue
        if line.startswith(("NOTE", "STYLE", "REGION")):
            index += 1
            while index < len(lines) and lines[index].strip():
                index += 1
            continue

        match = TIMESTAMP_RE.match(line)
        if match is None and index + 1 < len(lines):
            # Optional cue identifier before the timestamp.
            candidate = lines[index + 1].strip()
            match = TIMESTAMP_RE.match(candidate)
            if match is not None:
                index += 1

        if match is None:
            index += 1
            continue

        start = parse_timestamp(match.group("start"))
        end = parse_timestamp(match.group("end"))
        if end < start:
            raise TranscriptError(f"cue ends before it starts: {line}")

        index += 1
        body: list[str] = []
        while index < len(lines) and lines[index].strip():
            body.append(lines[index].strip())
            index += 1
        cleaned = normalize_text(" ".join(body))
        if cleaned:
            cues.append(Cue(start=start, end=end, text=cleaned, normalized_text=cleaned))

    return stitch_rolling_captions(cues)


def _word_overlap(previous: Sequence[str], current: Sequence[str]) -> int:
    maximum = min(len(previous), len(current))
    for size in range(maximum, 0, -1):
        if list(previous[-size:]) == list(current[:size]):
            return size
    return 0


def stitch_rolling_captions(cues: Sequence[Cue]) -> list[Cue]:
    """Remove only provable consecutive rolling-caption repetition.

    The original text remains in ``Cue.text``. ``normalized_text`` contains only
    newly introduced words when the next cue repeats a suffix of the previous cue.
    Empty extensions are retained in JSON but omitted from the plain-text export.
    """

    result: list[Cue] = []
    previous_words: list[str] = []
    for cue in cues:
        current_words = cue.text.split()
        overlap = _word_overlap(previous_words, current_words)
        normalized = " ".join(current_words[overlap:]).strip()
        if not previous_words:
            normalized = cue.text
        result.append(
            Cue(
                start=cue.start,
                end=cue.end,
                text=cue.text,
                normalized_text=normalized,
            )
        )
        previous_words = current_words
    return result


def youtube_video_id(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower().split(":", 1)[0]
    if host not in YOUTUBE_HOSTS:
        raise TranscriptError("URL must be a supported youtube.com or youtu.be video URL")

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/", 1)[0]
    elif parsed.path == "/watch":
        video_id = parse_qs(parsed.query).get("v", [""])[0]
    elif parsed.path.startswith(("/shorts/", "/live/", "/embed/")):
        parts = parsed.path.strip("/").split("/")
        video_id = parts[1] if len(parts) > 1 else ""
    else:
        raise TranscriptError("URL is not a single YouTube video URL")

    if not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", video_id or ""):
        raise TranscriptError("could not extract a valid YouTube video ID")
    if "list" in parse_qs(parsed.query):
        raise TranscriptError("playlist parameters are not accepted; submit one video only")
    return video_id


def canonical_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def run_command(command: Sequence[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = normalize_text(result.stderr)[-2000:]
        raise TranscriptError(
            f"command failed ({result.returncode}): {' '.join(command[:5])}; {stderr}"
        )
    return result


def yt_dlp_base() -> list[str]:
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "--ignore-config",
        "--no-playlist",
        "--extractor-args",
        "youtube:skip=translated_subs",
    ]


def fetch_metadata(url: str) -> dict[str, Any]:
    result = run_command(
        [
            *yt_dlp_base(),
            "--skip-download",
            "--dump-single-json",
            "--no-warnings",
            url,
        ]
    )
    try:
        metadata = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise TranscriptError("yt-dlp returned invalid metadata JSON") from exc
    if metadata.get("_type") in {"playlist", "multi_video"}:
        raise TranscriptError("metadata resolved to multiple videos")
    return metadata


def _language_candidates(preferences: Sequence[str]) -> list[str]:
    result: list[str] = []
    for language in preferences:
        language = language.strip()
        if not language:
            continue
        for candidate in (language, language.split("-", 1)[0]):
            if candidate and candidate not in result:
                result.append(candidate)
    return result


def select_caption_track(
    metadata: dict[str, Any], preferences: Sequence[str]
) -> tuple[str, str] | None:
    """Return ``(kind, language)`` with manual captions preferred over automatic."""

    candidates = _language_candidates(preferences)
    for kind, key in (("manual", "subtitles"), ("automatic", "automatic_captions")):
        tracks = metadata.get(key) or {}
        if not isinstance(tracks, dict):
            continue
        available = list(tracks)
        for requested in candidates:
            if requested in tracks:
                return kind, requested
            prefix_matches = sorted(
                language
                for language in available
                if language.lower().startswith(requested.lower() + "-")
            )
            if prefix_matches:
                return kind, prefix_matches[0]
    return None


def download_caption(url: str, video_id: str, kind: str, language: str, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    switch = "--write-subs" if kind == "manual" else "--write-auto-subs"
    run_command(
        [
            *yt_dlp_base(),
            "--skip-download",
            switch,
            "--sub-langs",
            language,
            "--sub-format",
            "vtt",
            "--paths",
            str(raw_dir),
            "-o",
            "%(id)s.%(ext)s",
            url,
        ]
    )
    matches = sorted(raw_dir.glob(f"{video_id}*.vtt"))
    if len(matches) != 1:
        raise TranscriptError(
            f"expected exactly one VTT caption file for {video_id}, found {len(matches)}"
        )
    return matches[0]


def download_audio(url: str, video_id: str, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            *yt_dlp_base(),
            "-f",
            "bestaudio/best",
            "--paths",
            str(raw_dir),
            "-o",
            "%(id)s.%(ext)s",
            url,
        ]
    )
    matches = sorted(path for path in raw_dir.glob(f"{video_id}.*") if path.is_file())
    if len(matches) != 1:
        raise TranscriptError(
            f"expected exactly one downloaded audio file for {video_id}, found {len(matches)}"
        )
    return matches[0]


def transcribe_audio(
    audio_path: Path,
    *,
    model_name: str,
    language: str | None,
    device: str,
    compute_type: str,
    glossary: str | None,
    model_revision: str,
) -> tuple[list[Cue], list[Word], dict[str, Any]]:
    try:
        from faster_whisper import WhisperModel  # type: ignore[import-not-found]
    except ImportError as exc:
        raise TranscriptError(
            "ASR mode requires requirements-youtube-transcript-asr.txt"
        ) from exc

    model = WhisperModel(
        model_name,
        device=device,
        compute_type=compute_type,
        revision=model_revision,
    )
    segments, info = model.transcribe(
        str(audio_path),
        language=None if language in {None, "", "auto"} else language,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False,
        hallucination_silence_threshold=2.0,
        initial_prompt=glossary or None,
        hotwords=glossary or None,
    )

    cues: list[Cue] = []
    words: list[Word] = []
    for segment in segments:
        text = normalize_text(segment.text)
        if text:
            cues.append(
                Cue(
                    start=float(segment.start),
                    end=float(segment.end),
                    text=text,
                    normalized_text=text,
                )
            )
        for item in segment.words or []:
            words.append(
                Word(
                    start=float(item.start) if item.start is not None else None,
                    end=float(item.end) if item.end is not None else None,
                    word=normalize_text(item.word),
                    probability=(
                        float(item.probability) if item.probability is not None else None
                    ),
                )
            )

    detected = {
        "language": getattr(info, "language", None),
        "language_probability": getattr(info, "language_probability", None),
        "duration": getattr(info, "duration", None),
        "duration_after_vad": getattr(info, "duration_after_vad", None),
    }
    return cues, words, detected


def validate_cues(cues: Sequence[Cue], duration: float | None) -> dict[str, Any]:
    warnings: list[str] = []
    monotonic = True
    prior_start = -1.0
    intervals: list[tuple[float, float]] = []
    for cue in cues:
        if cue.start < prior_start or cue.end < cue.start:
            monotonic = False
        prior_start = cue.start
        intervals.append((cue.start, cue.end))

    intervals.sort()
    merged: list[list[float]] = []
    for start, end in intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    covered = sum(max(0.0, end - start) for start, end in merged)
    max_end = max((cue.end for cue in cues), default=0.0)
    timeline_coverage = covered / duration if duration and duration > 0 else None
    end_coverage = max_end / duration if duration and duration > 0 else None

    if not cues:
        warnings.append("no transcript cues were produced")
    if not monotonic:
        warnings.append("cue timestamps are not monotonic")
    if end_coverage is not None and end_coverage < 0.8:
        warnings.append("transcript ends before 80% of the video timeline")

    text = " ".join(cue.normalized_text for cue in cues if cue.normalized_text)
    return {
        "cue_count": len(cues),
        "word_count": len(text.split()),
        "character_count": len(text),
        "timestamps_monotonic": monotonic,
        "timeline_coverage_ratio": round(timeline_coverage, 6)
        if timeline_coverage is not None
        else None,
        "end_coverage_ratio": round(end_coverage, 6)
        if end_coverage is not None
        else None,
        "maximum_end_seconds": round(max_end, 3),
        "warnings": warnings,
    }


def timestamp_label(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds_whole, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds_whole:02d}.{milliseconds:03d}"


def write_transcript_artifacts(
    output_dir: Path,
    cues: Sequence[Cue],
    words: Sequence[Word],
    *,
    video_id: str,
    canonical_url: str,
) -> dict[str, dict[str, Any]]:
    transcript_json = output_dir / "transcript.json"
    transcript_text = output_dir / "transcript.txt"
    write_json(
        transcript_json,
        {
            "schema_version": "youtube-transcript@1",
            "video_id": video_id,
            "canonical_url": canonical_url,
            "cues": [asdict(cue) for cue in cues],
            "words": [asdict(word) for word in words],
        },
    )
    transcript_text.write_text(
        "\n".join(
            f"[{timestamp_label(cue.start)} --> {timestamp_label(cue.end)}] "
            f"{cue.normalized_text}"
            for cue in cues
            if cue.normalized_text
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "transcript_json": {
            "path": transcript_json.relative_to(output_dir).as_posix(),
            "sha256": sha256_file(transcript_json),
        },
        "transcript_text": {
            "path": transcript_text.relative_to(output_dir).as_posix(),
            "sha256": sha256_file(transcript_text),
        },
    }


def base_manifest(args: argparse.Namespace, video_id: str, retrieved_at: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "youtube_transcript.py", "version": TOOL_VERSION},
        "status": "blocked",
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
            "rights_basis": args.rights_basis,
            "rights_reference": args.rights_reference,
            "attested_by": args.attested_by,
            "attested_at": retrieved_at,
        },
        "acquisition": {
            "requested_mode": args.mode,
            "backend": None,
            "caption_kind": None,
            "language": None,
            "source_format": None,
            "retrieved_at": retrieved_at,
            "raw_source": None,
            "source_audio_retained": False,
            "asr": None,
        },
        "validation": {
            "cue_count": 0,
            "word_count": 0,
            "character_count": 0,
            "timestamps_monotonic": False,
            "timeline_coverage_ratio": None,
            "end_coverage_ratio": None,
            "maximum_end_seconds": 0.0,
            "warnings": [],
            "quality_grade": "blocked",
            "human_review_required": True,
        },
        "artifacts": {},
        "authority": {
            "may_complete_note": False,
            "may_raise_claim_evidence": False,
            "may_enable_skill_routing": False,
        },
        "error": None,
    }


def apply_metadata(manifest: dict[str, Any], metadata: dict[str, Any]) -> None:
    upload_date = metadata.get("upload_date")
    published_at = None
    if isinstance(upload_date, str) and re.fullmatch(r"\d{8}", upload_date):
        published_at = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
    manifest["video"].update(
        {
            "title": metadata.get("title"),
            "channel": metadata.get("channel") or metadata.get("uploader"),
            "channel_id": metadata.get("channel_id") or metadata.get("uploader_id"),
            "duration_seconds": float(metadata["duration"])
            if metadata.get("duration") is not None
            else None,
            "published_at": published_at,
        }
    )


def ensure_rights(args: argparse.Namespace) -> None:
    if args.rights_basis not in ALLOWED_RIGHTS_BASES:
        raise TranscriptError(f"unsupported rights basis: {args.rights_basis}")
    if not args.rights_reference.strip():
        raise TranscriptError("--rights-reference is required")
    if not args.attested_by.strip():
        raise TranscriptError("--attested-by is required")
    if args.mode not in ALLOWED_MODES:
        raise TranscriptError(f"unsupported mode: {args.mode}")
    if args.mode in {"asr", "auto"} and not args.allow_audio_download:
        raise TranscriptError("ASR requires explicit --allow-audio-download")
    if args.mode in {"asr", "auto"} and not re.fullmatch(
        r"[0-9a-f]{40}", args.asr_model_revision
    ):
        raise TranscriptError("ASR model revision must be a full 40-character Git SHA")


def acquire(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    ensure_rights(args)
    video_id = youtube_video_id(args.url)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    retrieved_at = utc_now()
    manifest = base_manifest(args, video_id, retrieved_at)
    manifest_path = output_dir / "manifest.json"

    try:
        existing = [path for path in output_dir.iterdir() if path.name != "manifest.json"]
        if existing:
            raise TranscriptError("output directory must be empty for an atomic acquisition")
        metadata = fetch_metadata(args.url)
        if metadata.get("id") and metadata["id"] != video_id:
            raise TranscriptError("resolved video ID does not match requested URL")
        apply_metadata(manifest, metadata)
        duration = manifest["video"]["duration_seconds"]
        preferences = [item.strip() for item in args.languages.split(",") if item.strip()]
        raw_dir = output_dir / "raw"
        selected = select_caption_track(metadata, preferences)

        cues: list[Cue]
        words: list[Word] = []
        if args.mode in {"captions", "auto"} and selected is not None:
            kind, language = selected
            caption_path = download_caption(args.url, video_id, kind, language, raw_dir)
            cues = parse_webvtt(caption_path.read_text(encoding="utf-8"))
            manifest["acquisition"].update(
                {
                    "backend": "yt-dlp-captions",
                    "caption_kind": kind,
                    "language": language,
                    "source_format": "webvtt",
                    "raw_source": {
                        "path": caption_path.relative_to(output_dir).as_posix(),
                        "sha256": sha256_file(caption_path),
                    },
                }
            )
            quality_grade = "manual-caption" if kind == "manual" else "platform-auto-caption"
        elif args.mode == "captions":
            raise TranscriptError(
                "no manual or automatic caption track matched the requested languages"
            )
        else:
            audio_path = download_audio(args.url, video_id, raw_dir)
            audio_sha = sha256_file(audio_path)
            glossary = None
            if args.glossary:
                glossary = Path(args.glossary).read_text(encoding="utf-8").strip()
            cues, words, detected = transcribe_audio(
                audio_path,
                model_name=args.asr_model,
                language=args.asr_language,
                device=args.asr_device,
                compute_type=args.asr_compute_type,
                glossary=glossary,
                model_revision=args.asr_model_revision,
            )
            manifest["acquisition"].update(
                {
                    "backend": "faster-whisper",
                    "language": detected.get("language") or args.asr_language,
                    "source_format": audio_path.suffix.lstrip(".") or "audio",
                    "raw_source": {"path": None, "sha256": audio_sha},
                    "source_audio_retained": bool(args.keep_audio),
                    "asr": {
                        "model": args.asr_model,
                        "model_revision": args.asr_model_revision,
                        "device": args.asr_device,
                        "compute_type": args.asr_compute_type,
                        "beam_size": 5,
                        "word_timestamps": True,
                        "vad_filter": True,
                        "condition_on_previous_text": False,
                        "hallucination_silence_threshold": 2.0,
                        "glossary_sha256": hashlib.sha256(glossary.encode()).hexdigest()
                        if glossary
                        else None,
                        "detected": detected,
                    },
                }
            )
            if args.keep_audio:
                manifest["acquisition"]["raw_source"]["path"] = (
                    audio_path.relative_to(output_dir).as_posix()
                )
            else:
                audio_path.unlink(missing_ok=True)
            quality_grade = "asr-unreviewed"

        validation = validate_cues(cues, duration)
        validation.update(
            {
                "quality_grade": quality_grade,
                "human_review_required": True,
            }
        )
        if not cues:
            raise TranscriptError("acquisition produced no transcript cues")
        if not validation["timestamps_monotonic"]:
            raise TranscriptError("acquisition produced non-monotonic timestamps")

        manifest["artifacts"] = write_transcript_artifacts(
            output_dir,
            cues,
            words,
            video_id=video_id,
            canonical_url=canonical_video_url(video_id),
        )
        manifest["validation"] = validation
        manifest["status"] = "needs-review"
        manifest["error"] = None
        write_json(manifest_path, manifest)
        return manifest, 0
    except Exception as exc:  # noqa: BLE001 - convert all runtime failures to blocked evidence
        manifest["status"] = "blocked"
        manifest["error"] = {
            "type": type(exc).__name__,
            "message": normalize_text(str(exc))[:2000],
        }
        manifest["validation"]["warnings"] = [
            "acquisition failed closed; do not generate a completed note from this artifact"
        ]
        write_json(manifest_path, manifest)
        return manifest, 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Single YouTube video URL")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--mode", choices=sorted(ALLOWED_MODES), default="captions")
    parser.add_argument(
        "--languages",
        default="en,zh-Hant,zh-TW,zh",
        help="Comma-separated caption language preference",
    )
    parser.add_argument("--rights-basis", choices=sorted(ALLOWED_RIGHTS_BASES), required=True)
    parser.add_argument("--rights-reference", required=True)
    parser.add_argument("--attested-by", required=True)
    parser.add_argument(
        "--allow-audio-download",
        action="store_true",
        help="Required explicit gate for ASR or auto fallback",
    )
    parser.add_argument("--keep-audio", action="store_true")
    parser.add_argument("--asr-model", default="large-v3")
    parser.add_argument(
        "--asr-model-revision",
        default=DEFAULT_ASR_MODEL_REVISION,
        help="Pinned Hugging Face model Git revision",
    )
    parser.add_argument("--asr-language", default="auto")
    parser.add_argument("--asr-device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--asr-compute-type", default="float16")
    parser.add_argument("--glossary", help="UTF-8 technical proper-noun glossary")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        _, return_code = acquire(args)
    except TranscriptError as exc:
        # Validation failures before an output directory/video ID can be established.
        parser.error(str(exc))
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
