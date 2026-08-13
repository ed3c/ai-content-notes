#!/usr/bin/env python3
"""Materialize a projection bundle and a human-readable Markdown view."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import projection_dispatch
from semantic_runtime_common import load_json, sha256_file, stable_id, utc_now, validate, write_json


def build_markdown(projections: list[dict[str, object]]) -> str:
    parts = []
    for projection in projections:
        rendered = projection["rendered"]
        body = rendered["markdown"] or rendered["ascii"]
        parts.append(f"## {projection['title']}\n\n<!-- PROJECTION_ID: {projection['projection_id']} -->\n\n{body}")
    return "\n\n".join(parts).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--created-at")
    parser.add_argument("--graph-schema", type=Path, default=Path("schemas/relation-graph.schema.json"))
    parser.add_argument("--plan-schema", type=Path, default=Path("schemas/projection-plan-runtime.schema.json"))
    parser.add_argument("--bundle-schema", type=Path, default=Path("schemas/projection-bundle-runtime.schema.json"))
    args = parser.parse_args()
    graph, plan = load_json(args.graph), load_json(args.plan)
    validate(graph, args.graph_schema)
    validate(plan, args.plan_schema)
    digest = sha256_file(args.graph)
    if plan["source_graph_digest"] != digest:
        raise ValueError("projection plan graph digest mismatch")
    nodes = {item["node_id"]: item for item in graph["nodes"]}
    edges = {item["relation_id"]: item for item in graph["edges"]}
    projections = [projection_dispatch.render(item, nodes, edges) for item in plan["projections"]]
    bundle = {
        "schema_version": "projection-bundle@2",
        "bundle_id": plan.get("bundle_id") or stable_id("projection-bundle", digest),
        "source_graph_digest": digest,
        "projections": projections,
        "created_at": args.created_at or plan.get("created_at") or utc_now(),
    }
    validate(bundle, args.bundle_schema)
    write_json(args.output, bundle)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(build_markdown(projections), encoding="utf-8")
    print(json.dumps({"bundle_id": bundle["bundle_id"], "projection_count": len(projections)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
