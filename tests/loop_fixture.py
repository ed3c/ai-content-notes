"""A synthetic v7.1 LOOP agent, so the harness can be exercised without a model.

The harness under test is deterministic; the compile intelligence it drives is
not. This module supplies a scripted stand-in that behaves the way the protocol
says a LOOP agent behaves: it reads the request the harness hands it, echoes the
registry digest it was given, emits the three channels, and reaches DONE on its
second round.

It is deliberately not clever. Everything interesting in a run has to come from
the harness's own validators, so a fixture that could repair its own mistakes
would hide exactly the failures these tests exist to catch.

Usable in-process (`respond(request)`) or as a subprocess responder:

    python3 tests/loop_fixture.py <request.json>
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_SOURCE = REPOSITORY_ROOT / "evals" / "runner" / "synthetic-loop" / "source.md"
PROMPT_GIT_BLOB_SHA1 = "7f3019f4b41a90728cd48a523d742c7c59721bf6"
PROTOCOL = "zettelkasten-v7.1-evidence-first-narrative-alive-dual-plane"


def card_body(
    stable_id: str,
    title: str,
    thesis: str,
    why: str,
    status_line: str,
    evidence_id: str,
    quote: str,
    falsifier: str,
    links: str,
) -> str:
    return "\n".join(
        [
            f"### {stable_id}｜{title}",
            "",
            f"- **核心命題**：{thesis}",
            f"- **為什麼重要**：{why}",
            "",
            f"- **證據與狀態**：{status_line}",
            f"  - [[{evidence_id}]]：{quote}",
            f"- **反證／限制**：{falsifier}",
            f"- **Typed Links**：{links}",
        ]
    )


def meta(stable_id: str, canonical_key: str, series: str, provenance: list[str]) -> dict[str, Any]:
    return {
        "stable_id": stable_id,
        "canonical_key": canonical_key,
        "series": series,
        "lifecycle": "ACTIVE",
        "revision": 1,
        "scope": "synthetic subject evals/runner/synthetic-loop/source.md; harness fixture only",
        "confidence_basis": "來自同一份合成素材的字面陳述，未對外部世界做任何主張。",
        "source_dependency_key": "synthetic:runner-loop",
        "source_provenance": provenance,
        "unresolved_links": [],
    }


def add(stable_id: str, canonical_key: str, series: str, body: str, provenance: list[str]) -> dict[str, Any]:
    return {
        "op": "ADD",
        "stable_id": stable_id,
        "canonical_key": canonical_key,
        "series": series,
        "revision": 1,
        "visible_payload": body,
        "card_meta": meta(stable_id, canonical_key, series, provenance),
    }


ROUND_ONE = [
    add(
        "N-round-budget-hides-truncation",
        "N | batch-compiler | stops-on | round-budget | synthetic-loop | source-digest:synthetic",
        "N",
        card_body(
            "N-round-budget-hides-truncation",
            "輪數上限讓截斷的批次長得跟完成的批次一樣",
            "以 N 輪為停止條件時，被截斷的最後一輪與真正完成的最後一輪輸出同構，兩者都留下 state 與 registry。",
            "停止條件若是操作者的耐心而非工作的性質，退出碼 0 就會被當成完成訊號。",
            "SOURCE_STATEMENT · SUPPORTED · MEDIUM",
            "EV-synthetic-loop-round-budget",
            "TEXT_MATCH::stops on a property of the operator's patience",
            "若最後一輪另外攜帶可獨立查核的完成收據，此同構即消失。",
            "FLOW → [[D-stall-check-costs-one-comparison]]",
        ),
        ["artifact:evals/runner/synthetic-loop/source.md", "TEXT_MATCH::a round budget stops the wrong thing"],
    ),
    add(
        "D-stall-check-costs-one-comparison",
        "D | stall-check | differs-from | round-budget | synthetic-loop | source-digest:synthetic",
        "D",
        card_body(
            "D-stall-check-costs-one-comparison",
            "重複偵測與輪數上限的差別是一次比較",
            "連續兩輪產出相同 registry 與相同 cursor 即為停滯；偵測成本是與前一輪的一次比較。",
            "輪數上限分不出停滯與緩慢，重複偵測分得出，且不會截斷仍在前進的執行。",
            "OBSERVATION · SUPPORTED · MEDIUM",
            "EV-synthetic-loop-stall-check",
            "TEXT_MATCH::Detecting the repeat costs one comparison",
            "若 registry 摘要含 wall clock，比較會永遠不相等，偵測失效。",
            "ROOT ← [[N-round-budget-hides-truncation]]",
        ),
        ["artifact:evals/runner/synthetic-loop/source.md", "TEXT_MATCH::a stall is not the same as a budget"],
    ),
]

ROUND_TWO = [
    add(
        "P-recheck-the-finished-batch",
        "P | finished-batch | verified-by | second-reconciliation | synthetic-loop | source-digest:synthetic",
        "P",
        card_body(
            "P-recheck-the-finished-batch",
            "把完成宣告換成對自己輸出再跑一次確定性管線",
            "宣告 DONE 後，對同一批卡片再 reconcile 一次；不是位元組相同就不算完成。",
            "由產出工作的同一個程序發出的完成訊號是自我回報，不帶資訊。",
            "NORMATIVE · SUPPORTED · MEDIUM",
            "EV-synthetic-loop-second-pass",
            "TEXT_MATCH::if reconciling the finished batch a second time is not byte-identical",
            "第二次 reconcile 只驗確定性部分；模型判斷的品質面不在其射程內。",
            "IMPLEMENTS → [[D-stall-check-costs-one-comparison]]",
        ),
        ["artifact:evals/runner/synthetic-loop/source.md", "TEXT_MATCH::the completion contract has to be checked"],
    ),
]

ROUNDS = [ROUND_ONE, ROUND_TWO]


def gates(status: str) -> dict[str, Any]:
    state: dict[str, Any] = {"status": status, "evidence": [], "failures": []}
    if status == "PASS":
        state["evidence"] = ["artifact:evals/runner/synthetic-loop/source.md"]
    if status == "FAIL":
        state["failures"] = ["synthetic failure"]
    return {f"QG-{index:02d}": dict(state) for index in range(1, 25)}


def _claimed_after_digest(operations: list[dict[str, Any]]) -> str:
    """What the fixture believes the next registry digest is.

    A model cannot hash, so this is a claim by construction. The harness records
    it and chains on its own reconciliation instead, which is the point.
    """
    payload = json.dumps(operations, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def channels_text(
    request: dict[str, Any],
    operations: list[dict[str, Any]],
    status: str,
    cursor_value: str,
    cursor_complete: bool,
) -> str:
    """The three v7.1 LOOP channels for one round, as a raw response would carry them."""
    last = status == "DONE"
    source_digest = request["source"]["source_digest"]
    after = _claimed_after_digest(operations)
    render_order = [item["stable_id"] for item in operations if "stable_id" in item]

    patch = {
        "schema_version": "zettelkasten-card-patch@2",
        "protocol": PROTOCOL,
        "prompt_git_blob_sha1": PROMPT_GIT_BLOB_SHA1,
        "source_digest": source_digest,
        "registry_before_digest": request["registry_before_digest"],
        "registry_after_digest": after,
        "operations": operations,
        "render_order": render_order,
        "audit_sidecar_ref": f"artifact:rounds/round-{request['round']:02d}.request.json",
    }
    report = {
        "schema_version": "zettelkasten-assertion-report@2",
        "protocol": PROTOCOL,
        "prompt": {
            "path": "governance/CARD_PROTOCOL_V7_1.md",
            "git_blob_sha1": PROMPT_GIT_BLOB_SHA1,
        },
        "source_digest": source_digest,
        "compiler_output_digest": after,
        "validator": {"name": "loop-fixture", "version": "1", "mode": "deterministic"},
        "quality_gates": gates("PASS" if last else "NOT_RUN"),
        "summary": (
            {"pass": 24, "fail": 0, "not_run": 0, "hard_gate_failures": []}
            if last
            else {"pass": 0, "fail": 0, "not_run": 24, "hard_gate_failures": []}
        ),
        "generated_at": "2026-09-01T00:00:00Z",
    }
    state = {
        "schema_version": "zettelkasten-compiler-state@2",
        "protocol": PROTOCOL,
        "prompt_git_blob_sha1": PROMPT_GIT_BLOB_SHA1,
        "run_mode": "LOOP",
        "state_channel": "SIDECAR",
        "render_order": "TASK_VALUE_FIRST",
        "render_mode": "PAYLOAD_FIRST",
        "status": status,
        "source_id": request["source"]["source_id"],
        "content_id": request["source"]["content_id"],
        "source_digest": source_digest,
        "registry_digest": after,
        "source_cursor": {
            "cursor_type": "section",
            "value": cursor_value,
            "complete": cursor_complete,
            "source_digest": source_digest,
        },
        "source_queue_empty": last,
        "baseline_guard_pass": True,
        "quality_gates": gates("PASS" if last else "NOT_RUN"),
        "remaining_work": [] if last else ["section 3"],
        "blocked_by": [],
        "updated_at": "2026-09-01T00:00:00Z",
    }
    blocks = [("CARD_PATCH", patch), ("ASSERTION_REPORT", report), ("NEXT_STATE", state)]
    return "prose the harness must ignore\n\n" + "\n\n".join(
        f"<!-- {name}\n{json.dumps(value, ensure_ascii=False)}\n-->" for name, value in blocks
    )


def respond(request: dict[str, Any], rounds: list[list[dict[str, Any]]] | None = None) -> str:
    """The scripted run: CONTINUE through the rounds, DONE on the last one."""
    rounds = ROUNDS if rounds is None else rounds
    index = request["round"] - 1
    if index >= len(rounds):
        raise SystemExit(f"fixture has no round {request['round']}")
    last = index == len(rounds) - 1
    return channels_text(
        request,
        rounds[index],
        "DONE" if last else "CONTINUE",
        f"section-{request['round'] * 2}",
        last,
    )


def noop_continue(request: dict[str, Any]) -> str:
    """A round that changes nothing and says CONTINUE. A loop that never ends."""
    return channels_text(
        request,
        [{"op": "NOOP", "reason": "nothing to compile this round"}],
        "CONTINUE",
        "section-1",
        False,
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: loop_fixture.py <request.json>")
    request = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    sys.stdout.write(respond(request))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
