"""Compose precision and redundancy semantic-yield gates."""

from __future__ import annotations

from typing import Any

import semantic_precision
import semantic_redundancy


def evaluate(fixture: dict[str, Any], candidate_text: str) -> dict[str, Any]:
    thresholds = fixture.get("thresholds", {})
    return {
        "HG-04": semantic_precision.evaluate(
            candidate_text,
            fixture.get("forbidden_precision_patterns", []),
            float(thresholds.get("HG-04", 1.0)),
        ),
        "HG-05": semantic_redundancy.evaluate(
            candidate_text,
            float(fixture.get("redundancy_similarity_threshold", 0.72)),
            float(thresholds.get("HG-05", 0.95)),
        ),
    }
