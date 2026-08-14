#!/usr/bin/env python3
"""Build a deterministic evidence-bound relation graph and rank theses.

The builder consumes one exact ``multimodal-source-pack@1`` receipt. It does
not acquire media, invoke a model, render cards, or prove that a relation is
true. It validates declared grounding, computes stable semantic identities,
and emits a reproducible graph for later projection and evaluation leaves.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from collections import defaultdict, deque
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence

from jsonschema import Draft202012Validator, FormatChecker

INPUT_SCHEMA_VERSION = "relation-graph-input@1"
OUTPUT_SCHEMA_VERSION = "relation-graph@1"
BUILDER_VERSION = "build-relation-graph@1"
SOURCE_PACK_SCHEMA_VERSION = "multimodal-source-pack@1"

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
CAUSAL_RELATION_KINDS = {
    "causes",
    "enables",
    "flows_to",
    "feeds",
    "transforms",
    "implements",
}


class RelationGraphError(RuntimeError):
    """Raised when a relation graph cannot be built safely."""


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RelationGraphError(f"unable to read JSON object: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RelationGraphError(f"expected JSON object: {path}")
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
        raise RelationGraphError(
            f"{label} must already be normalized lowercase identity text: "
            f"{value!r} -> {normalized!r}"
        )
    if not normalized:
        raise RelationGraphError(f"{label} must not be empty")
    return normalized


def _slug(value: str, limit: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (slug or "semantic")[:limit].rstrip("-") or "semantic"


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
    raise RelationGraphError(f"{label} schema validation failed: " + "; ".join(rendered))


def _safe_relative_file(root: Path, raw_path: str) -> tuple[Path, str]:
    if "\\" in raw_path or "\x00" in raw_path:
        raise RelationGraphError(
            f"artifact path is not canonical POSIX text: {raw_path!r}"
        )
    pure = PurePosixPath(raw_path)
    if (
        not raw_path
        or pure.is_absolute()
        or pure.as_posix() != raw_path
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        raise RelationGraphError(
            f"artifact path must be a normalized relative path: {raw_path!r}"
        )

    root = root.resolve(strict=True)
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise RelationGraphError(f"symlink artifact paths are forbidden: {raw_path}")
    try:
        candidate = current.resolve(strict=True)
    except OSError as exc:
        raise RelationGraphError(f"artifact is missing: {raw_path}") from exc
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise RelationGraphError(f"artifact escapes root: {raw_path}") from exc
    if not candidate.is_file():
        raise RelationGraphError(f"artifact is not a regular file: {raw_path}")
    return candidate, pure.as_posix()


def _source_pack(
    root: Path,
    contract: dict[str, Any],
    source_pack_schema: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    path, canonical_path = _safe_relative_file(root, contract["path"])
    payload = path.read_bytes()
    actual_sha = _sha256_bytes(payload)
    if actual_sha != contract["sha256"]:
        raise RelationGraphError(
            f"source pack sha256 mismatch: expected {contract['sha256']}, "
            f"observed {actual_sha}"
        )

    pack = _read_json_object(path)
    _validate(pack, source_pack_schema, SOURCE_PACK_SCHEMA_VERSION)
    expected_fields = ("pack_id", "descriptor_digest", "source_set_digest")
    for field in expected_fields:
        if pack[field] != contract[field]:
            raise RelationGraphError(
                f"source pack {field} mismatch: expected {contract[field]}, "
                f"observed {pack[field]}"
            )
    if not pack["authority"]["may_compile_cards"]:
        raise RelationGraphError(
            "source pack authority does not permit semantic/card compilation"
        )

    declared_dependencies = set(pack["source_dependency_keys"])
    used_dependencies: set[str] = set()
    artifacts: dict[str, dict[str, Any]] = {}
    for artifact in pack["artifacts"]:
        artifact_id = artifact["artifact_id"]
        if artifact_id in artifacts:
            raise RelationGraphError(
                f"source pack contains duplicate artifact_id: {artifact_id}"
            )
        dependency_key = artifact["source_dependency_key"]
        if dependency_key not in declared_dependencies:
            raise RelationGraphError(
                "source-pack artifact references undeclared dependency: "
                f"{artifact_id}: {dependency_key}"
            )
        used_dependencies.add(dependency_key)
        artifacts[artifact_id] = artifact
    missing_dependencies = declared_dependencies - used_dependencies
    if missing_dependencies:
        raise RelationGraphError(
            "source-pack dependencies have no artifact: "
            + ", ".join(sorted(missing_dependencies))
        )

    identity = {
        "path": canonical_path,
        "sha256": actual_sha,
        "bytes": len(payload),
        "pack_id": pack["pack_id"],
        "descriptor_digest": pack["descriptor_digest"],
        "source_set_digest": pack["source_set_digest"],
        "source_dependency_keys": sorted(pack["source_dependency_keys"]),
    }
    return identity, artifacts


def _anchors(
    raw_anchors: list[dict[str, Any]],
    artifacts: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    anchors: list[dict[str, Any]] = []
    anchors_by_id: dict[str, dict[str, Any]] = {}

    for raw in raw_anchors:
        anchor_id = raw["anchor_id"]
        if anchor_id in anchors_by_id:
            raise RelationGraphError(f"duplicate anchor_id: {anchor_id}")
        artifact_id = raw["artifact_id"]
        artifact = artifacts.get(artifact_id)
        if artifact is None:
            raise RelationGraphError(
                f"anchor {anchor_id} references unknown source-pack artifact: "
                f"{artifact_id}"
            )

        kind = raw["anchor_kind"]
        modality = artifact["modality"]
        role = artifact["role"]
        if kind == "visual" and modality not in {"video-frame", "visual-evidence"}:
            raise RelationGraphError(
                f"visual anchor {anchor_id} must reference a visual artifact"
            )
        if kind == "evidence" and modality in {"video-frame", "visual-evidence"}:
            raise RelationGraphError(
                f"visual artifacts must use anchor_kind=visual: {anchor_id}"
            )
        if kind == "execution" and role != "audit-artifact":
            raise RelationGraphError(
                f"execution anchor {anchor_id} must reference an audit-artifact"
            )

        anchor = {
            "anchor_id": anchor_id,
            "anchor_kind": kind,
            "artifact_id": artifact_id,
            "artifact_role": role,
            "artifact_modality": modality,
            "artifact_sha256": artifact["sha256"],
            "source_dependency_key": artifact["source_dependency_key"],
            "locator": raw.get("locator"),
            "description": raw.get("description"),
        }
        anchors_by_id[anchor_id] = anchor
        anchors.append(anchor)

    anchors.sort(key=lambda item: item["anchor_id"])
    return anchors, anchors_by_id


def _anchor_refs(
    ids: Iterable[str],
    expected_kind: str,
    anchors_by_id: dict[str, dict[str, Any]],
    owner: str,
) -> list[str]:
    normalized = sorted(set(ids))
    for anchor_id in normalized:
        anchor = anchors_by_id.get(anchor_id)
        if anchor is None:
            raise RelationGraphError(f"{owner} references unknown anchor: {anchor_id}")
        if anchor["anchor_kind"] != expected_kind:
            raise RelationGraphError(
                f"{owner} references {anchor['anchor_kind']} anchor "
                f"{anchor_id} as {expected_kind}"
            )
    return normalized


def _nodes(
    raw_nodes: list[dict[str, Any]],
    anchors_by_id: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    nodes_by_key: dict[str, dict[str, Any]] = {}
    node_ids: set[str] = set()

    for raw in raw_nodes:
        canonical_key = _require_normalized_identity(
            raw["canonical_key"], "node canonical_key"
        )
        if canonical_key in nodes_by_key:
            raise RelationGraphError(f"duplicate node canonical_key: {canonical_key}")

        node_id = _stable_id("NODE", canonical_key)
        if raw.get("node_id") is not None and raw["node_id"] != node_id:
            raise RelationGraphError(
                f"node_id drift for {canonical_key}: expected {node_id}, "
                f"observed {raw['node_id']}"
            )
        if node_id in node_ids:
            raise RelationGraphError(f"duplicate deterministic node_id: {node_id}")
        node_ids.add(node_id)

        node = {
            "node_id": node_id,
            "canonical_key": canonical_key,
            "label": _display_text(raw["label"]),
            "node_kind": raw["node_kind"],
            "aliases": sorted({_display_text(item) for item in raw["aliases"]}),
            "evidence_ids": _anchor_refs(
                raw["evidence_ids"],
                "evidence",
                anchors_by_id,
                f"node {canonical_key}",
            ),
            "visual_ids": _anchor_refs(
                raw["visual_ids"],
                "visual",
                anchors_by_id,
                f"node {canonical_key}",
            ),
            "tags": sorted({_identity_text(item) for item in raw["tags"]}),
        }
        nodes_by_key[canonical_key] = node
        nodes.append(node)

    nodes.sort(key=lambda item: item["canonical_key"])
    return nodes, nodes_by_key


def _relation_key(
    subject_key: str,
    relation_kind: str,
    predicate: str,
    object_key: str,
) -> str:
    return (
        f"{subject_key} | {relation_kind} | "
        f"{_identity_text(predicate)} | {object_key}"
    )


def _relations(
    raw_relations: list[dict[str, Any]],
    nodes_by_key: dict[str, dict[str, Any]],
    anchors_by_id: dict[str, dict[str, Any]],
    pack_dependency_keys: set[str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    relations: list[dict[str, Any]] = []
    relations_by_key: dict[str, dict[str, Any]] = {}
    relation_ids: set[str] = set()

    for raw in raw_relations:
        subject_key = _require_normalized_identity(
            raw["subject_key"], "relation subject_key"
        )
        object_key = _require_normalized_identity(
            raw["object_key"], "relation object_key"
        )
        if subject_key not in nodes_by_key or object_key not in nodes_by_key:
            raise RelationGraphError(
                f"relation references unknown node: {subject_key} -> {object_key}"
            )
        predicate = _display_text(raw["predicate"])
        canonical_key = _relation_key(
            subject_key,
            raw["relation_kind"],
            predicate,
            object_key,
        )
        if raw["relation_key"] != canonical_key:
            raise RelationGraphError(
                f"relation_key drift: expected {canonical_key!r}, "
                f"observed {raw['relation_key']!r}"
            )
        if canonical_key in relations_by_key:
            raise RelationGraphError(
                f"duplicate relation canonical_key: {canonical_key}"
            )

        relation_id = _stable_id("REL", canonical_key)
        if raw.get("relation_id") is not None and raw["relation_id"] != relation_id:
            raise RelationGraphError(
                f"relation_id drift for {canonical_key}: expected {relation_id}, "
                f"observed {raw['relation_id']}"
            )
        if relation_id in relation_ids:
            raise RelationGraphError(
                f"duplicate deterministic relation_id: {relation_id}"
            )
        relation_ids.add(relation_id)

        evidence_ids = _anchor_refs(
            raw["evidence_ids"],
            "evidence",
            anchors_by_id,
            f"relation {canonical_key}",
        )
        visual_ids = _anchor_refs(
            raw["visual_ids"],
            "visual",
            anchors_by_id,
            f"relation {canonical_key}",
        )
        execution_ids = _anchor_refs(
            raw["execution_artifact_ids"],
            "execution",
            anchors_by_id,
            f"relation {canonical_key}",
        )
        grounding_ids = evidence_ids + visual_ids
        dependency_keys = sorted(
            {
                anchors_by_id[anchor_id]["source_dependency_key"]
                for anchor_id in grounding_ids
            }
        )
        unknown_dependencies = set(dependency_keys) - pack_dependency_keys
        if unknown_dependencies:
            raise RelationGraphError(
                f"relation {canonical_key} resolved unknown dependencies: "
                + ", ".join(sorted(unknown_dependencies))
            )

        verification = raw["verification"]
        if verification == "SUPPORTED" and not grounding_ids:
            raise RelationGraphError(
                f"SUPPORTED relation requires evidence or visual anchors: "
                f"{canonical_key}"
            )
        if verification == "CORROBORATED" and len(dependency_keys) < 2:
            raise RelationGraphError(
                f"CORROBORATED relation requires at least two independent "
                f"source dependencies: {canonical_key}"
            )
        if verification == "TESTED" and not execution_ids:
            raise RelationGraphError(
                f"TESTED relation requires execution_artifact_ids: {canonical_key}"
            )
        if verification == "FALSIFIED" and not (grounding_ids or execution_ids):
            raise RelationGraphError(
                f"FALSIFIED relation requires grounding: {canonical_key}"
            )

        relation = {
            "relation_id": relation_id,
            "canonical_key": canonical_key,
            "subject": nodes_by_key[subject_key]["node_id"],
            "subject_canonical_key": subject_key,
            "predicate": predicate,
            "object": nodes_by_key[object_key]["node_id"],
            "object_canonical_key": object_key,
            "relation_kind": raw["relation_kind"],
            "claim_kind": raw["claim_kind"],
            "verification": verification,
            "confidence": raw["confidence"],
            "evidence_ids": evidence_ids,
            "visual_ids": visual_ids,
            "execution_artifact_ids": execution_ids,
            "source_dependency_keys": dependency_keys,
            "decision_use": _display_text(raw["decision_use"]),
            "falsifier": _display_text(raw["falsifier"]),
            "projection_hints": sorted(set(raw["projection_hints"])),
            "uncertain": bool(raw["uncertain"]),
        }
        relations_by_key[canonical_key] = relation
        relations.append(relation)

    relations.sort(key=lambda item: item["canonical_key"])
    return relations, relations_by_key


def _adjacency(relations: Iterable[dict[str, Any]]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    for relation in relations:
        if relation["relation_kind"] in CAUSAL_RELATION_KINDS:
            graph[relation["subject"]].add(relation["object"])
    return graph


def _reachable(starts: Iterable[str], graph: dict[str, set[str]]) -> set[str]:
    seen = set(starts)
    queue = deque(sorted(seen))
    while queue:
        node = queue.popleft()
        for child in sorted(graph.get(node, set())):
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return seen


def _clamp(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


def _score(metrics: dict[str, float]) -> float:
    return round(
        sum(metrics[name] * weight for name, weight in WEIGHTS.items()),
        6,
    )


def _theses(
    raw_candidates: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    relations_by_key: dict[str, dict[str, Any]],
    total_nodes: int,
    total_pack_dependencies: int,
) -> list[dict[str, Any]]:
    graph = _adjacency(relations)
    degree: dict[str, int] = defaultdict(int)
    for relation in relations:
        degree[relation["subject"]] += 1
        degree[relation["object"]] += 1
    max_degree = max(degree.values(), default=1)

    ranking: list[dict[str, Any]] = []
    candidate_keys: set[str] = set()
    candidate_ids: set[str] = set()

    for raw in raw_candidates:
        canonical_key = _require_normalized_identity(
            raw["canonical_key"], "thesis canonical_key"
        )
        if canonical_key in candidate_keys:
            raise RelationGraphError(
                f"duplicate thesis canonical_key: {canonical_key}"
            )
        candidate_keys.add(canonical_key)

        candidate_id = _stable_id("TH", canonical_key)
        if raw.get("candidate_id") is not None and raw["candidate_id"] != candidate_id:
            raise RelationGraphError(
                f"candidate_id drift for {canonical_key}: expected {candidate_id}, "
                f"observed {raw['candidate_id']}"
            )
        if candidate_id in candidate_ids:
            raise RelationGraphError(
                f"duplicate deterministic candidate_id: {candidate_id}"
            )
        candidate_ids.add(candidate_id)

        relation_keys = sorted(set(raw["relation_keys"]))
        unknown = [key for key in relation_keys if key not in relations_by_key]
        if unknown:
            raise RelationGraphError(
                f"thesis {canonical_key} references unknown relation_keys: {unknown}"
            )
        selected = [relations_by_key[key] for key in relation_keys]
        blocked = [
            relation["canonical_key"]
            for relation in selected
            if relation["uncertain"]
            or relation["verification"] in {"CONTESTED", "FALSIFIED"}
        ]
        if blocked:
            raise RelationGraphError(
                f"thesis {canonical_key} hides uncertain/contested/falsified "
                f"relations: {blocked}"
            )

        involved = {
            item
            for relation in selected
            for item in (relation["subject"], relation["object"])
        }
        starts = {relation["subject"] for relation in selected}
        reach = _reachable(starts, graph)
        causal_reach = len(reach) / max(total_nodes, 1)
        centrality = (
            sum(degree.get(node, 0) / max_degree for node in involved)
            / max(len(involved), 1)
        )
        dependency_keys = {
            key for relation in selected for key in relation["source_dependency_keys"]
        }
        source_recurrence = len(dependency_keys) / max(total_pack_dependencies, 1)
        evidence_strength = sum(
            VERIFICATION_STRENGTH[relation["verification"]]
            * CONFIDENCE_STRENGTH[relation["confidence"]]
            for relation in selected
        ) / len(selected)
        metrics = {
            "causal_reach": _clamp(causal_reach),
            "centrality": _clamp(centrality),
            "source_recurrence": _clamp(source_recurrence),
            "decision_impact": _clamp(raw["decision_impact"]),
            "source_emphasis": _clamp(raw["source_emphasis"]),
            "novelty": _clamp(raw["novelty"]),
            "evidence_strength": _clamp(evidence_strength),
        }
        ranking.append(
            {
                "candidate_id": candidate_id,
                "canonical_key": canonical_key,
                "proposition": _display_text(raw["proposition"]),
                "relation_ids": sorted(
                    relation["relation_id"] for relation in selected
                ),
                "score": _score(metrics),
                "score_breakdown": metrics,
            }
        )

    ranking.sort(key=lambda item: (-item["score"], item["candidate_id"]))
    return ranking


def build_relation_graph(
    *,
    input_path: Path,
    root: Path,
    created_at: str,
    schema_root: Path | None = None,
) -> dict[str, Any]:
    """Build and validate one relation graph without writing it."""

    schema_root = schema_root or root / "schemas"
    input_schema = _read_json_object(
        schema_root / "relation-graph-input.schema.json"
    )
    output_schema = _read_json_object(schema_root / "relation-graph.schema.json")
    source_pack_schema = _read_json_object(
        schema_root / "multimodal-source-pack.schema.json"
    )
    source = _read_json_object(input_path)
    _validate(source, input_schema, INPUT_SCHEMA_VERSION)

    source_pack, artifacts = _source_pack(
        root,
        source["source_pack"],
        source_pack_schema,
    )
    anchors, anchors_by_id = _anchors(source["anchors"], artifacts)
    nodes, nodes_by_key = _nodes(source["nodes"], anchors_by_id)
    relations, relations_by_key = _relations(
        source["relations"],
        nodes_by_key,
        anchors_by_id,
        set(source_pack["source_dependency_keys"]),
    )
    ranking = _theses(
        source["thesis_candidates"],
        relations,
        relations_by_key,
        len(nodes),
        len(source_pack["source_dependency_keys"]),
    )

    normalized_input = {
        "source_pack": source_pack,
        "anchors": anchors,
        "nodes": nodes,
        "relations": relations,
        "thesis_candidates": [
            {
                "candidate_id": item["candidate_id"],
                "canonical_key": item["canonical_key"],
                "proposition": item["proposition"],
                "relation_ids": item["relation_ids"],
                "score_breakdown": item["score_breakdown"],
            }
            for item in sorted(ranking, key=lambda value: value["candidate_id"])
        ],
    }
    input_digest = _sha256_bytes(_canonical_bytes(normalized_input))
    graph_subject = {
        "source_pack": source_pack,
        "anchors": anchors,
        "nodes": nodes,
        "relations": relations,
        "thesis_ranking": ranking,
    }
    graph_subject_digest = _sha256_bytes(_canonical_bytes(graph_subject))
    graph_id = f"GRAPH-{graph_subject_digest.removeprefix('sha256:')[:16]}"
    if source.get("graph_id") is not None and source["graph_id"] != graph_id:
        raise RelationGraphError(
            f"graph_id drift: expected {graph_id}, observed {source['graph_id']}"
        )

    result = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "builder_version": BUILDER_VERSION,
        "graph_id": graph_id,
        "input_digest": input_digest,
        "graph_subject_digest": graph_subject_digest,
        "source_pack": source_pack,
        "anchors": anchors,
        "nodes": nodes,
        "relations": relations,
        "thesis_ranking": ranking,
        "selected_thesis_id": ranking[0]["candidate_id"],
        "created_at": created_at,
    }
    _validate(result, output_schema, OUTPUT_SCHEMA_VERSION)
    return result


def _write_or_check(result: dict[str, Any], output: Path, check: bool) -> None:
    expected = _pretty_json(result)
    if check:
        if not output.is_file():
            raise RelationGraphError(f"check output is missing: {output}")
        actual = output.read_text(encoding="utf-8")
        if actual != expected:
            raise RelationGraphError(f"persisted relation graph is stale: {output}")
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=output.name + ".", dir=output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(expected)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--schema-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--created-at", required=True)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build_relation_graph(
            input_path=args.input,
            root=args.root,
            created_at=args.created_at,
            schema_root=args.schema_root,
        )
        _write_or_check(result, args.output, args.check)
    except RelationGraphError as exc:
        raise SystemExit(str(exc)) from exc
    print(_pretty_json(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
