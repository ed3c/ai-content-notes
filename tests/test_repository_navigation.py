from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "evals" / "semantic-yield" / "README.md"
BATCH = ROOT / "evals" / "semantic-yield" / "CvRngaQZQ3Y"
MANIFEST = BATCH / "card-manifest.json"
ROOT_README = ROOT / "README.md"
AGENT_FILES = (ROOT / "AGENTS.md", ROOT / "CLAUDE.md")
GIT_DOCS = ROOT / "docs" / "git"


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


def test_agent_entrypoints_route_to_catalog_status_and_git_governance() -> None:
    for path in AGENT_FILES:
        text = path.read_text(encoding="utf-8")
        assert "evals/semantic-yield/README.md" in text
        assert "docs/SEMANTIC_YIELD_INTEGRATION_STATUS.md" in text
        assert "docs/git/REPO_PROFILE.md" in text
        assert "docs/git/GIT_TOWN_ADMISSION.md" in text
        assert "docs/git/STACKED_PRS.md" in text
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


def test_git_town_profile_fails_closed_and_stack_is_traceable() -> None:
    required = (
        GIT_DOCS / "README.md",
        GIT_DOCS / "REPO_PROFILE.md",
        GIT_DOCS / "GIT_TOWN_ADMISSION.md",
        GIT_DOCS / "WORKER_PROTOCOL.md",
        GIT_DOCS / "STACKED_PRS.md",
    )
    assert all(path.is_file() for path in required)

    profile = (GIT_DOCS / "REPO_PROFILE.md").read_text(encoding="utf-8")
    admission = (GIT_DOCS / "GIT_TOWN_ADMISSION.md").read_text(
        encoding="utf-8"
    )
    stack = (GIT_DOCS / "STACKED_PRS.md").read_text(encoding="utf-8")

    assert "github-repository-id:1327995338" in profile
    assert "profile state: BLOCKED_POLICY" in profile
    assert "version: ABSENT" in profile
    assert "CI_PUBLICATION_GATE: ABSENT" in profile
    assert "live_git_town_sync: NOT_EXERCISED" in admission

    for pr_number in (18, 19, 20, 21):
        assert f"PR #{pr_number}" in stack
    for leaf in (
        "runtime/01-source-pack-and-run-receipt",
        "runtime/02-relation-graph-and-thesis-ranking",
        "runtime/03a-knowledge-view-projections",
        "runtime/03b-source-driven-batch-planner",
        "runtime/03c-semantic-yield-evaluator",
        "runtime/visual-01-rights-gated-frame-contracts",
        "runtime/provider-01-model-run-adapter",
        "runtime/04-convergence-and-cvrngaqzq3y-replay",
    ):
        assert leaf in stack


def test_documentation_stack_is_recorded_as_merged_not_draft() -> None:
    readme = ROOT_README.read_text(encoding="utf-8")
    stack = (GIT_DOCS / "STACKED_PRS.md").read_text(encoding="utf-8")

    merge_commits = (
        "bbf92a4106b720f5b50707029779984d6672951f",
        "073fbdd2c1d09b71f22a30b7458aa0be06b932d6",
        "c10f8b4572546262c34f93712c54798fdc451830",
        "a2bd35a615c6754c5be70494bef55b65216bda7c",
    )
    for pr_number in (18, 19, 20, 21):
        assert f"Merged PR #{pr_number}" in readme
        assert f"Merged PR #{pr_number}" in stack
        assert f"Draft PR #{pr_number}" not in readme
        assert f"Draft PR #{pr_number}" not in stack
    for merge_commit in merge_commits:
        assert merge_commit in readme
        assert merge_commit in stack


def test_root_readme_indexes_completed_and_planned_stack_without_overclaim() -> None:
    text = ROOT_README.read_text(encoding="utf-8")
    for pr_number in (18, 19, 20, 21):
        assert f"PR #{pr_number}" in text
    assert "## Molecular runtime leaf stack" in text
    assert "exact Git Town admission: ABSENT / BLOCKED_POLICY" in text
    assert "live sync: NOT_EXERCISED" in text
    assert "These leaves are `PLANNED`, not implemented PRs" in text
    assert "Git branch graph != live Git Town synchronization receipt" in text
