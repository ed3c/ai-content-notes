#!/usr/bin/env python3
"""Acquire review-only YouTube caption evidence through AI-Video-Transcriber.

The pinned upstream project performs subtitle discovery and parsing. This adapter
verifies the checkout, preserves the returned Markdown, binds evidence digests,
and emits v7.1 source-manifest input. It never enables audio fallback, cookies,
proxies, browser sessions, or note-completion authority.
"""

from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path
from typing import Any, Sequence

from ai_video_transcriber_contract import (
    AUTHORIZATION_STATUSES,
    DEFAULT_UPSTREAM_COMMIT,
    AdapterError,
    artifact_entry,
    base_manifest,
    build_source_manifest,
    build_validation,
    canonical_video_url,
    caption_kind,
    parse_upstream_markdown,
    published_date,
    utc_now,
    validate_authorization,
    write_json,
    write_transcript_artifacts,
    youtube_video_id,
)
from ai_video_transcriber_upstream import (
    fetch_metadata_async,
    fetch_upstream_subtitles,
    verify_upstream,
)

__all__ = [
    "AdapterError",
    "base_manifest",
    "parse_upstream_markdown",
    "validate_authorization",
    "youtube_video_id",
]


async def acquire(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    validate_authorization(args)
    video_id = youtube_video_id(args.url)
    canonical_url = canonical_video_url(video_id)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    created_at = utc_now()
    manifest = base_manifest(args, video_id, created_at)
    manifest_path = output_dir / "manifest.json"

    try:
        existing = [path for path in output_dir.iterdir() if path.name != "manifest.json"]
        if existing:
            raise AdapterError("output directory must be empty for an atomic acquisition")
        upstream_root = Path(args.upstream_root).resolve()
        prompt_path = Path(args.prompt_path).resolve()
        if not prompt_path.is_file():
            raise AdapterError("v7.1 prompt path does not exist")
        manifest["upstream"] = verify_upstream(upstream_root, args.upstream_commit)
        metadata = await fetch_metadata_async(canonical_url)
        if metadata.get("id") and metadata["id"] != video_id:
            raise AdapterError("resolved video ID does not match requested URL")
        upstream_markdown, title, language = await fetch_upstream_subtitles(
            upstream_root, canonical_url, output_dir / "upstream-work"
        )
        cues = parse_upstream_markdown(upstream_markdown)
        duration = (
            float(metadata["duration"])
            if metadata.get("duration") is not None
            else None
        )
        kind = caption_kind(metadata, language)
        artifacts = write_transcript_artifacts(
            output_dir,
            upstream_markdown=upstream_markdown,
            cues=cues,
            video_id=video_id,
            canonical_url=canonical_url,
        )
        source_manifest = build_source_manifest(
            output_dir=output_dir,
            video_id=video_id,
            caption_type=kind,
            upstream_commit=args.upstream_commit,
            cues=cues,
            artifacts=artifacts,
            prompt_path=prompt_path,
            created_at=created_at,
            authorization_status=args.authorization_status,
        )
        source_manifest_path = output_dir / "source-manifest.json"
        artifacts["source_manifest"] = artifact_entry(source_manifest_path, output_dir)
        manifest["video"].update(
            {
                "title": title or metadata.get("title"),
                "channel": metadata.get("channel") or metadata.get("uploader"),
                "channel_id": metadata.get("channel_id")
                or metadata.get("uploader_id"),
                "duration_seconds": duration,
                "published_at": published_date(metadata),
            }
        )
        manifest["acquisition"].update(
            {"caption_kind": kind, "language": language}
        )
        manifest["validation"] = build_validation(cues, duration)
        if (
            language
            and language not in manifest["acquisition"]["requested_languages"]
        ):
            manifest["validation"]["warnings"].append(
                "upstream language priority selected a track outside the requested list"
            )
        if args.authorization_status != "verified":
            manifest["validation"]["warnings"].append(
                "authorization is unverified-evaluation-only; do not mark the note completed"
            )
        manifest["artifacts"] = artifacts
        manifest["status"] = "needs-review"
        manifest["error"] = None
        manifest["source_manifest_digest"] = (
            f"sha256:{artifacts['source_manifest']['sha256']}"
        )
        manifest["source_manifest_id"] = source_manifest["manifest_id"]
        write_json(manifest_path, manifest)
        return manifest, 0
    except Exception as exc:  # noqa: BLE001 - convert runtime failures to blocked evidence
        manifest["status"] = "blocked"
        manifest["error"] = {
            "type": type(exc).__name__,
            "message": re.sub(r"\s+", " ", str(exc)).strip()[:2000],
        }
        manifest["validation"]["warnings"] = [
            "acquisition failed closed; do not compile a completed note from this run"
        ]
        write_json(manifest_path, manifest)
        return manifest, 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--upstream-root", required=True)
    parser.add_argument("--upstream-commit", default=DEFAULT_UPSTREAM_COMMIT)
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
    _, return_code = asyncio.run(acquire(args))
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
