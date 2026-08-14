#!/usr/bin/env python3
"""Build a deterministic, digest-bound multimodal source-pack receipt.

This builder does not acquire media, invoke a model, repair source text, or
assert claim truth. It binds a typed descriptor to regular files below an
explicit root and emits a schema-validated identity receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

from jsonschema import Draft202012Validator, FormatChecker

DESCRIPTOR_SCHEMA_VERSION = "multimodal-source-pack-descriptor@1"
OUTPUT_SCHEMA_VERSION = "multimodal-source-pack@1"
BUILDER_VERSION = "build-multimodal-source-pack@1"
MODALITY_KEYS = {
    "transcript": "transcript",
    "video-frame": "video_frames",
    "visual-evidence": "visual_evidence",
    "audio": "audio",
    "metadata": "metadata",
}


class SourcePackError(RuntimeError):
    """Raised when source-pack materialization must fail closed."""


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SourcePackError(f"unable to read JSON object: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SourcePackError(f"expected JSON object: {path}")
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
    raise SourcePackError(f"{label} schema validation failed: " + "; ".join(rendered))


def _safe_relative_file(root: Path, raw_path: str) -> tuple[Path, str]:
    """Return a regular, non-symlink file below root and its POSIX path."""

    if "\\" in raw_path or "\x00" in raw_path:
        raise SourcePackError(f"artifact path is not canonical POSIX text: {raw_path!r}")
    pure = PurePosixPath(raw_path)
    if (
        not raw_path
        or pure.is_absolute()
        or pure.as_posix() != raw_path
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        raise SourcePackError(f"artifact path must be a normalized relative path: {raw_path!r}")

    root = root.resolve(strict=True)
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise SourcePackError(f"symlink artifact paths are forbidden: {raw_path}")

    try:
        candidate = current.resolve(strict=True)
    except OSError as exc:
        raise SourcePackError(f"artifact is missing: {raw_path}") from exc
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise SourcePackError(f"artifact escapes root: {raw_path}") from exc
    if not candidate.is_file():
        raise SourcePackError(f"artifact is not a regular file: {raw_path}")
    return candidate, pure.as_posix()


def _artifact_identity(path: Path) -> tuple[str, int]:
    payload = path.read_bytes()
    return _sha256_bytes(payload), len(payload)


def _semantic_checks(descriptor: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    declared_keys = set(descriptor["source_dependency_keys"])
    artifacts: list[dict[str, Any]] = []
    artifact_ids: set[str] = set()
    artifact_paths: set[str] = set()
    used_keys: set[str] = set()
    modality_counts = {key: 0 for key in descriptor["modalities"]}
    subject_source_count = 0

    for raw in descriptor["artifacts"]:
        artifact_id = raw["artifact_id"]
        if artifact_id in artifact_ids:
            raise SourcePackError(f"duplicate artifact_id: {artifact_id}")
        artifact_ids.add(artifact_id)

        source_dependency_key = raw["source_dependency_key"]
        if source_dependency_key not in declared_keys:
            raise SourcePackError(
                "artifact references undeclared source_dependency_key: "
                f"{artifact_id}: {source_dependency_key}"
            )
        used_keys.add(source_dependency_key)

        candidate, canonical_path = _safe_relative_file(root, raw["path"])
        if canonical_path in artifact_paths:
            raise SourcePackError(f"duplicate artifact path: {canonical_path}")
        artifact_paths.add(canonical_path)

        if raw["role"] == "derived-source" and raw["primary_or_secondary"] != "derived":
            raise SourcePackError(
                f"derived-source artifact must be marked derived: {artifact_id}"
            )
        if raw["primary_or_secondary"] == "derived" and raw["role"] == "subject-matter-source":
            raise SourcePackError(
                f"derived artifact cannot be a subject-matter source: {artifact_id}"
            )
        if raw["role"] == "subject-matter-source":
            subject_source_count += 1

        modality_key = MODALITY_KEYS[raw["modality"]]
        modality_counts[modality_key] += 1
        digest, byte_count = _artifact_identity(candidate)
        artifacts.append(
            {
                "artifact_id": artifact_id,
                "modality": raw["modality"],
                "role": raw["role"],
                "media_type": raw["media_type"],
                "path": canonical_path,
                "sha256": digest,
                "bytes": byte_count,
                "source_id": raw.get("source_id"),
                "source_dependency_key": source_dependency_key,
                "primary_or_secondary": raw["primary_or_secondary"],
                "locator_range": raw.get("locator_range"),
            }
        )

    missing_keys = declared_keys - used_keys
    if missing_keys:
        raise SourcePackError(
            "declared source_dependency_keys have no artifact: "
            + ", ".join(sorted(missing_keys))
        )
    if subject_source_count == 0:
        raise SourcePackError("source pack requires at least one subject-matter-source artifact")

    for modality_key, contract in descriptor["modalities"].items():
        count = modality_counts[modality_key]
        status = contract["status"]
        if status in {"AVAILABLE", "PARTIAL"} and count == 0:
            raise SourcePackError(
                f"modality {modality_key} is {status} but has no declared artifact"
            )
        if status in {"BLOCKED", "NOT_REQUESTED"} and count != 0:
            raise SourcePackError(
                f"modality {modality_key} is {status} but declares {count} artifact(s)"
            )

    authority = descriptor["authority"]
    verified_only = (
        authority["may_reconstruct_visuals"]
        or authority["may_treat_visual_text_as_source_exact"]
        or authority["may_complete_note"]
        or authority["may_publish_raw_media"]
    )
    if verified_only and authority["authorization_status"] != "verified":
        raise SourcePackError(
            "visual reconstruction, exact visual text, completion, and publication "
            "permissions require authorization_status=verified"
        )
    if authority["may_treat_visual_text_as_source_exact"]:
        if descriptor["modalities"]["visual_evidence"]["status"] != "AVAILABLE":
            raise SourcePackError(
                "exact visual text authority requires visual_evidence status AVAILABLE"
            )

    return sorted(artifacts, key=lambda item: item["artifact_id"])


def build_source_pack(
    *,
    descriptor_path: Path,
    root: Path,
    created_at: str,
    schema_root: Path | None = None,
) -> dict[str, Any]:
    """Build and validate one source-pack receipt without writing it."""

    schema_root = schema_root or root / "schemas"
    descriptor_schema = _read_json_object(
        schema_root / "multimodal-source-pack-descriptor.schema.json"
    )
    output_schema = _read_json_object(schema_root / "multimodal-source-pack.schema.json")
    descriptor = _read_json_object(descriptor_path)
    _validate(descriptor, descriptor_schema, DESCRIPTOR_SCHEMA_VERSION)

    artifacts = _semantic_checks(descriptor, root)
    descriptor_payload = descriptor_path.read_bytes()
    descriptor_digest = _sha256_bytes(descriptor_payload)

    source_subject = {
        "pack_id": descriptor["pack_id"],
        "content_id": descriptor["content_id"],
        "source_dependency_keys": sorted(descriptor["source_dependency_keys"]),
        "modalities": descriptor["modalities"],
        "authority": descriptor["authority"],
        "artifacts": artifacts,
    }
    result = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "builder_version": BUILDER_VERSION,
        "pack_id": descriptor["pack_id"],
        "content_id": descriptor["content_id"],
        "descriptor_digest": descriptor_digest,
        "source_set_digest": _sha256_bytes(_canonical_bytes(source_subject)),
        "source_dependency_keys": sorted(descriptor["source_dependency_keys"]),
        "modalities": descriptor["modalities"],
        "artifacts": artifacts,
        "authority": descriptor["authority"],
        "created_at": created_at,
    }
    _validate(result, output_schema, OUTPUT_SCHEMA_VERSION)
    return result


def _write_or_check(result: dict[str, Any], output: Path, check: bool) -> None:
    expected = _pretty_json(result)
    if check:
        if not output.is_file():
            raise SourcePackError(f"check output is missing: {output}")
        actual = output.read_text(encoding="utf-8")
        if actual != expected:
            raise SourcePackError(f"persisted source-pack receipt is stale: {output}")
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
    parser.add_argument("--descriptor", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--schema-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--created-at", required=True)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build_source_pack(
            descriptor_path=args.descriptor,
            root=args.root,
            created_at=args.created_at,
            schema_root=args.schema_root,
        )
        _write_or_check(result, args.output, args.check)
    except SourcePackError as exc:
        raise SystemExit(str(exc)) from exc
    print(_pretty_json(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
