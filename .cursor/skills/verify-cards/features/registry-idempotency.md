# Registry idempotency

An operator reconciles a directory of rendered cards into one registry, and
expects the same bytes back on a second pass over unchanged inputs. That is
QG-24, and it is what makes a `DONE` mean the batch stopped changing rather
than the run stopped paying. `--check` is the operator-facing form: it verifies
the persisted registry against a fresh reconciliation and writes nothing.

## Sub-features

- `reconcile-write` produces `card-registry.json` from a card directory and a prior registry.
- `reconcile-check` verifies a persisted registry byte-for-byte and refuses a stale one.
- `reconcile-revision` leaves `registry_revision` unchanged when nothing about the batch changed.
- `reconcile-gap` reports a card short of the registry contract as a gap and writes no registry.

## How to get to it (user POV)

- Run `python3 tools/reconcile_card_registry.py --cards <dir> --source-id <id> --source-digest <sha> --updated-at <ts> --prior <registry> --output <registry> --check`.
- Drop `--check` to write the registry instead of verifying it.
- Read `card_count`, `registry_revision` and `gap_count` from the printed JSON.
- The harness performs the same reconciliation on the operator's behalf every round; `--check` is how the operator asks the question themselves.

## Driving it with the card pipeline CLI

Preconditions:

- Both doctor commands pass.
- `$VERIFY_RUN/synthetic` exists from the compile-to-DONE drive, DONE and untouched since.
- The commands below run from the repository root.

- **Check a committed production batch.** The sqlite-testing registry must
  verify against its own cards. Run:

  ```sh
  python3 tools/reconcile_card_registry.py \
    --cards evals/loop-batches/sqlite-testing/cards \
    --source-id article:sqlite.org-testing \
    --source-digest sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24 \
    --updated-at 2026-08-31T17:29:21Z \
    --prior evals/loop-batches/sqlite-testing/card-registry.json \
    --output evals/loop-batches/sqlite-testing/card-registry.json \
    --check
  ```

  Exit `0`, stdout `{"card_count": 10, "gap_count": 0, "registry_revision": 3}`.
  The `--source-digest` is the one in that batch's `run-receipt.json`; a
  different digest is a different question.

- **Confirm `--check` wrote nothing.** Run `git status --porcelain`. It must be
  empty. `--check` names an `--output` path it does not write to; the only way
  to know that is to look at the tree afterwards.

- **Check the run you just drove.** Run the same command shape against
  `$VERIFY_RUN/synthetic`, with `--source-id synthetic:runner-loop`,
  `--source-digest sha256:3f181200dced1cc1a898acae23d71f60ae59ebbe7e003f8eb78cec669b996d55`,
  `--updated-at 2026-09-01T00:00:00Z`, and both `--prior` and `--output`
  pointing at `$VERIFY_RUN/synthetic/card-registry.json`. Exit `0`, stdout
  `{"card_count": 3, "gap_count": 0, "registry_revision": 2}`. The revision did
  not advance: reconciling an unchanged batch a second time is a NOOP replay,
  not a new revision.

- **Prove the check refuses a drifted batch.** Change one card and ask again:

  ```sh
  printf '\n<!-- drift -->\n' >> "$VERIFY_RUN/synthetic/cards/N-round-budget-hides-truncation.md"
  ```

  Rerun the previous command unchanged. Exit `2`, stderr
  `registry reconciliation refused: persisted registry is stale`. Revision is
  content-addressed, so a byte added to a card is a different registry. Without
  this drive the green check above is a check that has never said no.

- **Proof.** Record all four commands with exit codes and stdout/stderr. The
  drifted-batch refusal belongs in the evidence beside the green checks.

## Gotchas

- `--check` needs a persisted `--output` file: without it the command refuses with `--check needs a persisted --output registry` (exit `2`), which is a usage error, not a verdict about the batch.
- `--updated-at` and `--source-digest` are inputs to the rendered bytes. Guessing either one turns a real idempotency check into a mismatch that looks like drift.
- A batch that ships `card-registry-gap-report.json` instead of a registry is in a recorded-gap state; `--check` then needs `--gap-report` and verifies that the gap has not moved. Passing `--output` at such a batch asks the wrong question.
- Outside `--check`, a standing gap exits `1` and writes no registry. Do not read exit `1` here as "the tool crashed".
- The drift drive leaves `$VERIFY_RUN/synthetic` unusable for any later drive. Do it last, or drive a fresh run directory afterwards.
- `git status --porcelain` after the drift drive must still be empty: the drift went into `$VERIFY_RUN`, never into the checkout. If it is not empty, a command was pointed at the wrong tree.
