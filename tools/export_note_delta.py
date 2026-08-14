#!/usr/bin/env python3
"""Export a privacy-preserving, deterministic note-delta manifest.

The exporter binds a complete private note to a reviewed claim-map sidecar by Git blob SHA.
It never emits the note body and never changes downstream Skill lifecycle or routability.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

HEX40 = re.compile(r"^[a-f0-9]{40}$")
CLAIM_ID = re.compile(r"^claim:[a-z0-9._-]+$")
CAPABILITY_ID = re.compile(r"^[a-z0-9-]+(?:\.[a-z0-9-]+)+$")
VALID_KINDS = {"fact", "inference", "assumption", "invariant"}
VALID_EVIDENCE = {"E0", "E1"}
VALID_SKILL_IMPACTS = {
    "none",
    "new-candidate",
    "update-candidate",
    "invalidate",
    "deprecate",
    "review-and-requalify",
}


class ContractError(ValueError):
    """Raised when a note or claim map violates the canonical contract."""


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if value[0:1] in {"'", '"'}:
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            pass
    return value


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        raise ContractError("note must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ContractError("note frontmatter is not terminated")
    lines = [
        (number, line)
        for number, line in enumerate(text[4:end].splitlines(), start=2)
        if line.strip() and not line.lstrip().startswith("#")
    ]
    result: dict[str, Any] = {}
    block: dict[str, Any] | None = None
    for index, (line_number, line) in enumerate(lines):
        if ":" not in line:
            raise ContractError(
                f"frontmatter line {line_number} is not a supported scalar key/value"
            )
        indented = line.startswith((" ", "\t"))
        # Migrated v6.6 notes carry a nested `migration:` provenance block.
        # Exactly one level of nesting under a valueless parent key is supported.
        if indented and block is None:
            raise ContractError(
                f"frontmatter line {line_number} is indented without a block parent"
            )
        key, value = line.split(":", 1)
        key = key.strip()
        target = result if not indented else block
        if not key or key in target:
            raise ContractError(f"invalid or duplicate frontmatter key: {key!r}")
        opens_block = (
            not indented
            and not value.strip()
            and index + 1 < len(lines)
            and lines[index + 1][1].startswith((" ", "\t"))
        )
        if opens_block:
            block = {}
            result[key] = block
            continue
        if not indented:
            block = None
        target[key] = _parse_scalar(value)
    return result


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git object identity


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _is_uri(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _relative(path: Path, root: Path, label: str) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ContractError(f"{label} must be inside repository root") from exc


def validate_binding(
    note_path: Path,
    claim_map_path: Path,
    repository_root: Path,
) -> tuple[dict[str, Any], dict[str, Any], str, str, str]:
    note_bytes = note_path.read_bytes()
    note_text = note_bytes.decode("utf-8")
    frontmatter = parse_frontmatter(note_text)
    claim_map = json.loads(claim_map_path.read_text(encoding="utf-8"))

    _require(claim_map.get("schema_version") == "claim-map@1", "unsupported claim map")
    binding = claim_map.get("note")
    claims = claim_map.get("claims")
    _require(isinstance(binding, dict), "claim map note binding is required")
    _require(isinstance(claims, list) and claims, "claim map requires at least one claim")

    note_rel = _relative(note_path, repository_root, "note")
    claim_map_rel = _relative(claim_map_path, repository_root, "claim map")
    blob_sha = git_blob_sha(note_bytes)

    required_frontmatter = {
        "id",
        "title",
        "source_url",
        "category",
        "note_format",
        "repository",
        "path",
    }
    missing = sorted(required_frontmatter - frontmatter.keys())
    _require(not missing, f"note frontmatter missing: {', '.join(missing)}")
    _require(frontmatter["repository"] == "ed3c/ai-content-notes", "repository mismatch")
    _require(frontmatter["path"] == note_rel, "frontmatter path does not match note path")
    _require(_is_uri(str(frontmatter["source_url"])), "frontmatter source_url is invalid")
    _require(
        frontmatter["note_format"] == "zettelkasten-v6.6-cyberpunk",
        "unsupported note_format",
    )

    expected_binding = {
        "id": frontmatter["id"],
        "title": frontmatter["title"],
        "repository": frontmatter["repository"],
        "path": note_rel,
        "blob_sha": blob_sha,
        "source_url": frontmatter["source_url"],
        "category": frontmatter["category"],
        "note_format": frontmatter["note_format"],
    }
    for key, expected in expected_binding.items():
        _require(binding.get(key) == expected, f"note binding mismatch for {key}")

    seen: set[str] = set()
    for index, claim in enumerate(claims):
        prefix = f"claim[{index}]"
        _require(isinstance(claim, dict), f"{prefix} must be an object")
        claim_id = claim.get("id")
        _require(isinstance(claim_id, str) and CLAIM_ID.fullmatch(claim_id), f"{prefix}.id")
        _require(claim_id not in seen, f"duplicate claim id: {claim_id}")
        seen.add(claim_id)
        _require(claim.get("kind") in VALID_KINDS, f"{prefix}.kind")
        _require(
            isinstance(claim.get("statement"), str) and len(claim["statement"].strip()) >= 10,
            f"{prefix}.statement",
        )
        source = claim.get("source")
        _require(isinstance(source, dict), f"{prefix}.source")
        _require(_is_uri(str(source.get("canonical_url", ""))), f"{prefix}.source URL")
        _require(bool(source.get("publisher")), f"{prefix}.source publisher")
        _require(bool(source.get("retrieved_at")), f"{prefix}.source retrieved_at")
        _require(bool(source.get("anchor")), f"{prefix}.source anchor")
        anchor = claim.get("note_anchor")
        _require(
            isinstance(anchor, dict)
            and isinstance(anchor.get("card_ids"), list)
            and bool(anchor["card_ids"]),
            f"{prefix}.note_anchor.card_ids",
        )
        evidence = claim.get("evidence")
        _require(isinstance(evidence, dict), f"{prefix}.evidence")
        _require(evidence.get("grade") in VALID_EVIDENCE, f"{prefix}.evidence.grade")
        if evidence.get("grade") == "E1":
            _require(evidence.get("complete_source") is True, f"{prefix} E1 requires complete source")
        for runtime_flag in (
            "locally_reproduced",
            "sandbox_attested",
            "production_observed",
        ):
            _require(evidence.get(runtime_flag) is False, f"{prefix}.{runtime_flag} must be false")
        mappings = claim.get("mappings")
        _require(isinstance(mappings, dict), f"{prefix}.mappings")
        capabilities = mappings.get("capability_ids")
        _require(isinstance(capabilities, list) and capabilities, f"{prefix}.capability_ids")
        _require(
            all(isinstance(item, str) and CAPABILITY_ID.fullmatch(item) for item in capabilities),
            f"{prefix}.capability_ids contains an invalid ID",
        )
        _require(
            mappings.get("skill_impact") in VALID_SKILL_IMPACTS,
            f"{prefix}.skill_impact",
        )
        license_state = claim.get("license")
        _require(isinstance(license_state, dict), f"{prefix}.license")
        _require(
            set(license_state) == {"code", "model", "data", "trajectory"},
            f"{prefix}.license must separate all artifact planes",
        )
        _require(isinstance(claim.get("relations"), dict), f"{prefix}.relations")
        _require(isinstance(claim.get("review"), dict), f"{prefix}.review")

    return frontmatter, claim_map, note_rel, claim_map_rel, blob_sha


def _split_identifier(value: str) -> list[str]:
    return [part for part in re.split(r"[.\-_/]+", value) if len(part) >= 2]


def derive_terms(claim_map: dict[str, Any]) -> list[str]:
    values: set[str] = set()
    for claim in claim_map["claims"]:
        mappings = claim["mappings"]
        values.add(mappings["domain"])
        for field in ("capability_ids", "principle_ids"):
            for identifier in mappings[field]:
                values.add(identifier)
                values.update(_split_identifier(identifier))
        values.update(claim["note_anchor"]["card_ids"])
    return sorted(values, key=lambda item: (item.casefold(), item))


def build_manifest(
    note_path: Path,
    claim_map_path: Path,
    repository_root: Path,
    source_commit: str,
    readback_verified: bool,
) -> dict[str, Any]:
    _require(bool(HEX40.fullmatch(source_commit)), "source commit must be a 40-character SHA")
    _require(readback_verified, "GitHub read-back must be verified before delta export")
    frontmatter, claim_map, note_rel, claim_map_rel, blob_sha = validate_binding(
        note_path, claim_map_path, repository_root
    )
    claims = claim_map["claims"]

    capability_ids = sorted(
        {
            capability
            for claim in claims
            for capability in claim["mappings"]["capability_ids"]
        }
    )
    lifecycle = sorted(
        {
            stage
            for claim in claims
            for stage in claim["mappings"]["engineering_lifecycle"]
        }
    )
    principles = sorted(
        {
            principle
            for claim in claims
            for principle in claim["mappings"]["principle_ids"]
        }
    )
    artifact_planes = sorted(
        {
            plane
            for claim in claims
            for plane in claim["mappings"]["artifact_planes"]
        }
    )

    return {
        "schema_version": "ai-content-note-delta@1",
        "source_repository": "ed3c/ai-content-notes",
        "source_commit": source_commit,
        "generated_by": "tools/export_note_delta.py",
        "changed_notes": [
            {
                "id": frontmatter["id"],
                "title": frontmatter["title"],
                "path": note_rel,
                "blob_sha": blob_sha,
                "claim_map_path": claim_map_rel,
                "source_url": frontmatter["source_url"],
                "domain": frontmatter["category"],
                "terms": derive_terms(claim_map),
                "claim_ids": sorted(claim["id"] for claim in claims),
                "capability_ids": capability_ids,
                "engineering_lifecycle": lifecycle,
                "principle_ids": principles,
                "artifact_planes": artifact_planes,
                "skill_impact": "review-and-requalify",
                "readback_verified": True,
            }
        ],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--note", type=Path, required=True)
    parser.add_argument("--claim-map", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--readback-verified", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        root = args.repository_root.resolve()
        note = args.note if args.note.is_absolute() else root / args.note
        claim_map = args.claim_map if args.claim_map.is_absolute() else root / args.claim_map
        manifest = build_manifest(
            note,
            claim_map,
            root,
            args.source_commit,
            args.readback_verified,
        )
        encoded = json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if args.output:
            output = args.output if args.output.is_absolute() else root / args.output
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(encoded, encoding="utf-8")
        else:
            sys.stdout.write(encoded)
        if args.check:
            # Binding validation already ran. Re-encoding confirms JSON determinism.
            _require(json.loads(encoded) == manifest, "manifest JSON round-trip failed")
        return 0
    except (ContractError, FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"note-delta export failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
