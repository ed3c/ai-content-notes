"""Combine six semantic-yield gates into one auditable result."""

from __future__ import annotations

from typing import Any

import semantic_artifacts
import semantic_yield_coverage
import semantic_yield_quality


def evaluate(
    fixture: dict[str, Any],
    graph: dict[str, Any],
    bundle: dict[str, Any],
    coverage_manifest: dict[str, Any],
    visual_ledger: dict[str, Any],
    candidate_text: str,
) -> dict[str, Any]:
    gates = {
        **semantic_yield_coverage.evaluate(
            fixture,
            graph,
            bundle,
            coverage_manifest,
            visual_ledger,
        ),
        **semantic_yield_quality.evaluate(fixture, candidate_text),
    }
    required_visuals = fixture["required"].get("visual_ids", [])
    return {
        "schema_version": "semantic-yield-result@1",
        "fixture_id": fixture["fixture_id"],
        "gates": dict(sorted(gates.items())),
        "visual_render_ratio": round(
            len(semantic_artifacts.rendered_visual_ids(visual_ledger))
            / max(len(required_visuals), 1),
            6,
        ),
        "status": "PASS"
        if all(item["status"] == "PASS" for item in gates.values())
        else "FAIL",
    }
