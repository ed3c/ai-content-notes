#!/usr/bin/env python3
"""Build an evidence-bound relation graph and rank explanatory theses."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_VERSION = "relation-graph@1"
WEIGHTS = {
    "causal_reach": 0.25,
    "centrality": 0.20,
    "source_recurrence": 0.15,
    "decision_impact": 0.15,
    "source_emphasis": 0.10,
    "novelty": 0.10,
    "evidence_strength": 0.05,
}
VERIFICATION_STRENGTH = {
    "FALSIFIED": 0.0,
    "UNCHECKED": 0.2,
    "CONTESTED": 0.3,
    "SUPPORTED": 0.65,
    "CORROBORATED": 0.9,
    "TESTED": 1.0,
}
CONFIDENCE_STRENGTH = {"LOW": 0.3, "MEDIUM": 0.65, "HIGH": 1.0}


class RelationGraphError(RuntimeError):
    """Raised when assertions cannot form a grounded relation graph."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RelationGraphError(f"expected JSON object: {path}")
    return value


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:64] or "node"


def stable_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def normalize_node(raw: dict[str, Any]) -> dict[str, Any]:
    label = str(raw.get("label", "")).strip()
    if not label:
        raise RelationGraphError("every node requires a label")
    node_id = str(raw.get("node_id") or f"NODE-{slug(label)}-{stable_digest(raw)[:8]}")
    return {
        "node_id": node_id,
        "label": label,
        "node_kind": raw.get("node_kind", "claim"),
        "aliases": sorted(set(raw.get("aliases", []))),
        "evidence_ids": sorted(set(raw.get("evidence_ids", []))),
        "visual_ids": sorted(set(raw.get("visual_ids", []))),
        "tags": sorted(set(raw.get("tags", []))),
    }


def normalize_edge(raw: dict[str, Any], node_ids: set[str]) -> dict[str, Any]:
    subject, obj = str(raw.get("subject", "")), str(raw.get("object", ""))
    if subject not in node_ids or obj not in node_ids:
        raise RelationGraphError(f"relation references unknown node: {subject} -> {obj}")
    predicate = str(raw.get("predicate", "")).strip()
    if not predicate:
        raise RelationGraphError("every relation requires a predicate")
    evidence_ids = sorted(set(raw.get("evidence_ids", [])))
    visual_ids = sorted(set(raw.get("visual_ids", [])))
    verification = str(raw.get("verification", "UNCHECKED"))
    if verification in {"SUPPORTED", "CORROBORATED", "TESTED"} and not (
        evidence_ids or visual_ids
    ):
        raise RelationGraphError(
            f"{verification} relation must include evidence_ids or visual_ids"
        )
    decision_use = str(raw.get("decision_use", "")).strip()
    falsifier = str(raw.get("falsifier", "")).strip()
    if not decision_use or not falsifier:
        raise RelationGraphError(
            "every relation requires an explicit decision_use and falsifier"
        )
    canonical = {
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "relation_kind": raw.get("relation_kind", "flows_to"),
    }
    relation_id = str(
        raw.get("relation_id")
        or f"REL-{slug(subject)}-{slug(predicate)}-{slug(obj)}-{stable_digest(canonical)[:8]}"
    )
    return {
        "relation_id": relation_id,
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "relation_kind": raw.get("relation_kind", "flows_to"),
        "claim_kind": raw.get("claim_kind", "INFERENCE"),
        "verification": verification,
        "confidence": raw.get("confidence", "MEDIUM"),
        "evidence_ids": evidence_ids,
        "visual_ids": visual_ids,
        "decision_use": decision_use,
        "falsifier": falsifier,
        "projection_hints": sorted(set(raw.get("projection_hints", []))),
        "uncertain": bool(raw.get("uncertain", False)),
    }


