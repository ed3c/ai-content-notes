#!/usr/bin/env python3
"""Validate the traceability implementation-preflight contract.

This verifier proves only preparation-graph consistency. It does not execute source,
Google, GitHub, rights, runtime, or product-outcome lanes.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_ATOMS = {"I0", "I1", "I2", "E1", "I3", "I4", "G0"}
REQUIRED_FIELDS = {
    "owner",
    "title",
    "state",
    "start_dependencies",
    "completion_dependencies",
    "planned_paths",
    "outputs",
    "negative_controls",
    "evidence_ceiling",
    "next_safe_transition",
}
READY_STATES = {"READY_TO_START", "READY_TO_START_EXTERNAL_REPO"}
BLOCKED_STATES = {"BLOCKED_BY_DEPENDENCIES", "BLOCKED_BY_I0", "BLOCKED_BY_IMPLEMENTATION_ATOMS"}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("preflight must be a JSON object")
    return value


def validate(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("schema") != "traceability-implementation-preflight@1":
        errors.append("unexpected schema")
    if value.get("phase_target") != "TRACEABILITY_PREIMPLEMENTATION_READY":
        errors.append("unexpected phase target")

    atoms = value.get("atoms")
    if not isinstance(atoms, list):
        return errors + ["atoms must be a list"]

    ids = [atom.get("id") for atom in atoms if isinstance(atom, dict)]
    duplicates = sorted(key for key, count in Counter(ids).items() if key and count > 1)
    if duplicates:
        errors.append(f"duplicate atom ids: {duplicates}")
    missing = sorted(REQUIRED_ATOMS - set(ids))
    if missing:
        errors.append(f"missing required atoms: {missing}")

    by_id = {atom.get("id"): atom for atom in atoms if isinstance(atom, dict) and atom.get("id")}
    for atom_id, atom in by_id.items():
        missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in atom)
        if missing_fields:
            errors.append(f"{atom_id} missing fields: {missing_fields}")
            continue
        if not atom["owner"]:
            errors.append(f"{atom_id} missing owner")
        if not atom["outputs"]:
            errors.append(f"{atom_id} missing outputs")
        if not atom["negative_controls"]:
            errors.append(f"{atom_id} missing negative controls")
        if not atom["evidence_ceiling"]:
            errors.append(f"{atom_id} missing evidence ceiling")
        if atom["state"] not in READY_STATES | BLOCKED_STATES:
            errors.append(f"{atom_id} has unsupported state {atom['state']!r}")

    i3 = by_id.get("I3", {})
    i3_deps = set(i3.get("start_dependencies", []))
    required_i3 = {
        "I0 exact admitted source identity fields",
        "ed3c/kotlin-auto-webview#120",
        "ed3c/kotlin-auto-webview#121",
        "ed3c/kotlin-auto-webview#123",
    }
    if i3.get("state") != "BLOCKED_BY_DEPENDENCIES":
        errors.append("I3 must remain blocked before prerequisites are admitted")
    if not required_i3.issubset(i3_deps):
        errors.append("I3 missing required source/KAW start dependencies")

    i4 = by_id.get("I4", {})
    if i4.get("state") != "BLOCKED_BY_I0":
        errors.append("I4 must remain blocked on I0")
    if "I0 exact admitted source identity/digest contract" not in set(i4.get("start_dependencies", [])):
        errors.append("I4 missing I0 dependency")

    g0 = by_id.get("G0", {})
    if not {"I0", "I1", "I2", "E1"}.issubset(set(g0.get("start_dependencies", []))):
        errors.append("G0 missing first-wave convergence dependencies")

    ready_ids = {atom_id for atom_id, atom in by_id.items() if atom.get("state") in READY_STATES}
    if not {"I0", "I1", "I2", "E1"}.issubset(ready_ids):
        errors.append("first wave must keep I0/I1/I2/E1 start-ready")

    external = value.get("human_external_authority")
    if not isinstance(external, list) or not external:
        errors.append("human_external_authority must be a non-empty list")

    path_owners: dict[str, list[str]] = {}
    for atom_id, atom in by_id.items():
        for path in atom.get("planned_paths", []):
            path_owners.setdefault(path, []).append(atom_id)
    overlaps = {path: owners for path, owners in path_owners.items() if len(owners) > 1}
    if overlaps:
        errors.append(f"exact path lease overlap: {overlaps}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        default="docs/reference-registry/implementation-preflight.json",
        type=Path,
    )
    args = parser.parse_args()
    errors = validate(load(args.path))
    report = {"status": "FAIL" if errors else "PASS", "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
