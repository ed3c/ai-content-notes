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
RUNTIME_DOCS = ROOT / "docs" / "runtime"
PROMOTION_DOC = ROOT / "docs" / "DOMAIN_CONTEXT_SUPPLY_PLANE.md"
INTAKE_PACKET = ROOT / "evals" / "source-intake" / "modern-web-architecture"
SIGNAL_PACKET = ROOT / "evals" / "product-signal" / "modern-web-architecture"
EVIDENCE_PLANE_DOCS = (
    ROOT / "docs" / "source-intake" / "README.md",
    INTAKE_PACKET / "README.md",
    SIGNAL_PACKET / "README.md",
)
EVIDENCE_PLANE_MERGES = (
    "3326f24fabf1cc80c65e977870ee05746e162ab6",
    "0f7f551ebbca067a02621abd8a2d538189a8855b",
    "beefeb0e792a771638ad1968db126d302729256d",
)
# Where the architecture-compiler product line actually landed after it left this
# repository under #83: ed3c/skill-concerns#36 and ed3c/noodles#255. A merge SHA is
# immutable provider truth; the issue number that names its owner is not.
DECOUPLED_PRODUCT_LINE_MERGES = (
    "832415ea3ca1fb61a8b974032246ff27b25576c1",
    "fe05ed440e90afb7c44b487c1069b186dd22f4e2",
)
# Sections that state repository-wide law rather than host-specific procedure.
SHARED_LAW_SECTIONS = (
    "## Anti-overengineering laws",
    "## Required behavior",
    "## State transition guard",
)


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def section(text: str, heading: str) -> str:
    """Return one `## ` section, heading included, up to the next `## `."""
    lines = text.splitlines()
    start = lines.index(heading)
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    return "\n".join(lines[start:end]).strip()


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


def test_promotion_policy_is_reachable_and_keeps_escalation_optional() -> None:
    """Every entrypoint that routes to the promotion policy must reach a real file.

    Three entrypoints link to this doc. Without this reader the doc can be deleted
    or renamed and the suite stays green, leaving three dangling pointers - which
    is how the repository's own closed-issue audit describes the failure it exists
    to refuse.
    """
    assert PROMOTION_DOC.is_file()
    policy = PROMOTION_DOC.read_text(encoding="utf-8")

    for path in (*AGENT_FILES, ROOT_README):
        assert "docs/DOMAIN_CONTEXT_SUPPLY_PLANE.md" in path.read_text(encoding="utf-8")

    # The default path stays lightweight: escalation is gated, never a default stage.
    for marker in ("## Promotion Gate", "Shape", "Guard", "Guide"):
        assert marker in policy
    for escalation in ("FeatureMap", "Spatial Loop"):
        assert f"{escalation} only" in policy or f"{escalation} escalation" in policy

    # Knowledge convergence must not read as runtime verification.
    assert "CONVERGED knowledge != runtime VERIFIED" in policy

    # The architecture-compiler product line left under #83; it must not return here.
    # The successor owner is named by issue number, but the *landing* it points at
    # is pinned by merge SHA - an issue number survives a close, a retitle or a
    # delete, so on its own it certifies a mention rather than a landed artifact.
    assert "skill-concerns#19" in policy
    for merge_sha in DECOUPLED_PRODUCT_LINE_MERGES:
        assert merge_sha in policy, merge_sha
    assert "Lauren Tan" not in policy


def test_agent_contract_and_claude_adapter_carry_the_same_repository_law() -> None:
    """AGENTS.md and CLAUDE.md must agree wherever they state repository-wide law.

    They are a pair maintained by hand, and the pair had already drifted: AGENTS.md
    carried Required behavior 16 (`sources/<content-id>/` retention) while CLAUDE.md
    stopped at 15, so the Claude adapter was blind to a law the Codex contract
    enforced. Nothing read the two lists against each other, which is the same
    "no reader, silent rot" failure the promotion doc exists to refuse. Host-specific
    prose stays free; these three sections are law and must be byte-identical.
    """
    agents, claude = (path.read_text(encoding="utf-8") for path in AGENT_FILES)
    for heading in SHARED_LAW_SECTIONS:
        assert section(agents, heading) == section(claude, heading), heading

    # A tautology guard: the assertion above is only worth running while the
    # sections are non-empty and actually carry the numbered law list.
    required = section(agents, "## Required behavior")
    assert required.count("\n1. ") == 1
    assert "\n18. " in required


def test_root_readme_exposes_directory_state_machine_and_data_flow() -> None:
    text = ROOT_README.read_text(encoding="utf-8")
    required_markers = (
        "## Repository directory map",
        "## Directory-to-State-Machine ownership",
        "## State machine",
        "## Actual data flow",
        "DISCOVERED",
        "RIGHTS_AND_COMPLETENESS_REVIEW",
        "SOURCE_PACK_BOUND",
        "MODEL_RUN_BOUND",
        "EVIDENCE_BOUND",
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

    for pr_number in (18, 19, 20, 21, 22, 24):
        assert f"#{pr_number}" in stack
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
        "f67ccad478f30d6b17a4ebbf73aaab41f2f05dda",
    )
    for pr_number in (18, 19, 20, 21, 22):
        assert f"Merged PR #{pr_number}" in readme
        assert f"PR #{pr_number}" in stack
        assert f"Draft PR #{pr_number}" not in readme
        assert f"Draft PR #{pr_number}" not in stack
    for merge_commit in merge_commits:
        assert merge_commit in readme
        assert merge_commit in stack


