#!/usr/bin/env python3
"""Parse the three v7.1 LOOP output channels out of a captured raw response.

`governance/CARD_PROTOCOL_V7_1.md` section 10 declares that a LOOP run emits
CARD_PATCH, ASSERTION_REPORT and NEXT_STATE, and section 5 declares the
`STATE_CHANNEL: HTML_COMMENT` sidecar form used by CARD_META and RUN_STATE.
This adapter reads that form; it does not extend, reinterpret or supply any
part of the prompt.

The parser is deliberately hostile to its input. A raw model response is
untrusted data, so a truncated comment, malformed JSON, a duplicate key, a
duplicate channel, a repeated stable id, or a registry digest that does not
chain are each a hard failure rather than a best-effort recovery.

It also refuses to launder authority. `quality_gates` inside a parsed channel
is a model-authored label, never a gate result: the return value carries
`gate_authority: "none"` and the labels are quarantined under
`model_authored_gate_labels`. An external validator remains the only thing
that can turn QG-01..QG-24 into a pass.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

PROMPT_GIT_BLOB_SHA1 = "7f3019f4b41a90728cd48a523d742c7c59721bf6"
PROTOCOL = "zettelkasten-v7.1-evidence-first-narrative-alive-dual-plane"

CHANNEL_SCHEMAS = {
    "CARD_PATCH": "schemas/card-patch-v7.1.schema.json",
    "ASSERTION_REPORT": "schemas/assertion-report-v7.1.schema.json",
    "NEXT_STATE": "schemas/compiler-state-v7.1.schema.json",
}
OPEN = re.compile(r"<!--[ \t]*(CARD_PATCH|ASSERTION_REPORT|NEXT_STATE)\b")
TERMINAL_STATES = {"CONTINUE", "DONE", "BLOCKED", "FAILED"}


class ChannelError(RuntimeError):
    """Raised when a captured response cannot be trusted as three channels."""


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise ChannelError(f"duplicate JSON key in channel payload: {key}")
        seen[key] = value
    return seen


def _strict_json(payload: str, channel: str) -> dict[str, Any]:
    try:
        value = json.loads(payload, object_pairs_hook=_no_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise ChannelError(f"{channel} payload is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ChannelError(f"{channel} payload is not a JSON object")
    return value


def split_channels(text: str) -> dict[str, str]:
    """Return raw payload text per channel, failing closed on a truncated block."""
    blocks: dict[str, str] = {}
    for match in OPEN.finditer(text):
        channel = match.group(1)
        end = text.find("-->", match.end())
        if end < 0:
            raise ChannelError(f"{channel} channel is truncated: no closing comment")
        if channel in blocks:
            raise ChannelError(f"duplicate {channel} channel in one response")
        blocks[channel] = text[match.end() : end]
    missing = sorted(set(CHANNEL_SCHEMAS) - set(blocks))
    if missing:
        raise ChannelError(f"missing required channel: {', '.join(missing)}")
    return blocks


def _validate(instance: dict[str, Any], schema_path: Path, channel: str) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        rendered = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ChannelError(f"{channel} failed schema validation: {rendered}")


def _check_operations(patch: dict[str, Any]) -> None:
    stable_ids: set[str] = set()
    for operation in patch["operations"]:
        stable_id = operation.get("stable_id")
        if stable_id is None:
            continue
        if stable_id in stable_ids:
            raise ChannelError(f"duplicate stable_id in one patch: {stable_id}")
        stable_ids.add(stable_id)
        if operation["op"] == "SUPERSEDE" and "superseded_by" not in operation:
            raise ChannelError(f"SUPERSEDE without superseded_by: {stable_id}")
    unknown = sorted(set(patch["render_order"]) - stable_ids)
    if unknown:
        raise ChannelError(f"render_order names ids absent from operations: {unknown}")


def _check_consistency(channels: dict[str, dict[str, Any]]) -> None:
    patch = channels["CARD_PATCH"]
    report = channels["ASSERTION_REPORT"]
    state = channels["NEXT_STATE"]

    blobs = {
        patch["prompt_git_blob_sha1"],
        report["prompt"]["git_blob_sha1"],
        state["prompt_git_blob_sha1"],
    }
    if blobs != {PROMPT_GIT_BLOB_SHA1}:
        raise ChannelError(f"channels do not agree on the pinned prompt blob: {sorted(blobs)}")
    if {patch["protocol"], report["protocol"], state["protocol"]} != {PROTOCOL}:
        raise ChannelError("channels do not agree on the protocol identity")

    digests = {patch["source_digest"], report["source_digest"], state["source_digest"]}
    if len(digests) != 1:
        raise ChannelError(f"channels do not agree on source_digest: {sorted(digests)}")
    if state["source_cursor"]["source_digest"] != state["source_digest"]:
        raise ChannelError("source cursor is bound to a different source digest")

    # The registry must chain: the state a run hands forward is the registry the
    # patch produced. Anything else is a stale registry revision.
    if patch["registry_after_digest"] != state["registry_digest"]:
        raise ChannelError(
            "stale registry revision: CARD_PATCH.registry_after_digest "
            f"{patch['registry_after_digest']} != NEXT_STATE.registry_digest "
            f"{state['registry_digest']}"
        )
    if state["status"] not in TERMINAL_STATES:
        raise ChannelError(f"unknown completion state: {state['status']}")
    _check_operations(patch)


def parse(text: str, root: Path) -> dict[str, Any]:
    blocks = split_channels(text)
    channels = {
        channel: _strict_json(payload, channel) for channel, payload in blocks.items()
    }
    for channel, relative in CHANNEL_SCHEMAS.items():
        _validate(channels[channel], root / relative, channel)
    _check_consistency(channels)
    return {
        "channels": channels,
        "status": channels["NEXT_STATE"]["status"],
        "source_digest": channels["CARD_PATCH"]["source_digest"],
        "registry_after_digest": channels["CARD_PATCH"]["registry_after_digest"],
        "operation_count": len(channels["CARD_PATCH"]["operations"]),
        # QG labels arrive inside the response and are therefore claims by the
        # thing under test. They are quarantined, never promoted.
        "gate_authority": "none",
        "model_authored_gate_labels": {
            "assertion_report": channels["ASSERTION_REPORT"]["quality_gates"],
            "next_state": channels["NEXT_STATE"]["quality_gates"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-response", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.raw_response.is_file():
        raise ChannelError(f"missing raw response artifact: {args.raw_response}")
    result = parse(args.raw_response.read_text(encoding="utf-8"), args.root.resolve())
    summary = {
        "status": result["status"],
        "operation_count": result["operation_count"],
        "gate_authority": result["gate_authority"],
        "source_digest": result["source_digest"],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ChannelError as error:
        print(f"compiler channel rejected: {error}", file=sys.stderr)
        raise SystemExit(2) from error