def adjacency(edges: Iterable[dict[str, Any]]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        if edge["relation_kind"] in {
            "causes",
            "enables",
            "flows_to",
            "feeds",
            "transforms",
            "implements",
        }:
            graph[edge["subject"]].add(edge["object"])
    return graph


def reachable(start: Iterable[str], graph: dict[str, set[str]]) -> set[str]:
    seen = set(start)
    queue = deque(start)
    while queue:
        node = queue.popleft()
        for child in graph.get(node, set()):
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return seen


def clamp(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


def thesis_metrics(
    candidate: dict[str, Any],
    edges_by_id: dict[str, dict[str, Any]],
    graph: dict[str, set[str]],
    degree: dict[str, int],
    max_degree: int,
    max_evidence: int,
    total_nodes: int,
) -> dict[str, float]:
    relation_ids = candidate.get("relation_ids", [])
    unknown = [item for item in relation_ids if item not in edges_by_id]
    if unknown:
        raise RelationGraphError(
            f"thesis candidate references unknown relation IDs: {unknown}"
        )
    relations = [edges_by_id[item] for item in relation_ids]
    if not relations:
        raise RelationGraphError(
            f"thesis candidate has no valid relation IDs: {candidate.get('candidate_id')}"
        )
    involved = {
        item
        for relation in relations
        for item in (relation["subject"], relation["object"])
    }
    reach = reachable({relation["subject"] for relation in relations}, graph)
    causal_reach = (len(reach) - 1) / max(total_nodes - 1, 1)
    centrality = sum(
        degree.get(node, 0) / max(max_degree, 1) for node in involved
    ) / len(involved)
    evidence = {item for relation in relations for item in relation["evidence_ids"]}
    visuals = {item for relation in relations for item in relation["visual_ids"]}
    source_recurrence = (len(evidence) + len(visuals)) / max(max_evidence, 1)
    evidence_strength = sum(
        VERIFICATION_STRENGTH.get(relation["verification"], 0.2)
        * CONFIDENCE_STRENGTH.get(relation["confidence"], 0.3)
        for relation in relations
    ) / len(relations)
    return {
        "causal_reach": clamp(causal_reach),
        "centrality": clamp(centrality),
        "source_recurrence": clamp(source_recurrence),
        "decision_impact": clamp(candidate.get("decision_impact", 0.5)),
        "source_emphasis": clamp(candidate.get("source_emphasis", 0.5)),
        "novelty": clamp(candidate.get("novelty", 0.5)),
        "evidence_strength": clamp(evidence_strength),
    }


def score(metrics: dict[str, float]) -> float:
    return round(sum(metrics[name] * weight for name, weight in WEIGHTS.items()), 6)


def validate(value: dict[str, Any], schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--created-at")
    parser.add_argument(
        "--schema", type=Path, default=Path("schemas/relation-graph.schema.json")
    )
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    source = load_json(args.input)
    raw_nodes = source.get("nodes")
    raw_edges = source.get("edges")
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        raise RelationGraphError("input requires nodes and edges arrays")
    nodes = [normalize_node(item) for item in raw_nodes]
    node_ids = {node["node_id"] for node in nodes}
    if len(node_ids) != len(nodes):
        raise RelationGraphError("duplicate node_id")
    edges = [normalize_edge(item, node_ids) for item in raw_edges]
    edge_ids = {edge["relation_id"] for edge in edges}
    if len(edge_ids) != len(edges):
        raise RelationGraphError("duplicate relation_id")

    graph = adjacency(edges)
    degree: dict[str, int] = defaultdict(int)
    for edge in edges:
        degree[edge["subject"]] += 1
        degree[edge["object"]] += 1
    max_degree = max(degree.values(), default=1)
    evidence_counts = [
        len(set(edge["evidence_ids"])) + len(set(edge["visual_ids"]))
        for edge in edges
    ]
    max_evidence = max(evidence_counts, default=1)
    edges_by_id = {edge["relation_id"]: edge for edge in edges}

    ranking = []
    for candidate in source.get("thesis_candidates", []):
        metrics = thesis_metrics(
            candidate,
            edges_by_id,
            graph,
            degree,
            max_degree,
            max_evidence,
            len(nodes),
        )
        ranking.append(
            {
                "candidate_id": candidate["candidate_id"],
                "proposition": candidate["proposition"],
                "relation_ids": candidate["relation_ids"],
                "score": score(metrics),
                "score_breakdown": metrics,
            }
        )
    ranking.sort(key=lambda item: (-item["score"], item["candidate_id"]))

    result = {
        "schema_version": SCHEMA_VERSION,
        "graph_id": source.get("graph_id")
        or f"graph-{stable_digest({'nodes': nodes, 'edges': edges})[:12]}",
        "source_pack_digest": source["source_pack_digest"],
        "nodes": nodes,
        "edges": edges,
        "thesis_ranking": ranking,
        "created_at": args.created_at or source.get("created_at") or utc_now(),
    }
    validate(result, args.schema)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    graph = run(args)
    print(
        json.dumps(
            {
                "graph_id": graph["graph_id"],
                "node_count": len(graph["nodes"]),
                "edge_count": len(graph["edges"]),
                "selected_thesis": graph["thesis_ranking"][0]["candidate_id"]
                if graph["thesis_ranking"]
                else None,
                "output": str(args.output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
