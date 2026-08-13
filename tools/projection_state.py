"""State-plane knowledge projection."""

from __future__ import annotations

from typing import Any

from view_core import mermaid_id, selected_edges


def _label(value: object) -> str:
    return str(value).replace('"', "'").replace("\n", " ").strip()


def render(plan: dict[str, Any], nodes: dict[str, dict[str, Any]], edges_by_id: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, str | None]]:
    planes = plan.get("options", {}).get("planes", [])
    if len(planes) < 2:
        raise ValueError("state-plane projection requires at least two planes")
    all_ids = [node_id for plane in planes for node_id in plane.get("node_ids", [])]
    missing = [node_id for node_id in all_ids if node_id not in nodes]
    if missing:
        raise ValueError(f"unknown state-plane nodes: {missing}")
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("state-plane nodes must be unique across planes")
    mermaid = ["flowchart LR"]
    ascii_lines: list[str] = []
    for index, plane in enumerate(planes, start=1):
        mermaid.append(f'    subgraph PLANE_{index}["{_label(plane["label"])}"]')
        labels = []
        for node_id in plane["node_ids"]:
            labels.append(str(nodes[node_id]["label"]))
            mermaid.append(f'        {mermaid_id(node_id)}["{_label(nodes[node_id]["label"])}"]')
        mermaid.append("    end")
        ascii_lines.append(f"[{plane['label']}] " + " | ".join(labels))
    for edge in selected_edges(plan, edges_by_id):
        if edge["subject"] in all_ids and edge["object"] in all_ids:
            connector = "-.->" if edge.get("uncertain") else "-->"
            mermaid.append(f"    {mermaid_id(edge['subject'])} {connector}|{_label(edge['predicate'])}| {mermaid_id(edge['object'])}")
    data = {"planes": [{"label": plane["label"], "nodes": [{"node_id": node_id, "label": nodes[node_id]["label"]} for node_id in plane["node_ids"]]} for plane in planes]}
    return data, {"markdown": "```mermaid\n" + "\n".join(mermaid) + "\n```", "mermaid": "\n".join(mermaid), "ascii": "\n".join(ascii_lines)}
