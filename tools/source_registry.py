#!/usr/bin/env python3
"""Validate and canonicalize rights-aware source-registry@1 packets.

This module is deliberately transport-neutral. It validates a persisted source
pointer after an adapter has resolved and read it back; it does not fetch a
GitHub, Drive, Sheet, PDF, web, interview, or runtime subject by itself.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

STATE_ORDER = {
    "SOURCE_REFERENCED": 0,
    "IDENTITY_RESOLVED": 1,
    "RIGHTS_AND_COMPLETENESS_REVIEWED": 2,
    "SNAPSHOT_CAPTURED": 3,
    "LOCATORS_BOUND": 4,
    "DIGESTED": 5,
    "READ_BACK_VERIFIED": 6,
    "ADMITTED": 7,
}


class RegistryError(RuntimeError):
    """Raised when a registry or its schema cannot be read."""


def _canonical_payload(registry: dict[str, Any]) -> bytes:
    payload = copy.deepcopy(registry)
    payload.pop("registry_digest", None)
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def compute_registry_digest(registry: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_canonical_payload(registry)).hexdigest()


def git_blob_sha1(payload: bytes) -> str:
    """Return the Git object name for these bytes, matching `git hash-object`.

    Git object names are content-addressed, so this is an exact, offline
    read-back primitive for any blob this lane persists or consumes.

    This is the repository's only implementation of the Git blob object name.
    `AGENTS.md` makes this digest the immutability check for the v7.1 prompt
    payload, so a correction applied here has to reach every consumer: no other
    module or test may derive the `blob <len>\\0` header or call `sha1` on it.
    """
    header = f"blob {len(payload)}\0".encode()
    return hashlib.sha1(  # noqa: S324 - Git object identity, not a security digest
        header + payload, usedforsecurity=False
    ).hexdigest()


def canonicalize(registry: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic deep copy with stable list ordering and digest."""
    result = copy.deepcopy(registry)
    for entry in result.get("entries", []):
        entry["blockers"] = sorted(entry.get("blockers", []))
        completeness = entry.get("completeness", {})
        completeness["missing_parts"] = sorted(completeness.get("missing_parts", []))
        entry["locators"] = sorted(
            entry.get("locators", []),
            key=lambda item: (
                str(item.get("kind", "")),
                str(item.get("value", "")),
                str(item.get("digest", "")),
            ),
        )
    result["entries"] = sorted(
        result.get("entries", []),
        key=lambda item: str(item.get("source_id", "")),
    )
    result["registry_digest"] = compute_registry_digest(result)
    return result


