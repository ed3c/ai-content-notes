"""Shared validation helpers for evidence-bound knowledge views."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


class ViewError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ViewError(f"expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def mermaid_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", value)
    return cleaned if cleaned and not cleaned[0].isdigit() else f"N_{cleaned}"


def selected_edges(plan: dict[str, Any], edges: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for relation_id in plan.get("relation_ids", []):
        if relation_id not in edges:
            raise ViewError(f"unknown relation: {relation_id}")
        selected.append(edges[relation_id])
    return selected


def allowed_anchors(plan: dict[str, Any], edges: dict[str, dict[str, Any]]) -> tuple[set[str], set[str]]:
    chosen = selected_edges(plan, edges)
    evidence = {item for edge in chosen for item in edge.get("evidence_ids", [])}
    visuals = set(plan.get("visual_evidence_ids", [])) | {
        item for edge in chosen for item in edge.get("visual_ids", [])
    }
    return evidence, visuals
