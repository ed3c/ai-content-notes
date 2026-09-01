---
name: verify-cards
description: "Drive the ai-content-notes card pipeline the way its operator does — tools/run_loop_harness.py compiling a subject to the v7.1 completion contract, tools/reconcile_card_registry.py holding a batch to idempotency, tools/publication_guard.py issuing the external verdict — and capture evidence. Use before claiming the card line works, after touching tools/, schemas/ or governance/, or when a run's DONE needs to be believed rather than reported."
---

# Verify the card pipeline

The user of this repository is an operator at a terminal compiling a retained
subject into a batch of v7.1 cards. There is no server, no UI and no port: the
surface is a set of short-lived CLI processes, each one writing into a run
directory it was handed. That shape decides everything below — "launch" means
prepare a checkout and pick a fresh run directory, and every drive is its own
process rather than a session against something already running.

Three commands are the whole surface an operator touches:

| command | what the operator is doing |
| --- | --- |
| `tools/run_loop_harness.py` | compile a subject round by round until the completion contract stops the run |
| `tools/reconcile_card_registry.py` | hold a rendered batch to one registry, and to the same bytes on a second pass |
| `tools/publication_guard.py` | ask the external gate whether a batch may ship |

Everything else in `tools/` is an acquisition or projection adapter feeding
those three, and is out of this skill's scope until the feature map says
otherwise.

## Launch

There is nothing to keep alive. Prepare the checkout once per session, then
give each drive its own run directory.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-contracts.txt
```

Use `.venv/bin/python` for every command in this skill (the drives below write
`python3` for readability; substitute the venv interpreter). `requirements-contracts.txt`
pins `jsonschema`, `pytest` and `ruff` — the harness refuses to run without
`jsonschema`, so a missing venv shows up as an import error rather than a
verdict.

Pick one run root for the whole verification run and export it:

```sh
export VERIFY_RUN=$(mktemp -d "${TMPDIR:-/tmp}/verify-cards.XXXXXX")
echo "$VERIFY_RUN"
```

Spell the template out rather than using `mktemp -t`: on macOS `-t` ignores
`TMPDIR` and lands in the Darwin user temp directory, which a sandboxed shell
often cannot write to. The failure arrives as `Operation not permitted` from a
later drive rather than from `mktemp`.

Every drive writes into a fresh subdirectory of `$VERIFY_RUN`. Never point
`--run-dir` at a committed batch under `evals/`: the harness owns its run
directory and will write cards, a registry and a receipt into it.

**Isolation:** unlimited. Each drive is a separate process writing only into
its own `--run-dir`, so two verification runs can proceed side by side as long
as they hold different `VERIFY_RUN` roots. The one shared resource is the
checkout itself, and every drive in this skill reads it without writing to it.

## Doctor

Two read-only commands, both run before the first drive and again after any
drive that surprised you. They answer "is this checkout worth driving?".

```sh
git hash-object governance/CARD_PROTOCOL_V7_1.md
python3 -c "import json;print(json.load(open('governance/CARD_PROTOCOL_CURRENT.json'))['git_blob_sha1'])"
```

Both must print `7f3019f4b41a90728cd48a523d742c7c59721bf6`. The harness stamps
that sha into every request it sends; if the two disagree, the prompt payload
moved and every round of every drive below is compiled against something other
than the pointer says.

```sh
python3 tools/publication_guard.py
```

Exit `0` with `"finding_count": 0` over the three committed batches
(`loop-batches/sqlite-testing`, `semantic-yield/CvRngaQZQ3Y`,
`semantic-yield/CvRngaQZQ3Y-v2`). This one command also proves the interpreter
resolves `jsonschema`, that `governance/CARD_PROTOCOL_V7_1.md` still states
every rule the guard implements (a renamed rule exits `2`, not `1`), and that
the tree's own batches reconcile. Exit `2` is a doctor failure — fix the
checkout, do not drive it.

## Drive

Each feature file in [`features/`](features/README.md) carries its own recipe.
The harness is driven with a **responder**: a command invoked once per round as
`CMD <request.json>`, whose stdout is the raw model response. Two responders
exist in this repository and neither one is a model:

- `python3 tests/loop_fixture.py` — the scripted LOOP agent. Reaches DONE on
  its second round against `evals/runner/synthetic-loop/source.md`.
- `.cursor/skills/verify-cards/drive_planted_signal.py respond [--anchor]` —
  the same scripted agent with the planted-control card withheld or added. See
  [Helpers](#helpers).

A third mode replaces the responder entirely: `--replay DIR` serves
`DIR/round-NN.raw.md`, the exact filenames a finished run wrote, so a committed
batch's `rounds/` directory replays byte-for-byte with no renaming step.

Handles are stable strings, not positions: subjects are named by repo-relative
path, controls by their `key`, cards by `stable_id`, and every verdict is read
out of the receipt JSON by field name rather than from console prose.

The shortest drive that proves the line is alive, start to finish:

```sh
python3 tools/run_loop_harness.py \
  --run-dir "$VERIFY_RUN/synthetic" \
  --source evals/runner/synthetic-loop/source.md \
  --source-id synthetic:runner-loop --content-id synthetic-loop \
  --updated-at 2026-09-01T00:00:00Z \
  --responder "python3 tests/loop_fixture.py"
