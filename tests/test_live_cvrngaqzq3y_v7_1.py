from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = ROOT / "evals" / "live" / "CvRngaQZQ3Y"
MANIFEST = EVAL_ROOT / "card-manifest.json"
RUN = EVAL_ROOT / "run.json"
RESULT = EVAL_ROOT / "result.json"


def load_materializer() -> ModuleType:
    path = ROOT / "tools" / "materialize_card_batch.py"
    spec = importlib.util.spec_from_file_location("materialize_card_batch", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_prompt_and_source_are_digest_bound_without_prompt_mutation() -> None:
    manifest = load_json(MANIFEST)
    run = load_json(RUN)
    protocol = manifest["protocol"]
    source = manifest["source"]
    assert protocol["path"] == "governance/CARD_PROTOCOL_V7_1.md"
    assert protocol["git_blob_sha1"] == "7f3019f4b41a90728cd48a523d742c7c59721bf6"
    assert protocol["sha256"] == "9388c4f17172dc970f7228ded2f0df54a1111b22047faa11f8e7db36579165dd"
    assert run["protocol"]["modified_for_run"] is False
    assert source["source_dependency_key"] == "youtube-video:CvRngaQZQ3Y"
    assert source["primary_or_secondary"] == "secondary"
    assert source["normalized_transcript_sha256"] == (
        "bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
    )


def test_private_acquisition_never_grants_note_or_claim_authority() -> None:
    run = load_json(RUN)
    result = load_json(RESULT)
    acquisition = run["acquisition"]
    authority = result["authority"]
    assert acquisition["authorization_status"] == "unverified-evaluation-only"
    assert acquisition["rights_basis"] == "user-directed-evaluation"
    assert acquisition["note_completion_allowed"] is False
    assert acquisition["independent_corroboration_count"] == 0
    assert authority["may_complete_note"] is False
    assert authority["may_raise_claim_evidence"] is False
    assert authority["may_enable_skill_routing"] is False
    assert authority["may_publish_raw_transcript"] is False
    assert authority["may_count_transport_fallback_as_independent_corroboration"] is False


def test_normalization_is_exact_and_raw_source_remains_authoritative() -> None:
    manifest = load_json(MANIFEST)
    run = load_json(RUN)
    normalization = manifest["normalization"]
    assert normalization["status"] == "REVIEW_REQUIRED"
    assert normalization["raw_source_remains_authoritative"] is True
    assert normalization["raw_subject_word_count"] == 11290
    assert normalization["normalized_word_count"] == 3797
    assert normalization["removed_adjacent_duplicate_tokens"] == 7214
    assert normalization["removed_cross_cue_overlap_tokens"] == 279
    assert normalization["removed_transport_footer_characters"] == 240
    assert normalization["collapse_event_count"] == 542
    assert run["normalization"]["lexical_or_semantic_correction_performed"] is False


def test_materialized_batch_is_source_shaped_unique_and_payload_first() -> None:
    materializer = load_materializer()
    manifest, rendered = materializer.build_output(MANIFEST)
    card_ids = re.findall(
        r"^###\s+([A-Z][A-Za-z0-9._:-]*)｜.+$", rendered, re.MULTILINE
    )
    assert card_ids == manifest["card_order"]
    assert len(card_ids) == manifest["card_count"]
    assert len(card_ids) == len(set(card_ids))
    # The batch shape follows what the source supports, so the rendered series
    # sequence is checked against the declared plan rather than a fixed quota.
    assert [card_id.split("-", 1)[0] for card_id in card_ids] == manifest["series_order"]
    assert card_ids[0].startswith("N-"), "the batch must lead with a human entry"
    first_card = rendered.split("### ", 2)[1]
    first_lines = [line.strip() for line in first_card.splitlines() if line.strip()]
    assert "**核心命題**" in first_lines[1]
    assert "**為什麼重要**" in first_lines[2]
    assert rendered.count("<!-- CARD_META") == 12
    assert "<!-- RUN_STATE" in rendered


def test_every_card_is_one_source_supported_decision_case() -> None:
    """Anti-fragmentation: one decision-relevant case, one card, one source.

    This replaces the previous fixed series quota. A quota only proves the
    batch matched a template; these assertions prove each rendered card is a
    distinct decision case that the exact normalized source digest supports.
    """
    materializer = load_materializer()
    manifest, rendered = materializer.build_output(MANIFEST)
    source_digest = manifest["source"]["normalized_transcript_sha256"]

    metas = [
        json.loads(block)
        for block in re.findall(r"<!-- CARD_META\s*(\{.*?\})\s*-->", rendered, re.S)
    ]
    assert len(metas) == manifest["card_count"]
    assert [meta["stable_id"] for meta in metas] == manifest["card_order"]

    canonical_keys = [meta["canonical_key"] for meta in metas]
    assert len(set(canonical_keys)) == len(canonical_keys), "merged cases must not fragment"

    evidence_bearing = 0
    for meta in metas:
        scope = meta["canonical_key"].rsplit("|", 1)[-1].strip()
        assert meta["canonical_key"].split("|", 1)[0].strip() == meta["series"]
        assert meta["source_dependency_key"] == manifest["source"]["source_dependency_key"]

        if meta["series"] in {"N", "C", "S", "P", "D"}:
            # A claim-bearing card is identified by the exact normalized source.
            evidence_bearing += 1
            assert scope == f"source-digest:{source_digest[:8]}", meta["stable_id"]
            assert f"sha256:{source_digest}" in meta["source_provenance"], meta["stable_id"]
        elif meta["series"] == "V":
            # A verification card is identified by its execution state, never by
            # the source, so an unrun replay cannot inherit source support.
            assert scope == "not-run", meta["stable_id"]
        else:
            assert meta["series"] == "K"
            # A gap card is scoped to the run that observed the gap.
            assert scope.startswith("run-"), meta["stable_id"]

    assert evidence_bearing >= 1
    assert {meta["series"] for meta in metas} <= {"N", "C", "S", "P", "D", "V", "K"}


def test_epistemic_and_test_honesty_are_preserved() -> None:
    materializer = load_materializer()
    _, rendered = materializer.build_output(MANIFEST)
    result = load_json(RESULT)
    assert "CORROBORATED" not in rendered
    assert "**Execution Status**：UNTESTED" in rendered
    assert "**Observed Result**：NOT_RUN" in rendered
    assert "**Verdict**：NOT_RUN" in rendered
    assert "**Artifacts**：NONE" in rendered
    assert result["test_honesty"]["tested_claim_count"] == 0
    assert result["status"] == "CONTINUE"
    assert all(
        state == "NOT_RUN_EXTERNALLY"
        for state in result["quality_gate_status"].values()
    )


def test_all_cards_share_one_dependency_origin_and_record_provenance() -> None:
    materializer = load_materializer()
    _, rendered = materializer.build_output(MANIFEST)
    dependencies = re.findall(
        r'"source_dependency_key":\s*"([^"]+)"', rendered
    )
    assert len(dependencies) == 12
    assert set(dependencies) == {"youtube-video:CvRngaQZQ3Y"}
    assert rendered.count(
        "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
    ) >= 10


def test_no_raw_transcript_or_private_evidence_body_is_committed() -> None:
    prohibited_names = {
        "transcript.json",
        "transcript.txt",
        "raw_broker_response.md",
        "normalized-transcript.json",
        "normalized-transcript.txt",
    }
    committed = {
        path.name
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    assert prohibited_names.isdisjoint(committed)
    for path in EVAL_ROOT.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert "Generated by https://youtube-transcript.ai" not in text
        assert "## Transcript\n\n[0:00]" not in text


def test_result_points_to_digest_bound_materialized_output() -> None:
    manifest = load_json(MANIFEST)
    result = load_json(RESULT)
    logical = result["logical_output"]
    assert logical["sha256"] == manifest["logical_output_sha256"]
    assert logical["bytes"] == manifest["logical_output_bytes"]
    assert logical["materialized_from"] == (
        "evals/live/CvRngaQZQ3Y/card-manifest.json"
    )
    assert result["verdict"] == "VALID_EVALUATION_CARD_BATCH_WITH_BLOCKERS"
