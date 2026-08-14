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

import build_model_run_receipt  # noqa: E402
import build_multimodal_source_pack  # noqa: E402

SCHEMA_ROOT = REPOSITORY_ROOT / "schemas"
CREATED_AT = "2026-08-14T10:30:00Z"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


def source_descriptor() -> dict[str, object]:
    return {
        "schema_version": "multimodal-source-pack-descriptor@1",
        "pack_id": "pack-video-001",
        "content_id": "video-001",
        "source_dependency_keys": ["youtube-video:video-001"],
        "modalities": {
            "transcript": {"status": "AVAILABLE", "reason": None},
            "video_frames": {
                "status": "BLOCKED",
                "reason": "authorized frame artifact unavailable",
            },
            "visual_evidence": {
                "status": "BLOCKED",
                "reason": "authorized frame artifact unavailable",
            },
            "audio": {"status": "NOT_REQUESTED", "reason": "ASR disabled"},
            "metadata": {"status": "AVAILABLE", "reason": None},
        },
        "artifacts": [
            {
                "artifact_id": "transcript-normalized",
                "modality": "transcript",
                "role": "subject-matter-source",
                "media_type": "text/markdown",
                "path": "artifacts/transcript.md",
                "source_id": "youtube:video-001:secondary-transcript",
                "source_dependency_key": "youtube-video:video-001",
                "primary_or_secondary": "secondary",
                "locator_range": "00:00:00..00:01:00",
            },
            {
                "artifact_id": "source-metadata",
                "modality": "metadata",
                "role": "audit-artifact",
                "media_type": "application/json",
                "path": "artifacts/metadata.json",
                "source_id": "youtube:video-001",
                "source_dependency_key": "youtube-video:video-001",
                "primary_or_secondary": "secondary",
                "locator_range": None,
            },
        ],
        "authority": {
            "authorization_status": "evaluation-only",
            "rights_basis": "user-directed-evaluation",
            "rights_reference": None,
            "may_compile_cards": True,
            "may_reconstruct_visuals": False,
            "may_treat_visual_text_as_source_exact": False,
            "may_complete_note": False,
            "may_publish_raw_media": False,
        },
    }


def prepare_source_root(tmp_path: Path) -> Path:
    root = tmp_path / "root"
    (root / "artifacts").mkdir(parents=True)
    (root / "artifacts" / "transcript.md").write_text(
        "# Transcript\n\nAgent autonomy creates runtime traces.\n",
        encoding="utf-8",
    )
    write_json(root / "artifacts" / "metadata.json", {"video_id": "video-001"})
    return root


