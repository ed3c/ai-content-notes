from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "evals" / "semantic-yield" / "README.md"
BATCH = ROOT / "evals" / "semantic-yield" / "CvRngaQZQ3Y"
MANIFEST = BATCH / "card-manifest.json"
ROOT_README = ROOT / "README.md"
AGENT_FILES = (ROOT / "AGENTS.md", ROOT / "CLAUDE.md")


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_modified_flow_catalog_matches_persisted_card_manifest() -> None:
    manifest = load_json(MANIFEST)
    card_order = manifest["card_order"]
    assert isinstance(card_order, list)
    assert manifest["card_count"] == 10
    assert manifest["status"] == "CONTINUE"

    actual_cards = {path.stem for path in (BATCH / "cards").glob("*.md")}
    assert actual_cards == set(card_order)

    catalog = CATALOG.read_text(encoding="utf-8")
    readme = ROOT_README.read_text(encoding="utf-8")
    for stable_id in card_order:
        assert stable_id in catalog
        assert stable_id in readme


def test_live_baseline_is_not_described_as_modified_flow_coverage() -> None:
    catalog = CATALOG.read_text(encoding="utf-8")
    readme = ROOT_README.read_text(encoding="utf-8")
    for text in (catalog, readme):
        assert "evals/live/CvRngaQZQ3Y/" in text
        assert "evals/semantic-yield/CvRngaQZQ3Y/" in text
        assert "transcript-only" in text


def test_agent_entrypoints_route_to_catalog_and_status_ssot() -> None:
    for path in AGENT_FILES:
        text = path.read_text(encoding="utf-8")
        assert "evals/semantic-yield/README.md" in text
        assert "docs/SEMANTIC_YIELD_INTEGRATION_STATUS.md" in text
        assert "PASS_WITH_DEFERRED_VISUAL_AND_PARTIAL_QG" in text
        assert "CONTINUE" in text


def test_root_readme_exposes_directory_state_machine_and_data_flow() -> None:
    text = ROOT_README.read_text(encoding="utf-8")
    required_markers = (
        "## Repository directory map",
        "## Directory-to-State-Machine ownership",
        "## State machine",
        "## Actual data flow",
        "DISCOVERED",
        "RIGHTS_AND_COMPLETENESS_REVIEW",
        "SEMANTIC_MODELED",
        "CARD_BATCH_RENDERED",
        "HOST_VALIDATED",
        "PERSISTED_AND_READ_BACK",
    )
    for marker in required_markers:
        assert marker in text


def test_current_batch_links_validator_and_run_state() -> None:
    expected = (
        BATCH / "knowledge-views.md",
        BATCH / "semantic-validator-report.json",
        BATCH / "semantic-yield.result.json",
        BATCH / "run-state.md",
    )
    assert all(path.is_file() for path in expected)

    result = load_json(BATCH / "semantic-yield.result.json")
    assert result["status"] == "CONTINUE"
    assert result["external_validator"] == (
        "HOST_DETERMINISTIC_PASS_WITH_DEFERRED_VISUAL"
    )