def test_runtime_leaf01_contracts_are_materialized() -> None:
    required = (
        RUNTIME_DOCS / "README.md",
        ROOT / "schemas" / "multimodal-source-pack-descriptor.schema.json",
        ROOT / "schemas" / "multimodal-source-pack.schema.json",
        ROOT / "schemas" / "model-run-receipt-descriptor.schema.json",
        ROOT / "schemas" / "model-run-receipt.schema.json",
        ROOT / "tools" / "build_multimodal_source_pack.py",
        ROOT / "tools" / "build_model_run_receipt.py",
        ROOT / "tests" / "test_source_pack_and_run_receipt.py",
    )
    assert all(path.is_file() for path in required)

    readme = ROOT_README.read_text(encoding="utf-8")
    stack = (GIT_DOCS / "STACKED_PRS.md").read_text(encoding="utf-8")
    runtime = (RUNTIME_DOCS / "README.md").read_text(encoding="utf-8")

    assert "Merged PR #24" in readme
    assert "Merged PR #24" in stack
    assert "d39d4791eed8c0cd3b1227ef8aeafd9685736e91" in readme
    assert "d39d4791eed8c0cd3b1227ef8aeafd9685736e91" in stack
    assert "multimodal-source-pack@1" in readme
    assert "model-run-receipt@1" in readme
    assert "runtime/01-source-pack-and-run-receipt" in runtime


def test_root_readme_indexes_completed_and_planned_stack_without_overclaim() -> None:
    text = ROOT_README.read_text(encoding="utf-8")
    for pr_number in (18, 19, 20, 21, 22, 24):
        assert f"PR #{pr_number}" in text
    assert "## Molecular runtime leaf stack" in text
    assert "exact Git Town admission: ABSENT / BLOCKED_POLICY" in text
    assert "live sync: NOT_EXERCISED" in text
    assert (
        "Leaf 01 is implemented; all remaining leaves are `PLANNED`, "
        "not implemented PRs"
    ) in text
    assert "Git branch graph != live Git Town synchronization receipt" in text
    assert "source-pack receipt != source accuracy or claim truth" in text
    assert "model-run receipt != model quality or claim verification" in text


def test_evidence_plane_is_reachable_from_the_root_entrypoints() -> None:
    readme = ROOT_README.read_text(encoding="utf-8")
    assert "## Product Reverse Evidence Plane" in readme

    index = (ROOT / "INDEX.md").read_text(encoding="utf-8")
    assert "Product Reverse Evidence Plane" in index

    routed = (
        "docs/source-intake/README.md",
        "evals/source-intake/modern-web-architecture/",
        "evals/product-signal/modern-web-architecture/",
        "schemas/source-registry.schema.json",
        "schemas/product-signal.schema.json",
        "tools/source_registry.py",
        "tools/pdf_source_adapter.py",
        "tools/product_signal.py",
    )
    for path in routed:
        assert path in readme, path

    for agent_file in AGENT_FILES:
        text = agent_file.read_text(encoding="utf-8")
        assert "## Product Reverse Evidence Plane route" in text
        assert "docs/source-intake/README.md" in text
        assert "evals/source-intake/modern-web-architecture/README.md" in text
        assert "evals/product-signal/modern-web-architecture/README.md" in text
        for merge_sha in EVIDENCE_PLANE_MERGES:
            assert merge_sha in text, (agent_file, merge_sha)

    for merge_sha in EVIDENCE_PLANE_MERGES:
        assert merge_sha in readme, merge_sha


def test_evidence_plane_prose_matches_the_persisted_packet_bytes() -> None:
    signal = load_json(SIGNAL_PACKET / "product-signal.json")
    receipt = load_json(INTAKE_PACKET / "readback-receipt.json")
    readme = ROOT_README.read_text(encoding="utf-8")

    assert signal["decision"] == "VALIDATE"
    assert "decision         VALIDATE" in readme

    evidence_state = signal["evidence_state"]
    assert isinstance(evidence_state, dict)
    rendered = " ".join(
        f"{lane}={evidence_state[lane]}"
        for lane in ("source", "user", "paid", "runtime", "legal")
    )
    assert f"evidence_state   {rendered}" in readme

    assert signal["product_signal_digest"] in readme
    assert receipt["source_registry_digest"] in readme
    source_binding = signal["source_binding"]
    assert isinstance(source_binding, dict)
    assert source_binding["source_digest"] in readme

    unresolved = signal["unresolved_contradictions"]
    assert isinstance(unresolved, list)
    assert unresolved
    for contradiction in unresolved:
        assert contradiction in readme


def test_no_evidence_plane_doc_still_calls_a_merged_stack_pr_unmerged() -> None:
    # Bans "unmerged" only where it names one of *this lane's* merged PRs, on
    # the same line — not the word outright. A doc may still truthfully call
    # a genuinely unmerged branch (e.g. #54) unmerged elsewhere in the same file.
    merged_pr_numbers = ("52", "53", "73")
    for doc in EVIDENCE_PLANE_DOCS:
        text = doc.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "unmerged" in line:
                for pr_number in merged_pr_numbers:
                    assert f"PR #{pr_number}" not in line, (doc, pr_number, line)
        assert any(sha in text for sha in EVIDENCE_PLANE_MERGES), doc
