from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import build_relation_graph  # noqa: E402

SCHEMA_ROOT = REPOSITORY_ROOT / "schemas"
CREATED_AT = "2026-08-14T11:00:00Z"


def sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def artifact(
    path: Path,
    artifact_id: str,
    modality: str,
    role: str,
    dependency: str,
) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "artifact_id": artifact_id,
        "modality": modality,
        "role": role,
        "media_type": "application/json" if path.suffix == ".json" else "text/markdown",
        "path": path.name,
        "sha256": sha256_bytes(payload),
        "bytes": len(payload),
        "source_id": artifact_id,
        "source_dependency_key": dependency,
        "primary_or_secondary": "derived" if role == "derived-source" else "secondary",
        "locator_range": None,
    }


def prepare_root(tmp_path: Path) -> tuple[Path, Path, dict[str, object]]:
    root = tmp_path / "root"
    root.mkdir()
    transcript_a = root / "transcript-a.md"
    transcript_b = root / "transcript-b.md"
    visual = root / "visual.md"
    execution = root / "execution.json"
    transcript_a.write_text(
        "Agent autonomy reduces static predictability.\n",
        encoding="utf-8",
    )
    transcript_b.write_text(
        "Runtime traces become the evidence surface.\n",
        encoding="utf-8",
    )
    visual.write_text("fit(Model, Harness, Task)\n", encoding="utf-8")
    write_json(execution, {"status": "pass", "artifact": "fixture"})

    pack = {
        "schema_version": "multimodal-source-pack@1",
        "builder_version": "build-multimodal-source-pack@1",
        "pack_id": "pack-relation-fixture",
        "content_id": "relation-fixture",
        "descriptor_digest": "sha256:" + "1" * 64,
        "source_set_digest": "sha256:" + "2" * 64,
        "source_dependency_keys": ["origin:a", "origin:b"],
        "modalities": {
            "transcript": {"status": "AVAILABLE", "reason": None},
            "video_frames": {"status": "NOT_REQUESTED", "reason": None},
            "visual_evidence": {"status": "AVAILABLE", "reason": None},
            "audio": {"status": "NOT_REQUESTED", "reason": None},
            "metadata": {"status": "AVAILABLE", "reason": None},
        },
        "artifacts": [
            artifact(
                transcript_a,
                "transcript-a",
                "transcript",
                "subject-matter-source",
                "origin:a",
            ),
            artifact(
                transcript_b,
                "transcript-b",
                "transcript",
                "subject-matter-source",
                "origin:b",
            ),
            artifact(
                visual,
                "visual-a",
                "visual-evidence",
                "derived-source",
                "origin:a",
            ),
            artifact(
                execution,
                "execution-a",
                "metadata",
                "audit-artifact",
                "origin:a",
            ),
        ],
        "authority": {
            "authorization_status": "evaluation-only",
            "rights_basis": "fixture",
            "rights_reference": None,
            "may_compile_cards": True,
            "may_reconstruct_visuals": False,
            "may_treat_visual_text_as_source_exact": False,
            "may_complete_note": False,
            "may_publish_raw_media": False,
        },
        "created_at": "2026-08-14T10:59:00Z",
    }
    pack_path = root / "source-pack.json"
    write_json(pack_path, pack)
    return root, pack_path, pack


def relation_key(subject: str, kind: str, predicate: str, obj: str) -> str:
    return f"{subject} | {kind} | {predicate.lower()} | {obj}"


