"""Retained subject artifacts must be bound, or the retention proves nothing."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import verify_source_retention as retention  # noqa: E402


def sha256(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def retain(root: Path, content_id: str, name: str, payload: bytes) -> str:
    path = root / "sources" / content_id / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return sha256(payload)


def manifest(root: Path, content_id: str, sources: list[dict]) -> None:
    path = root / "sources" / content_id / "source-manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"content_id": content_id, "sources": sources}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_an_absent_sources_tree_passes(tmp_path: Path) -> None:
    assert retention.verify(tmp_path) == []


def test_an_empty_sources_tree_passes(tmp_path: Path) -> None:
    (tmp_path / "sources").mkdir()
    assert retention.verify(tmp_path) == []


def test_a_declared_and_matching_artifact_passes(tmp_path: Path) -> None:
    digest = retain(tmp_path, "CvRngaQZQ3Y", "normalized.vtt", b"WEBVTT\n\n00:00.000 --> 00:02.000\nhi\n")
    manifest(
        tmp_path,
        "CvRngaQZQ3Y",
        [{"source_id": "yt", "retained_path": "normalized.vtt", "sha256": digest}],
    )
    assert retention.verify(tmp_path) == []


def test_an_undeclared_retained_file_fails_closed(tmp_path: Path) -> None:
    retain(tmp_path, "CvRngaQZQ3Y", "normalized.vtt", b"body")
    manifest(tmp_path, "CvRngaQZQ3Y", [])
    failures = retention.verify(tmp_path)
    assert any("retained but not declared" in item for item in failures)


def test_a_digest_that_does_not_match_fails_closed(tmp_path: Path) -> None:
    retain(tmp_path, "CvRngaQZQ3Y", "normalized.vtt", b"body")
    manifest(
        tmp_path,
        "CvRngaQZQ3Y",
        [{"source_id": "yt", "retained_path": "normalized.vtt", "sha256": sha256(b"other")}],
    )
    failures = retention.verify(tmp_path)
    assert any("does not match its declared digest" in item for item in failures)


def test_a_declared_but_absent_artifact_fails_closed(tmp_path: Path) -> None:
    manifest(
        tmp_path,
        "CvRngaQZQ3Y",
        [{"source_id": "yt", "retained_path": "gone.vtt", "sha256": sha256(b"x")}],
    )
    failures = retention.verify(tmp_path)
    assert any("declared but not retained" in item for item in failures)


def test_a_retained_directory_without_a_manifest_fails_closed(tmp_path: Path) -> None:
    retain(tmp_path, "CvRngaQZQ3Y", "normalized.vtt", b"body")
    failures = retention.verify(tmp_path)
    assert failures == ["CvRngaQZQ3Y: no source-manifest.json"]


def test_nested_retained_files_are_bound_by_relative_path(tmp_path: Path) -> None:
    digest = retain(tmp_path, "CvRngaQZQ3Y", "raw/captions.vtt", b"raw body")
    manifest(
        tmp_path,
        "CvRngaQZQ3Y",
        [{"source_id": "yt", "retained_path": "raw/captions.vtt", "sha256": digest}],
    )
    assert retention.verify(tmp_path) == []


def test_a_malformed_manifest_fails_closed(tmp_path: Path) -> None:
    retain(tmp_path, "CvRngaQZQ3Y", "normalized.vtt", b"body")
    path = tmp_path / "sources" / "CvRngaQZQ3Y" / "source-manifest.json"
    path.write_text("{not json", encoding="utf-8")
    failures = retention.verify(tmp_path)
    assert any("not valid JSON" in item for item in failures)


def test_the_repository_tree_is_admissible_today() -> None:
    """Retention is a forward rule; the current tree retains nothing yet."""
    assert retention.verify(REPOSITORY_ROOT) == []


def test_a_missing_root_fails_closed(tmp_path: Path) -> None:
    original = sys.argv
    sys.argv = ["verify_source_retention.py", "--root", str(tmp_path / "absent")]
    try:
        with pytest.raises(retention.RetentionError, match="missing repository root"):
            retention.main()
    finally:
        sys.argv = original