def build_pack(tmp_path: Path) -> tuple[Path, dict[str, object], Path]:
    root = prepare_source_root(tmp_path)
    descriptor_path = tmp_path / "source-pack.descriptor.json"
    write_json(descriptor_path, source_descriptor())
    result = build_multimodal_source_pack.build_source_pack(
        descriptor_path=descriptor_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    output = root / "receipts" / "source-pack.json"
    write_json(output, result)
    return root, result, output


def model_descriptor(root: Path, source_pack_path: Path) -> dict[str, object]:
    prompt = root / "inputs" / "prompt.md"
    prompt.parent.mkdir(parents=True, exist_ok=True)
    prompt.write_text("immutable prompt\n", encoding="utf-8")
    (root / "outputs").mkdir(parents=True, exist_ok=True)
    write_json(root / "outputs" / "raw-response.json", {"cards": ["N-example"]})
    (root / "outputs" / "compiled.md").write_text(
        "### N-example｜Example\n", encoding="utf-8"
    )
    return {
        "schema_version": "model-run-receipt-descriptor@1",
        "run_id": "run-001",
        "provider": "fixture-provider",
        "model_api_identifier": "fixture-model@2026-08-14",
        "model_display_name": "Fixture Model",
        "prompt": {
            "path": "inputs/prompt.md",
            "media_type": "text/markdown",
            "git_blob_sha1": git_blob_sha1(prompt),
        },
        "source_pack_path": source_pack_path.relative_to(root).as_posix(),
        "raw_response": {
            "path": "outputs/raw-response.json",
            "media_type": "application/json",
        },
        "compiled_output": {
            "path": "outputs/compiled.md",
            "media_type": "text/markdown",
        },
        "sampling": {
            "temperature": 0,
            "top_p": 1,
            "seed": 42,
            "max_output_tokens": 4096,
            "stop_sequences": [],
        },
        "execution": {
            "status": "completed",
            "started_at": "2026-08-14T10:00:00Z",
            "finished_at": "2026-08-14T10:00:02Z",
            "exit_or_http_status": 200,
            "error_type": None,
            "tool_execution": False,
        },
    }


def test_schemas_are_valid_draft_2020_12() -> None:
    schema_names = (
        "multimodal-source-pack-descriptor.schema.json",
        "multimodal-source-pack.schema.json",
        "model-run-receipt-descriptor.schema.json",
        "model-run-receipt.schema.json",
    )
    for name in schema_names:
        path = SCHEMA_ROOT / name
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_source_pack_is_deterministic_and_digest_bound(tmp_path: Path) -> None:
    root = prepare_source_root(tmp_path)
    descriptor_path = tmp_path / "descriptor.json"
    write_json(descriptor_path, source_descriptor())

    first = build_multimodal_source_pack.build_source_pack(
        descriptor_path=descriptor_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    second = build_multimodal_source_pack.build_source_pack(
        descriptor_path=descriptor_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    assert first == second
    assert first["schema_version"] == "multimodal-source-pack@1"
    assert first["source_dependency_keys"] == ["youtube-video:video-001"]
    assert [item["artifact_id"] for item in first["artifacts"]] == [
        "source-metadata",
        "transcript-normalized",
    ]

    old_digest = first["source_set_digest"]
    (root / "artifacts" / "transcript.md").write_text(
        "# Transcript\n\nChanged bytes.\n", encoding="utf-8"
    )
    changed = build_multimodal_source_pack.build_source_pack(
        descriptor_path=descriptor_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    assert changed["descriptor_digest"] == first["descriptor_digest"]
    assert changed["source_set_digest"] != old_digest


def test_source_pack_check_rejects_stale_receipt(tmp_path: Path) -> None:
    root = prepare_source_root(tmp_path)
    descriptor_path = tmp_path / "descriptor.json"
    write_json(descriptor_path, source_descriptor())
    output = tmp_path / "source-pack.json"
    result = build_multimodal_source_pack.build_source_pack(
        descriptor_path=descriptor_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    build_multimodal_source_pack._write_or_check(result, output, check=False)
    build_multimodal_source_pack._write_or_check(result, output, check=True)

    output.write_text("{}\n", encoding="utf-8")
    with pytest.raises(
        build_multimodal_source_pack.SourcePackError,
        match="stale",
    ):
        build_multimodal_source_pack._write_or_check(result, output, check=True)


def test_source_pack_rejects_undeclared_dependency_and_modality_drift(
    tmp_path: Path,
) -> None:
    root = prepare_source_root(tmp_path)
    descriptor = source_descriptor()
    descriptor["artifacts"][0]["source_dependency_key"] = "unknown-origin"
    descriptor_path = tmp_path / "descriptor.json"
    write_json(descriptor_path, descriptor)
    with pytest.raises(
        build_multimodal_source_pack.SourcePackError,
        match="undeclared source_dependency_key",
    ):
        build_multimodal_source_pack.build_source_pack(
            descriptor_path=descriptor_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    descriptor = source_descriptor()
    descriptor["modalities"]["transcript"] = {
        "status": "BLOCKED",
        "reason": "blocked for test",
    }
    write_json(descriptor_path, descriptor)
    with pytest.raises(
        build_multimodal_source_pack.SourcePackError,
        match="transcript is BLOCKED",
    ):
        build_multimodal_source_pack.build_source_pack(
            descriptor_path=descriptor_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_source_pack_rejects_traversal_symlink_and_unverified_visual_authority(
    tmp_path: Path,
) -> None:
    root = prepare_source_root(tmp_path)
    descriptor_path = tmp_path / "descriptor.json"

    noncanonical = source_descriptor()
    noncanonical["artifacts"][0]["path"] = "artifacts//transcript.md"
    write_json(descriptor_path, noncanonical)
    with pytest.raises(
        build_multimodal_source_pack.SourcePackError,
        match="normalized relative path",
    ):
        build_multimodal_source_pack.build_source_pack(
            descriptor_path=descriptor_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    traversal = source_descriptor()
    traversal["artifacts"][0]["path"] = "../outside.md"
    write_json(descriptor_path, traversal)
    with pytest.raises(
        build_multimodal_source_pack.SourcePackError,
        match="normalized relative path",
    ):
        build_multimodal_source_pack.build_source_pack(
            descriptor_path=descriptor_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    symlink_target = root / "artifacts" / "transcript.md"
    symlink_path = root / "artifacts" / "transcript-link.md"
    symlink_path.symlink_to(symlink_target)
    symlinked = source_descriptor()
    symlinked["artifacts"][0]["path"] = "artifacts/transcript-link.md"
    write_json(descriptor_path, symlinked)
    with pytest.raises(
        build_multimodal_source_pack.SourcePackError,
        match="symlink",
    ):
        build_multimodal_source_pack.build_source_pack(
            descriptor_path=descriptor_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    visual = source_descriptor()
    visual["authority"]["may_reconstruct_visuals"] = True
    write_json(descriptor_path, visual)
    with pytest.raises(
        build_multimodal_source_pack.SourcePackError,
        match="schema validation failed|require authorization_status=verified",
    ):
        build_multimodal_source_pack.build_source_pack(
            descriptor_path=descriptor_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_model_run_receipt_binds_exact_subjects(tmp_path: Path) -> None:
    root, _, source_pack_path = build_pack(tmp_path)
    descriptor = model_descriptor(root, source_pack_path)
    descriptor_path = tmp_path / "model-run.descriptor.json"
    write_json(descriptor_path, descriptor)

    first = build_model_run_receipt.build_model_run_receipt(
        descriptor_path=descriptor_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    second = build_model_run_receipt.build_model_run_receipt(
        descriptor_path=descriptor_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    assert first == second
    assert first["schema_version"] == "model-run-receipt@1"
    assert first["prompt"]["git_blob_sha1"] == descriptor["prompt"]["git_blob_sha1"]
    assert first["source_pack"]["pack_id"] == "pack-video-001"

    old_subject = first["subject_digest"]
    write_json(root / "outputs" / "raw-response.json", {"cards": ["N-changed"]})
    changed = build_model_run_receipt.build_model_run_receipt(
        descriptor_path=descriptor_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    assert changed["descriptor_digest"] == first["descriptor_digest"]
    assert changed["subject_digest"] != old_subject


def test_model_run_receipt_rejects_prompt_git_blob_mismatch(tmp_path: Path) -> None:
    root, _, source_pack_path = build_pack(tmp_path)
    descriptor = model_descriptor(root, source_pack_path)
    descriptor["prompt"]["git_blob_sha1"] = "0" * 40
    descriptor_path = tmp_path / "model-run.descriptor.json"
    write_json(descriptor_path, descriptor)

    with pytest.raises(
        build_model_run_receipt.ModelRunReceiptError,
        match="git_blob_sha1 mismatch",
    ):
        build_model_run_receipt.build_model_run_receipt(
            descriptor_path=descriptor_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_model_run_receipt_check_rejects_stale_subject(tmp_path: Path) -> None:
    root, _, source_pack_path = build_pack(tmp_path)
    descriptor = model_descriptor(root, source_pack_path)
    descriptor_path = tmp_path / "model-run.descriptor.json"
    write_json(descriptor_path, descriptor)
    output = tmp_path / "model-run.json"

    first = build_model_run_receipt.build_model_run_receipt(
        descriptor_path=descriptor_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    build_model_run_receipt._write_or_check(first, output, check=False)
    build_model_run_receipt._write_or_check(first, output, check=True)

    (root / "outputs" / "compiled.md").write_text(
        "### N-other｜Changed\n", encoding="utf-8"
    )
    changed = build_model_run_receipt.build_model_run_receipt(
        descriptor_path=descriptor_path,
        root=root,
        created_at=CREATED_AT,
        schema_root=SCHEMA_ROOT,
    )
    with pytest.raises(
        build_model_run_receipt.ModelRunReceiptError,
        match="stale",
    ):
        build_model_run_receipt._write_or_check(changed, output, check=True)


def test_model_run_receipt_rejects_path_alias_and_invalid_execution(
    tmp_path: Path,
) -> None:
    root, _, source_pack_path = build_pack(tmp_path)
    descriptor = model_descriptor(root, source_pack_path)
    descriptor_path = tmp_path / "model-run.descriptor.json"

    aliased = copy.deepcopy(descriptor)
    aliased["compiled_output"]["path"] = aliased["raw_response"]["path"]
    aliased["compiled_output"]["media_type"] = "application/json"
    write_json(descriptor_path, aliased)
    with pytest.raises(
        build_model_run_receipt.ModelRunReceiptError,
        match="paths must be distinct",
    ):
        build_model_run_receipt.build_model_run_receipt(
            descriptor_path=descriptor_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )

    invalid = copy.deepcopy(descriptor)
    invalid["execution"]["finished_at"] = "2026-08-14T09:59:59Z"
    write_json(descriptor_path, invalid)
    with pytest.raises(
        build_model_run_receipt.ModelRunReceiptError,
        match="precedes",
    ):
        build_model_run_receipt.build_model_run_receipt(
            descriptor_path=descriptor_path,
            root=root,
            created_at=CREATED_AT,
            schema_root=SCHEMA_ROOT,
        )


def test_builders_do_not_generate_timestamps(tmp_path: Path) -> None:
    root = prepare_source_root(tmp_path)
    descriptor_path = tmp_path / "descriptor.json"
    write_json(descriptor_path, source_descriptor())
    first = build_multimodal_source_pack.build_source_pack(
        descriptor_path=descriptor_path,
        root=root,
        created_at="2026-01-01T00:00:00Z",
        schema_root=SCHEMA_ROOT,
    )
    second = build_multimodal_source_pack.build_source_pack(
        descriptor_path=descriptor_path,
        root=root,
        created_at="2026-01-02T00:00:00Z",
        schema_root=SCHEMA_ROOT,
    )
    assert first["source_set_digest"] == second["source_set_digest"]
    assert first["created_at"] != second["created_at"]
