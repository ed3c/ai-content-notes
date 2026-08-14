"""Evidence-bound comparison matrix projection."""

from __future__ import annotations

from typing import Any

from view_core import allowed_anchors


def render(plan: dict[str, Any], edges_by_id: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, str | None]]:
    options = plan.get("options", {})
    columns = options.get("columns", [])
    rows = options.get("rows", [])
    if len(columns) < 2 or not rows:
        raise ValueError("comparison projection requires columns and rows")
    allowed_evidence, allowed_visuals = allowed_anchors(plan, edges_by_id)
    allowed_visuals.update(plan.get("visual_evidence_ids", []))
    rendered_rows = []
    normalized = []
    for row in rows:
        cells = row.get("cells", [])
        if len(cells) != len(columns):
            raise ValueError(f"comparison row {row.get('label')} has wrong cell count")
        values = []
        saved = []
        for cell in cells:
            evidence = set(cell.get("evidence_ids", []))
            visuals = set(cell.get("visual_ids", []))
            if not evidence <= allowed_evidence or not visuals <= allowed_visuals:
                raise ValueError("comparison cell uses anchors outside selected relations")
            if cell.get("status") in {"SUPPORTED", "CORROBORATED", "TESTED"} and not (evidence or visuals):
                raise ValueError(f"{cell['status']} comparison cell requires an evidence anchor")
            value = "UNKNOWN" if cell.get("status") == "UNKNOWN" else str(cell.get("value"))
            if cell.get("status") == "UNKNOWN" and cell.get("value") not in {None, "UNKNOWN"}:
                raise ValueError("UNKNOWN comparison cells must render UNKNOWN")
            values.append(value)
            saved.append({**cell, "value": value})
        rendered_rows.append(f"| {row['label']} | " + " | ".join(values) + " |")
        normalized.append({"label": row["label"], "cells": saved})
    header = "| Dimension | " + " | ".join(columns) + " |"
    separator = "|---|" + "|".join("---" for _ in columns) + "|"
    markdown = "\n".join([header, separator, *rendered_rows])
    return {"columns": columns, "rows": normalized}, {"markdown": markdown, "mermaid": None, "ascii": markdown}
