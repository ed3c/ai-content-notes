# 2026-09-01 first proof

The run that made this skill a deliverable rather than a draft: every recipe in
[`../../features/`](../../features/README.md) driven once through the real CLI,
then the skill's own cleanup, then a readback confirming these artifacts still
exist. `create-verification-skill` step 4 is the bar — a generated skill that
was never executed is a draft.

## Identity

```text
repository   ed3c/ai-content-notes
base commit  f6b6603d174cf5e424e214f3cc394890136e0dc7 (main, before this branch's commit)
branch       verify-cards
interpreter  Python 3.14.6 from .venv, requirements-contracts.txt
run root     VERIFY_RUN=/tmp/claude-501/verify-cards.2I5LGq (removed by cleanup)
```

The receipts were copied out of `$VERIFY_RUN` before cleanup, exactly as the
skill's Evidence section requires; `drive-log.txt` is written last, so its own
final listing shows the previous run's copy of itself. The `git status
--porcelain` lines near the end record the uncommitted state this branch was
in while the proof was being produced — the skill, its evidence and the test
were untracked, and `README.md` modified. Nothing else was dirty, which is the
readback behind "no drive writes into the checkout".

Every drive wrote into `$VERIFY_RUN`; nothing wrote into the checkout. The
`git status --porcelain` lines in the transcript show only the untracked skill
and test being added by this branch, which is why `--check` can be believed
when it says it wrote nothing.

## Artifacts

```text
drive-log.txt                     every command, its stdout/stderr and its exit code, in order
synthetic-run-receipt.json         compile-to-DONE, live responder, DONE in 2 rounds
sqlite-replay-run-receipt.json     compile-to-DONE, replay of the committed batch, DONE in 3 rounds
planted-unmapped-run-receipt.json  planted-signal refusal: declared DONE, admitted BLOCKED
planted-mapped-run-receipt.json    planted-signal admission: one card added, DONE
publication-guard-report.json      guard verdict over the three committed batches
```

`drive-log.txt` is deliberately not named `transcript.txt`:
`tests/test_live_cvrngaqzq3y_v7_1.py:176` bans that exact filename anywhere in
the tree, because the invariant it enforces is that no raw source transcript or
private evidence body is committed. A command log is not what that gate is
about, and the right answer is to stay out of its way rather than widen its
predicate. Future evidence directories should follow the same naming.

## What the refusals prove

Four commands in the transcript are red on purpose, and they are the half that
makes the green half mean something:

| line | command | refusal |
| --- | --- | --- |
| 109 | `publication_guard.py --root <empty tree>` | exit 2 `PROTOCOL_ABSENT` — the guard fails closed rather than reporting no findings |
| 140 | `run_loop_harness.py --replay <one round>` | exit 2 `replay has no round 2` — an exhausted replay is an absent round, not a quiet DONE |
| 150 | `run_loop_harness.py --high-signal <plant> --responder "... respond"` | exit 1 `BLOCKED`, `declared_status: DONE` vs `status: BLOCKED` |
| 173 | the same controls against the unplanted subject | exit 2 `... is not present in the source` |
| 193 | `reconcile_card_registry.py --check` after one byte changed | exit 2 `persisted registry is stale` |

`planted-unmapped-run-receipt.json` and `planted-mapped-run-receipt.json` differ
in exactly one thing: whether the responder emitted `K-unobserved-interruption`,
the one card that anchors the plant with `TEXT_MATCH::`.

## Reproducing this run

Every command is in `drive-log.txt` verbatim. To re-drive the whole skill from
the merged tree:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-contracts.txt
export VERIFY_RUN=$(mktemp -d "${TMPDIR:-/tmp}/verify-cards.XXXXXX")
# then the recipes in .cursor/skills/verify-cards/features/, in index order
```

The shortest single command that re-proves the pipeline is alive:

```sh
.venv/bin/python tools/run_loop_harness.py \
  --run-dir "$VERIFY_RUN/synthetic" \
  --source evals/runner/synthetic-loop/source.md \
  --source-id synthetic:runner-loop --content-id synthetic-loop \
  --updated-at 2026-09-01T00:00:00Z \
  --responder "python3 tests/loop_fixture.py"
```

The shape of this directory is held by `tests/test_verify_cards_skill.py`; run
it with `.venv/bin/python -m pytest -q tests/test_verify_cards_skill.py`.

## Absolute paths in these artifacts

`publication-guard-report.json`'s `root`, and the run roots quoted in the
transcript, name the throwaway clone this run happened in. They are recorded as
observed rather than rewritten: a receipt that was edited after the fact is not
a receipt. The identities that survive the clone are the `source_digest`,
`registry_digest` and `high_signal_digest` fields in the run receipts, and
`source_path` in each one is already repo-relative.
