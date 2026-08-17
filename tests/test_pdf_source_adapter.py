"""Fail-closed tests for the live PDF source adapter."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pdf_source_adapter as adapter  # noqa: E402
import source_registry  # noqa: E402


DESCRIPTOR_SCHEMA = json.loads(
    (ROOT / "schemas" / "pdf-source-descriptor.schema.json").read_text(encoding="utf-8")
)
REGISTRY_SCHEMA = json.loads(
    (ROOT / "schemas" / "source-registry.schema.json").read_text(encoding="utf-8")
)
CANARY = ROOT / "evals" / "source-intake" / "modern-web-architecture"


def synthetic_pdf(page_count: int = 2) -> bytes:
    pages = b"\n".join(
        f"{index} 0 obj << /Type /Page /Parent 99 0 R >> endobj".encode()
        for index in range(1, page_count + 1)
    )
    return b"%PDF-1.4\n" + pages + b"\n%%EOF\n"


def sha256(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def descriptor_for(payload: bytes, page_count: int = 2) -> dict:
    return {
        "schema_version": "pdf-source-descriptor@1",
        "source_id": "pdf:test-subject",
        "source_dependency_key": "drive-file:test-subject",
        "requested_url": "https://drive.google.com/file/d/test-subject/view",
        "resolved_url": "https://drive.google.com/file/d/test-subject/view",
        "external_id": "test-subject",
        "observed_revision": f"drive:size={len(payload)};sha256={sha256(payload)[7:]}",
        "expected_digest": sha256(payload),
        "expected_size_bytes": len(payload),
        "expected_page_count": page_count,
        "primary_or_secondary": "SECONDARY",
        "producer_subject": {
            "repository": "ed3c/ai-content-notes",
            "revision": "1" * 40,
            "tree_sha": "2" * 40,
        },
        "generated_at": "2026-08-17T19:27:06Z",
        "resolved_at": "2026-08-17T19:27:06Z",
        "rights": {
            "basis": "OWNER_PROVIDED",
            "decision": "PASS",
            "evidence_uri": "https://github.com/ed3c/ai-content-notes/issues/51",
            "reviewed_at": "2026-08-17T19:27:06Z",
        },
        "completeness": {"status": "COMPLETE", "reviewed": True, "missing_parts": []},
        "content_profile": {
            "has_text": True,
            "has_images": True,
            "has_tables": True,
            "material_visuals": True,
        },
        "visual_review": {
            "status": "PASS",
            "reviewed_page_range": f"1-{page_count}",
            "material_visual_pages": [1],
            "regions": [
                {"page": 1, "region": "full-page", "kind": "MIXED", "summary": "test visual"}
            ],
            "reviewed_at": "2026-08-17T19:27:06Z",
            "reviewer_mode": "MODEL_VISUAL_REVIEW",
        },
        "retention": {"policy": "EXTERNAL_REFERENCE_ONLY"},
        "projection_mode": "OWNER_DECISION_PENDING",
        "authority_ceiling": "SOURCE_INPUT_ONLY",
    }


def write_pdf(tmp_path: Path, payload: bytes) -> Path:
    path = tmp_path / "subject.pdf"
    path.write_bytes(payload)
    return path


def test_valid_pdf_generates_live_admitted_registry(tmp_path: Path) -> None:
    payload = synthetic_pdf()
    observation = adapter.inspect_pdf(write_pdf(tmp_path, payload))
    descriptor = descriptor_for(payload)
    assert adapter.validate_descriptor(descriptor, DESCRIPTOR_SCHEMA, observation) == []
    registry = adapter.build_registry(descriptor, observation)
    assert source_registry.validate_registry(registry, REGISTRY_SCHEMA) == []
    entry = registry["entries"][0]
    assert registry["evidence_mode"] == "LIVE"
    assert entry["state"] == "ADMITTED"
    assert entry["authority_ceiling"] == "SOURCE_INPUT_ONLY"
    assert entry["readback"]["content_digest"] == observation["sha256"]


@pytest.mark.parametrize(
    ("field", "value", "failure"),
    [
        ("expected_digest", "sha256:" + "0" * 64, "PDF_DIGEST_MISMATCH"),
        ("expected_size_bytes", 1, "PDF_SIZE_MISMATCH"),
        ("expected_page_count", 9, "PDF_PAGE_COUNT_MISMATCH"),
    ],
)
def test_exact_byte_contract_fails_closed(
    tmp_path: Path, field: str, value: object, failure: str
) -> None:
    payload = synthetic_pdf()
    observation = adapter.inspect_pdf(write_pdf(tmp_path, payload))
    descriptor = descriptor_for(payload)
    descriptor[field] = value
    assert any(failure in item for item in adapter.validate_descriptor(descriptor, DESCRIPTOR_SCHEMA, observation))


def test_non_pdf_header_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(adapter.PdfSourceError, match="not a PDF header"):
        adapter.inspect_pdf(write_pdf(tmp_path, b"not a pdf\n%%EOF\n"))


def test_missing_eof_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(adapter.PdfSourceError, match="EOF marker missing"):
        adapter.inspect_pdf(write_pdf(tmp_path, b"%PDF-1.4\n/Type /Page\n"))


def test_material_visuals_require_regions(tmp_path: Path) -> None:
    payload = synthetic_pdf()
    observation = adapter.inspect_pdf(write_pdf(tmp_path, payload))
    descriptor = descriptor_for(payload)
    descriptor["visual_review"]["regions"] = []
    failures = adapter.validate_descriptor(descriptor, DESCRIPTOR_SCHEMA, observation)
    assert any("MATERIAL_VISUAL_LOCATORS_MISSING" in item for item in failures)


def test_every_declared_material_visual_page_requires_a_region(tmp_path: Path) -> None:
    payload = synthetic_pdf()
    observation = adapter.inspect_pdf(write_pdf(tmp_path, payload))
    descriptor = descriptor_for(payload)
    descriptor["visual_review"]["material_visual_pages"] = [1, 2]
    failures = adapter.validate_descriptor(descriptor, DESCRIPTOR_SCHEMA, observation)
    assert any("MATERIAL_VISUAL_PAGE_WITHOUT_REGION" in item for item in failures)


def test_visual_pages_must_be_in_range(tmp_path: Path) -> None:
    payload = synthetic_pdf()
    observation = adapter.inspect_pdf(write_pdf(tmp_path, payload))
    descriptor = descriptor_for(payload)
    descriptor["visual_review"]["material_visual_pages"] = [3]
    descriptor["visual_review"]["regions"][0]["page"] = 3
    failures = adapter.validate_descriptor(descriptor, DESCRIPTOR_SCHEMA, observation)
    assert any("OUT_OF_RANGE:3" in item for item in failures)


def test_rights_must_pass_before_admission(tmp_path: Path) -> None:
    payload = synthetic_pdf()
    observation = adapter.inspect_pdf(write_pdf(tmp_path, payload))
    descriptor = descriptor_for(payload)
    descriptor["rights"]["decision"] = "NEEDS_REVIEW"
    failures = adapter.validate_descriptor(descriptor, DESCRIPTOR_SCHEMA, observation)
    assert any("SOURCE_RIGHTS_NOT_PASS" in item for item in failures)


def test_source_must_be_complete_before_admission(tmp_path: Path) -> None:
    payload = synthetic_pdf()
    observation = adapter.inspect_pdf(write_pdf(tmp_path, payload))
    descriptor = descriptor_for(payload)
    descriptor["completeness"] = {
        "status": "PARTIAL",
        "reviewed": True,
        "missing_parts": ["page 2"],
    }
    failures = adapter.validate_descriptor(descriptor, DESCRIPTOR_SCHEMA, observation)
    assert any("SOURCE_COMPLETENESS_NOT_PASS" in item for item in failures)


def test_raw_pdf_commit_is_not_admitted_in_this_leaf(tmp_path: Path) -> None:
    payload = synthetic_pdf()
    observation = adapter.inspect_pdf(write_pdf(tmp_path, payload))
    descriptor = descriptor_for(payload)
    descriptor["retention"] = {"policy": "COMMIT_ALLOWED", "retained_path": "sources/test.pdf"}
    failures = adapter.validate_descriptor(descriptor, DESCRIPTOR_SCHEMA, observation)
    assert any("RAW_PDF_COMMIT_NOT_ADMITTED" in item for item in failures)


def test_generation_is_deterministic(tmp_path: Path) -> None:
    payload = synthetic_pdf()
    observation = adapter.inspect_pdf(write_pdf(tmp_path, payload))
    descriptor = descriptor_for(payload)
    first = adapter.build_registry(descriptor, observation)
    second = adapter.build_registry(copy.deepcopy(descriptor), copy.deepcopy(observation))
    assert first == second
    assert adapter.canonical_json(first) == adapter.canonical_json(second)


def test_receipt_preserves_non_claims(tmp_path: Path) -> None:
    payload = synthetic_pdf()
    observation = adapter.inspect_pdf(write_pdf(tmp_path, payload))
    descriptor = descriptor_for(payload)
    registry = adapter.build_registry(descriptor, observation)
    receipt = adapter.build_receipt(descriptor, observation, registry)
    assert receipt["authority_ceiling"] == "SOURCE_INPUT_ONLY"
    assert any("not factual accuracy" in item for item in receipt["non_claims"])
    assert any("paid demand" in item for item in receipt["non_claims"])


def test_committed_live_canary_packet_is_self_consistent() -> None:
    descriptor_path = CANARY / "source-descriptor.json"
    registry_path = CANARY / "source-registry.json"
    receipt_path = CANARY / "readback-receipt.json"
    visual_path = CANARY / "visual-review.json"
    if not all(path.is_file() for path in (descriptor_path, registry_path, receipt_path, visual_path)):
        pytest.skip("live canary is added in the child materialization commit")

    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    visual = json.loads(visual_path.read_text(encoding="utf-8"))

    assert source_registry.validate_registry(registry, REGISTRY_SCHEMA) == []
    assert registry["registry_digest"] == receipt["source_registry_digest"]
    assert registry["entries"][0]["content"]["digest"] == descriptor["expected_digest"]
    assert receipt["local_file"]["sha256"] == descriptor["expected_digest"]
    assert receipt["local_file"]["size_bytes"] == descriptor["expected_size_bytes"]
    assert receipt["local_file"]["page_count"] == descriptor["expected_page_count"]
    assert visual["status"] == descriptor["visual_review"]["status"]
    assert visual["material_visual_pages"] == descriptor["visual_review"]["material_visual_pages"]
    assert registry["entries"][0]["authority_ceiling"] == "SOURCE_INPUT_ONLY"
