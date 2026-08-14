"""Equation-shaped knowledge projection."""

from __future__ import annotations

from typing import Any

from view_core import allowed_anchors


def render(plan: dict[str, Any], nodes: dict[str, dict[str, Any]], edges_by_id: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, str | None]]:
    options = plan.get("options", {})
    expression = str(options.get("expression", "")).strip()
    terms = options.get("terms", [])
    if not expression or not terms:
        raise ValueError("equation projection requires expression and terms")
    missing = [term.get("node_id") for term in terms if term.get("node_id") not in nodes]
    if missing:
        raise ValueError(f"unknown equation nodes: {missing}")
    evidence, visuals = allowed_anchors(plan, edges_by_id)
    if not evidence and not visuals:
        raise ValueError("equation projection requires evidence or visual anchors")
    rows = [f"| `{term['symbol']}` | {term['meaning']} | `[[{term['node_id']}]]` |" for term in terms]
    markdown = f"```text\n{expression}\n```\n\n| Symbol | Meaning | Graph node |\n|---|---|---|\n" + "\n".join(rows)
    return {"expression": expression, "terms": terms, "evidence_ids": sorted(evidence), "visual_ids": sorted(visuals)}, {"markdown": markdown, "mermaid": None, "ascii": expression}
