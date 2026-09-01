# Planted-signal refusal

Section 9 lets a run declare DONE when `high_signal_unmapped = 0`, and that
number would otherwise come from the run that wants to be finished. `--high-signal`
lets an operator hand the harness a list of `{key, quote}` controls before the
compile starts; DONE stays unreachable until some card anchors each quote with
the protocol's own `TEXT_MATCH::` locator. The user-visible behavior is a
refusal an operator can cause on purpose and watch happen.

## Sub-features

- `plant-seed` writes a subject carrying one known high-signal item, and the control file naming it.
- `plant-unmapped` drives that subject with the anchoring card withheld: the run must end BLOCKED naming the control key.
- `plant-mapped` drives the identical run with the anchoring card added: the run must reach DONE.
- `plant-outside-subject` refuses a control whose quote is not an exact substring of the subject.

## How to get to it (user POV)

- Pass `--high-signal <controls.json>` to `python3 tools/run_loop_harness.py` alongside any responder or replay.
- Read `high_signal_unmapped` and `blocked_by` from the printed one-line JSON, or from `<run-dir>/run-receipt.json`.
- Read `high_signal_control`, `high_signal_declared` and `high_signal_digest` from the receipt to see which control file was actually checked.
- Run `.cursor/skills/verify-cards/drive_planted_signal.py seed --out <dir>` to produce a plantable subject without hand-editing one.

## Driving it with the card pipeline CLI

Preconditions:

- Both doctor commands pass.
- `$VERIFY_RUN` is exported and `$VERIFY_RUN/planted` does not exist yet.
- The commands below run from the repository root.

- **Seed the plant.** Write the planted subject and its control file. Run
  `.cursor/skills/verify-cards/drive_planted_signal.py seed --out "$VERIFY_RUN/planted"`.
  Exit `0`, stdout names `planted-source.md`, `high-signal.json` and the key
  `planted-unobserved-interruption`. The command refuses if the plant is already
  in `evals/runner/synthetic-loop/source.md`, because a control the subject
  states on its own is not a control.

- **Drive the refusal.** Compile the planted subject with the anchoring card
  withheld. Run:

  ```sh
  python3 tools/run_loop_harness.py \
    --run-dir "$VERIFY_RUN/planted/unmapped" \
    --source "$VERIFY_RUN/planted/planted-source.md" \
    --source-id synthetic:runner-loop --content-id synthetic-loop \
    --updated-at 2026-09-01T00:00:00Z \
    --high-signal "$VERIFY_RUN/planted/high-signal.json" \
    --responder ".cursor/skills/verify-cards/drive_planted_signal.py respond"
  ```

  Exit `1`. stdout is `{"blocked_by": ["high_signal_unmapped: planted-unobserved-interruption"], "card_count": 3, "high_signal_unmapped": ["planted-unobserved-interruption"], "registry_digest": "sha256:9f65486cdd20a4821ec050fc955c4a12e4087a003113d1506beb36e0a49da4e2", "round_count": 2, "status": "BLOCKED"}`.
  The compile intelligence declared `DONE` on round 2; the harness admitted
  `BLOCKED`. Confirm with
  `python3 -c "import json;r=json.load(open('$VERIFY_RUN/planted/unmapped/run-receipt.json'));print(r['rounds'][-1]['declared_status'], r['rounds'][-1]['status'])"`,
  which prints `DONE BLOCKED`.

- **Drive the admission.** Change exactly one thing — the card that anchors the
  plant — and rerun. Run the same command with `--run-dir "$VERIFY_RUN/planted/mapped"`
  and `--responder ".cursor/skills/verify-cards/drive_planted_signal.py respond --anchor"`.
  Exit `0`. stdout is `{"blocked_by": [], "card_count": 4, "high_signal_unmapped": [], "registry_digest": "sha256:9b69a7e8498b5a3cfd10f94b01a407365cff313267bbdcf43a019136dbca8a05", "round_count": 2, "status": "DONE"}`.
  The fourth card is `K-unobserved-interruption`; confirm with
  `ls "$VERIFY_RUN/planted/mapped/cards"`.

- **Prove the control file is bound to the receipt.** Run
  `python3 -c "import json;r=json.load(open('$VERIFY_RUN/planted/mapped/run-receipt.json'));print(r['high_signal_control'], r['high_signal_declared'], r['high_signal_digest'])"`.
  Expect `PRESENT 1 sha256:...`. The digest binds the receipt to the exact
  controls file checked, so a control file edited after the run (unmapped keys
  deleted) no longer matches its own receipt.

- **Prove a control outside the subject is refused, not failed.** Run the
  refusal drive again but against the unplanted subject
  (`--source evals/runner/synthetic-loop/source.md`, a new `--run-dir`, the same
  `--high-signal`). Exit `2`, stderr
  `loop harness refused: high-signal control planted-unobserved-interruption is not present in the source`.
  A control that is not in the subject would fail forever and prove nothing
  about coverage, so the harness refuses it up front rather than reporting an
  unmapped key.

- **Proof.** Copy both `run-receipt.json` files into the evidence directory. The
  BLOCKED one is half the proof: a control that has never refused anything is
  not a control.

## Gotchas

- The refusal drive exits `1`, not `0`. A verification script that stops on the first non-zero exit will report the refusal as a broken run.
- The two drives must differ in exactly one thing. Different `--run-dir`, `--source-id`, `--updated-at` or subject file between them means the comparison proves nothing.
- Never point both drives at the same `--run-dir`. The second would read the first's registry as prior state, and the cards from the refused run would still be on disk.
- `high_signal_unmapped: []` on a run started without `--high-signal` means "no controls were declared", not "coverage is complete". Check `high_signal_control` first; it reads `ABSENT` in that case.
- The controls for the committed sqlite-testing batch were authored in the same pass as its cards, so that batch exercises the mechanism rather than independently proving coverage. `evals/loop-batches/README.md` says so; do not upgrade it in a report.
- The equivalent in-process proof is `tests/test_planted_signal_falsifier.py`. It is not a substitute for this drive: it never runs the CLI, which is the thing the operator uses.
