"""Evidence-bound ordered process projection."""

from __future__ import annotations

from typing import Any

from view_core import allowed_anchors


def _label(value: object) -> str:
    return str(value).replace("\n", " ").strip()


def render(plan: dict[str, Any], nodes: dict[str, dict[str, Any]], edges_by_id: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, str | None]]:
    events = sorted(plan.get("options", {}).get("events", []), key=lambda item: item["order"])
    if len(events) < 2:
        raise ValueError("timeline projection requires at least two events")
    missing = [event.get("node_id") for event in events if event.get("node_id") not in nodes]
    if missing:
        raise ValueError(f"unknown timeline nodes: {missing}")
    allowed, _ = allowed_anchors(plan, edges_by_id)
    for event in events:
        outside = set(event.get("evidence_ids", [])) - allowed
        if outside:
            raise ValueError(f"timeline event uses evidence outside selected relations: {sorted(outside)}")
    markdown = "\n".join(f"{index}. **{event['label']}** — `[[{event['node_id']}]]`" for index, event in enumerate(events, start=1))
    mermaid = ["timeline", f"    title {_label(plan['title'])}"]
    mermaid.extend(f"    {event['order']} : {_label(event['label'])}" for event in events)
    return {"events": events}, {"markdown": markdown, "mermaid": "\n".join(mermaid), "ascii": " -> ".join(event["label"] for event in events)}
