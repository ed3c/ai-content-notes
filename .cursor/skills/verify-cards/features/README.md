# Card pipeline verification map

This directory is the maintained source for verifying the user-facing behavior
of the ai-content-notes card pipeline. Read this index before driving anything,
then use the matching feature file as the recipe. A proof that drives one
convenient entry point is incomplete while this index lists others.

## Baseline preconditions

- Work from a clean checkout: `git status --porcelain` is empty before the first drive.
- Install the pinned contracts into `.venv` per the skill's Launch section and use `.venv/bin/python`.
- Export one run root for the whole run: `export VERIFY_RUN=$(mktemp -d "${TMPDIR:-/tmp}/verify-cards.XXXXXX")`.
- Give every drive its own subdirectory of `$VERIFY_RUN`; never pass a committed `evals/` batch as `--run-dir`.
- Run the two doctor commands and require blob sha `7f3019f4b41a90728cd48a523d742c7c59721bf6` and `"finding_count": 0`.
- Never drive a run directory that a previous drive left behind. Delete it, or use a new name.

## Driving conventions

- Start every recipe from the baseline state unless its preconditions say otherwise.
- Prefer stable handles: repo-relative subject paths, control `key`s, card `stable_id`s, receipt field names.
- Treat every command as literal. Keep quoted flags, ids and timestamps unchanged; `--updated-at` is stamped into the registry and changing it changes the bytes.
- Read verdicts out of `run-receipt.json` by field name, never out of console prose.
- Restore nothing: no drive in this map mutates the checkout, so cleanup is `rm -rf "$VERIFY_RUN"` and nothing else. Proof artifacts under `evidence/` are never removed.

## Proof and skip reporting

- Capture the exact command, its exit code, its stdout, and the `run-receipt.json` it wrote.
- A DONE claim needs its side effects named: the cards on disk, the registry on disk, one request file per round.
- A refusal is proof only when the refusing run is captured too. Record the BLOCKED receipt beside the DONE one.
- Record the feature ID and the entry point used with every artifact.
- Report an unreachable path with the attempted command and the unmet precondition. Never report a skipped entry point as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing the
user-visible behavior. It then uses exactly four H2 sections in this order.

1. `Sub-features` lists short IDs with one line for each behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with the card pipeline CLI` starts with `Preconditions:` and pairs each user action with an exact command and observable result.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

Keep implementation details out of the map. Name only user paths, stable
handles, required state, commands, and observable proof.

## Features

- [Compile to DONE](./compile-to-done.md) covers driving a subject round by round until the completion contract stops the run, live and by replay.
- [Planted-signal refusal](./planted-signal-refusal.md) covers both directions of the high-signal control that makes `high_signal_unmapped = 0` refutable.
- [Registry idempotency](./registry-idempotency.md) covers one canonical key to one stable id, and a second reconciliation that is byte-identical.
- [Guard verdicts](./guard-verdicts.md) covers the external publication gate: what it enforces, what it leaves prompt-enforced, and how it fails.
