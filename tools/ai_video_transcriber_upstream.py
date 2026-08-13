"""Pinned upstream loader for wendy7756/AI-Video-Transcriber."""

from __future__ import annotations

import asyncio
import importlib.util
import re
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any

from ai_video_transcriber_contract import (
    AdapterError,
    UPSTREAM_LICENSE,
    UPSTREAM_MODULE,
    UPSTREAM_REPOSITORY,
    sha256_file,
)


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AdapterError(f"git {' '.join(args)} failed: {result.stderr.strip()[:500]}")
    return result.stdout.strip()


def verify_upstream(root: Path, expected_commit: str) -> dict[str, str]:
    if not re.fullmatch(r"[0-9a-f]{40}", expected_commit):
        raise AdapterError("upstream commit must be a full 40-character Git SHA")
    module_path, license_path = root / UPSTREAM_MODULE, root / "LICENSE"
    if not module_path.is_file() or not license_path.is_file():
        raise AdapterError("upstream checkout is missing video_processor.py or LICENSE")
    actual_commit = run_git(root, "rev-parse", "HEAD")
    if actual_commit != expected_commit:
        raise AdapterError(
            f"upstream checkout mismatch: expected {expected_commit}, got {actual_commit}"
        )
    license_text = license_path.read_text(encoding="utf-8", errors="replace")
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        raise AdapterError("upstream LICENSE is not recognizable as Apache-2.0")
    return {
        "repository": UPSTREAM_REPOSITORY,
        "commit": actual_commit,
        "license": UPSTREAM_LICENSE,
        "module_path": UPSTREAM_MODULE,
        "module_sha256": sha256_file(module_path),
        "license_sha256": sha256_file(license_path),
    }


def load_upstream_module(root: Path) -> ModuleType:
    module_path = root / UPSTREAM_MODULE
    spec = importlib.util.spec_from_file_location(
        "ai_video_transcriber_video_processor", module_path
    )
    if spec is None or spec.loader is None:
        raise AdapterError("could not load upstream video_processor module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "VideoProcessor"):
        raise AdapterError("upstream module does not expose VideoProcessor")
    return module


def fetch_metadata(url: str) -> dict[str, Any]:
    try:
        import yt_dlp  # type: ignore[import-not-found]
    except ImportError as exc:
        raise AdapterError("runtime requires requirements-youtube-transcript.txt") from exc
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "extractor_args": {"youtube": {"skip": ["translated_subs"]}},
    }
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=False)
    if not isinstance(info, dict) or info.get("_type") in {"playlist", "multi_video"}:
        raise AdapterError("yt-dlp metadata did not resolve to one video")
    return info


async def fetch_upstream_subtitles(
    root: Path, canonical_url: str, working_dir: Path
) -> tuple[str, str | None, str | None]:
    module = load_upstream_module(root)
    processor = module.VideoProcessor()
    markdown, title, language = await processor.fetch_subtitles(canonical_url, working_dir)
    if not markdown:
        raise AdapterError(
            "AI-Video-Transcriber found no usable caption track; audio fallback is disabled"
        )
    return markdown, title, language


async def fetch_metadata_async(url: str) -> dict[str, Any]:
    return await asyncio.to_thread(fetch_metadata, url)
