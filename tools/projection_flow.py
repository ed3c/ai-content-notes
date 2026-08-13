"""Causal and architecture graph projection."""

from __future__ import annotations

from typing import Any

from view_core import mermaid_id, selected_edges


def _label(value: object) -> str:
    return str(value).replace('"', "'").replace("\n", " ").strip()


def render(plan: dict[str, Any], nodes: dict[str, dict[str, Any]], edges_by_id: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, str | None]]:
    edges = selected_edges(plan, edges_by_id)
    options = plan.get("options", {})
    selected = {node_id for edge in edges for node_id in (edge["subject"], edge["object"])}
    preferred = list(options.get("node_order", []))
    missing = [node_id for node_id in preferred if node_id not in nodes]
    if missing:
        raise ValueError(f"unknown projection nodes: {missing}")
    order = [*filter(selected.__contains__, preferred), *sorted(selected - set(preferred))]
    direction = options.get("direction", "LR")
    include_predicates = bool(options.get("include_predicates", True))
    mermaid = [f"flowchart {direction}"]
    for node_id in order:
        mermaid.append(f'    {mermaid_id(node_id)}["{_label(nodes[node_id]["label"])}"]')
    ascii_lines: list[str] = []
    data_edges: list[dict[str, Any]] = []
    for edge in edges:
        predicate = _label(edge["predicate"]) if include_predicates else ""
        connector = "-.->" if edge.get("uncertain") else "-->"
        label = f"|{predicate}|" if predicate else ""
        mermaid.append(f"    {mermaid_id(edge['subject'])} {connector}{label} {mermaid_id(edge['object'])}")
        marker = " ?" if edge.get("uncertain") else ""
        ascii_lines.append(f"{nodes[edge['subject']]['label']} --{edge['predicate']}{marker}--> {nodes[edge['object']]['label']}")
        data_edges.append({"relation_id": edge["relation_id"], "from": edge["subject"], "to": edge["object"], "predicate": edge["predicate"], "uncertain": bool(edge.get("uncertain"))})
    return {"nodes": [{"node_id": node_id, "label": nodes[node_id]["label"]} for node_id in order], "edges": data_edges}, {"markdown": "```mermaid\n" + "\n".join(mermaid) + "\n```", "mermaid": "\n".join(mermaid), "ascii": "\n".join(ascii_lines)}
