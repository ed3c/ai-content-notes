#!/usr/bin/env python3
"""Bind exact PDF bytes to a live source-registry@1 packet.

The adapter is intentionally narrow. It proves byte identity, basic PDF
structure, declared page coverage, and reviewed visual locators. It does not
prove the source's factual accuracy, product internals, licenses, performance,
market demand, or downstream product closure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from source_registry import canonical_document, canonicalize, validate_registry

PDF_HEADER = b"%PDF-"
PDF_EOF = b"%%EOF"
PAGE_PATTERN = re.compile(br"/Type\s*/Page\b")


class PdfSourceError(RuntimeError):
    """Raised when a PDF source packet cannot be read or generated."""


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise PdfSourceError(f"missing {label}: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PdfSourceError(f"invalid {label} JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PdfSourceError(f"{label} must be a JSON object: {path}")
    return payload


def _sha256(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def inspect_pdf(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise PdfSourceError(f"missing PDF: {path}")
    payload = path.read_bytes()
    if not payload.startswith(PDF_HEADER):
        raise PdfSourceError(f"not a PDF header: {path}")
    if not payload.rstrip().endswith(PDF_EOF):
        raise PdfSourceError(f"PDF EOF marker missing: {path}")
    page_count = len(PAGE_PATTERN.findall(payload))
    if page_count < 1:
        raise PdfSourceError(f"no page objects found: {path}")
    return {
        "file_name": path.name,
        "size_bytes": len(payload),
        "sha256": _sha256(payload),
        "page_count": page_count,
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

    if descriptor["expected_digest"] != observation["sha256"]:
        failures.append("descriptor: PDF_DIGEST_MISMATCH")
    if descriptor["expected_size_bytes"] != observation["size_bytes"]:
        failures.append("descriptor: PDF_SIZE_MISMATCH")
    if descriptor["expected_page_count"] != observation["page_count"]:
        failures.append("descriptor: PDF_PAGE_COUNT_MISMATCH")

    rights = descriptor["rights"]
    completeness = descriptor["completeness"]
    visual = descriptor["visual_review"]
    profile = descriptor["content_profile"]

    if rights["decision"] != "PASS":
        failures.append("descriptor: SOURCE_RIGHTS_NOT_PASS")
    if completeness["status"] != "COMPLETE" or not completeness["reviewed"]:
        failures.append("descriptor: SOURCE_COMPLETENESS_NOT_PASS")
    if completeness["missing_parts"]:
        failures.append("descriptor: COMPLETE_SOURCE_HAS_MISSING_PARTS")

    start_page, end_page = (int(part) for part in visual["reviewed_page_range"].split("-", 1))
    if start_page != 1 or end_page != observation["page_count"]:
        failures.append("descriptor: VISUAL_REVIEW_RANGE_INCOMPLETE")

    pages = visual["material_visual_pages"]
    regions = visual["regions"]
    region_pages = {item["page"] for item in regions}
    if profile["material_visuals"]:
        if visual["status"] not in {"PASS", "PARTIAL"}:
            failures.append("descriptor: MATERIAL_VISUAL_REVIEW_NOT_EXERCISED")
        if not pages or not regions:
            failures.append("descriptor: MATERIAL_VISUAL_LOCATORS_MISSING")
        if not set(pages).issubset(region_pages):
            failures.append("descriptor: MATERIAL_VISUAL_PAGE_WITHOUT_REGION")
    for page in pages:
        if page < 1 or page > observation["page_count"]:
            failures.append(f"descriptor: MATERIAL_VISUAL_PAGE_OUT_OF_RANGE:{page}")
    for item in regions:
        page = item["page"]
        if page < 1 or page > observation["page_count"]:
            failures.append(f"descriptor: VISUAL_REGION_PAGE_OUT_OF_RANGE:{page}")

    if descriptor["authority_ceiling"] != "SOURCE_INPUT_ONLY":
        failures.append("descriptor: AUTHORITY_CEILING_WIDENED")
    if descriptor["retention"]["policy"] == "COMMIT_ALLOWED":
        failures.append("descriptor: RAW_PDF_COMMIT_NOT_ADMITTED_IN_THIS_LEAF")
    return failures


def _visual_locators(descriptor: dict[str, Any]) -> list[dict[str, str]]:
    locators: list[dict[str, str]] = [
        {"kind": "page", "value": f"1-{descriptor['expected_page_count']}"},
        {"kind": "section", "value": "complete PDF body"},
    ]
    for item in descriptor["visual_review"]["regions"]:
        locators.append(
            {
                "kind": "visual_region",
                "value": f"page:{item['page']}:{item['region']}:{item['kind']}",
            }
        )
    return locators


def build_registry(
    descriptor: dict[str, Any], observation: dict[str, Any]
) -> dict[str, Any]:
    entry = {
        "source_id": descriptor["source_id"],
        "source_kind": "PDF",
        "source_dependency_key": descriptor["source_dependency_key"],
        "primary_or_secondary": descriptor["primary_or_secondary"],
        "requested_url": descriptor["requested_url"],
        "resolved_url": descriptor["resolved_url"],
        "state": "ADMITTED",
        "identity": {
            "immutable": False,
            "resolved_at": descriptor["resolved_at"],
            "external_id": descriptor["external_id"],
            "observed_revision": descriptor["observed_revision"],
        },
        "rights": descriptor["rights"],
        "completeness": descriptor["completeness"],
        "content": {
            "content_scope": "COMPLETE_BODY",
            "media_type": "application/pdf",
            "digest": observation["sha256"],
            "size_bytes": observation["size_bytes"],
            "has_text": descriptor["content_profile"]["has_text"],
            "has_images": descriptor["content_profile"]["has_images"],
            "has_tables": descriptor["content_profile"]["has_tables"],
            "material_visuals": descriptor["content_profile"]["material_visuals"],
            "visual_review_state": descriptor["visual_review"]["status"],
        },
        "locators": _visual_locators(descriptor),
        "readback": {
            "status": "PASS",
            "method": "LOCAL_FILE_HASH",
            "observed_at": descriptor["resolved_at"],
            "evidence_uri": descriptor["resolved_url"],
            "content_digest": observation["sha256"],
        },
        "retention": {"policy": descriptor["retention"]["policy"]},
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
    visual = descriptor["visual_review"]
    return {
        "schema_version": "pdf-source-readback-receipt@1",
        "source_id": descriptor["source_id"],
        "source_dependency_key": descriptor["source_dependency_key"],
        "source_subject": {
            "drive_file_id": descriptor["external_id"],
            "url": descriptor["resolved_url"],
            "observed_revision": descriptor["observed_revision"],
        },
        "producer_subject": descriptor["producer_subject"],
        "observed_at": descriptor["resolved_at"],
        "local_file": observation,
        "visual_review": {
            "status": visual["status"],
            "reviewed_page_range": visual["reviewed_page_range"],
            "material_visual_pages": sorted(visual["material_visual_pages"]),
            "region_count": len(visual["regions"]),
            "reviewer_mode": visual["reviewer_mode"],
        },
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
            "The receipt proves exact source bytes and declared locators, not factual accuracy.",
            "Named product internals, libraries, performance, costs, and licenses remain source statements or hypotheses.",
            "Source admission does not prove implementation, user value, paid demand, merge, or release.",
        ],
    }


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def generate(
    pdf_path: Path,
    descriptor_path: Path,
    descriptor_schema_path: Path,
    registry_schema_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    observation = inspect_pdf(pdf_path)
    descriptor = _load_json(descriptor_path, "PDF descriptor")
    descriptor_schema = _load_json(descriptor_schema_path, "PDF descriptor schema")
    registry_schema = _load_json(registry_schema_path, "source registry schema")

    failures = validate_descriptor(descriptor, descriptor_schema, observation)
    if failures:
        raise PdfSourceError("; ".join(failures))
    registry = build_registry(descriptor, observation)
    registry_failures = validate_registry(registry, registry_schema)
    if registry_failures:
        raise PdfSourceError("; ".join(registry_failures))
    receipt = build_receipt(descriptor, observation, registry)
    return registry, receipt, observation


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--descriptor", type=Path, required=True)
    parser.add_argument(
        "--descriptor-schema",
        type=Path,
        default=root / "schemas" / "pdf-source-descriptor.schema.json",
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
            args.pdf,
            args.descriptor,
            args.descriptor_schema,
            args.registry_schema,
        )
    except PdfSourceError as error:
        print(f"PDF source adapter rejected the subject: {error}", file=sys.stderr)
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
