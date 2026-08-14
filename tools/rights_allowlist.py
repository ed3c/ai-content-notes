#!/usr/bin/env python3
"""Fail-closed acquisition rights lookup for ranked YouTube rows.

The daily workflow asks one question before any acquisition: does this exact
canonical video id have an attested rights record that permits this exact
backend, today? Anything short of yes is `blocked` with an exact reason, and
the caller moves to the next ranked row instead of raising.

Public visibility is not authorization and is not expressible here: the
allowlist schema has no such `rights_basis`. This adapter performs no network
access and introduces no cookie, proxy, browser-session, PO-token-provider or
anti-bot bypass. It only reads a committed attestation record.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path("schemas/rights-allowlist.schema.json")
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")

# A rights_reference is an audit pointer, never a credential. These shapes are
# rejected so an allowlist cannot become a place secrets are committed.
SECRET_SHAPES = (
    re.compile(r"(?i)\b(bearer|authorization|api[_-]?key|token|secret|password)\b"),
    re.compile(r"(?i)[?&](access_token|key|sig|signature|token)="),
    re.compile(r"\b[A-Fa-f0-9]{32,}\b"),
)


class RightsError(RuntimeError):
    """Raised when the allowlist artifact itself is unusable."""


def load_allowlist(path: Path, schema_path: Path | None = None) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RightsError(f"unreadable rights allowlist: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RightsError(f"expected JSON object: {path}")
    schema = json.loads((schema_path or SCHEMA_PATH).read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        rendered = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise RightsError(f"rights allowlist failed validation: {rendered}")
    seen: set[str] = set()
    for entry in value["entries"]:
        if entry["video_id"] in seen:
            raise RightsError(f"duplicate rights record: {entry['video_id']}")
        seen.add(entry["video_id"])
    return value


def _blocked(video_id: str, backend: str, reason: str) -> dict[str, Any]:
    return {
        "video_id": video_id,
        "backend": backend,
        "decision": "blocked",
        "blocked_reason": reason,
        "rights_basis": None,
        "attestor": None,
        "gold_transcript": None,
    }


def resolve(
    allowlist: dict[str, Any],
    video_id: str,
    backend: str,
    as_of: str,
) -> dict[str, Any]:
    """Return an admission decision. Never raises for an unauthorized row."""
    if not VIDEO_ID.match(video_id or ""):
        return _blocked(video_id, backend, "video_id is not a canonical YouTube id")

    matches = [entry for entry in allowlist["entries"] if entry["video_id"] == video_id]
    if not matches:
        return _blocked(video_id, backend, "no rights record for this video id")
    entry = matches[0]

    if entry["authorization_status"] != "verified":
        return _blocked(
            video_id,
            backend,
            f"authorization_status is {entry['authorization_status']}, not verified",
        )
    if any(shape.search(entry["rights_reference"]) for shape in SECRET_SHAPES):
        return _blocked(video_id, backend, "rights_reference looks like a credential")
    if entry["expires_on"] is not None and entry["expires_on"] < as_of:
        return _blocked(
            video_id, backend, f"attestation expired on {entry['expires_on']}"
        )
    if entry["attested_on"] > as_of:
        return _blocked(video_id, backend, "attestation is dated in the future")
    if backend not in entry["permitted_backends"]:
        return _blocked(video_id, backend, f"backend {backend} is not permitted")

    return {
        "video_id": video_id,
        "backend": backend,
        "decision": "permitted",
        "blocked_reason": None,
        "rights_basis": entry["rights_basis"],
        "attestor": entry["attestor"],
        "gold_transcript": entry["gold_transcript"],
    }


def plan_batch(
    allowlist: dict[str, Any],
    ranked_video_ids: list[str],
    backend: str,
    as_of: str,
) -> list[dict[str, Any]]:
    """Decide every ranked row. A blocked row never stops the ones after it."""
    return [resolve(allowlist, video_id, backend, as_of) for video_id in ranked_video_ids]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allowlist", required=True, type=Path)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--video-id", action="append", default=[], required=True)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--as-of", required=True, help="YYYY-MM-DD evaluation date")
    args = parser.parse_args()

    decisions = plan_batch(
        load_allowlist(args.allowlist, args.schema),
        args.video_id,
        args.backend,
        args.as_of,
    )
    print(json.dumps({"decisions": decisions}, ensure_ascii=False, indent=2, sort_keys=True))
    # A blocked row is a normal outcome, not a tool failure: the caller
    # continues to the next ranked item.
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RightsError as error:
        print(f"rights allowlist unusable: {error}", file=sys.stderr)
        raise SystemExit(2) from error
