"""Source registry contracts fail closed on identity and evidence laundering."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import source_registry  # noqa: E402

SCHEMA = json.loads(
    (REPOSITORY_ROOT / "schemas" / "source-registry.schema.json").read_text(
        encoding="utf-8"
    )
)
VALID_PATH = (
    REPOSITORY_ROOT
    / "examples"
    / "source-registry"
    / "example-source-registry.json"
)
INVALID_TITLE_PATH = (
    REPOSITORY_ROOT
    / "examples"
    / "source-registry"
    / "invalid-title-snippet.json"
)


def load_valid() -> dict:
    return json.loads(VALID_PATH.read_text(encoding="utf-8"))


def refresh(registry: dict) -> dict:
    return source_registry.canonicalize(registry)


def failures(registry: dict) -> list[str]:
    return source_registry.validate_registry(refresh(registry), SCHEMA)


def test_example_registry_is_valid_and_canonical() -> None:
    registry = load_valid()
    assert source_registry.validate_registry(registry, SCHEMA) == []
    assert VALID_PATH.read_text(encoding="utf-8") == (
        source_registry.canonical_document(registry)
    )


def test_fixture_covers_github_pdf_doc_and_sheet() -> None:
    kinds = {entry["source_kind"] for entry in load_valid()["entries"]}
    assert kinds == {"GITHUB_BLOB", "PDF", "GOOGLE_DOC", "GOOGLE_SHEET"}


def test_title_or_snippet_only_cannot_advance() -> None:
    registry = json.loads(INVALID_TITLE_PATH.read_text(encoding="utf-8"))
    result = source_registry.validate_registry(registry, SCHEMA)
    assert any("TITLE_SNIPPET_PROMOTED" in item for item in result)


def test_title_or_snippet_only_can_be_preserved_as_blocked() -> None:
    registry = load_valid()
    entry = registry["entries"][0]
    registry["entries"] = [entry]
    entry["state"] = "BLOCKED"
    entry["content"]["content_scope"] = "TITLE_OR_SNIPPET_ONLY"
    entry["content"].pop("digest", None)
    entry["rights"]["decision"] = "BLOCKED"
    entry["completeness"]["status"] = "BLOCKED"
    entry["readback"] = {"status": "NOT_EXERCISED", "method": "NOT_EXERCISED"}
    entry["blockers"] = ["complete source body unavailable"]
    assert failures(registry) == []


def test_public_visibility_is_not_a_rights_basis() -> None:
    registry = load_valid()
    registry["entries"][0]["rights"]["basis"] = "PUBLIC_VISIBILITY_ONLY"
    result = failures(registry)
    assert any("PUBLIC_VISIBILITY_USED_AS_RIGHTS" in item for item in result)


def test_github_blob_requires_exact_commit_blob_and_path() -> None:
    registry = load_valid()
    registry["entries"][0]["identity"].pop("commit_sha")
    result = failures(registry)
    assert any("GITHUB_BLOB_IDENTITY_INCOMPLETE" in item for item in result)


def test_github_resolved_url_must_contain_the_bound_commit() -> None:
    registry = load_valid()
    registry["entries"][0]["resolved_url"] = (
        "https://github.com/ed3c/ai-content-notes/blob/main/AGENTS.md"
    )
    result = failures(registry)
    assert any("GITHUB_RESOLVED_URL_NOT_IMMUTABLE" in item for item in result)


def test_sheet_requires_range_row_key_and_locators() -> None:
    registry = load_valid()
    entry = next(
        item for item in registry["entries"] if item["source_kind"] == "GOOGLE_SHEET"
    )
    entry["identity"].pop("row_key")
    entry["locators"] = [
        item for item in entry["locators"] if item["kind"] != "row_key"
    ]
    result = failures(registry)
    assert any("SHEET_RANGE_OR_ROW_KEY_MISSING" in item for item in result)
    assert any("SHEET_LOCATORS_MISSING" in item for item in result)


def test_drive_notification_cannot_be_content_proof() -> None:
    registry = load_valid()
    entry = next(
        item for item in registry["entries"] if item["source_kind"] == "GOOGLE_DOC"
    )
    entry["change_notification_only"] = True
    result = failures(registry)
    assert any("NOTIFICATION_USED_AS_CONTENT_PROOF" in item for item in result)
    assert any("NOTIFICATION_ADVANCED_STATE" in item for item in result)


def test_material_pdf_visuals_require_a_visual_locator() -> None:
    registry = load_valid()
    entry = next(item for item in registry["entries"] if item["source_kind"] == "PDF")
    entry["locators"] = [
        item for item in entry["locators"] if item["kind"] != "visual_region"
    ]
    result = failures(registry)
    assert any("PDF_VISUAL_LOCATOR_MISSING" in item for item in result)


def test_material_pdf_visuals_require_visual_review() -> None:
    registry = load_valid()
    entry = next(item for item in registry["entries"] if item["source_kind"] == "PDF")
    entry["content"]["visual_review_state"] = "NOT_EXERCISED"
    result = failures(registry)
    assert any("PDF_VISUAL_REVIEW_NOT_EXERCISED" in item for item in result)


def test_google_doc_requires_export_digest_and_revision_locator() -> None:
    registry = load_valid()
    entry = next(
        item for item in registry["entries"] if item["source_kind"] == "GOOGLE_DOC"
    )
    entry["content"].pop("export_digest")
    entry["locators"] = [
        item for item in entry["locators"] if item["kind"] != "document_revision"
    ]
    result = failures(registry)
    assert any("DOC_EXPORT_DIGEST_MISSING" in item for item in result)
    assert any("DOC_REVISION_LOCATOR_MISSING" in item for item in result)


def test_readback_digest_must_match_the_snapshot_digest() -> None:
    registry = load_valid()
    registry["entries"][0]["readback"]["content_digest"] = (
        "sha256:" + "9" * 64
    )
    result = failures(registry)
    assert any("READBACK_DIGEST_MISMATCH" in item for item in result)


def test_fixture_cannot_widen_authority_or_be_admitted() -> None:
    registry = load_valid()
    registry["entries"][0]["authority_ceiling"] = "SOURCE_INPUT_ONLY"
    registry["entries"][0]["state"] = "ADMITTED"
    result = failures(registry)
    assert any("FIXTURE_AUTHORITY_WIDENED" in item for item in result)
    assert any("FIXTURE_PROMOTED_TO_ADMITTED" in item for item in result)


def test_duplicate_source_ids_fail_closed() -> None:
    registry = load_valid()
    registry["entries"].append(copy.deepcopy(registry["entries"][0]))
    result = failures(registry)
    assert any("DUPLICATE_SOURCE_ID" in item for item in result)


def test_live_admission_can_close_only_with_full_evidence() -> None:
    registry = load_valid()
    registry["evidence_mode"] = "LIVE"
    registry["entries"] = [registry["entries"][0]]
    entry = registry["entries"][0]
    entry["state"] = "ADMITTED"
    entry["authority_ceiling"] = "SOURCE_INPUT_ONLY"
    assert failures(registry) == []


def test_registry_digest_is_subject_bound() -> None:
    registry = load_valid()
    registry["registry_digest"] = "sha256:" + "0" * 64
    result = source_registry.validate_registry(registry, SCHEMA)
    assert result == ["registry: REGISTRY_DIGEST_MISMATCH"]
