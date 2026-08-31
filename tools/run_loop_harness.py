#!/usr/bin/env python3
"""Drive a v7.1 RUN_MODE LOOP compilation to its completion contract.

`governance/CARD_PROTOCOL_V7_1.md` section 10 says a LOOP run emits CARD_PATCH,
ASSERTION_REPORT and NEXT_STATE each round, and section 9 says the run ends on
DONE / BLOCKED / FAILED. Both halves existed only as prompt text: the channels
could be parsed (`tools/parse_compiler_channels.py`) and a rendered batch could
be reconciled (`tools/reconcile_card_registry.py`), but nothing fed one round's
state into the next, and nothing decided when the loop was over.

This is that harness, and only that harness. The compile intelligence is the
calling agent executing the protocol; the runner never writes a card, never
judges a claim, and never invents a state. It does five deterministic things:

1.  hands the agent the source, the prior state and the current registry;
2.  validates all three channels against their schemas every round, by calling
    the existing parser rather than re-deriving what a channel is;
3.  binds the response to *this* run: the source digest must be the digest of
    the file on disk, and `registry_before_digest` must echo the digest the
    runner handed over. A round compiled against a hallucinated prior state is
    refused, not merged;
4.  applies the patch by writing cards and reconciling them into the registry,
    so registry state is produced by the reconciler and never by a model;
5.  stops on the completion contract. There is no round budget: CONTINUE loops
    again. A CONTINUE that changes neither the registry nor the source cursor
    is not progress, and ends the run FAILED — a stall, not a cap.

Two authorities are refused on purpose, and both are named in the receipt:

    gate_authority: "none"      QG-01..QG-24 labels arrive inside the response
                                and stay quarantined, exactly as the channel
                                parser leaves them.
    digest_authority: "runner"  a model cannot compute SHA-256. Its
                                `registry_after_digest` is recorded as a claim;
                                the digest that chains into the next round is
                                the one reconciliation actually produced.

DONE is likewise not a word the model gets to say alone. A DONE round is
admitted only if the batch reconciles clean, re-reconciles byte-identically
without advancing the revision, every id in `render_order` exists on disk, and
every declared high-signal control is mapped. A DONE that fails those becomes
BLOCKED naming what failed.

`--high-signal` is that last check, and it is what makes section 9's
`high_signal_unmapped = 0` falsifiable instead of self-reported. The file is a
JSON list of `{"key", "quote"}`; each quote must be an exact substring of the
source, because a control that is not in the subject controls nothing. An item
is mapped when some card declares `TEXT_MATCH::<quote>` in its CARD_META
`source_provenance` — the protocol's own locator vocabulary (section 3), so the
check reads what the cards already have to say rather than inventing a field.

Usage:
    python3 tools/run_loop_harness.py --run-dir RUN --source SRC \
        --source-id ID --content-id CID --updated-at TS \
        [--high-signal CONTROLS.json] (--responder CMD | --replay DIR)

The responder is invoked once per round as `CMD <request.json>`; its stdout is
the raw model response. `--replay DIR` serves `DIR/round-NN.raw.md` instead --
the exact name this harness writes, so a finished run's `rounds/` directory
replays as-is with no renaming step in between.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import parse_compiler_channels as channels  # noqa: E402
import reconcile_card_registry as registry  # noqa: E402

# "no registry yet", written so round one has an exact digest to echo instead
# of a special case. SHA-256 of the empty byte string.
EMPTY_REGISTRY_DIGEST = "sha256:" + hashlib.sha256(b"").hexdigest()
TERMINAL_STATES = {"DONE", "BLOCKED", "FAILED"}
REGISTRY_SCHEMA = Path("schemas/card-registry.schema.json")


class HarnessError(RuntimeError):
    """Raised when a round cannot be trusted. Never a compile verdict."""


def digest_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def registry_digest(value: dict[str, Any] | None) -> str:
    """Wall-clock-free digest of a registry, or the empty-registry constant."""
    if value is None:
        return EMPTY_REGISTRY_DIGEST
    return digest_bytes(registry.content_identity(value).encode("utf-8"))


def render_card(operation: dict[str, Any]) -> str:
    """A card file: the visible payload plus the CARD_META sidecar (section 5)."""
    meta = json.dumps(operation["card_meta"], ensure_ascii=False, indent=2, sort_keys=True)
    return operation["visible_payload"].rstrip() + "\n\n<!-- CARD_META\n" + meta + "\n-->\n"


def _rewrite_lifecycle(path: Path, lifecycle: str, revision: int) -> None:
    text = path.read_text(encoding="utf-8")
    match = registry.CARD_META.search(text)
    if match is None:
        raise HarnessError(f"cannot change lifecycle of a card with no CARD_META: {path.name}")
    try:
        meta = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise HarnessError(f"card sidecar is not valid JSON: {path.name}: {exc}") from exc
    meta["lifecycle"] = lifecycle
    meta["revision"] = revision
    rendered = json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True)
    path.write_text(
        registry.CARD_META.sub(lambda _: f"<!-- CARD_META\n{rendered}\n-->", text, count=1),
        encoding="utf-8",
    )


def apply_operations(operations: list[dict[str, Any]], cards_dir: Path) -> None:
    """Write the patch to disk. The reconciler, not this function, owns identity."""
    cards_dir.mkdir(parents=True, exist_ok=True)
    for operation in operations:
        op = operation["op"]
        if op == "NOOP":
            continue
        path = cards_dir / f"{operation['stable_id']}.md"
        if op in {"ADD", "UPDATE"}:
            if op == "UPDATE" and not path.is_file():
                raise HarnessError(f"UPDATE names a card that does not exist: {path.name}")
            if op == "ADD" and path.is_file():
                raise HarnessError(f"ADD would overwrite an existing card: {path.name}")
            path.write_text(render_card(operation), encoding="utf-8")
            continue
        if not path.is_file():
            raise HarnessError(f"{op} names a card that does not exist: {path.name}")
        _rewrite_lifecycle(
            path,
            "SUPERSEDED" if op == "SUPERSEDE" else "DEPRECATED",
            int(operation["revision"]),
        )


def _display_path(path: Path, repo_root: Path) -> str:
    """Repo-relative when the path lives under repo_root, so a receipt's
    subject identity survives the clone that produced it being deleted --
    an absolute host path stops meaning anything the moment it is gone."""
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def build_request(
    round_number: int,
    source_path: Path,
    source_digest: str,
    source_id: str,
    content_id: str,
    before_digest: str,
    prior_state: dict[str, Any] | None,
    cards_dir: Path,
    registry_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    return {
        "schema_version": "loop-harness-request@1",
        "round": round_number,
        "run_mode": "LOOP",
        "state_channel": "SIDECAR",
        "protocol": channels.PROTOCOL,
        "prompt": {
            "path": "governance/CARD_PROTOCOL_V7_1.md",
            "git_blob_sha1": channels.PROMPT_GIT_BLOB_SHA1,
        },
        "source": {
            "path": _display_path(source_path, repo_root),
            "source_id": source_id,
            "content_id": content_id,
            "source_digest": source_digest,
        },
        "registry_before_digest": before_digest,
        "registry_path": _display_path(registry_path, repo_root) if registry_path.is_file() else None,
        "cards_directory": _display_path(cards_dir, repo_root),
        "prior_state": prior_state,
    }


def _responder_from_command(command: str, cwd: Path) -> Callable[[int, Path], str]:
    argv = shlex.split(command)
    if not argv:
        raise HarnessError("--responder is empty")

    def call(round_number: int, request_path: Path) -> str:
        result = subprocess.run(  # noqa: S603 - operator-supplied compile intelligence
            [*argv, str(request_path)],
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        if result.returncode != 0:
            detail = result.stderr.strip().splitlines()[-1:] or ["<no stderr>"]
            raise HarnessError(
                f"round {round_number}: responder exited {result.returncode}: {detail[0]}"
            )
        if not result.stdout.strip():
            raise HarnessError(f"round {round_number}: responder produced an empty response")
        return result.stdout

    return call


def _responder_from_replay(replay_dir: Path) -> Callable[[int, Path], str]:
    def call(round_number: int, request_path: Path) -> str:
        del request_path
        # Same name the harness writes, so any completed run's `rounds/`
        # directory is replayable as-is with no renaming step in between.
        path = replay_dir / f"round-{round_number:02d}.raw.md"
        if not path.is_file():
            # An exhausted replay is an absent round, never a quiet DONE.
            raise HarnessError(f"replay has no round {round_number}: {path}")
        return path.read_text(encoding="utf-8")

    return call


def load_high_signal(path: Path, source_text: str) -> list[dict[str, str]]:
    """Read the high-signal controls, and prove each one is really in the subject."""
    try:
        items = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HarnessError(f"cannot read high-signal controls: {path}: {exc}") from exc
    if not isinstance(items, list) or not items:
        raise HarnessError(f"high-signal controls must be a non-empty list: {path}")
    controls: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            raise HarnessError(f"high-signal entry is not an object: {item!r}")
        key, quote = item.get("key"), item.get("quote")
        if not isinstance(key, str) or not key or not isinstance(quote, str) or not quote:
            raise HarnessError(f"high-signal entry needs a key and a quote: {item!r}")
        if quote not in source_text:
            # A planted control that is not in the source is not a control; it
            # would fail forever and prove nothing about coverage.
            raise HarnessError(f"high-signal control {key} is not present in the source")
        controls.append({"key": key, "quote": quote})
    return controls


def unmapped_high_signal(controls: list[dict[str, str]], cards_dir: Path) -> list[str]:
    """Controls no card anchored, by the protocol's own TEXT_MATCH locator."""
    anchors: set[str] = set()
    for path in sorted(cards_dir.glob("*.md")):
        match = registry.CARD_META.search(path.read_text(encoding="utf-8"))
        if match is None:
            continue
        try:
            meta = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue  # a broken sidecar is the reconciler's finding, not this one
        anchors.update(str(entry) for entry in meta.get("source_provenance", []))
    return [
        control["key"]
        for control in controls
        if f"TEXT_MATCH::{control['quote']}" not in anchors
    ]


