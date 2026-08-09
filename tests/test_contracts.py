from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "notes/agent-runtime/2026-07-30-langsmith-llm-gateway-runtime-controls.md"
CLAIM_MAP = ROOT / "examples/claim-maps/langsmith-llm-gateway.claim-map.json"


def load_exporter() -> ModuleType:
    path = ROOT / "tools/export_note_delta.py"
    spec = importlib.util.spec_from_file_location("export_note_delta", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_errors(instance: object, schema_name: str) -> list[str]:
    schema = load_json(ROOT / "schemas" / schema_name)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in sorted(validator.iter_errors(instance), key=str)]


def test_declared_canonical_paths_exist() -> None:
    expected = [
        "CONTEXT.md",
        "INDEX.md",
        "RANK.md",
        "MIGRATION_MANIFEST.json",
        "governance/PARAMETERS.md",
        "governance/WORKFLOW.md",
        "governance/CARD_PROTOCOL_V6_6.md",
        "governance/CITATION_MAPPING.md",
        "governance/LICENSE_POLICY.md",
        "governance/SHEET_CONTRACT.md",
        "schemas/claim-map.schema.json",
        "schemas/note-delta.schema.json",
        "schemas/rank-entry.schema.json",
        "templates/NOTE_TEMPLATE.md",
        "templates/LIBRARY_CANDIDATE_TEMPLATE.md",
    ]
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_all_contract_schemas_are_valid_draft_2020_12() -> None:
    for name in (
        "claim-map.schema.json",
        "note-delta.schema.json",
        "rank-entry.schema.json",
    ):
        Draft202012Validator.check_schema(load_json(ROOT / "schemas" / name))


def test_complete_note_claim_map_is_schema_valid_and_blob_bound() -> None:
    claim_map = load_json(CLAIM_MAP)
    assert schema_errors(claim_map, "claim-map.schema.json") == []

    exporter = load_exporter()
    frontmatter, bound_map, note_rel, claim_map_rel, blob_sha = exporter.validate_binding(
        NOTE, CLAIM_MAP, ROOT
    )
    assert frontmatter["id"] == "langchain:llm-gateway-runtime-controls"
    assert note_rel == "notes/agent-runtime/2026-07-30-langsmith-llm-gateway-runtime-controls.md"
    assert claim_map_rel == "examples/claim-maps/langsmith-llm-gateway.claim-map.json"
    assert blob_sha == "e3ada83629260ac9267d7ae97f3bbba7c08892a6"
    assert bound_map["note"]["blob_sha"] == blob_sha


def test_claim_ids_are_unique_and_non_facts_remain_review_gated() -> None:
    claims = load_json(CLAIM_MAP)["claims"]
    ids = [claim["id"] for claim in claims]
    assert len(ids) == len(set(ids))
    assert len(claims) == 5
    for claim in claims:
        if claim["kind"] in {"inference", "assumption", "invariant"}:
            assert claim["review"]["status"] in {"pending", "needs-source"}
            assert claim["status"] == "review-required"


def test_note_delta_is_deterministic_schema_valid_and_body_free() -> None:
    exporter = load_exporter()
    first = exporter.build_manifest(NOTE, CLAIM_MAP, ROOT, "0" * 40, True)
    second = exporter.build_manifest(NOTE, CLAIM_MAP, ROOT, "0" * 40, True)
    assert first == second
    assert schema_errors(first, "note-delta.schema.json") == []

    encoded = json.dumps(first, ensure_ascii=False, sort_keys=True)
    assert "### N1" not in encoded
    assert "核心衝突" not in encoded
    assert "body" not in first["changed_notes"][0]
    assert "content" not in first["changed_notes"][0]
    assert first["changed_notes"][0]["skill_impact"] == "review-and-requalify"
    assert first["changed_notes"][0]["readback_verified"] is True


def test_export_refuses_unverified_readback() -> None:
    exporter = load_exporter()
    with pytest.raises(exporter.ContractError, match="read-back"):
        exporter.build_manifest(NOTE, CLAIM_MAP, ROOT, "0" * 40, False)


def test_export_refuses_tampered_note_blob(tmp_path: Path) -> None:
    exporter = load_exporter()
    note = tmp_path / "notes" / "agent-runtime" / "sample.md"
    note.parent.mkdir(parents=True)
    note.write_text(
        """---
id: sample:note
title: Sample note
source: Example
source_url: https://example.com/source
published_at: '2026-08-09'
monetization_score: 50
category: agent-runtime
language: zh-TW
note_format: zettelkasten-v6.6-cyberpunk
storage: private-github-markdown
repository: ed3c/ai-content-notes
path: notes/agent-runtime/sample.md
citation_mapping: pending
library_mapping: pending
---

### D1：Sample
- **影子證據**：sample
""",
        encoding="utf-8",
    )
    claim_map = copy.deepcopy(load_json(CLAIM_MAP))
    claim_map["note"].update(
        {
            "id": "sample:note",
            "title": "Sample note",
            "path": "notes/agent-runtime/sample.md",
            "blob_sha": "0" * 40,
            "source_url": "https://example.com/source",
        }
    )
    sidecar = tmp_path / "examples" / "claim-maps" / "sample.claim-map.json"
    sidecar.parent.mkdir(parents=True)
    sidecar.write_text(json.dumps(claim_map), encoding="utf-8")

    with pytest.raises(exporter.ContractError, match="blob_sha"):
        exporter.validate_binding(note, sidecar, tmp_path)


def test_migration_manifest_does_not_claim_missing_legacy_notes() -> None:
    manifest = load_json(ROOT / "MIGRATION_MANIFEST.json")
    assert manifest["status"] == "incomplete"
    assert manifest["expected_legacy_note_count"] == 22
    assert manifest["materialized_legacy_entries"] == []
    assert manifest["known_issue"]["issue_number"] == 2
