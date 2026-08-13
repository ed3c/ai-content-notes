"""Source-shaped first-batch coverage selection."""

from __future__ import annotations

from typing import Any

TAGS = (
    "human_entry",
    "detail",
    "action",
    "comparison",
    "critical_uncertainty",
    "visual_projection",
)


def select(cards: list[dict[str, Any]], required: list[str], limit: int = 12) -> dict[str, Any]:
    ordered = sorted(cards, key=lambda item: (-float(item.get("task_value", 0)), item["card_id"]))
    needed = set(required) & set(TAGS)
    chosen: list[dict[str, Any]] = []
    covered: set[str] = set()
    while needed - covered and len(chosen) < limit:
        missing = needed - covered
        options = [item for item in ordered if item not in chosen and missing & set(item.get("coverage_tags", []))]
        if not options:
            break
        item = max(options, key=lambda value: (len(missing & set(value.get("coverage_tags", []))), float(value.get("task_value", 0)), value["card_id"]))
        chosen.append(item)
        covered.update(item.get("coverage_tags", []))
    for item in ordered:
        if len(chosen) >= limit:
            break
        if item not in chosen:
            chosen.append(item)
            covered.update(item.get("coverage_tags", []))
    missing = sorted(needed - covered)
    return {
        "selected_card_ids": [item["card_id"] for item in chosen],
        "selected_series": [item["series"] for item in chosen],
        "coverage": {tag: tag in covered for tag in TAGS},
        "missing_required_coverage": missing,
        "status": "PASS" if not missing else "BLOCKED",
    }
