"""Detect unsupported precision patterns in rendered knowledge output."""

from __future__ import annotations

import re
from typing import Any


def evaluate(text: str, forbidden_patterns: list[str], threshold: float = 1.0) -> dict[str, Any]:
    findings = []
    for pattern in forbidden_patterns:
        matches = sorted(set(re.findall(pattern, text, flags=re.IGNORECASE)))
        if matches:
            findings.append({"pattern": pattern, "matches": matches})
    score = 1.0 - len(findings) / max(len(forbidden_patterns), 1)
    return {
        "score": round(score, 6),
        "threshold": threshold,
        "status": "PASS" if score >= threshold else "FAIL",
        "evidence": [f"checked:{pattern}" for pattern in forbidden_patterns],
        "failures": findings,
    }
