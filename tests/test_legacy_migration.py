"""Contracts for the digest-pinned legacy note materialization."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import materialize_legacy_migration as migration  # noqa: E402
from export_note_delta import ContractError, parse_frontmatter  # noqa: E402

MANIFEST = json.loads((REPOSITORY_ROOT / "MIGRATION_MANIFEST.json").read_text(encoding="utf-8"))


def test_every_note_frontmatter_parses_and_matches_its_path() -> None:
    notes = sorted((REPOSITORY_ROOT / "notes").rglob("*.md"))
    assert notes, "no notes materialized"
    for note in notes:
        relative = note.relative_to(REPOSITORY_ROOT).as_posix()
        frontmatter = parse_frontmatter(note.read_text(encoding="utf-8"))
        assert frontmatter["repository"] == migration.TARGET_REPOSITORY
        assert frontmatter["path"] == relative


def test_nested_provenance_block_is_parsed_without_flattening() -> None:
    text = (
        "---\n"
        'id: "vendor:example"\n'
        "migration:\n"
        "  from_repository: ed3c/openwiki-ablation\n"
        '  from_path: "ai-content-notes/notes/x/y.md"\n'
        "citation_mapping: pending\n"
        "---\n\nbody\n"
    )
    parsed = parse_frontmatter(text)
    assert parsed["migration"] == {
        "from_repository": "ed3c/openwiki-ablation",
        "from_path": "ai-content-notes/notes/x/y.md",
    }
    assert parsed["citation_mapping"] == "pending"


def test_indentation_without_a_block_parent_fails_closed() -> None:
    text = "---\n  from_path: orphan\nid: x\n---\n\nbody\n"
    with pytest.raises(ContractError):
        parse_frontmatter(text)


def test_manifest_records_every_materialized_legacy_note() -> None:
    entries = MANIFEST["materialized_legacy_entries"]
    assert len(entries) == MANIFEST["expected_legacy_note_count"] == 22
    assert MANIFEST["materialized_legacy_note_count"] == 22
    assert MANIFEST["payload_sha256"] == "sha256:" + migration.PAYLOAD_SHA256
    for entry in entries:
        target = REPOSITORY_ROOT / entry["path"]
        assert target.is_file(), entry["path"]
        assert entry["path"].startswith("notes/")
        assert entry["legacy_from_path"].startswith("ai-content-notes/notes/")
        assert entry["bytes"] == target.stat().st_size
    assert len({entry["content_id"] for entry in entries}) == 22
    assert len({entry["path"] for entry in entries}) == 22


def test_archive_members_outside_notes_are_not_restored() -> None:
    assert migration._safe_note_name("./notes/a/b.md") == "notes/a/b.md"
    assert migration._safe_note_name("./governance/PARAMETERS.md") is None
    assert migration._safe_note_name("./README.md") is None
    with pytest.raises(ContractError):
        migration._safe_note_name("notes/../../escape.md")


def test_payload_digest_drift_fails_closed(tmp_path: Path) -> None:
    bootstrap = tmp_path / migration.BOOTSTRAP_DIRECTORY
    bootstrap.mkdir()
    (bootstrap / "payload.00").write_bytes(b"bm90LXRoZS1wYXlsb2Fk")
    with pytest.raises(ContractError, match="digest drift"):
        migration.read_payload(tmp_path)


def test_missing_payload_fails_closed(tmp_path: Path) -> None:
    (tmp_path / migration.BOOTSTRAP_DIRECTORY).mkdir()
    with pytest.raises(ContractError, match="no bootstrap payload"):
        migration.read_payload(tmp_path)


def test_frontmatter_path_disagreement_fails_closed() -> None:
    payload = (
        "---\n"
        'id: "vendor:example"\n'
        "repository: ed3c/ai-content-notes\n"
        'path: "notes/a/other.md"\n'
        "note_format: zettelkasten-v6.6-cyberpunk\n"
        "migration:\n"
        '  from_path: "ai-content-notes/notes/a/b.md"\n'
        "---\n\nbody\n"
    ).encode("utf-8")
    with pytest.raises(ContractError, match="frontmatter path"):
        migration.note_entry("notes/a/b.md", payload)
