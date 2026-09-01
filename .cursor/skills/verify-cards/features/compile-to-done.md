# Compile a subject to DONE

An operator hands the harness a retained subject and a compile intelligence,
and the harness runs rounds until the v7.1 section 9 completion contract stops
it. There is no round budget: `DONE` is admitted only when the batch reconciles
clean, re-reconciles byte-identically without advancing the revision, and every
id in `render_order` exists on disk. `CONTINUE`, `BLOCKED` and `FAILED` all end
the run in a receipt the operator reads instead of a console line they trust.

## Sub-features

- `loop-live` drives a subject with a responder command, one round at a time.
- `loop-replay` re-serves a finished run's `rounds/` directory with no responder at all.
- `loop-admit` withholds DONE until the mechanically checkable half of the completion contract passes.
- `loop-absent-round` refuses an exhausted replay instead of reporting a quiet DONE.

## How to get to it (user POV)

- Run `python3 tools/run_loop_harness.py --responder "<command>"` against a subject file.
- Run `python3 tools/run_loop_harness.py --replay <rounds directory>` against a batch that already finished.
- Read the run's verdict from `<run-dir>/run-receipt.json`, or from the one-line JSON the command prints.
- Read the batch itself from `<run-dir>/cards/` and `<run-dir>/card-registry.json`.

## Driving it with the card pipeline CLI

Preconditions:

- Both doctor commands pass.
- `$VERIFY_RUN` is exported and `$VERIFY_RUN/synthetic`, `$VERIFY_RUN/replay` and `$VERIFY_RUN/truncated` do not exist yet.
- The commands below run from the repository root.

- **Drive a live run to DONE.** Compile the synthetic subject with the scripted
  LOOP agent. Run:

  ```sh
  python3 tools/run_loop_harness.py \
    --run-dir "$VERIFY_RUN/synthetic" \
    --source evals/runner/synthetic-loop/source.md \
    --source-id synthetic:runner-loop --content-id synthetic-loop \
    --updated-at 2026-09-01T00:00:00Z \
    --responder "python3 tests/loop_fixture.py"
  ```

  Exit `0`. stdout is `{"blocked_by": [], "card_count": 3, "high_signal_unmapped": [], "registry_digest": "sha256:641320142d78eb0acb6c4ae4970ada264ce855593d4932a427f0bd06ea301e34", "round_count": 2, "status": "DONE"}`.

- **Confirm the side effects, not the summary.** The run must have left the
  batch on disk. Run `ls "$VERIFY_RUN/synthetic/cards"` and expect exactly
  `D-stall-check-costs-one-comparison.md`, `N-round-budget-hides-truncation.md`
  and `P-recheck-the-finished-batch.md`. Run
  `ls "$VERIFY_RUN/synthetic/rounds"` and expect a `round-01` and `round-02`
  pair of `.request.json` and `.raw.md`, one request per round actually sent.

- **Read the admitted status, not the declared one.** Run
  `python3 -c "import json;r=json.load(open('$VERIFY_RUN/synthetic/run-receipt.json'));print([(x['round'],x['declared_status'],x['status']) for x in r['rounds']], r['stopped_on'], r['gate_authority'], r['digest_authority'])"`.
  Expect `[(1, 'CONTINUE', 'CONTINUE'), (2, 'DONE', 'DONE')] completion-contract none runner`.
  `declared_status` is what the compile intelligence said; `status` is what the
  harness admitted. A proof that reads only the second field cannot tell the
  two apart when they diverge.

- **Replay a finished production batch.** The committed sqlite-testing batch
  replays from its own `rounds/` directory. Run:

  ```sh
  python3 tools/run_loop_harness.py \
    --run-dir "$VERIFY_RUN/replay" \
    --source sources/sqlite-testing/article.txt \
    --source-id article:sqlite.org-testing --content-id sqlite-testing \
    --updated-at 2026-08-31T17:29:21Z \
    --high-signal evals/loop-batches/sqlite-testing/high-signal.json \
    --replay evals/loop-batches/sqlite-testing/rounds
  ```

  Exit `0`. stdout is `{"blocked_by": [], "card_count": 10, "high_signal_unmapped": [], "registry_digest": "sha256:ec3f4cf0bea3fcafb98e305b7a4b71886864a939ec63c76457e4847d7361db4c", "round_count": 3, "status": "DONE"}`.
  That `registry_digest` equals the one in
  `evals/loop-batches/sqlite-testing/run-receipt.json`, which is the readback:
  the committed batch is reproducible from its own captured rounds.

- **Prove an exhausted replay refuses.** A replay that runs out of rounds must
  refuse, not report DONE. Build a truncated copy and drive it:

  ```sh
  mkdir -p "$VERIFY_RUN/truncated-rounds"
  cp "$VERIFY_RUN/synthetic/rounds/round-01.raw.md" "$VERIFY_RUN/truncated-rounds/"
  python3 tools/run_loop_harness.py \
    --run-dir "$VERIFY_RUN/truncated" \
    --source evals/runner/synthetic-loop/source.md \
    --source-id synthetic:runner-loop --content-id synthetic-loop \
    --updated-at 2026-09-01T00:00:00Z \
    --replay "$VERIFY_RUN/truncated-rounds"
  ```

  Exit `2`, stderr `loop harness refused: replay has no round 2: <path>/round-02.raw.md`.
  A DONE from the first drive means nothing unless this one is red.

- **Proof.** Copy `$VERIFY_RUN/synthetic/run-receipt.json` and
  `$VERIFY_RUN/replay/run-receipt.json` into the evidence directory, together
  with the four commands, their exit codes and their stdout/stderr.

## Gotchas

- `--updated-at` is stamped into the registry, so a different timestamp changes `registry_digest` and the expected stdout above stops matching. It is not a free parameter.
- Exit `1` means the run ended in a non-DONE terminal state (`BLOCKED`/`FAILED`); exit `2` means the harness refused a round it could not trust. Treating both as "failed" loses the distinction the harness exists to draw.
- `--replay` writes: it produces a full run directory. It is not a read-only inspection of the batch being replayed.
- The one-line stdout omits `rounds`, `model_authored_gate_labels` and `model_authored_registry_after_digest`. Those live only in `run-receipt.json`; a proof built from stdout alone cannot show that a model's digest claim was ignored.
- Do not reuse a run directory. The harness reads an existing `card-registry.json` as prior state, so a leftover directory silently makes the next drive a different run.
- The stall detector (a `CONTINUE` that advances neither registry nor cursor ends the run `FAILED`) has no CLI responder in this repository; it is exercised in `tests/test_loop_harness.py`. Do not report it as verified through the recipes above.
