#!/usr/bin/env python3
"""Bind exact GitHub blob bytes to a live source-registry@1 packet.

The adapter is intentionally narrow. It proves that the retained bytes are the
exact Git object the pinned GitHub URL names, by recomputing the Git blob SHA-1
from those bytes. It does not prove the source's factual accuracy, repository
intent, license validity, runtime behavior, or downstream product closure.

Git blob identity is content-addressed, so this read-back is exact and offline:
a byte that changes changes the blob SHA-1. A branch or tag URL names a moving
target and is refused; only a 40-hex commit-pinned URL can be admitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from source_registry import canonical_document, canonicalize, validate_registry


class GithubSourceError(RuntimeError):
    """Raised when a GitHub source packet cannot be read or generated."""


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise GithubSourceError(f"missing {label}: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GithubSourceError(f"invalid {label} JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise GithubSourceError(f"{label} must be a JSON object: {path}")
    return payload


def _sha256(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def git_blob_sha1(payload: bytes) -> str:
    """Return the Git object name for these bytes, matching `git hash-object`."""
    header = f"blob {len(payload)}\0".encode()
    return hashlib.sha1(header + payload).hexdigest()  # noqa: S324 - Git object identity


def inspect_blob(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise GithubSourceError(f"missing retained blob: {path}")
    payload = path.read_bytes()
    if not payload:
        raise GithubSourceError(f"retained blob is empty: {path}")
    return {
        "file_name": path.name,
        "size_bytes": len(payload),
        "sha256": _sha256(payload),
        "git_blob_sha1": git_blob_sha1(payload),
    }


def _schema_failures(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures: list[str] = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        failures.append(f"schema:{location}: {error.message}")
    return failures


def validate_descriptor(
    descriptor: dict[str, Any],
    descriptor_schema: dict[str, Any],
    observation: dict[str, Any],
) -> list[str]:
    failures = _schema_failures(descriptor, descriptor_schema)
    if failures:
        return failures

    # The exact read-back: the retained bytes must be the named Git object.
    if descriptor["blob_sha"] != observation["git_blob_sha1"]:
        failures.append("descriptor: GITHUB_BLOB_SHA_MISMATCH")
    if descriptor["expected_digest"] != observation["sha256"]:
        failures.append("descriptor: GITHUB_CONTENT_DIGEST_MISMATCH")
    if descriptor["expected_size_bytes"] != observation["size_bytes"]:
        failures.append("descriptor: GITHUB_SIZE_MISMATCH")

    # A branch/tag URL is a moving target and can never carry exact read-back.
    resolved_url = str(descriptor["resolved_url"])
    if descriptor["commit_sha"] not in resolved_url:
        failures.append("descriptor: GITHUB_RESOLVED_URL_NOT_COMMIT_PINNED")
    if descriptor["path"] not in resolved_url:
        failures.append("descriptor: GITHUB_RESOLVED_URL_PATH_MISMATCH")
    if descriptor["repository"] not in resolved_url:
        failures.append("descriptor: GITHUB_RESOLVED_URL_REPOSITORY_MISMATCH")

    rights = descriptor["rights"]
    completeness = descriptor["completeness"]
    profile = descriptor["content_profile"]

    if rights["decision"] != "PASS":
        failures.append("descriptor: SOURCE_RIGHTS_NOT_PASS")
    if rights["basis"] in {"PUBLIC_VISIBILITY_ONLY", "UNKNOWN"}:
        failures.append("descriptor: PUBLIC_VISIBILITY_USED_AS_RIGHTS")
    if completeness["status"] != "COMPLETE" or not completeness["reviewed"]:
        failures.append("descriptor: SOURCE_COMPLETENESS_NOT_PASS")
    if completeness["missing_parts"]:
        failures.append("descriptor: COMPLETE_SOURCE_HAS_MISSING_PARTS")
    if profile["content_scope"] != "COMPLETE_BODY":
        failures.append("descriptor: GITHUB_PARTIAL_CONTENT_NOT_ADMITTED")

    if descriptor["authority_ceiling"] != "SOURCE_INPUT_ONLY":
        failures.append("descriptor: AUTHORITY_CEILING_WIDENED")
    return failures


def build_registry(
    descriptor: dict[str, Any], observation: dict[str, Any]
) -> dict[str, Any]:
    entry = {
        "source_id": descriptor["source_id"],
        "source_kind": "GITHUB_BLOB",
        "source_dependency_key": descriptor["source_dependency_key"],
        "primary_or_secondary": descriptor["primary_or_secondary"],
        "requested_url": descriptor["requested_url"],
        "resolved_url": descriptor["resolved_url"],
        "state": "ADMITTED",
        "identity": {
            "immutable": True,
            "resolved_at": descriptor["resolved_at"],
            "repository": descriptor["repository"],
            "commit_sha": descriptor["commit_sha"],
            "blob_sha": descriptor["blob_sha"],
            "path": descriptor["path"],
        },
        "rights": descriptor["rights"],
        "completeness": descriptor["completeness"],
        "content": {
            "content_scope": descriptor["content_profile"]["content_scope"],
            "media_type": descriptor["content_profile"]["media_type"],
            "digest": observation["sha256"],
            "size_bytes": observation["size_bytes"],
            "has_text": descriptor["content_profile"]["has_text"],
            "has_images": descriptor["content_profile"]["has_images"],
            "has_tables": descriptor["content_profile"]["has_tables"],
            "material_visuals": False,
            "visual_review_state": "NOT_APPLICABLE",
        },
        "locators": [
            {"kind": "path", "value": descriptor["path"]},
            {"kind": "commit", "value": descriptor["commit_sha"]},
        ],
        "readback": {
            "status": "PASS",
            "method": "GITHUB_BLOB_SHA",
            "observed_at": descriptor["resolved_at"],
            "evidence_uri": descriptor["resolved_url"],
            "content_digest": observation["sha256"],
        },
        "retention": descriptor["retention"],
        "change_notification_only": False,
        "authority_ceiling": descriptor["authority_ceiling"],
        "blockers": [],
    }
    registry = {
        "schema_version": "source-registry@1",
        "registry_id": f"registry-{descriptor['source_id'].replace(':', '-')}",
        "evidence_mode": "LIVE",
        "canonical_authority": "GITHUB",
        "projection_mode": descriptor["projection_mode"],
        "subject": descriptor["producer_subject"],
        "generated_at": descriptor["generated_at"],
        "entries": [entry],
        "registry_digest": "sha256:" + "0" * 64,
    }
    return canonicalize(registry)


def build_receipt(
    descriptor: dict[str, Any],
    observation: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "github-source-readback-receipt@1",
        "source_id": descriptor["source_id"],
        "source_dependency_key": descriptor["source_dependency_key"],
        "source_subject": {
            "repository": descriptor["repository"],
            "commit_sha": descriptor["commit_sha"],
            "blob_sha": descriptor["blob_sha"],
            "path": descriptor["path"],
            "url": descriptor["resolved_url"],
        },
        "producer_subject": descriptor["producer_subject"],
        "observed_at": descriptor["resolved_at"],
        "local_file": observation,
        "readback_method": "GIT_BLOB_SHA1_RECOMPUTE",
        "states": {
            "identity": "PASS",
            "rights": descriptor["rights"]["decision"],
            "completeness": descriptor["completeness"]["status"],
            "readback": "PASS",
            "source_registry": "PASS",
        },
        "source_registry_digest": registry["registry_digest"],
        "retention_policy": descriptor["retention"]["policy"],
        "authority_ceiling": descriptor["authority_ceiling"],
        "non_claims": [
            "The receipt proves exact Git blob identity, not the file's factual accuracy.",
            "Repository content, licenses, performance and product internals remain source statements or hypotheses.",
            "Source admission does not prove implementation, user value, paid demand, merge, or release.",
        ],
    }


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def generate(
    blob_path: Path,
    descriptor_path: Path,
    descriptor_schema_path: Path,
    registry_schema_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    observation = inspect_blob(blob_path)
    descriptor = _load_json(descriptor_path, "GitHub descriptor")
    descriptor_schema = _load_json(descriptor_schema_path, "GitHub descriptor schema")
    registry_schema = _load_json(registry_schema_path, "source registry schema")

    failures = validate_descriptor(descriptor, descriptor_schema, observation)
    if failures:
        raise GithubSourceError("; ".join(failures))
    registry = build_registry(descriptor, observation)
    registry_failures = validate_registry(registry, registry_schema)
    if registry_failures:
        raise GithubSourceError("; ".join(registry_failures))
    receipt = build_receipt(descriptor, observation, registry)
    return registry, receipt, observation


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blob", type=Path, required=True)
    parser.add_argument("--descriptor", type=Path, required=True)
    parser.add_argument(
        "--descriptor-schema",
        type=Path,
        default=root / "schemas" / "github-source-descriptor.schema.json",
    )
    parser.add_argument(
        "--registry-schema",
        type=Path,
        default=root / "schemas" / "source-registry.schema.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        registry, receipt, observation = generate(
            args.blob,
            args.descriptor,
            args.descriptor_schema,
            args.registry_schema,
        )
    except GithubSourceError as error:
        print(f"GitHub source adapter rejected the subject: {error}", file=sys.stderr)
        return 2

    registry_text = canonical_document(registry)
    receipt_text = canonical_json(receipt)
    failures: list[str] = []
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != registry_text:
            failures.append("OUTPUT_REGISTRY_DRIFT")
        if not args.receipt.is_file() or args.receipt.read_text(encoding="utf-8") != receipt_text:
            failures.append("OUTPUT_RECEIPT_DRIFT")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(registry_text, encoding="utf-8")
        args.receipt.write_text(receipt_text, encoding="utf-8")

    report = {
        "failure_count": len(failures),
        "failures": failures,
        "observation": observation,
        "registry_digest": registry["registry_digest"],
        "source_id": receipt["source_id"],
        "status": "PASS" if not failures else "FAIL",
    }
    print(canonical_json(report), end="")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