def _admit_done(
    card_paths: list[Path],
    current: dict[str, Any],
    source_id: str,
    source_digest: str,
    updated_at: str,
    render_order: list[str],
    cards_dir: Path,
    controls: list[dict[str, str]] | None = None,
) -> list[str]:
    """The mechanically checkable half of the section 9 completion contract."""
    reasons: list[str] = []
    for key in unmapped_high_signal(controls or [], cards_dir):
        reasons.append(f"high_signal_unmapped: {key}")
    missing = [name for name in render_order if not (cards_dir / f"{name}.md").is_file()]
    if missing:
        reasons.append(f"render_order names cards absent from disk: {', '.join(sorted(missing))}")
    try:
        replay, gaps = registry.reconcile(
            card_paths, source_id, source_digest, updated_at, prior=current
        )
    except registry.RegistryError as failure:
        return [*reasons, f"registry refused a second reconciliation: {failure}"]
    if gaps:
        return [*reasons, f"registry gap on re-run: {'; '.join(gaps)}"]
    if replay["registry_revision"] != current["registry_revision"]:
        reasons.append(
            "re-running an unchanged batch advanced registry_revision "
            f"{current['registry_revision']} -> {replay['registry_revision']}"
        )
    if registry.render(replay) != registry.render(current):
        reasons.append("re-running an unchanged batch did not reproduce the same registry")
    return reasons