def graph_input(
    root: Path,
    pack_path: Path,
    pack: dict[str, object],
) -> dict[str, object]:
    pack_payload = pack_path.read_bytes()
    r1 = relation_key(
        "agent autonomy",
        "causes",
        "Reduces Static Predictability",
        "static predictability",
    )
    r2 = relation_key(
        "static predictability",
        "causes",
        "Makes Runtime Traces Primary Evidence",
        "runtime traces",
    )
    r3 = relation_key(
        "runtime traces",
        "enables",
        "Feeds Decision-Shaped Trace Mining",
        "trace mining",
    )
    r4 = relation_key(
        "trace mining",
        "validates",
        "Supports Deterministic Replay",
        "replay decision",
    )
    return {
        "schema_version": "relation-graph-input@1",
        "graph_id": None,
        "source_pack": {
            "path": pack_path.relative_to(root).as_posix(),
            "sha256": sha256_bytes(pack_payload),
            "pack_id": pack["pack_id"],
            "descriptor_digest": pack["descriptor_digest"],
            "source_set_digest": pack["source_set_digest"],
        },
        "anchors": [
            {
                "anchor_id": "EV-a",
                "anchor_kind": "evidence",
                "artifact_id": "transcript-a",
                "locator": "TEXT_MATCH::Agent autonomy",
                "description": "first origin",
            },
            {
                "anchor_id": "EV-b",
                "anchor_kind": "evidence",
                "artifact_id": "transcript-b",
                "locator": "TEXT_MATCH::Runtime traces",
                "description": "second origin",
            },
            {
                "anchor_id": "VIS-a",
                "anchor_kind": "visual",
                "artifact_id": "visual-a",
                "locator": "TEXT_MATCH::fit(Model, Harness, Task)",
                "description": "derived visual annotation",
            },
            {
                "anchor_id": "EXEC-a",
                "anchor_kind": "execution",
                "artifact_id": "execution-a",
                "locator": "fixture-result",
                "description": "execution fixture",
            },
        ],
        "nodes": [
            {
                "node_id": None,
                "canonical_key": "agent autonomy",
                "label": "Agent Autonomy",
                "node_kind": "claim",
                "aliases": [],
                "evidence_ids": ["EV-a"],
                "visual_ids": [],
                "tags": ["agent"],
            },
            {
                "node_id": None,
                "canonical_key": "static predictability",
                "label": "Static Predictability",
                "node_kind": "claim",
                "aliases": [],
                "evidence_ids": ["EV-a"],
                "visual_ids": [],
                "tags": ["determinism"],
            },
            {
                "node_id": None,
                "canonical_key": "runtime traces",
                "label": "Runtime Traces",
                "node_kind": "artifact",
                "aliases": ["Execution Traces"],
                "evidence_ids": ["EV-a", "EV-b"],
                "visual_ids": [],
                "tags": ["trace"],
            },
            {
                "node_id": None,
                "canonical_key": "trace mining",
                "label": "Trace Mining",
                "node_kind": "decision",
                "aliases": [],
                "evidence_ids": ["EV-b"],
                "visual_ids": ["VIS-a"],
                "tags": ["mining"],
            },
            {
                "node_id": None,
                "canonical_key": "replay decision",
                "label": "Replay Decision",
                "node_kind": "decision",
                "aliases": [],
                "evidence_ids": [],
                "visual_ids": [],
                "tags": ["verification"],
            },
        ],
        "relations": [
            {
                "relation_id": None,
                "relation_key": r1,
                "subject_key": "agent autonomy",
                "predicate": "Reduces Static Predictability",
                "object_key": "static predictability",
                "relation_kind": "causes",
                "claim_kind": "INFERENCE",
                "verification": "SUPPORTED",
                "confidence": "MEDIUM",
                "evidence_ids": ["EV-a"],
                "visual_ids": [],
                "execution_artifact_ids": [],
                "decision_use": "Choose runtime evidence over static-only review",
                "falsifier": (
                    "A fixed deterministic workflow is completely predicted "
                    "by static tests"
                ),
                "projection_hints": ["causal-dataflow"],
                "uncertain": False,
            },
            {
                "relation_id": None,
                "relation_key": r2,
                "subject_key": "static predictability",
                "predicate": "Makes Runtime Traces Primary Evidence",
                "object_key": "runtime traces",
                "relation_kind": "causes",
                "claim_kind": "INFERENCE",
                "verification": "SUPPORTED",
                "confidence": "MEDIUM",
                "evidence_ids": ["EV-a"],
                "visual_ids": [],
                "execution_artifact_ids": [],
                "decision_use": "Require trace capture before optimization",
                "falsifier": "Static inspection predicts all production behavior",
                "projection_hints": ["causal-dataflow"],
                "uncertain": False,
            },
            {
                "relation_id": None,
                "relation_key": r3,
                "subject_key": "runtime traces",
                "predicate": "Feeds Decision-Shaped Trace Mining",
                "object_key": "trace mining",
                "relation_kind": "enables",
                "claim_kind": "INFERENCE",
                "verification": "CORROBORATED",
                "confidence": "MEDIUM",
                "evidence_ids": ["EV-a", "EV-b"],
                "visual_ids": [],
                "execution_artifact_ids": [],
                "decision_use": "Build evaluation cases from runtime evidence",
                "falsifier": (
                    "Trace mining cannot produce reproducible decision cases"
                ),
                "projection_hints": ["causal-dataflow", "architecture"],
                "uncertain": False,
            },
            {
                "relation_id": None,
                "relation_key": r4,
                "subject_key": "trace mining",
                "predicate": "Supports Deterministic Replay",
                "object_key": "replay decision",
                "relation_kind": "validates",
                "claim_kind": "OBSERVATION",
                "verification": "TESTED",
                "confidence": "HIGH",
                "evidence_ids": [],
                "visual_ids": [],
                "execution_artifact_ids": ["EXEC-a"],
                "decision_use": "Verify builder replay",
                "falsifier": "The persisted replay differs for the same subject",
                "projection_hints": [],
                "uncertain": False,
            },
        ],
        "thesis_candidates": [
            {
                "candidate_id": None,
                "canonical_key": (
                    "autonomy makes trace mining the improvement substrate"
                ),
                "proposition": (
                    "Agent autonomy lowers static predictability, making runtime "
                    "traces and trace mining the improvement substrate."
                ),
                "relation_keys": [r1, r2, r3],
                "decision_impact": 0.95,
                "source_emphasis": 0.9,
                "novelty": 0.9,
            },
            {
                "candidate_id": None,
                "canonical_key": "trace mining supports replay",
                "proposition": "Trace mining supports deterministic replay.",
                "relation_keys": [r4],
                "decision_impact": 0.4,
                "source_emphasis": 0.4,
                "novelty": 0.2,
            },
        ],
    }


