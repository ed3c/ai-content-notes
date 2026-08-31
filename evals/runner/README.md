# LOOP harness fixtures｜迴圈 harness 素材

`tools/run_loop_harness.py` drives a `RUN_MODE: LOOP` compilation to the
section 9 completion contract. This directory holds the subjects it is driven
against in tests. It holds no card batch: run output (cards, registry, captured
rounds, receipt) is written to a caller-supplied `--run-dir`, never here, so
`tools/publication_guard.py` never sees a synthetic batch as a publication
candidate.

```text
synthetic-loop/source.md    a synthetic subject written for this repository:
                            no third-party rights, no acquisition provenance,
                            and not evidence about anything outside itself
```

The scripted LOOP agent that compiles it lives with the tests
(`tests/loop_fixture.py`) because it is a stand-in for the compile
intelligence, not a repository adapter. `tests/test_loop_harness.py` is the
acceptance receipt: a synthetic-source run reaching DONE with every round
schema-valid and the registry idempotent on re-run.

Two authorities the harness refuses, both named in every receipt:

- `gate_authority: "none"` — QG-01..QG-24 labels inside a response are model
  claims, quarantined exactly as `tools/parse_compiler_channels.py` leaves
  them. `tools/publication_guard.py` remains the external gate.
- `digest_authority: "runner"` — a model cannot compute SHA-256, so its
  `registry_after_digest` is recorded as a claim while the digest that chains
  into the next round is the one `tools/reconcile_card_registry.py` produced.
