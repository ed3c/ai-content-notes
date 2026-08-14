"""Measure cross-card core-claim redundancy without model calls."""

from __future__ import annotations

import re
from itertools import combinations
from typing import Any

CARD = re.compile(r"^###\s+([^｜\n]+)｜", re.MULTILINE)
CORE = re.compile(r"^\s*- \*\*核心命題\*\*[：:]\s*(.+)$", re.MULTILINE)
TOKEN = re.compile(r"[A-Za-z0-9_\-]+|[\u4e00-\u9fff]+")


def token_set(value: str) -> set[str]:
    return {token.lower() for token in TOKEN.findall(value) if len(token) > 1}


def claims(text: str) -> list[tuple[str, str]]:
    matches = list(CARD.finditer(text))
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        core = CORE.search(text[match.start():end])
        if core:
            result.append((match.group(1).strip(), core.group(1).strip()))
    return result


def evaluate(text: str, similarity_threshold: float = 0.72, minimum_score: float = 0.95) -> dict[str, Any]:
    parsed = claims(text)
    failures = []
    for (left_id, left), (right_id, right) in combinations(parsed, 2):
        a, b = token_set(left), token_set(right)
        similarity = len(a & b) / max(len(a | b), 1)
        if similarity >= similarity_threshold:
            failures.append({"left": left_id, "right": right_id, "similarity": round(similarity, 6)})
    pairs = len(parsed) * (len(parsed) - 1) // 2
    score = 1.0 - len(failures) / max(pairs, 1)
    return {
        "score": round(score, 6),
        "threshold": minimum_score,
        "status": "PASS" if score >= minimum_score else "FAIL",
        "evidence": [f"claims:{len(parsed)}", f"pairs:{pairs}"],
        "failures": failures,
    }
