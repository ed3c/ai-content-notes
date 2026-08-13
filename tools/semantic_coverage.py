from __future__ import annotations

from typing import Any


def evaluate(required: list[str], observed: set[str], threshold: float = 1.0) -> dict[str, Any]:
    expected = set(required)
    missing = sorted(expected - observed)
    score = (len(expected) - len(missing)) / max(len(expected), 1)
    return {
        "score": round(score, 6),
        "threshold": threshold,
        "status": "PASS" if score >= threshold else "FAIL",
        "evidence": sorted(expected & observed),
        "failures": missing,
    }