def run(
    run_dir: Path,
    source_path: Path,
    source_id: str,
    content_id: str,
    updated_at: str,
    responder: Callable[[int, Path], str],
    repo_root: Path,
    high_signal: Path | None = None,
) -> dict[str, Any]:
    if not source_path.is_file():
        raise HarnessError(f"missing source artifact: {source_path}")
    source_bytes = source_path.read_bytes()
    source_digest = digest_bytes(source_bytes)
    controls = (
        load_high_signal(high_signal, source_bytes.decode("utf-8"))
        if high_signal is not None
        else []
    )

    cards_dir = run_dir / "cards"
    rounds_dir = run_dir / "rounds"
    registry_path = run_dir / "card-registry.json"
    rounds_dir.mkdir(parents=True, exist_ok=True)
    cards_dir.mkdir(parents=True, exist_ok=True)

    current: dict[str, Any] | None = (
        json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.is_file() else None
    )
    prior_state: dict[str, Any] | None = None
    records: list[dict[str, Any]] = []
    status = "CONTINUE"
    blocked_by: list[str] = []
    round_number = 0

    while status not in TERMINAL_STATES:
        round_number += 1
        before_digest = registry_digest(current)
        request = build_request(
            round_number,
            source_path,
            source_digest,
            source_id,
            content_id,
            before_digest,
            prior_state,
            cards_dir,
            registry_path,
            repo_root,
        )
        request_path = rounds_dir / f"round-{round_number:02d}.request.json"
        request_path.write_text(
            json.dumps(request, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        raw = responder(round_number, request_path)
        (rounds_dir / f"round-{round_number:02d}.raw.md").write_text(raw, encoding="utf-8")

        try:
            parsed = channels.parse(raw, repo_root)
        except channels.ChannelError as failure:
            raise HarnessError(f"round {round_number}: {failure}") from failure

        patch = parsed["channels"]["CARD_PATCH"]
        state = parsed["channels"]["NEXT_STATE"]

        # Bind the response to this run. Schema validity only proves a response
        # is well formed; these prove it is a response to the state we handed over.
        if patch["source_digest"] != source_digest:
            raise HarnessError(
                f"round {round_number}: response compiled a different source: "
                f"{patch['source_digest']} != {source_digest}"
            )
        if patch["registry_before_digest"] != before_digest:
            raise HarnessError(
                f"round {round_number}: response carries a stale prior registry: "
                f"{patch['registry_before_digest']} != {before_digest}"
            )
        if state["run_mode"] != "LOOP":
            raise HarnessError(f"round {round_number}: run_mode is not LOOP: {state['run_mode']}")
        if (state["source_id"], state["content_id"]) != (source_id, content_id):
            raise HarnessError(
                f"round {round_number}: state names a different subject: "
                f"{state['source_id']}/{state['content_id']}"
            )

        apply_operations(patch["operations"], cards_dir)
        card_paths = sorted(cards_dir.glob("*.md"))
        try:
            reconciled, gaps = registry.reconcile(
                card_paths, source_id, source_digest, updated_at, prior=current
            )
        except registry.RegistryError as failure:
            raise HarnessError(f"round {round_number}: {failure}") from failure
        if gaps:
            raise HarnessError(f"round {round_number}: card batch does not reconcile: {'; '.join(gaps)}")
        try:
            registry.validate(reconciled, repo_root / REGISTRY_SCHEMA)
        except registry.RegistryError as failure:
            raise HarnessError(f"round {round_number}: {failure}") from failure
        registry_path.write_text(registry.render(reconciled), encoding="utf-8")

        after_digest = registry_digest(reconciled)
        status = state["status"]
        if status == "DONE":
            blocked_by = _admit_done(
                card_paths,
                reconciled,
                source_id,
                source_digest,
                updated_at,
                patch["render_order"],
                cards_dir,
                controls,
            )
            if blocked_by:
                status = "BLOCKED"

        cursor = state["source_cursor"]
        record = {
            "round": round_number,
            "declared_status": state["status"],
            "status": status,
            "operation_count": parsed["operation_count"],
            "registry_before_digest": before_digest,
            "registry_after_digest": after_digest,
            "model_authored_registry_after_digest": patch["registry_after_digest"],
            "registry_revision": reconciled["registry_revision"],
            "card_count": len(reconciled["cards"]),
            "source_cursor": cursor,
            "model_authored_gate_labels": parsed["model_authored_gate_labels"],
            "raw_response": str(
                (rounds_dir / f"round-{round_number:02d}.raw.md").relative_to(run_dir)
            ),
        }

        # No round budget. A CONTINUE that moves neither the registry nor the
        # cursor is a stall, and a stall is a failure rather than a reason to
        # keep paying for rounds.
        if status == "CONTINUE" and records:
            previous = records[-1]
            if (previous["registry_after_digest"], previous["source_cursor"]) == (
                after_digest,
                cursor,
            ):
                status = "FAILED"
                record["status"] = "FAILED"
                blocked_by = [
                    f"round {round_number} advanced neither the registry nor the source cursor"
                ]

        records.append(record)
        prior_state = state
        current = reconciled

    return {
        "schema_version": "loop-harness-receipt@1",
        "source_id": source_id,
        "content_id": content_id,
        "source_path": _display_path(source_path, repo_root),
        "source_digest": source_digest,
        "status": status,
        "blocked_by": blocked_by,
        "round_count": round_number,
        "rounds": records,
        "registry_digest": registry_digest(current),
        "registry_revision": (current or {}).get("registry_revision"),
        "card_count": len((current or {}).get("cards", {})),
        "stopped_on": "completion-contract",
        "gate_authority": "none",
        "digest_authority": "runner",
        "high_signal_control": "PRESENT" if controls else "ABSENT",
        "high_signal_declared": len(controls),
        "high_signal_unmapped": unmapped_high_signal(controls, cards_dir),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a v7.1 LOOP compilation to its contract")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--content-id", required=True)
    parser.add_argument("--updated-at", required=True, help="wall clock stamped into the registry")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--receipt", type=Path)
    parser.add_argument(
        "--high-signal",
        type=Path,
        help="JSON list of {key, quote} controls that DONE requires a card to anchor",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--responder", help="command invoked as CMD <request.json> each round")
    source.add_argument(
        "--replay", type=Path, help="a completed run's rounds/ directory, replayed as-is"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    responder = (
        _responder_from_replay(args.replay.resolve())
        if args.replay
        else _responder_from_command(args.responder, repo_root)
    )
    receipt = run(
        args.run_dir.resolve(),
        args.source.resolve(),
        args.source_id,
        args.content_id,
        args.updated_at,
        responder,
        repo_root,
        args.high_signal.resolve() if args.high_signal else None,
    )
    rendered = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path = args.receipt or (args.run_dir.resolve() / "run-receipt.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": receipt["status"],
                "round_count": receipt["round_count"],
                "card_count": receipt["card_count"],
                "registry_digest": receipt["registry_digest"],
                "blocked_by": receipt["blocked_by"],
                "high_signal_unmapped": receipt["high_signal_unmapped"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if receipt["status"] == "DONE" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except HarnessError as error:
        print(f"loop harness refused: {error}", file=sys.stderr)
        raise SystemExit(2) from error
