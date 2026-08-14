"""Dispatch projection plans to deterministic renderers."""

from __future__ import annotations

from typing import Any

import projection_equation
import projection_flow
import projection_state
import projection_table
import projection_timeline


def render(plan: dict[str, Any], nodes: dict[str, dict[str, Any]], edges: dict[str, dict[str, Any]]) -> dict[str, Any]:
    kind = plan["projection_kind"]
    if kind in {"causal-dataflow", "architecture"}:
        data, rendered = projection_flow.render(plan, nodes, edges)
    elif kind == "state-planes":
        data, rendered = projection_state.render(plan, nodes, edges)
    elif kind == "equation":
        data, rendered = projection_equation.render(plan, nodes, edges)
    elif kind == "comparison-matrix":
        data, rendered = projection_table.render(plan, edges)
    elif kind == "timeline":
        data, rendered = projection_timeline.render(plan, nodes, edges)
    else:
        raise ValueError(f"unsupported projection kind: {kind}")
    return {
        "projection_id": plan["projection_id"],
        "projection_kind": kind,
        "title": plan["title"],
        "source_relation_ids": plan.get("relation_ids", []),
        "source_card_ids": plan.get("source_card_ids", []),
        "visual_evidence_ids": plan.get("visual_evidence_ids", []),
        "uncertainty_policy": plan.get("uncertainty_policy", "LABEL_UNKNOWN"),
        "question_tags": plan.get("question_tags", []),
        "data": data,
        "rendered": rendered,
    }