def build_fixture(
    tmp_path: Path,
) -> tuple[Path, Path, dict[str, object], Path]:
    root, pack_path, pack = prepare_root(tmp_path)
    source = graph_input(root, pack_path, pack)
    input_path = tmp_path / "relation-input.json"
    write_json(input_path, source)
    return root, pack_path, source, input_path


def test_schemas_are_valid_draft_2020_12() -> None:
    for name in ("relation-graph-input.schema.json", "relation-graph.schema.json"):
        schema = json.loads((SCHEMA_ROOT / name).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)


def test_graph_is_deterministic_and_order_independent(tmp_path: Path) -> None:
    root, _, source, input_path = build_fixture(tmp_path)
    first = build_relation_graph.build_relation_graph(
        input_path=input_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )

    reordered = copy.deepcopy(source)
    reordered["anchors"].reverse()
    reordered["nodes"].reverse()
    reordered["relations"].reverse()
    reordered["thesis_candidates"].reverse()
    write_json(input_path, reordered)
    second = build_relation_graph.build_relation_graph(
        input_path=input_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )

    assert first == second
    assert first["selected_thesis_id"] == first["thesis_ranking"][0]["candidate_id"]
    assert first["thesis_ranking"][0]["canonical_key"] == (
        "autonomy makes trace mining the improvement substrate"
    )
    assert first["source_pack"]["source_dependency_keys"] == ["origin:a", "origin:b"]
    assert first["created_at"] == CREATED_AT


