"""Compose semantic coverage and mental-model gates."""

from __future__ import annotations

from typing import Any

import semantic_artifacts
import semantic_coverage


def gate(fixture: dict[str, Any], name: str, required: list[str], observed: set[str]) -> dict[str, Any]:
    threshold = float(fixture.get("thresholds", {}).get(name, 1.0))
    return semantic_coverage.evaluate(required, observed, threshold)


def evaluate(
    fixture: dict[str, Any],
    graph: dict[str, Any],
    bundle: dict[str, Any],
    coverage_manifest: dict[str, Any],
    visual_ledger: dict[str, Any],
) -> dict[str, Any]:
    required = fixture["required"]
    mental_required = [
        *[f"tag:{item}" for item in required.get("question_tags", [])],
        *[f"projection:{item}" for item in required.get("projection_kinds", [])],
    ]
    mental_observed = {
        *{f"tag:{item}" for item in semantic_artifacts.question_tags(bundle)},
        *{f"projection:{item}" for item in semantic_artifacts.projection_kinds(bundle)},
    }
    return {
        "HG-01": gate(fixture, "HG-01", required.get("knowledge_units", []), semantic_artifacts.mapped_knowledge_units(coverage_manifest)),
        "HG-02": gate(fixture, "HG-02", required.get("relation_ids", []), semantic_artifacts.relation_ids(graph)),
        "HG-03": gate(fixture, "HG-03", required.get("visual_ids", []), semantic_artifacts.accounted_visual_ids(visual_ledger)),
        "HG-06": gate(fixture, "HG-06", mental_required, mental_observed),
    }
