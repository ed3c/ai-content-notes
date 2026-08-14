#!/usr/bin/env python3
"""Materialize the 22 legacy v6.6 notes from the digest-pinned bootstrap payload.

The payload predates the current governance, schema and template contracts on
`main`, so only `notes/**` is extracted. Every other archive member is a stale
snapshot and is deliberately ignored rather than restored over newer files.

The adapter is the owning authority for the DISCOVERED -> materialized legacy
transition recorded in `MIGRATION_MANIFEST.json`. It fails closed on payload
digest drift, unsafe archive members, frontmatter that disagrees with the file
path, and on any note the canonical exporter cannot parse.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import tarfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from export_note_delta import ContractError, parse_frontmatter  # noqa: E402

PAYLOAD_SHA256 = "b3a80dd44ade0adf106399b7e1c595220ecabf24f0473a4520cf99d85f62f341"
BOOTSTRAP_DIRECTORY = ".bootstrap"
NOTE_PREFIX = "notes/"
EXPECTED_NOTE_COUNT = 22
TARGET_REPOSITORY = "ed3c/ai-content-notes"
REQUIRED_FRONTMATTER = ("id", "repository", "path", "note_format", "migration")


def _fail(message: str) -> None:
    raise ContractError(message)


def read_payload(root: Path) -> bytes:
    chunks = sorted((root / BOOTSTRAP_DIRECTORY).glob("payload.*"))
    if not chunks:
        _fail(f"no bootstrap payload chunks under {BOOTSTRAP_DIRECTORY}/")
    encoded = b"".join(chunk.read_bytes() for chunk in chunks)
    archive = base64.b64decode(encoded, validate=False)
    observed = hashlib.sha256(archive).hexdigest()
    if observed != PAYLOAD_SHA256:
        _fail(f"bootstrap payload digest drift: expected {PAYLOAD_SHA256}, observed {observed}")
    return archive


def _safe_note_name(name: str) -> str | None:
    """Return the repository-relative note path, or None for non-note members."""
    cleaned = name[2:] if name.startswith("./") else name
    if not cleaned.startswith(NOTE_PREFIX) or not cleaned.endswith(".md"):
        return None
    if cleaned != str(Path(cleaned)) or Path(cleaned).is_absolute() or ".." in Path(cleaned).parts:
        _fail(f"unsafe archive member: {name}")
    return cleaned


def extract_notes(archive: bytes, scratch: Path) -> dict[str, bytes]:
    scratch.mkdir(parents=True, exist_ok=True)
    blob = scratch / "payload.tar.xz"
    blob.write_bytes(archive)
    notes: dict[str, bytes] = {}
    with tarfile.open(blob, mode="r:xz") as handle:
        for member in handle.getmembers():
            relative = _safe_note_name(member.name)
            if relative is None:
                continue
            if not member.isfile():
                _fail(f"archive note member is not a regular file: {member.name}")
            extracted = handle.extractfile(member)
            if extracted is None:
                _fail(f"unreadable archive member: {member.name}")
            notes[relative] = extracted.read()
    if len(notes) != EXPECTED_NOTE_COUNT:
        _fail(f"expected {EXPECTED_NOTE_COUNT} legacy notes, archive carries {len(notes)}")
    return dict(sorted(notes.items()))


def note_entry(relative: str, payload: bytes) -> dict[str, Any]:
    frontmatter = parse_frontmatter(payload.decode("utf-8"))
    missing = [key for key in REQUIRED_FRONTMATTER if key not in frontmatter]
    if missing:
        _fail(f"{relative}: frontmatter missing {', '.join(missing)}")
    if frontmatter["repository"] != TARGET_REPOSITORY:
        _fail(f"{relative}: frontmatter repository is {frontmatter['repository']!r}")
    if frontmatter["path"] != relative:
        _fail(f"{relative}: frontmatter path is {frontmatter['path']!r}")
    migration = frontmatter["migration"]
    if not isinstance(migration, dict) or "from_path" not in migration:
        _fail(f"{relative}: migration provenance block is missing from_path")
    return {
        "content_id": frontmatter["id"],
        "path": relative,
        "sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "legacy_from_repository": migration.get("from_repository"),
        "legacy_from_path": migration["from_path"],
        "note_format": frontmatter["note_format"],
        "citation_mapping": frontmatter.get("citation_mapping"),
    }


def build_entries(notes: dict[str, bytes]) -> list[dict[str, Any]]:
    entries = [note_entry(relative, payload) for relative, payload in notes.items()]
    content_ids = [entry["content_id"] for entry in entries]
    if len(set(content_ids)) != len(content_ids):
        _fail("duplicate legacy content_id in the bootstrap payload")
    return entries


def render_manifest(manifest: dict[str, Any], entries: list[dict[str, Any]]) -> dict[str, Any]:
    updated = dict(manifest)
    updated["status"] = "notes-materialized"
    updated["materialized_legacy_entries"] = entries
    updated["materialized_legacy_note_count"] = len(entries)
    updated["payload_sha256"] = "sha256:" + PAYLOAD_SHA256
    updated["note"] = (
        "Only notes/** was restored from the bootstrap payload. The archived "
        "README, INDEX, RANK, CONTEXT, governance, schema and template members "
        "predate the current contracts on main and are not authority. Sheet URL "
        "repointing and GitHub read-back remain outstanding."
    )
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path, default=Path("MIGRATION_MANIFEST.json"))
    parser.add_argument("--scratch", type=Path, default=Path(".migration-scratch"))
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the persisted notes and manifest without writing",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    notes = extract_notes(read_payload(root), args.scratch.resolve())
    entries = build_entries(notes)
    manifest = render_manifest(json.loads(manifest_path.read_text(encoding="utf-8")), entries)
    rendered = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    if args.check:
        drift = [
            relative
            for relative, payload in notes.items()
            if not (root / relative).is_file() or (root / relative).read_bytes() != payload
        ]
        if drift:
            _fail(f"materialized notes are missing or stale: {', '.join(sorted(drift))}")
        if manifest_path.read_text(encoding="utf-8") != rendered:
            _fail("persisted MIGRATION_MANIFEST.json does not match the payload")
    else:
        for relative, payload in notes.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        manifest_path.write_text(rendered, encoding="utf-8")

    print(
        json.dumps(
            {
                "materialized_legacy_note_count": len(entries),
                "payload_sha256": "sha256:" + PAYLOAD_SHA256,
                "mode": "check" if args.check else "write",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