def test_source_pack_subject_must_match_exact_file(tmp_path: Path) -> None:
    root, pack_path, _, input_path = build_fixture(tmp_path)
    write_json(pack_path, {"schema_version": "mutated"})
    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="source pack sha256 mismatch",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_source_pack_rejects_undeclared_artifact_dependency(tmp_path: Path) -> None:
    root, pack_path, source, input_path = build_fixture(tmp_path)
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    pack["artifacts"][0]["source_dependency_key"] = "origin:unknown"
    write_json(pack_path, pack)
    source["source_pack"]["sha256"] = sha256_bytes(pack_path.read_bytes())
    write_json(input_path, source)

    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="undeclared dependency",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_unknown_node_and_anchor_fail_closed(tmp_path: Path) -> None:
    root, _, source, input_path = build_fixture(tmp_path)

    unknown_node = copy.deepcopy(source)
    unknown_node["relations"][0]["object_key"] = "missing node"
    unknown_node["relations"][0]["relation_key"] = relation_key(
        "agent autonomy",
        "causes",
        "Reduces Static Predictability",
        "missing node",
    )
    write_json(input_path, unknown_node)
    with pytest.raises(build_relation_graph.RelationGraphError, match="unknown node"):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    unknown_anchor = copy.deepcopy(source)
    unknown_anchor["relations"][0]["evidence_ids"] = ["EV-missing"]
    write_json(input_path, unknown_anchor)
    with pytest.raises(build_relation_graph.RelationGraphError, match="unknown anchor"):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_corroborated_requires_two_independent_dependencies(tmp_path: Path) -> None:
    root, _, source, input_path = build_fixture(tmp_path)
    source["relations"][2]["evidence_ids"] = ["EV-a"]
    write_json(input_path, source)
    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="at least two independent source dependencies",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_tested_requires_execution_artifact(tmp_path: Path) -> None:
    root, _, source, input_path = build_fixture(tmp_path)
    source["relations"][3]["execution_artifact_ids"] = []
    write_json(input_path, source)
    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="TESTED relation requires execution_artifact_ids",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_duplicate_canonical_identity_and_explicit_id_drift_fail(
    tmp_path: Path,
) -> None:
    root, _, source, input_path = build_fixture(tmp_path)

    duplicate = copy.deepcopy(source)
    duplicate["nodes"].append(copy.deepcopy(duplicate["nodes"][0]))
    write_json(input_path, duplicate)
    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="duplicate node canonical_key",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    drift = copy.deepcopy(source)
    drift["nodes"][0]["node_id"] = "NODE-wrong"
    write_json(input_path, drift)
    with pytest.raises(build_relation_graph.RelationGraphError, match="node_id drift"):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    relation_drift = copy.deepcopy(source)
    relation_drift["relations"][0]["relation_id"] = "REL-wrong"
    write_json(input_path, relation_drift)
    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="relation_id drift",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_relation_key_drift_and_duplicate_relation_fail(tmp_path: Path) -> None:
    root, _, source, input_path = build_fixture(tmp_path)

    drift = copy.deepcopy(source)
    drift["relations"][0]["relation_key"] = "wrong | key"
    write_json(input_path, drift)
    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="relation_key drift",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    duplicate = copy.deepcopy(source)
    duplicate["relations"].append(copy.deepcopy(duplicate["relations"][0]))
    write_json(input_path, duplicate)
    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="duplicate relation canonical_key",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_thesis_rejects_unknown_or_falsified_relations(tmp_path: Path) -> None:
    root, _, source, input_path = build_fixture(tmp_path)

    unknown = copy.deepcopy(source)
    unknown["thesis_candidates"][0]["relation_keys"].append("missing relation")
    write_json(input_path, unknown)
    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="unknown relation_keys",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    falsified = copy.deepcopy(source)
    falsified["relations"][0]["verification"] = "FALSIFIED"
    write_json(input_path, falsified)
    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="hides uncertain/contested/falsified",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_graph_id_and_candidate_id_drift_fail(tmp_path: Path) -> None:
    root, _, source, input_path = build_fixture(tmp_path)

    source["graph_id"] = "GRAPH-wrong"
    write_json(input_path, source)
    with pytest.raises(build_relation_graph.RelationGraphError, match="graph_id drift"):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    source["graph_id"] = None
    source["thesis_candidates"][0]["candidate_id"] = "TH-wrong"
    write_json(input_path, source)
    with pytest.raises(
        build_relation_graph.RelationGraphError,
        match="candidate_id drift",
    ):
        build_relation_graph.build_relation_graph(
            input_path=input_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_persisted_check_rejects_stale_graph(tmp_path: Path) -> None:
    root, _, _, input_path = build_fixture(tmp_path)
    output = tmp_path / "relation-graph.json"
    result = build_relation_graph.build_relation_graph(
        input_path=input_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    build_relation_graph._write_or_check(result, output, check=False)
    build_relation_graph._write_or_check(result, output, check=True)

    output.write_text("{}\n", encoding="utf-8")
    with pytest.raises(build_relation_graph.RelationGraphError, match="stale"):
        build_relation_graph._write_or_check(result, output, check=True)


def test_builder_does_not_generate_wall_clock_time(tmp_path: Path) -> None:
    root, _, _, input_path = build_fixture(tmp_path)
    first = build_relation_graph.build_relation_graph(
        input_path=input_path,
        root=root,
        created_at="2026-01-01T00:00:00Z",
        schema_root=SCHEMA_ROOT,
    )
    second = build_relation_graph.build_relation_graph(
        input_path=input_path,
        root=root,
        created_at="2026-01-02T00:00:00Z",
        schema_root=SCHEMA_ROOT,
    )
    assert first["graph_subject_digest"] == second["graph_subject_digest"]
    assert first["graph_id"] == second["graph_id"]
    assert first["created_at"] != second["created_at"]
