"""Failure injection for the v7.1 LOOP output channel parser.

Covers the deterministic half of the failure list in issue #10: truncated
channel, malformed JSON, duplicate key, duplicate channel, missing artifact,
stale registry revision, and duplicate stable ids. Timeout and partial state
persistence belong to the invoking adapter, not to parsing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import parse_compiler_channels as channels  # noqa: E402

BLOB = channels.PROMPT_GIT_BLOB_SHA1
PROTOCOL = channels.PROTOCOL
SOURCE = "sha256:" + "1" * 64
REGISTRY_BEFORE = "sha256:" + "2" * 64
REGISTRY_AFTER = "sha256:" + "3" * 64
OUTPUT = "sha256:" + "4" * 64


def gates(status: str = "NOT_RUN") -> dict[str, Any]:
    state: dict[str, Any] = {"status": status, "evidence": [], "failures": []}
    if status == "PASS":
        state["evidence"] = ["validator:external"]
    if status == "FAIL":
        state["failures"] = ["gate failed"]
    return {f"QG-{index:02d}": dict(state) for index in range(1, 25)}


def card_patch(**overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": "zettelkasten-card-patch@2",
        "protocol": PROTOCOL,
        "prompt_git_blob_sha1": BLOB,
        "source_digest": SOURCE,
        "registry_before_digest": REGISTRY_BEFORE,
        "registry_after_digest": REGISTRY_AFTER,
        "operations": [
            {
                "op": "ADD",
                "stable_id": "N-example-case",
                "canonical_key": "N | a | b | c | d | e",
                "series": "N",
                "revision": 1,
                "visible_payload": "### N-example-case｜Example",
                "card_meta": {"stable_id": "N-example-case"},
            }
        ],
        "render_order": ["N-example-case"],
        "audit_sidecar_ref": "artifact:audit/run-1.json",
    }
    value.update(overrides)
    return value


def assertion_report(**overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": "zettelkasten-assertion-report@2",
        "protocol": PROTOCOL,
        "prompt": {"path": "governance/CARD_PROTOCOL_V7_1.md", "git_blob_sha1": BLOB},
        "source_digest": SOURCE,
        "compiler_output_digest": OUTPUT,
        "validator": {"name": "host", "version": "1", "mode": "deterministic"},
        "quality_gates": gates(),
        "summary": {"pass": 0, "fail": 0, "not_run": 24, "hard_gate_failures": []},
        "generated_at": "2026-08-14T00:00:00Z",
    }
    value.update(overrides)
    return value


def next_state(**overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": "zettelkasten-compiler-state@2",
        "protocol": PROTOCOL,
        "prompt_git_blob_sha1": BLOB,
        "run_mode": "LOOP",
        # Repository rule 11: a LOOP run keeps machine state in the sidecar
        # channel, never printed into the human document.
        "state_channel": "SIDECAR",
        "render_order": "TASK_VALUE_FIRST",
        "render_mode": "PAYLOAD_FIRST",
        "status": "CONTINUE",
        "source_id": "youtube-video:CvRngaQZQ3Y",
        "content_id": "CvRngaQZQ3Y",
        "source_digest": SOURCE,
        "registry_digest": REGISTRY_AFTER,
        "source_cursor": {
            "cursor_type": "timestamp",
            "value": "00:07:22",
            "complete": False,
            "source_digest": SOURCE,
        },
        "source_queue_empty": False,
        "baseline_guard_pass": True,
        "quality_gates": gates(),
        "remaining_work": ["second batch"],
        "blocked_by": [],
        "updated_at": "2026-08-14T00:00:00Z",
    }
    value.update(overrides)
    return value


def response(
    patch: dict[str, Any] | None = None,
    report: dict[str, Any] | None = None,
    state: dict[str, Any] | None = None,
) -> str:
    parts = [
        ("CARD_PATCH", card_patch() if patch is None else patch),
        ("ASSERTION_REPORT", assertion_report() if report is None else report),
        ("NEXT_STATE", next_state() if state is None else state),
    ]
    return "prose the host must ignore\n\n" + "\n\n".join(
        f"<!-- {name}\n{json.dumps(value, ensure_ascii=False)}\n-->" for name, value in parts
    )


def parse(text: str) -> dict[str, Any]:
    return channels.parse(text, REPOSITORY_ROOT)


def test_three_well_formed_channels_parse() -> None:
    result = parse(response())
    assert result["status"] == "CONTINUE"
    assert result["operation_count"] == 1
    assert result["registry_after_digest"] == REGISTRY_AFTER
    assert set(result["channels"]) == {"CARD_PATCH", "ASSERTION_REPORT", "NEXT_STATE"}


def test_model_authored_gate_labels_are_never_gate_authority() -> None:
    forged = response(report=assertion_report(
        quality_gates=gates("PASS"),
        summary={"pass": 24, "fail": 0, "not_run": 0, "hard_gate_failures": []},
    ))
    result = parse(forged)
    assert result["gate_authority"] == "none"
    assert "quality_gates" not in result
    quarantined = result["model_authored_gate_labels"]["assertion_report"]
    assert all(gate["status"] == "PASS" for gate in quarantined.values())


def test_truncated_channel_fails_closed() -> None:
    text = response()
    truncated = text[: text.rfind("-->")]
    with pytest.raises(channels.ChannelError, match="truncated"):
        parse(truncated)


def test_malformed_json_fails_closed() -> None:
    with pytest.raises(channels.ChannelError, match="not valid JSON"):
        parse(response().replace('"operations"', '"operations",', 1))


def test_duplicate_json_key_fails_closed() -> None:
    text = response().replace(
        '"status": "CONTINUE"', '"status": "CONTINUE", "status": "DONE"', 1
    )
    with pytest.raises(channels.ChannelError, match="duplicate JSON key"):
        parse(text)


def test_duplicate_channel_fails_closed() -> None:
    text = response()
    block = text[text.index("<!-- NEXT_STATE") :]
    with pytest.raises(channels.ChannelError, match="duplicate NEXT_STATE"):
        parse(text + "\n\n" + block)


def test_missing_channel_fails_closed() -> None:
    text = response()
    without_report = text[: text.index("<!-- ASSERTION_REPORT")] + text[
        text.index("<!-- NEXT_STATE") :
    ]
    with pytest.raises(channels.ChannelError, match="missing required channel"):
        parse(without_report)


def test_stale_registry_revision_fails_closed() -> None:
    with pytest.raises(channels.ChannelError, match="stale registry revision"):
        parse(response(state=next_state(registry_digest="sha256:" + "9" * 64)))


def test_channels_must_agree_on_the_pinned_prompt_blob() -> None:
    with pytest.raises(channels.ChannelError, match="schema validation"):
        parse(response(state=next_state(prompt_git_blob_sha1="0" * 40)))


def test_channels_must_agree_on_the_source_digest() -> None:
    with pytest.raises(channels.ChannelError, match="source_digest"):
        parse(response(report=assertion_report(source_digest="sha256:" + "8" * 64)))


def test_cursor_bound_to_a_different_source_fails_closed() -> None:
    drifted = next_state(
        source_cursor={
            "cursor_type": "timestamp",
            "value": "00:07:22",
            "complete": False,
            "source_digest": "sha256:" + "7" * 64,
        }
    )
    with pytest.raises(channels.ChannelError, match="different source digest"):
        parse(response(state=drifted))


def test_duplicate_stable_id_in_one_patch_fails_closed() -> None:
    operations = card_patch()["operations"]
    duplicated = card_patch(operations=[operations[0], dict(operations[0], revision=2)])
    with pytest.raises(channels.ChannelError, match="duplicate stable_id"):
        parse(response(patch=duplicated))


def test_supersede_without_a_target_fails_closed() -> None:
    patch = card_patch(
        operations=[{"op": "SUPERSEDE", "stable_id": "N-old-case", "revision": 2, "reason": "merged"}],
        render_order=["N-old-case"],
    )
    with pytest.raises(channels.ChannelError, match="SUPERSEDE without superseded_by"):
        parse(response(patch=patch))


def test_render_order_naming_an_absent_card_fails_closed() -> None:
    patch = card_patch(render_order=["N-example-case", "C-never-emitted"])
    with pytest.raises(channels.ChannelError, match="render_order names ids absent"):
        parse(response(patch=patch))


def test_noop_replay_is_a_valid_patch() -> None:
    patch = card_patch(
        operations=[{"op": "NOOP", "reason": "identical input digests"}],
        registry_before_digest=REGISTRY_AFTER,
        render_order=[],
    )
    result = parse(response(patch=patch))
    assert result["operation_count"] == 1
    assert result["channels"]["CARD_PATCH"]["operations"][0]["op"] == "NOOP"


def test_loop_run_may_not_declare_the_html_comment_state_channel() -> None:
    """Rule 11: a scheduled LOOP run never prints machine state into the doc."""
    with pytest.raises(channels.ChannelError, match="state_channel"):
        parse(response(state=next_state(state_channel="HTML_COMMENT")))


def test_done_may_not_be_declared_with_work_remaining() -> None:
    forged = next_state(
        status="DONE",
        remaining_work=["second batch"],
        source_queue_empty=True,
        baseline_guard_pass=True,
    )
    with pytest.raises(channels.ChannelError, match="schema validation"):
        parse(response(state=forged))


def test_missing_raw_response_artifact_fails_closed(tmp_path: Path) -> None:
    argv = [
        "parse_compiler_channels.py",
        "--raw-response",
        str(tmp_path / "absent.md"),
        "--root",
        str(REPOSITORY_ROOT),
    ]
    original = sys.argv
    sys.argv = argv
    try:
        with pytest.raises(channels.ChannelError, match="missing raw response artifact"):
            channels.main()
    finally:
        sys.argv = original
