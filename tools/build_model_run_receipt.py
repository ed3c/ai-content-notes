#!/usr/bin/env python3
"""Build a provider-neutral, exact-subject model-run receipt.

The builder does not invoke a provider. It binds already-persisted prompt,
source-pack, raw-response, and compiled-output files to declared provider,
model, sampling, and execution metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

from jsonschema import Draft202012Validator, FormatChecker

DESCRIPTOR_SCHEMA_VERSION = "model-run-receipt-descriptor@1"
OUTPUT_SCHEMA_VERSION = "model-run-receipt@1"
BUILDER_VERSION = "build-model-run-receipt@1"
SOURCE_PACK_SCHEMA_VERSION = "multimodal-source-pack@1"


class ModelRunReceiptError(RuntimeError):
    """Raised when a model-run receipt cannot be safely materialized."""


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ModelRunReceiptError(f"unable to read JSON object: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ModelRunReceiptError(f"expected JSON object: {path}")
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


def _git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


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
    raise ModelRunReceiptError(
        f"{label} schema validation failed: " + "; ".join(rendered)
    )


def _safe_relative_file(root: Path, raw_path: str) -> tuple[Path, str]:
    if "\\" in raw_path or "\x00" in raw_path:
        raise ModelRunReceiptError(
            f"artifact path is not canonical POSIX text: {raw_path!r}"
        )
    pure = PurePosixPath(raw_path)
    if (
        not raw_path
        or pure.is_absolute()
        or pure.as_posix() != raw_path
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        raise ModelRunReceiptError(
            f"artifact path must be a normalized relative path: {raw_path!r}"
        )

    root = root.resolve(strict=True)
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise ModelRunReceiptError(f"symlink artifact paths are forbidden: {raw_path}")
    try:
        candidate = current.resolve(strict=True)
    except OSError as exc:
        raise ModelRunReceiptError(f"artifact is missing: {raw_path}") from exc
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ModelRunReceiptError(f"artifact escapes root: {raw_path}") from exc
    if not candidate.is_file():
        raise ModelRunReceiptError(f"artifact is not a regular file: {raw_path}")
    return candidate, pure.as_posix()


def _artifact(
    root: Path,
    descriptor: dict[str, Any],
) -> tuple[dict[str, Any], bytes]:
    path, canonical_path = _safe_relative_file(root, descriptor["path"])
    payload = path.read_bytes()
    return (
        {
            "path": canonical_path,
            "media_type": descriptor["media_type"],
            "sha256": _sha256_bytes(payload),
            "bytes": len(payload),
        },
        payload,
    )


def _parse_datetime(value: str | None, field: str) -> datetime | None:
    if value is None:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ModelRunReceiptError(f"invalid {field}: {value}") from exc


def _execution_checks(execution: dict[str, Any]) -> None:
    started = _parse_datetime(execution["started_at"], "execution.started_at")
    finished = _parse_datetime(execution["finished_at"], "execution.finished_at")
    if started is not None and finished is not None and finished < started:
        raise ModelRunReceiptError("execution.finished_at precedes execution.started_at")
    if execution["status"] == "completed":
        if started is None or finished is None:
            raise ModelRunReceiptError(
                "completed execution requires started_at and finished_at"
            )
        if execution["error_type"] is not None:
            raise ModelRunReceiptError("completed execution cannot declare error_type")
    elif execution["status"] in {"failed", "cancelled"}:
        if execution["error_type"] is None:
            raise ModelRunReceiptError(
                f"{execution['status']} execution requires error_type"
            )


def build_model_run_receipt(
    *,
    descriptor_path: Path,
    root: Path,
    created_at: str,
    schema_root: Path | None = None,
) -> dict[str, Any]:
    """Build and validate one model-run receipt without writing it."""

    schema_root = schema_root or root / "schemas"
    descriptor_schema = _read_json_object(
        schema_root / "model-run-receipt-descriptor.schema.json"
    )
    output_schema = _read_json_object(schema_root / "model-run-receipt.schema.json")
    source_pack_schema = _read_json_object(
        schema_root / "multimodal-source-pack.schema.json"
    )
    descriptor = _read_json_object(descriptor_path)
    _validate(descriptor, descriptor_schema, DESCRIPTOR_SCHEMA_VERSION)
    _execution_checks(descriptor["execution"])

    prompt, prompt_payload = _artifact(root, descriptor["prompt"])
    expected_git_blob = descriptor["prompt"]["git_blob_sha1"]
    actual_git_blob = _git_blob_sha1(prompt_payload)
    if expected_git_blob is not None and expected_git_blob != actual_git_blob:
        raise ModelRunReceiptError(
            "prompt git_blob_sha1 mismatch: "
            f"expected {expected_git_blob}, observed {actual_git_blob}"
        )
    prompt["git_blob_sha1"] = expected_git_blob

    source_pack_path, source_pack_canonical = _safe_relative_file(
        root, descriptor["source_pack_path"]
    )
    source_pack_payload = source_pack_path.read_bytes()
    source_pack = _read_json_object(source_pack_path)
    _validate(source_pack, source_pack_schema, SOURCE_PACK_SCHEMA_VERSION)
    source_pack_artifact = {
        "path": source_pack_canonical,
        "media_type": "application/json",
        "sha256": _sha256_bytes(source_pack_payload),
        "bytes": len(source_pack_payload),
        "pack_id": source_pack["pack_id"],
        "descriptor_digest": source_pack["descriptor_digest"],
        "source_set_digest": source_pack["source_set_digest"],
    }

    raw_response, _ = _artifact(root, descriptor["raw_response"])
    compiled_output, _ = _artifact(root, descriptor["compiled_output"])

    paths = {
        prompt["path"],
        source_pack_artifact["path"],
        raw_response["path"],
        compiled_output["path"],
    }
    if len(paths) != 4:
        raise ModelRunReceiptError(
            "prompt, source pack, raw response, and compiled output paths must be distinct"
        )

    descriptor_digest = _sha256_bytes(descriptor_path.read_bytes())
    subject = {
        "run_id": descriptor["run_id"],
        "provider": descriptor["provider"],
        "model_api_identifier": descriptor["model_api_identifier"],
        "model_display_name": descriptor["model_display_name"],
        "prompt": prompt,
        "source_pack": source_pack_artifact,
        "sampling": descriptor["sampling"],
        "execution": descriptor["execution"],
        "raw_response": raw_response,
        "compiled_output": compiled_output,
    }
    result = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "builder_version": BUILDER_VERSION,
        "run_id": descriptor["run_id"],
        "descriptor_digest": descriptor_digest,
        "subject_digest": _sha256_bytes(_canonical_bytes(subject)),
        "provider": descriptor["provider"],
        "model_api_identifier": descriptor["model_api_identifier"],
        "model_display_name": descriptor["model_display_name"],
        "prompt": prompt,
        "source_pack": source_pack_artifact,
        "sampling": descriptor["sampling"],
        "execution": descriptor["execution"],
        "raw_response": raw_response,
        "compiled_output": compiled_output,
        "created_at": created_at,
    }
    _validate(result, output_schema, OUTPUT_SCHEMA_VERSION)
    return result


def _write_or_check(result: dict[str, Any], output: Path, check: bool) -> None:
    expected = _pretty_json(result)
    if check:
        if not output.is_file():
            raise ModelRunReceiptError(f"check output is missing: {output}")
        actual = output.read_text(encoding="utf-8")
        if actual != expected:
            raise ModelRunReceiptError(f"persisted model-run receipt is stale: {output}")
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
        result = build_model_run_receipt(
            descriptor_path=args.descriptor,
            root=args.root,
            created_at=args.created_at,
            schema_root=args.schema_root,
        )
        _write_or_check(result, args.output, args.check)
    except ModelRunReceiptError as exc:
        raise SystemExit(str(exc)) from exc
    print(_pretty_json(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