```

Exit `0` and stdout `{"blocked_by": [], "card_count": 3, "high_signal_unmapped": [], "registry_digest": "sha256:641320142d78eb0acb6c4ae4970ada264ce855593d4932a427f0bd06ea301e34", "round_count": 2, "status": "DONE"}`.

## Evidence

Proof artifacts live at:

```text
.cursor/skills/verify-cards/evidence/<run-id>/
```

`<run-id>` is a date plus a short name (`2026-09-01-first-proof`). This
directory is committed, is never a run directory, and is never removed by
cleanup. `evals/` is not an option: `tools/publication_guard.py` treats every
`evals/*/*/cards` directory as a publication candidate, so a synthetic
verification batch parked there would be gated as if it were a product.

Each run directory holds a `README.md` (identity, artifact index, what the
refusals prove, how to reproduce), the receipts the drives wrote, and a command
log named `drive-log.txt`. Not `transcript.txt`:
`tests/test_live_cvrngaqzq3y_v7_1.py:176` bans that exact filename anywhere in
the tree, because it exists to keep raw source transcripts and private evidence
bodies out of the repository. Stay out of that gate's way rather than widening
it.

Proof standards for this pipeline:

- **Exercise the real command.** The proof is the CLI an operator types with
  its exit code, not `harness.run(...)` called from Python. `tests/` already
  proves the in-process path; a verification run exists to prove the surface.
- **Capture the action and the resulting state.** For every drive, record the
  exact command, its exit code, its stdout, and the `run-receipt.json` the run
  wrote. The receipt carries the per-round record — declared status versus
  admitted status, `registry_before_digest`/`registry_after_digest`,
  `model_authored_registry_after_digest`, `model_authored_gate_labels` — which
  is where a refusal is visible and a summary line is not.
- **Verify side effects.** A DONE claim is proven by the files the run left:
  `cards/*.md` matching `render_order`, `card-registry.json` on disk, and
  `rounds/round-NN.request.json` for every round. Copy the receipt into the
  evidence directory; leave the cards in the run directory.
- **Verify a refusal by making it happen.** A gate that has never refused
  anything is not evidence. Every drive of the planted-signal feature runs both
  directions, and the BLOCKED receipt is part of the proof, not a failed
  attempt to be retried away.
- **No mocks.** Nothing here calls an external service. The scripted responder
  is not a mock of a model: it is the compile intelligence the harness was
  designed to accept, and the harness validates its output exactly as it would
  a model's.
- **Dry-run caution.** `--replay` reads from a directory and writes to
  `--run-dir` — it is not read-only. `reconcile_card_registry.py --check`
  genuinely writes nothing; confirm with `git status --porcelain` after any
  drive that claims to be read-only.

Record the run's identity alongside the artifacts: the checkout SHA
(`git rev-parse HEAD`), the interpreter version, and the `VERIFY_RUN` root used.

## Cleanup

```sh
rm -rf "$VERIFY_RUN"
git status --porcelain
```

`rm -rf "$VERIFY_RUN"` removes only the directories this run created; nothing
is killed by name, and no process outlives a drive because every drive is a
short-lived process that already exited. `git status --porcelain` must be empty
apart from the evidence directory you deliberately added — a drive that dirtied
the checkout wrote somewhere it should not have.

Run this after every failed iteration too, so a refused drive does not leave a
half-written run directory that the next drive mistakes for prior state.

Cleanup never touches `.cursor/skills/verify-cards/evidence/`. After cleanup,
confirm the proof survived:

```sh
ls .cursor/skills/verify-cards/evidence/
```

## Helpers

`drive_planted_signal.py` is the only script this skill ships. It is executable
and lives beside this file. It authors nothing: the plant, its quote and the
card that anchors it all come from `tests/loop_fixture.py`, so the CLI drive and
`tests/test_planted_signal_falsifier.py` cannot disagree about what the control
is.

```sh
# write the planted subject and its control file into a run directory
.cursor/skills/verify-cards/drive_planted_signal.py seed --out "$VERIFY_RUN/planted"

# responder that withholds the anchoring card (harness must refuse DONE)
.cursor/skills/verify-cards/drive_planted_signal.py respond REQUEST.json

# responder that emits it (the identical run reaches DONE)
.cursor/skills/verify-cards/drive_planted_signal.py respond --anchor REQUEST.json
```

`seed` exits non-zero if `evals/runner/synthetic-loop/source.md` already
contains the planted quote: a control the subject states on its own is not a
plant, and the two drive directions would silently become one.

## Maintenance

This skill satisfies the Step-0 target shape of the pinned
`/maintain-verification-skill` (cursor/plugins `pstack/skills/maintain-verification-skill`,
pinned at `b9ddc83c`): a project-local skill whose body carries launch and drive
sections and which owns a feature map. The maintenance loop can therefore run
on it as-is, with edit scope limited to this directory —
`SKILL.md`, `features/`, `drive_planted_signal.py` and `evidence/`. Its live
pass maps onto this skill's launch model as "a fresh isolated session per
drive": a new `--run-dir` per drive, doctor before the first one and again
after any drive that surprised you.

`tests/test_verify_cards_skill.py` is the mechanical reader for that shape. It
reds when a section is dropped, a feature file loses its four H2s, the helper
loses its executable bit, or the plant drifts out of `tests/loop_fixture.py`.
