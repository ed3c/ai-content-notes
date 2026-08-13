"""Shared deterministic helpers for the semantic-yield runtime."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


class ContractError(RuntimeError):
    """Raised when a semantic-yield artifact violates its host contract."""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError(f"expected JSON object: {path}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_slug(value: str, maximum: int = 64) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (slug or "artifact")[:maximum]


def stable_id(prefix: str, semantic_value: Any) -> str:
    digest = hashlib.sha256(canonical_json(semantic_value).encode("utf-8")).hexdigest()
    label = semantic_value if isinstance(semantic_value, str) else prefix
    return f"{prefix}-{stable_slug(str(label), 48)}-{digest[:10]}"


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate(instance: Any, schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(instance),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        rendered = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ContractError(f"schema validation failed for {schema_path}: {rendered}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / "schemas").is_dir() and (candidate / "tools").is_dir():
            return candidate
    raise ContractError(f"could not resolve repository root from {start}")
