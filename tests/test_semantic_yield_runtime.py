"""Focused tests for the prompt-external semantic-yield runtime.

Covers the five projection renderers, the relation-graph index boundary,
source-shaped first-batch selection and the HG-01..HG-06 gate composition.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import batch_coverage  # noqa: E402
import frame_sampling_plan  # noqa: E402
import materialize_knowledge_views  # noqa: E402
import projection_dispatch  # noqa: E402
import semantic_artifacts  # noqa: E402
import semantic_yield_result  # noqa: E402
from view_core import ViewError  # noqa: E402

NODES = {
    "NODE-autonomy": {"node_id": "NODE-autonomy", "label": "Autonomy"},
    "NODE-traces": {"node_id": "NODE-traces", "label": "Runtime traces"},
    "NODE-evals": {"node_id": "NODE-evals", "label": "Frozen evals"},
    "NODE-harness": {"node_id": "NODE-harness", "label": "Harness"},
}

EDGES = {
    "REL-a": {
        "relation_id": "REL-a",
        "subject": "NODE-autonomy",
        "object": "NODE-traces",
        "predicate": "elevates",
        "evidence_ids": ["EV-1"],
        "visual_ids": [],
        "uncertain": False,
    },
    "REL-b": {
        "relation_id": "REL-b",
        "subject": "NODE-traces",
        "object": "NODE-evals",
        "predicate": "feeds",
        "evidence_ids": ["EV-2"],
        "visual_ids": ["VIS-1"],
        "uncertain": True,
    },
    "REL-c": {
        "relation_id": "REL-c",
        "subject": "NODE-evals",
        "object": "NODE-harness",
        "predicate": "updates",
        "evidence_ids": ["EV-3"],
        "visual_ids": [],
        "uncertain": False,
    },
}


def plan(kind: str, **overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "projection_id": f"PROJ-{kind}",
        "projection_kind": kind,
        "title": f"{kind} view",
        "relation_ids": ["REL-a", "REL-b"],
        "source_card_ids": ["N-autonomy"],
        "visual_evidence_ids": [],
        "uncertainty_policy": "LABEL_UNKNOWN",
        "question_tags": ["dataflow"],
        "options": {},
    }
    base.update(overrides)
    return base


def test_index_graph_reads_the_relations_key() -> None:
    graph = {"nodes": list(NODES.values()), "relations": list(EDGES.values())}
    nodes, edges = materialize_knowledge_views.index_graph(graph)
    assert set(nodes) == set(NODES)
    assert set(edges) == set(EDGES)
    assert semantic_artifacts.relation_ids(graph) == set(EDGES)


def test_causal_dataflow_marks_uncertain_edges_dotted() -> None:
    rendered = projection_dispatch.render(
        plan("causal-dataflow", options={"node_order": ["NODE-autonomy"], "direction": "LR"}),
        NODES,
        EDGES,
    )
    assert rendered["projection_kind"] == "causal-dataflow"
    assert "-.->|feeds|" in rendered["rendered"]["mermaid"]
    assert "-->|elevates|" in rendered["rendered"]["mermaid"]
    assert rendered["source_relation_ids"] == ["REL-a", "REL-b"]


def test_state_planes_require_two_planes_and_unique_nodes() -> None:
    options = {
        "planes": [
            {"label": "Signal", "node_ids": ["NODE-autonomy", "NODE-traces"]},
            {"label": "Control", "node_ids": ["NODE-evals"]},
        ]
    }
    rendered = projection_dispatch.render(plan("state-planes", options=options), NODES, EDGES)
    assert "subgraph PLANE_1" in rendered["rendered"]["mermaid"]
    assert "[Signal] Autonomy | Runtime traces" in rendered["rendered"]["ascii"]

    single = {"planes": [{"label": "Only", "node_ids": ["NODE-autonomy"]}]}
    with pytest.raises(ValueError):
        projection_dispatch.render(plan("state-planes", options=single), NODES, EDGES)

    duplicated = {
        "planes": [
            {"label": "A", "node_ids": ["NODE-autonomy"]},
            {"label": "B", "node_ids": ["NODE-autonomy"]},
        ]
    }
    with pytest.raises(ValueError):
        projection_dispatch.render(plan("state-planes", options=duplicated), NODES, EDGES)


def test_equation_requires_anchored_relations() -> None:
    options = {
        "expression": "performance = f(model, harness, task)",
        "terms": [{"symbol": "m", "meaning": "model", "node_id": "NODE-harness"}],
    }
    rendered = projection_dispatch.render(
        plan("equation", relation_ids=["REL-c"], options=options), NODES, EDGES
    )
    assert rendered["data"]["evidence_ids"] == ["EV-3"]
    assert "performance = f(model, harness, task)" in rendered["rendered"]["markdown"]

    with pytest.raises(ValueError):
        projection_dispatch.render(
            plan("equation", relation_ids=["REL-c"], options={"expression": "", "terms": []}),
            NODES,
            EDGES,
        )


def test_timeline_rejects_evidence_outside_selected_relations() -> None:
    events = [
        {"order": 2, "label": "Mine traces", "node_id": "NODE-traces", "evidence_ids": ["EV-2"]},
        {"order": 1, "label": "Observe autonomy", "node_id": "NODE-autonomy", "evidence_ids": ["EV-1"]},
    ]
    rendered = projection_dispatch.render(plan("timeline", options={"events": events}), NODES, EDGES)
    assert rendered["rendered"]["ascii"] == "Observe autonomy -> Mine traces"

    leaked = [dict(events[0], evidence_ids=["EV-3"]), events[1]]
    with pytest.raises(ValueError):
        projection_dispatch.render(plan("timeline", options={"events": leaked}), NODES, EDGES)


def test_comparison_matrix_keeps_unsupported_cells_unknown() -> None:
    options = {
        "columns": ["Frontier", "Open"],
        "rows": [
            {
                "label": "Cost",
                "cells": [
                    {"status": "SUPPORTED", "value": "high", "evidence_ids": ["EV-1"]},
                    {"status": "UNKNOWN", "value": None},
                ],
            }
        ],
    }
    rendered = projection_dispatch.render(plan("comparison-matrix", options=options), NODES, EDGES)
    assert "| Cost | high | UNKNOWN |" in rendered["rendered"]["markdown"]

    forged = {
        "columns": ["Frontier", "Open"],
        "rows": [
            {
                "label": "Cost",
                "cells": [
                    {"status": "SUPPORTED", "value": "high", "evidence_ids": ["EV-1"]},
                    {"status": "UNKNOWN", "value": "0.80"},
                ],
            }
        ],
    }
    with pytest.raises(ValueError):
        projection_dispatch.render(plan("comparison-matrix", options=forged), NODES, EDGES)

    unanchored = {
        "columns": ["Frontier", "Open"],
        "rows": [
            {
                "label": "Cost",
                "cells": [
                    {"status": "SUPPORTED", "value": "high"},
                    {"status": "UNKNOWN", "value": None},
                ],
            }
        ],
    }
    with pytest.raises(ValueError):
        projection_dispatch.render(plan("comparison-matrix", options=unanchored), NODES, EDGES)


def test_projection_fails_closed_on_unknown_relation() -> None:
    with pytest.raises(ViewError):
        projection_dispatch.render(
            plan("causal-dataflow", relation_ids=["REL-missing"]), NODES, EDGES
        )


def test_batch_selection_is_source_shaped_not_series_quota() -> None:
    cards = [
        {"card_id": "N-1", "series": "N", "task_value": 0.9, "coverage_tags": ["human_entry"]},
        {"card_id": "C-1", "series": "C", "task_value": 0.8, "coverage_tags": ["detail"]},
        {"card_id": "P-1", "series": "P", "task_value": 0.7, "coverage_tags": ["action"]},
        {"card_id": "T-1", "series": "T", "task_value": 0.2, "coverage_tags": ["comparison"]},
        {"card_id": "D-1", "series": "D", "task_value": 0.6, "coverage_tags": ["detail", "action"]},
    ]
    required = ["human_entry", "detail", "action", "comparison"]
    result = batch_coverage.select(cards, required, limit=3)
    assert result["status"] == "PASS"
    assert result["missing_required_coverage"] == []
    # The low task-value T card is admitted only because the source needs a comparison.
    assert "T-1" in result["selected_card_ids"]

    blocked = batch_coverage.select(cards, [*required, "visual_projection"], limit=5)
    assert blocked["status"] == "BLOCKED"
    assert blocked["missing_required_coverage"] == ["visual_projection"]


def test_semantic_yield_result_reports_every_gate() -> None:
    fixture = {
        "fixture_id": "runtime-unit",
        "required": {
            "knowledge_units": ["ku-1"],
            "relation_ids": ["REL-a"],
            "visual_ids": ["VIS-1"],
            "projection_kinds": ["causal-dataflow"],
            "question_tags": ["dataflow"],
        },
        "forbidden_precision_patterns": [r"\x2480\+"],
        "thresholds": {"HG-05": 0.95},
        "redundancy_similarity_threshold": 0.84,
    }
    graph = {"nodes": list(NODES.values()), "relations": list(EDGES.values())}
    bundle = {
        "projections": [
            {
                "projection_id": "PROJ-1",
                "projection_kind": "causal-dataflow",
                "question_tags": ["dataflow"],
            }
        ]
    }
    coverage_manifest = {"items": [{"knowledge_unit_id": "ku-1", "disposition": "CARD_MAPPED"}]}
    visual_ledger = {"items": [{"visual_id": "VIS-1", "disposition": "RENDERED"}]}
    candidate = (
        "### N-one｜First card\n\n- **核心命題**：自主性提高使 runtime trace 成為主要證據。\n\n"
        "### C-two｜Second card\n\n- **核心命題**：模型排行榜無法單獨解釋任務表現。\n"
    )

    result = semantic_yield_result.evaluate(
        fixture, graph, bundle, coverage_manifest, visual_ledger, candidate
    )
    assert sorted(result["gates"]) == ["HG-01", "HG-02", "HG-03", "HG-04", "HG-05", "HG-06"]
    assert result["status"] == "PASS"
    assert result["visual_render_ratio"] == 1.0

    leaked = candidate + "\n供應商報價 $80+ 起。\n"
    failed = semantic_yield_result.evaluate(
        fixture, graph, bundle, coverage_manifest, visual_ledger, leaked
    )
    assert failed["gates"]["HG-04"]["status"] == "FAIL"
    assert failed["status"] == "FAIL"


def test_frame_sampling_blocks_unauthorized_rights() -> None:
    blocked = frame_sampling_plan.build("sha256:" + "0" * 64, 120.0, 4, "public-visibility")
    assert blocked["status"] == "BLOCKED"
    assert blocked["timestamps_seconds"] == []

    # The sampler used to accept `authorized-local-file`, a value no acquisition
    # adapter has ever emitted. It is now a blocked non-value like any other.
    retired = frame_sampling_plan.build("sha256:" + "0" * 64, 120.0, 4, "authorized-local-file")
    assert retired["status"] == "BLOCKED"

    planned = frame_sampling_plan.build("sha256:" + "0" * 64, 120.0, 4, "user-provided-media")
    assert planned["status"] == "PLANNED"
    assert planned["timestamps_seconds"][0] == 0.0
    assert len(planned["timestamps_seconds"]) == 4
    assert planned["timestamps_seconds"] == sorted(planned["timestamps_seconds"])


def test_a_candidate_with_no_cards_fails_redundancy_instead_of_scoring_one() -> None:
    """A gate that cannot see its subject has not passed."""
    import semantic_redundancy

    empty = semantic_redundancy.evaluate("## a projection view\n\nno cards here\n")
    assert empty["status"] == "FAIL"
    assert empty["score"] == 0.0
    assert empty["evidence"] == ["claims:0"]
    assert any("no core-claim card was observed" in item for item in empty["failures"])


def test_redundancy_still_scores_a_real_card_batch() -> None:
    import semantic_redundancy

    text = (
        "### N-one\uff5cFirst\n\n- **\u6838\u5fc3\u547d\u984c**\uff1a\u81ea\u4e3b\u6027\u63d0\u9ad8\u4f7f runtime trace \u6210\u70ba\u4e3b\u8981\u8b49\u64da\u3002\n\n"
        "### C-two\uff5cSecond\n\n- **\u6838\u5fc3\u547d\u984c**\uff1a\u6a21\u578b\u6392\u884c\u699c\u7121\u6cd5\u55ae\u7368\u89e3\u91cb\u4efb\u52d9\u8868\u73fe\u3002\n"
    )
    scored = semantic_redundancy.evaluate(text)
    assert scored["status"] == "PASS"
    assert scored["evidence"] == ["claims:2", "pairs:1"]


def test_one_duplicate_pair_fails_even_in_a_large_batch() -> None:
    """Batch size must not dilute the one thing this gate exists to catch."""
    import semantic_redundancy

    distinct = [
        "runtime traces accumulate faster than reviewers can read them",
        "context windows bound how much trajectory fits in one request",
        "harness engineering answers within minutes of a change",
        "fine tuning shifts spending from tokens toward hardware clusters",
        "sparse pass or fail scores hide the reason a run failed",
        "memory cannot remain an append only log across decades",
        "legal review demands human sign off before publication",
        "leaderboards rank models without naming the task distribution",
    ]
    claim = "task performance is the joint fit of model harness and task"
    cards = [
        f"### U{index}-card｜Unique {index}\n\n- **核心命題**：{sentence}\n"
        for index, sentence in enumerate(distinct)
    ]
    cards += [f"### A-card｜A\n\n- **核心命題**：{claim}\n",
              f"### B-card｜B\n\n- **核心命題**：{claim}\n"]
    result = semantic_redundancy.evaluate(
        "\n".join(cards), similarity_threshold=0.84, minimum_score=0.95
    )
    assert result["evidence"] == ["claims:10", "pairs:45"]
    # The ratio alone would have cleared the threshold: 1 bad pair in 45.
    assert result["score"] > 0.95
    assert result["status"] == "FAIL"
    assert len(result["failures"]) == 1
    assert {result["failures"][0]["left"], result["failures"][0]["right"]} == {"A-card", "B-card"}
