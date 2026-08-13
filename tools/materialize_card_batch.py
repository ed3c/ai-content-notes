#!/usr/bin/env python3
"""Materialize and verify a digest-bound v7.1 card batch from repository parts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Sequence

CARD_HEADING = re.compile(
    r"^###\s+(?P<stable_id>[A-Z][A-Za-z0-9._:-]*)｜.+$",
    re.MULTILINE,
)


class MaterializationError(RuntimeError):
    """Raised when a persisted card-batch contract is incomplete or stale."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise MaterializationError(f"expected a JSON object: {path}")
    return value


def resolve_repo_root(manifest_path: Path) -> Path:
    manifest_path = manifest_path.resolve()
    for candidate in (manifest_path.parent, *manifest_path.parents):
        if (candidate / ".git").exists() or (
            (candidate / "governance" / "CARD_PROTOCOL_V7_1.md").is_file()
            and (candidate / "evals").is_dir()
        ):
            return candidate
    raise MaterializationError("could not resolve repository root from manifest path")


def verify_file(root: Path, entry: dict[str, Any]) -> tuple[Path, str]:
    path_value = entry.get("path")
    expected_sha = entry.get("sha256")
    expected_bytes = entry.get("bytes")
    if not isinstance(path_value, str) or not path_value:
        raise MaterializationError("manifest part is missing path")
    if not isinstance(expected_sha, str) or not re.fullmatch(r"[a-f0-9]{64}", expected_sha):
        raise MaterializationError(f"manifest part has invalid sha256: {path_value}")
    path = root / path_value
    if not path.is_file():
        raise MaterializationError(f"manifest part does not exist: {path_value}")
    payload = path.read_bytes()
    actual_sha = sha256_bytes(payload)
    if actual_sha != expected_sha:
        raise MaterializationError(
            f"sha256 mismatch for {path_value}: expected {expected_sha}, got {actual_sha}"
        )
    if isinstance(expected_bytes, int) and len(payload) != expected_bytes:
        raise MaterializationError(
            f"byte-count mismatch for {path_value}: expected {expected_bytes}, got {len(payload)}"
        )
    return path, payload.decode("utf-8")


def extract_card_ids(text: str) -> list[str]:
    return [match.group("stable_id") for match in CARD_HEADING.finditer(text)]


def build_output(manifest_path: Path) -> tuple[dict[str, Any], str]:
    manifest = load_json(manifest_path)
    if manifest.get("schema_version") != "v7.1-card-batch-manifest@1":
        raise MaterializationError("unsupported card-batch manifest version")
    root = resolve_repo_root(manifest_path)

    parts = manifest.get("parts")
    if not isinstance(parts, list) or not parts:
        raise MaterializationError("manifest must contain at least one part")

    chunks: list[str] = []
    observed_card_ids: list[str] = []
    for entry in parts:
        if not isinstance(entry, dict):
            raise MaterializationError("every part entry must be an object")
        _, text = verify_file(root, entry)
        part_ids = extract_card_ids(text)
        expected_ids = entry.get("card_ids")
        if not isinstance(expected_ids, list) or part_ids != expected_ids:
            raise MaterializationError(
                f"card IDs do not match manifest for {entry.get('path')}: "
                f"expected {expected_ids}, got {part_ids}"
            )
        chunks.append(text.rstrip())
        observed_card_ids.extend(part_ids)

    run_state_path_value = manifest.get("run_state_path")
    run_state_sha = manifest.get("run_state_sha256")
    if not isinstance(run_state_path_value, str) or not isinstance(run_state_sha, str):
        raise MaterializationError("manifest is missing run-state binding")
    run_state_path = root / run_state_path_value
    if not run_state_path.is_file():
        raise MaterializationError("run-state file does not exist")
    run_state_bytes = run_state_path.read_bytes()
    if sha256_bytes(run_state_bytes) != run_state_sha:
        raise MaterializationError("run-state sha256 does not match manifest")
    run_state = run_state_bytes.decode("utf-8").rstrip()

    expected_order = manifest.get("card_order")
    expected_count = manifest.get("card_count")
    if observed_card_ids != expected_order:
        raise MaterializationError(
            f"card order mismatch: expected {expected_order}, got {observed_card_ids}"
        )
    if len(observed_card_ids) != expected_count:
        raise MaterializationError(
            f"card count mismatch: expected {expected_count}, got {len(observed_card_ids)}"
        )
    if len(observed_card_ids) != len(set(observed_card_ids)):
        raise MaterializationError("duplicate stable IDs exist in the card batch")

    rendered = "\n\n".join([*chunks, run_state]) + "\n"
    expected_logical_sha = manifest.get("logical_output_sha256")
    expected_logical_bytes = manifest.get("logical_output_bytes")
    actual_bytes = rendered.encode("utf-8")
    actual_sha = sha256_bytes(actual_bytes)
    if actual_sha != expected_logical_sha:
        raise MaterializationError(
            f"logical output sha256 mismatch: expected {expected_logical_sha}, got {actual_sha}"
        )
    if len(actual_bytes) != expected_logical_bytes:
        raise MaterializationError(
            f"logical output byte-count mismatch: expected {expected_logical_bytes}, got {len(actual_bytes)}"
        )
    return manifest, rendered


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest, rendered = build_output(args.manifest)
    if args.check and manifest.get("status") == "DONE":
        raise MaterializationError(
            "this evaluation batch must remain CONTINUE until rights, human review and external gates pass"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": manifest.get("status"),
                "card_count": manifest.get("card_count"),
                "logical_output_sha256": manifest.get("logical_output_sha256"),
                "output": str(args.output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