def canonical_document(registry: dict[str, Any]) -> str:
    return json.dumps(
        canonicalize(registry),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def _state_at_least(entry: dict[str, Any], state: str) -> bool:
    current = entry.get("state")
    if current == "BLOCKED":
        return False
    return STATE_ORDER.get(str(current), -1) >= STATE_ORDER[state]


def _locator_kinds(entry: dict[str, Any]) -> set[str]:
    return {str(item.get("kind")) for item in entry.get("locators", [])}


def _semantic_failures(registry: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    evidence_mode = registry.get("evidence_mode")
    seen: set[str] = set()

    for entry in registry.get("entries", []):
        source_id = str(entry.get("source_id", "<missing>"))
        prefix = f"{source_id}:"
        if source_id in seen:
            failures.append(f"{prefix} DUPLICATE_SOURCE_ID")
        seen.add(source_id)

        kind = entry.get("source_kind")
        state = entry.get("state")
        identity = entry.get("identity", {})
        rights = entry.get("rights", {})
        completeness = entry.get("completeness", {})
        content = entry.get("content", {})
        readback = entry.get("readback", {})
        retention = entry.get("retention", {})
        locator_kinds = _locator_kinds(entry)

        if evidence_mode == "FIXTURE" and entry.get("authority_ceiling") != (
            "CONTRACT_FIXTURE_ONLY"
        ):
            failures.append(f"{prefix} FIXTURE_AUTHORITY_WIDENED")
        if evidence_mode == "FIXTURE" and state == "ADMITTED":
            failures.append(f"{prefix} FIXTURE_PROMOTED_TO_ADMITTED")

        if state == "BLOCKED" and not entry.get("blockers"):
            failures.append(f"{prefix} BLOCKED_WITHOUT_REASON")
        if state != "BLOCKED" and entry.get("blockers"):
            failures.append(f"{prefix} NON_BLOCKED_WITH_BLOCKERS")

        if content.get("content_scope") == "TITLE_OR_SNIPPET_ONLY":
            if state != "BLOCKED":
                failures.append(f"{prefix} TITLE_SNIPPET_PROMOTED")

        if rights.get("basis") == "PUBLIC_VISIBILITY_ONLY" and rights.get(
            "decision"
        ) == "PASS":
            failures.append(f"{prefix} PUBLIC_VISIBILITY_USED_AS_RIGHTS")
        if rights.get("basis") == "UNKNOWN" and rights.get("decision") == "PASS":
            failures.append(f"{prefix} UNKNOWN_RIGHTS_PROMOTED")

        if entry.get("change_notification_only"):
            if readback.get("status") == "PASS" or content.get("digest"):
                failures.append(f"{prefix} NOTIFICATION_USED_AS_CONTENT_PROOF")
            if _state_at_least(entry, "SNAPSHOT_CAPTURED"):
                failures.append(f"{prefix} NOTIFICATION_ADVANCED_STATE")

        if _state_at_least(entry, "IDENTITY_RESOLVED"):
            if not identity.get("resolved_at"):
                failures.append(f"{prefix} MISSING_IDENTITY_RESOLUTION_TIME")
            if kind == "GITHUB_BLOB":
                required = ("repository", "commit_sha", "blob_sha", "path")
                if any(not identity.get(field) for field in required):
                    failures.append(f"{prefix} GITHUB_BLOB_IDENTITY_INCOMPLETE")
                commit_sha = str(identity.get("commit_sha", ""))
                if commit_sha and commit_sha not in str(entry.get("resolved_url", "")):
                    failures.append(f"{prefix} GITHUB_RESOLVED_URL_NOT_IMMUTABLE")
                if not identity.get("immutable"):
                    failures.append(f"{prefix} GITHUB_BLOB_MARKED_MUTABLE")
            elif kind in {"GITHUB_ISSUE", "GITHUB_PR"}:
                if not identity.get("external_id") or not identity.get(
                    "observed_revision"
                ):
                    failures.append(f"{prefix} GITHUB_MUTABLE_SNAPSHOT_UNBOUND")
            elif kind in {"PDF", "GOOGLE_DOC", "GOOGLE_SHEET"}:
                if not identity.get("external_id"):
                    failures.append(f"{prefix} EXTERNAL_ID_MISSING")
                if not identity.get("observed_revision"):
                    failures.append(f"{prefix} OBSERVED_REVISION_MISSING")

        if _state_at_least(entry, "RIGHTS_AND_COMPLETENESS_REVIEWED"):
            if not completeness.get("reviewed"):
                failures.append(f"{prefix} COMPLETENESS_NOT_REVIEWED")
            if rights.get("decision") == "NEEDS_REVIEW":
                failures.append(f"{prefix} RIGHTS_REVIEW_NOT_TERMINAL")

        if _state_at_least(entry, "SNAPSHOT_CAPTURED"):
            if content.get("content_scope") in {
                "METADATA_ONLY",
                "TITLE_OR_SNIPPET_ONLY",
            }:
                failures.append(f"{prefix} INCOMPLETE_CONTENT_SNAPSHOTTED")
            if not content.get("digest"):
                failures.append(f"{prefix} SNAPSHOT_DIGEST_MISSING")

        if _state_at_least(entry, "LOCATORS_BOUND") and not entry.get("locators"):
            failures.append(f"{prefix} LOCATORS_MISSING")

        if kind == "PDF" and content.get("material_visuals"):
            if _state_at_least(entry, "READ_BACK_VERIFIED"):
                if "visual_region" not in locator_kinds:
                    failures.append(f"{prefix} PDF_VISUAL_LOCATOR_MISSING")
                if content.get("visual_review_state") not in {"PASS", "PARTIAL"}:
                    failures.append(f"{prefix} PDF_VISUAL_REVIEW_NOT_EXERCISED")

        if kind == "GOOGLE_DOC" and _state_at_least(entry, "DIGESTED"):
            if not identity.get("observed_revision"):
                failures.append(f"{prefix} DOC_REVISION_MISSING")
            if not content.get("export_digest"):
                failures.append(f"{prefix} DOC_EXPORT_DIGEST_MISSING")
            if "document_revision" not in locator_kinds:
                failures.append(f"{prefix} DOC_REVISION_LOCATOR_MISSING")

        if kind == "GOOGLE_SHEET" and _state_at_least(entry, "LOCATORS_BOUND"):
            if not identity.get("sheet_range") or not identity.get("row_key"):
                failures.append(f"{prefix} SHEET_RANGE_OR_ROW_KEY_MISSING")
            if not {"sheet_range", "row_key"}.issubset(locator_kinds):
                failures.append(f"{prefix} SHEET_LOCATORS_MISSING")

        if _state_at_least(entry, "READ_BACK_VERIFIED"):
            if readback.get("status") != "PASS":
                failures.append(f"{prefix} READBACK_NOT_PASS")
            if readback.get("method") == "NOT_EXERCISED":
                failures.append(f"{prefix} READBACK_METHOD_NOT_EXERCISED")
            if readback.get("content_digest") != content.get("digest"):
                failures.append(f"{prefix} READBACK_DIGEST_MISMATCH")
            if not readback.get("observed_at"):
                failures.append(f"{prefix} READBACK_TIME_MISSING")

        if state == "ADMITTED":
            if rights.get("decision") != "PASS":
                failures.append(f"{prefix} ADMITTED_WITHOUT_RIGHTS_PASS")
            if completeness.get("status") != "COMPLETE":
                failures.append(f"{prefix} ADMITTED_WITHOUT_COMPLETE_SOURCE")
            if readback.get("status") != "PASS":
                failures.append(f"{prefix} ADMITTED_WITHOUT_READBACK")

        if retention.get("policy") == "COMMIT_ALLOWED":
            if not retention.get("retained_path") or not retention.get(
                "retention_digest"
            ):
                failures.append(f"{prefix} COMMITTED_RETENTION_UNBOUND")

    expected_digest = compute_registry_digest(registry)
    if registry.get("registry_digest") != expected_digest:
        failures.append("registry: REGISTRY_DIGEST_MISMATCH")
    return failures


def validate_registry(
    registry: dict[str, Any], schema: dict[str, Any]
) -> list[str]:
    failures: list[str] = []
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(registry), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        failures.append(f"schema:{location}: {error.message}")
    if not failures:
        failures.extend(_semantic_failures(registry))
    return failures


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RegistryError(f"missing {label}: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RegistryError(f"invalid {label} JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RegistryError(f"{label} must be a JSON object: {path}")
    return payload


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument(
        "--schema",
        type=Path,
        default=root / "schemas" / "source-registry.schema.json",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    registry = _load_json(args.registry, "registry")
    schema = _load_json(args.schema, "schema")
    failures = validate_registry(registry, schema)
    canonical = canonical_document(registry)
    if args.check and args.registry.read_text(encoding="utf-8") != canonical:
        failures.append("registry: CANONICAL_DOCUMENT_DRIFT")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(canonical, encoding="utf-8")

    report = {
        "evidence_mode": registry.get("evidence_mode"),
        "failure_count": len(failures),
        "failures": failures,
        "registry_digest": compute_registry_digest(registry),
        "registry_id": registry.get("registry_id"),
        "status": "PASS" if not failures else "FAIL",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RegistryError as error:
        print(f"source registry unusable: {error}", file=sys.stderr)
        raise SystemExit(2) from error
