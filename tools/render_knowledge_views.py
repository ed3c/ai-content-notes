#!/usr/bin/env python3
"""Render deterministic host-derived knowledge views from a relation graph.

The renderer binds one exact ``relation-graph@1`` receipt to a typed projection
plan. It emits JSON and Markdown views, but it never claims to reconstruct the
source video's original slide layout, text, chart axes, or visual values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

from jsonschema import Draft202012Validator, FormatChecker

PLAN_SCHEMA_VERSION = "knowledge-view-plan@1"
BUNDLE_SCHEMA_VERSION = "knowledge-view-bundle@1"
BUILDER_VERSION = "render-knowledge-views@1"
GRAPH_SCHEMA_VERSION = "relation-graph@1"
BLOCKED_VERIFICATION = {"CONTESTED", "FALSIFIED"}


class KnowledgeViewError(RuntimeError):
    """Raised when a projection cannot be rendered safely."""


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KnowledgeViewError(f"unable to read JSON object: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise KnowledgeViewError(f"expected JSON object: {path}")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _stable_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _display_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).strip().split())


def _identity_text(value: str) -> str:
    return _display_text(value).lower()


def _require_normalized_identity(value: str, label: str) -> str:
    normalized = _identity_text(value)
    if value != normalized:
        raise KnowledgeViewError(
            f"{label} must already be normalized lowercase identity text: "
            f"{value!r} -> {normalized!r}"
        )
    if not normalized:
        raise KnowledgeViewError(f"{label} must not be empty")
    return normalized


def _slug(value: str, limit: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (slug or "view")[:limit].rstrip("-") or "view"


def _stable_id(prefix: str, canonical_key: str) -> str:
    return f"{prefix}-{_slug(canonical_key)}-{_stable_hex(canonical_key)[:12]}"


def _validate(instance: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.path))
    if not errors:
        return
    rendered = []
    for error in errors:
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        rendered.append(f"{location}: {error.message}")
    raise KnowledgeViewError(f"{label} schema validation failed: " + "; ".join(rendered))


def _safe_relative_file(root: Path, raw_path: str) -> tuple[Path, str]:
    if "\\" in raw_path or "\x00" in raw_path:
        raise KnowledgeViewError(
            f"artifact path is not canonical POSIX text: {raw_path!r}"
        )
    pure = PurePosixPath(raw_path)
    if (
        not raw_path
        or pure.is_absolute()
        or pure.as_posix() != raw_path
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        raise KnowledgeViewError(
            f"artifact path must be a normalized relative path: {raw_path!r}"
        )

    root = root.resolve(strict=True)
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise KnowledgeViewError(f"symlink artifact paths are forbidden: {raw_path}")
    try:
        candidate = current.resolve(strict=True)
    except OSError as exc:
        raise KnowledgeViewError(f"artifact is missing: {raw_path}") from exc
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise KnowledgeViewError(f"artifact escapes root: {raw_path}") from exc
    if not candidate.is_file():
        raise KnowledgeViewError(f"artifact is not a regular file: {raw_path}")
    return candidate, pure.as_posix()


def _graph_subject(graph: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_pack": graph["source_pack"],
        "anchors": graph["anchors"],
        "nodes": graph["nodes"],
        "relations": graph["relations"],
        "thesis_ranking": graph["thesis_ranking"],
    }


def _load_graph(
    root: Path,
    contract: dict[str, Any],
    graph_schema: dict[str, Any],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    path, canonical_path = _safe_relative_file(root, contract["path"])
    payload = path.read_bytes()
    actual_sha = _sha256_bytes(payload)
    if actual_sha != contract["sha256"]:
        raise KnowledgeViewError(
            f"relation graph sha256 mismatch: expected {contract['sha256']}, "
            f"observed {actual_sha}"
        )

    graph = _read_json_object(path)
    _validate(graph, graph_schema, GRAPH_SCHEMA_VERSION)
    actual_subject = _sha256_bytes(_canonical_bytes(_graph_subject(graph)))
    if actual_subject != graph["graph_subject_digest"]:
        raise KnowledgeViewError(
            "relation graph contains stale graph_subject_digest: "
            f"expected {actual_subject}, observed {graph['graph_subject_digest']}"
        )
    expected_graph_id = f"GRAPH-{actual_subject.removeprefix('sha256:')[:16]}"
    if graph["graph_id"] != expected_graph_id:
        raise KnowledgeViewError(
            f"relation graph graph_id drift: expected {expected_graph_id}, "
            f"observed {graph['graph_id']}"
        )
    for field in ("graph_id", "graph_subject_digest"):
        if graph[field] != contract[field]:
            raise KnowledgeViewError(
                f"relation graph {field} mismatch: expected {contract[field]}, "
                f"observed {graph[field]}"
            )

    anchors_by_id = {item["anchor_id"]: item for item in graph["anchors"]}
    nodes_by_id = {item["node_id"]: item for item in graph["nodes"]}
    nodes_by_key = {item["canonical_key"]: item for item in graph["nodes"]}
    relations_by_id = {item["relation_id"]: item for item in graph["relations"]}
    if len(anchors_by_id) != len(graph["anchors"]):
        raise KnowledgeViewError("relation graph contains duplicate anchor_id")
    if len(nodes_by_id) != len(graph["nodes"]) or len(nodes_by_key) != len(
        graph["nodes"]
    ):
        raise KnowledgeViewError("relation graph contains duplicate node identity")
    if len(relations_by_id) != len(graph["relations"]):
        raise KnowledgeViewError("relation graph contains duplicate relation_id")

    for relation in graph["relations"]:
        if relation["subject"] not in nodes_by_id or relation["object"] not in nodes_by_id:
            raise KnowledgeViewError(
                f"relation graph relation references unknown node: "
                f"{relation['relation_id']}"
            )
        for field, expected_kind in (
            ("evidence_ids", "evidence"),
            ("visual_ids", "visual"),
            ("execution_artifact_ids", "execution"),
        ):
            for anchor_id in relation[field]:
                anchor = anchors_by_id.get(anchor_id)
                if anchor is None or anchor["anchor_kind"] != expected_kind:
                    raise KnowledgeViewError(
                        f"relation graph relation {relation['relation_id']} "
                        f"contains invalid {field} reference: {anchor_id}"
                    )

    thesis_ids = {item["candidate_id"] for item in graph["thesis_ranking"]}
    if graph["selected_thesis_id"] not in thesis_ids:
        raise KnowledgeViewError(
            "relation graph selected_thesis_id is not in thesis_ranking"
        )
    for thesis in graph["thesis_ranking"]:
        unknown_relations = set(thesis["relation_ids"]) - set(relations_by_id)
        if unknown_relations:
            raise KnowledgeViewError(
                f"relation graph thesis {thesis['candidate_id']} references "
                f"unknown relations: {sorted(unknown_relations)}"
            )

    identity = {
        "path": canonical_path,
        "sha256": actual_sha,
        "bytes": len(payload),
        "graph_id": graph["graph_id"],
        "graph_subject_digest": graph["graph_subject_digest"],
    }
    return graph, identity, nodes_by_id, nodes_by_key, relations_by_id


def _exact_config(config: dict[str, Any], allowed: set[str], owner: str) -> None:
    extra = set(config) - allowed
    missing = allowed - set(config)
    if extra or missing:
        raise KnowledgeViewError(
            f"{owner} config keys mismatch; missing={sorted(missing)}, "
            f"extra={sorted(extra)}"
        )


def _relations(
    relation_ids: list[str],
    relations_by_id: dict[str, dict[str, Any]],
    owner: str,
) -> list[dict[str, Any]]:
    normalized = sorted(set(relation_ids))
    selected = []
    for relation_id in normalized:
        relation = relations_by_id.get(relation_id)
        if relation is None:
            raise KnowledgeViewError(f"{owner} references unknown relation: {relation_id}")
        if relation["uncertain"] or relation["verification"] in BLOCKED_VERIFICATION:
            raise KnowledgeViewError(
                f"{owner} hides uncertain/contested/falsified relation: "
                f"{relation_id}"
            )
        selected.append(relation)
    return selected


def _mermaid_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def _node_aliases(node_ids: list[str]) -> dict[str, str]:
    return {node_id: f"N{index}" for index, node_id in enumerate(node_ids, start=1)}


def _flow(
    kind: str,
    config: dict[str, Any],
    relations: list[dict[str, Any]],
    nodes_by_id: dict[str, dict[str, Any]],
) -> tuple[str, str, int]:
    allowed = {"direction"}
    extra = set(config) - allowed
    if extra:
        raise KnowledgeViewError(
            f"{kind} config contains unsupported keys: {sorted(extra)}"
        )
    direction = config.get("direction", "LR")
    if direction not in {"LR", "RL", "TB", "BT"}:
        raise KnowledgeViewError(f"{kind} direction is invalid: {direction}")

    node_ids = sorted(
        {
            node_id
            for relation in relations
            for node_id in (relation["subject"], relation["object"])
        }
    )
    aliases = _node_aliases(node_ids)
    lines = [f"flowchart {direction}"]
    for node_id in node_ids:
        label = _mermaid_text(nodes_by_id[node_id]["label"])
        lines.append(f'    {aliases[node_id]}["{label}"]')
    for relation in relations:
        subject = aliases[relation["subject"]]
        obj = aliases[relation["object"]]
        predicate = _mermaid_text(relation["predicate"])
        lines.append(f"    {subject} -->|{predicate}| {obj}")
        lines.append(f"    %% {relation['relation_id']}")
    return "mermaid", "```mermaid\n" + "\n".join(lines) + "\n```", 0


def _equation(
    config: dict[str, Any],
    nodes_by_key: dict[str, dict[str, Any]],
) -> tuple[str, str, int, set[str]]:
    _exact_config(config, {"expression", "symbol_bindings"}, "equation")
    expression = _display_text(str(config["expression"]))
    if not expression:
        raise KnowledgeViewError("equation expression must not be empty")

    symbols: set[str] = set()
    node_ids: set[str] = set()
    rows = []
    bindings = config["symbol_bindings"]
    if not isinstance(bindings, list) or not bindings:
        raise KnowledgeViewError("equation symbol_bindings must be a non-empty array")
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"symbol", "node_key"}:
            raise KnowledgeViewError(
                "equation bindings require exactly symbol and node_key"
            )
        symbol = _display_text(str(binding["symbol"]))
        node_key = _require_normalized_identity(
            str(binding["node_key"]), "equation node_key"
        )
        if symbol in symbols:
            raise KnowledgeViewError(f"duplicate equation symbol: {symbol}")
        node = nodes_by_key.get(node_key)
        if node is None:
            raise KnowledgeViewError(
                f"equation symbol {symbol} references unknown node: {node_key}"
            )
        if re.search(rf"(?<!\w){re.escape(symbol)}(?!\w)", expression) is None:
            raise KnowledgeViewError(
                f"equation symbol is not present in expression: {symbol}"
            )
        symbols.add(symbol)
        node_ids.add(node["node_id"])
        rows.append((symbol, node["label"], node_key))

    body = [
        "```text",
        expression,
        "```",
        "",
        "| Symbol | Node | Canonical key |",
        "|---|---|---|",
    ]
    for symbol, label, node_key in sorted(rows):
        body.append(f"| {symbol} | {label} | `{node_key}` |")
    return "text", "\n".join(body), 0, node_ids


def _timeline(
    config: dict[str, Any],
    projection_relation_ids: set[str],
    nodes_by_key: dict[str, dict[str, Any]],
) -> tuple[str, str, int, set[str]]:
    _exact_config(config, {"steps"}, "timeline")
    steps = config["steps"]
    if not isinstance(steps, list) or len(steps) < 2:
        raise KnowledgeViewError("timeline requires at least two steps")
    used_relations: set[str] = set()
    node_ids: set[str] = set()
    node_keys: set[str] = set()
    labels: list[str] = []
    for step in steps:
        if not isinstance(step, dict) or set(step) != {
            "label",
            "node_key",
            "relation_ids",
        }:
            raise KnowledgeViewError(
                "timeline steps require exactly label, node_key and relation_ids"
            )
        node_key = _require_normalized_identity(
            str(step["node_key"]), "timeline node_key"
        )
        node = nodes_by_key.get(node_key)
        if node is None:
            raise KnowledgeViewError(f"timeline references unknown node: {node_key}")
        if node_key in node_keys:
            raise KnowledgeViewError(f"timeline repeats node_key: {node_key}")
        node_keys.add(node_key)
        node_ids.add(node["node_id"])
        labels.append(_display_text(str(step["label"])))
        step_relations = set(step["relation_ids"])
        if not step_relations <= projection_relation_ids:
            raise KnowledgeViewError(
                "timeline step references relation outside projection"
            )
        used_relations.update(step_relations)
    if used_relations != projection_relation_ids:
        raise KnowledgeViewError(
            "timeline relation coverage must equal projection relation_ids"
        )

    lines = ["flowchart LR"]
    for index, label in enumerate(labels, start=1):
        lines.append(f'    S{index}["{_mermaid_text(label)}"]')
    for index in range(1, len(labels)):
        lines.append(f"    S{index} --> S{index + 1}")
    for relation_id in sorted(used_relations):
        lines.append(f"    %% {relation_id}")
    return "mermaid", "```mermaid\n" + "\n".join(lines) + "\n```", 0, node_ids


def _state_planes(
    config: dict[str, Any],
    projection_relation_ids: set[str],
    nodes_by_key: dict[str, dict[str, Any]],
) -> tuple[str, str, int, set[str]]:
    _exact_config(config, {"lanes"}, "state-planes")
    lanes = config["lanes"]
    if not isinstance(lanes, list) or len(lanes) < 2:
        raise KnowledgeViewError("state-planes requires at least two lanes")
    labels: set[str] = set()
    used_relations: set[str] = set()
    node_ids: set[str] = set()
    rows = ["| Plane | Nodes | Relations |", "|---|---|---|"]
    for lane in lanes:
        if not isinstance(lane, dict) or set(lane) != {
            "label",
            "node_keys",
            "relation_ids",
        }:
            raise KnowledgeViewError(
                "state-plane lanes require exactly label, node_keys and relation_ids"
            )
        label = _display_text(str(lane["label"]))
        if label in labels:
            raise KnowledgeViewError(f"duplicate state-plane label: {label}")
        labels.add(label)
        node_keys = list(lane["node_keys"])
        if not node_keys:
            raise KnowledgeViewError(f"state-plane lane has no nodes: {label}")
        node_labels = []
        for raw_key in node_keys:
            node_key = _require_normalized_identity(
                str(raw_key), "state-plane node_key"
            )
            node = nodes_by_key.get(node_key)
            if node is None:
                raise KnowledgeViewError(
                    f"state-plane {label} references unknown node: {node_key}"
                )
            node_ids.add(node["node_id"])
            node_labels.append(node["label"])
        lane_relations = set(lane["relation_ids"])
        if not lane_relations <= projection_relation_ids:
            raise KnowledgeViewError(
                f"state-plane {label} references relation outside projection"
            )
        used_relations.update(lane_relations)
        rows.append(
            f"| {label} | {', '.join(node_labels)} | "
            f"{', '.join(sorted(lane_relations)) or 'N/A'} |"
        )
    if used_relations != projection_relation_ids:
        raise KnowledgeViewError(
            "state-plane relation coverage must equal projection relation_ids"
        )
    return "markdown-table", "\n".join(rows), 0, node_ids


def _comparison(
    config: dict[str, Any],
    projection_relation_ids: set[str],
) -> tuple[str, str, int]:
    _exact_config(config, {"columns", "rows"}, "comparison-matrix")
    columns = [_display_text(str(item)) for item in config["columns"]]
    if len(columns) < 2 or len(set(columns)) != len(columns):
        raise KnowledgeViewError(
            "comparison columns must contain at least two unique labels"
        )
    rows = config["rows"]
    if not isinstance(rows, list) or not rows:
        raise KnowledgeViewError("comparison rows must be a non-empty array")

    dimensions: set[str] = set()
    used_relations: set[str] = set()
    unknown_count = 0
    rendered = [
        "| Dimension | " + " | ".join(columns) + " |",
        "|" + "---|" * (len(columns) + 1),
    ]
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"dimension", "cells"}:
            raise KnowledgeViewError(
                "comparison rows require exactly dimension and cells"
            )
        dimension = _display_text(str(row["dimension"]))
        if dimension in dimensions:
            raise KnowledgeViewError(f"duplicate comparison dimension: {dimension}")
        dimensions.add(dimension)
        cells = row["cells"]
        if not isinstance(cells, list) or len(cells) != len(columns):
            raise KnowledgeViewError(
                f"comparison row {dimension} cell count does not match columns"
            )
        cell_values = []
        for cell in cells:
            if not isinstance(cell, dict) or set(cell) != {
                "value",
                "status",
                "relation_ids",
            }:
                raise KnowledgeViewError(
                    "comparison cells require value, status and relation_ids"
                )
            value = _display_text(str(cell["value"]))
            relation_ids = set(cell["relation_ids"])
            if not relation_ids <= projection_relation_ids:
                raise KnowledgeViewError(
                    f"comparison cell {dimension} references relation outside projection"
                )
            if cell["status"] == "GROUNDED":
                if value == "UNKNOWN" or not relation_ids:
                    raise KnowledgeViewError(
                        f"GROUNDED comparison cell requires a value and relation "
                        f"provenance: {dimension}"
                    )
                used_relations.update(relation_ids)
            elif cell["status"] == "UNKNOWN":
                if value != "UNKNOWN" or relation_ids:
                    raise KnowledgeViewError(
                        f"UNKNOWN comparison cell must contain exactly UNKNOWN "
                        f"without relation provenance: {dimension}"
                    )
                unknown_count += 1
            else:
                raise KnowledgeViewError(
                    f"comparison cell status is invalid: {cell['status']}"
                )
            cell_values.append(value.replace("|", "\\|"))
        rendered.append(f"| {dimension} | " + " | ".join(cell_values) + " |")
    if used_relations != projection_relation_ids:
        raise KnowledgeViewError(
            "comparison grounded relation coverage must equal projection relation_ids"
        )
    return "markdown-table", "\n".join(rendered), unknown_count


def _projection(
    raw: dict[str, Any],
    nodes_by_id: dict[str, dict[str, Any]],
    nodes_by_key: dict[str, dict[str, Any]],
    relations_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    canonical_key = _require_normalized_identity(
        raw["canonical_key"], "projection canonical_key"
    )
    projection_id = _stable_id("VIEW", canonical_key)
    if raw.get("projection_id") is not None and raw["projection_id"] != projection_id:
        raise KnowledgeViewError(
            f"projection_id drift for {canonical_key}: expected {projection_id}, "
            f"observed {raw['projection_id']}"
        )

    relations = _relations(
        raw["relation_ids"],
        relations_by_id,
        f"projection {canonical_key}",
    )
    relation_ids = [item["relation_id"] for item in relations]
    relation_id_set = set(relation_ids)
    relation_node_ids = {
        node_id
        for relation in relations
        for node_id in (relation["subject"], relation["object"])
    }
    kind = raw["projection_kind"]
    config = raw["config"]

    if kind in {"causal-dataflow", "architecture"}:
        rendered_format, content, unknown_count = _flow(
            kind,
            config,
            relations,
            nodes_by_id,
        )
        node_ids = relation_node_ids
    elif kind == "equation":
        rendered_format, content, unknown_count, config_nodes = _equation(
            config,
            nodes_by_key,
        )
        node_ids = relation_node_ids | config_nodes
    elif kind == "timeline":
        rendered_format, content, unknown_count, config_nodes = _timeline(
            config,
            relation_id_set,
            nodes_by_key,
        )
        node_ids = relation_node_ids | config_nodes
    elif kind == "state-planes":
        rendered_format, content, unknown_count, config_nodes = _state_planes(
            config,
            relation_id_set,
            nodes_by_key,
        )
        node_ids = relation_node_ids | config_nodes
    elif kind == "comparison-matrix":
        rendered_format, content, unknown_count = _comparison(
            config,
            relation_id_set,
        )
        node_ids = relation_node_ids
    else:
        raise KnowledgeViewError(f"unsupported projection kind: {kind}")

    anchor_ids = sorted(
        {
            anchor_id
            for relation in relations
            for field in (
                "evidence_ids",
                "visual_ids",
                "execution_artifact_ids",
            )
            for anchor_id in relation[field]
        }
    )
    return {
        "projection_id": projection_id,
        "canonical_key": canonical_key,
        "title": _display_text(raw["title"]),
        "projection_kind": kind,
        "relation_ids": relation_ids,
        "node_ids": sorted(node_ids),
        "rendered": {
            "format": rendered_format,
            "content": content,
        },
        "provenance": {
            "relation_ids": relation_ids,
            "node_ids": sorted(node_ids),
            "anchor_ids": anchor_ids,
        },
        "unknown_count": unknown_count,
    }


def _markdown(projections: list[dict[str, Any]]) -> str:
    parts = [
        "# Knowledge Views",
        "",
        "> Host-derived projections from an evidence-bound relation graph. "
        "These views are not reconstructions of source slides, chart axes, "
        "visual text, or original layout.",
    ]
    for projection in projections:
        parts.extend(
            [
                "",
                f"## {projection['title']}",
                "",
                f"<!-- PROJECTION_ID: {projection['projection_id']} -->",
                "",
                f"- **Kind**: `{projection['projection_kind']}`",
                "- **Authority**: `host-derived`; "
                "`source_visual_reconstruction=false`",
                "- **Relations**: "
                + ", ".join(f"`{item}`" for item in projection["relation_ids"]),
                "",
                projection["rendered"]["content"],
            ]
        )
    return "\n".join(parts).rstrip() + "\n"


def build_knowledge_views(
    *,
    plan_path: Path,
    root: Path,
    created_at: str,
    schema_root: Path | None = None,
) -> tuple[dict[str, Any], str]:
    """Build and validate a projection bundle and Markdown view."""

    schema_root = schema_root or root / "schemas"
    plan_schema = _read_json_object(
        schema_root / "knowledge-view-plan.schema.json"
    )
    bundle_schema = _read_json_object(
        schema_root / "knowledge-view-bundle.schema.json"
    )
    graph_schema = _read_json_object(schema_root / "relation-graph.schema.json")
    plan = _read_json_object(plan_path)
    _validate(plan, plan_schema, PLAN_SCHEMA_VERSION)

    (
        _graph,
        graph_identity,
        nodes_by_id,
        nodes_by_key,
        relations_by_id,
    ) = _load_graph(root, plan["relation_graph"], graph_schema)

    projections: list[dict[str, Any]] = []
    projection_keys: set[str] = set()
    projection_ids: set[str] = set()
    for raw in plan["projections"]:
        projection = _projection(
            raw,
            nodes_by_id,
            nodes_by_key,
            relations_by_id,
        )
        canonical_key = projection["canonical_key"]
        projection_id = projection["projection_id"]
        if canonical_key in projection_keys:
            raise KnowledgeViewError(
                f"duplicate projection canonical_key: {canonical_key}"
            )
        if projection_id in projection_ids:
            raise KnowledgeViewError(
                f"duplicate deterministic projection_id: {projection_id}"
            )
        projection_keys.add(canonical_key)
        projection_ids.add(projection_id)
        projections.append(projection)
    projections.sort(key=lambda item: item["canonical_key"])

    normalized_plan = {
        "relation_graph": graph_identity,
        "projections": projections,
    }
    plan_digest = _sha256_bytes(_canonical_bytes(normalized_plan))
    bundle_subject = {
        "relation_graph": graph_identity,
        "projection_authority": {
            "kind": "host-derived",
            "source_visual_reconstruction": False,
        },
        "projections": projections,
    }
    bundle_subject_digest = _sha256_bytes(_canonical_bytes(bundle_subject))
    bundle_id = f"BUNDLE-{bundle_subject_digest.removeprefix('sha256:')[:16]}"
    if plan.get("bundle_id") is not None and plan["bundle_id"] != bundle_id:
        raise KnowledgeViewError(
            f"bundle_id drift: expected {bundle_id}, observed {plan['bundle_id']}"
        )

    markdown = _markdown(projections)
    markdown_payload = markdown.encode("utf-8")
    bundle = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "builder_version": BUILDER_VERSION,
        "bundle_id": bundle_id,
        "plan_digest": plan_digest,
        "bundle_subject_digest": bundle_subject_digest,
        "relation_graph": graph_identity,
        "projection_authority": {
            "kind": "host-derived",
            "source_visual_reconstruction": False,
        },
        "projections": projections,
        "markdown_sha256": _sha256_bytes(markdown_payload),
        "markdown_bytes": len(markdown_payload),
        "created_at": created_at,
    }
    _validate(bundle, bundle_schema, BUNDLE_SCHEMA_VERSION)
    return bundle, markdown


def _write_or_check(
    bundle: dict[str, Any],
    markdown: str,
    output: Path,
    markdown_output: Path,
    check: bool,
) -> None:
    expected_json = _pretty_json(bundle)
    if check:
        if not output.is_file() or not markdown_output.is_file():
            raise KnowledgeViewError("check output or Markdown output is missing")
        if output.read_text(encoding="utf-8") != expected_json:
            raise KnowledgeViewError(f"persisted knowledge-view bundle is stale: {output}")
        if markdown_output.read_text(encoding="utf-8") != markdown:
            raise KnowledgeViewError(
                f"persisted knowledge-view Markdown is stale: {markdown_output}"
            )
        return

    for path, content in ((output, expected_json), (markdown_output, markdown)):
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--schema-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    parser.add_argument("--created-at", required=True)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        bundle, markdown = build_knowledge_views(
            plan_path=args.plan,
            root=args.root,
            created_at=args.created_at,
            schema_root=args.schema_root,
        )
        _write_or_check(
            bundle,
            markdown,
            args.output,
            args.markdown_output,
            args.check,
        )
    except KnowledgeViewError as exc:
        raise SystemExit(str(exc)) from exc
    print(_pretty_json(bundle), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
