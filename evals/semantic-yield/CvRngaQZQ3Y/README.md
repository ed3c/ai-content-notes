# CvRngaQZQ3Y｜v7.1 Semantic Yield Regeneration

This directory contains a second card compilation of the same normalized transcript, using the modified host-side process while leaving the immutable v7.1 prompt unchanged.

## What changed

```text
Transcript evidence
  -> relation graph
  -> central-thesis ranking
  -> equation / dataflow / state-plane / comparison projections
  -> source-driven batch selection
  -> epistemic and visual-gap review
  -> deterministic host validation
  -> 10-card output
```

The central entry changed from a procedural loop to the higher-causal-reach thesis:

```text
Agent autonomy increases
  -> static predictability decreases
  -> runtime traces become primary evidence
  -> trace mining becomes the improvement substrate
```

## Card order

1. [N-autonomy-trace-mining](cards/N-autonomy-trace-mining.md)
2. [C-model-harness-task-fit](cards/C-model-harness-task-fit.md)
3. [S-harness-finetune-harness](cards/S-harness-finetune-harness.md)
4. [T-trace-judge-comparison](cards/T-trace-judge-comparison.md)
5. [P-trace-driven-improvement-cycle](cards/P-trace-driven-improvement-cycle.md)
6. [D-trace-scale-bottleneck](cards/D-trace-scale-bottleneck.md)
7. [D-four-stage-trace-loop](cards/D-four-stage-trace-loop.md)
8. [C-continual-learning-state-planes](cards/C-continual-learning-state-planes.md)
9. [V-semantic-yield-replay](cards/V-semantic-yield-replay.md)
10. [K-visual-identifier-evidence-gap](cards/K-visual-identifier-evidence-gap.md)

## Derived views, validation and state

- [Knowledge Views](knowledge-views.md)
- [Card manifest](card-manifest.json)
- [Evidence ledger](evidence-ledger.json)
- [Deterministic semantic validator report](semantic-validator-report.json)
- [Semantic Yield result](semantic-yield.result.json)
- [Run state](run-state.md)

## Validator result

```text
validator: semantic-yield-validator@1
overall: PASS_WITH_DEFERRED_VISUAL_AND_PARTIAL_QG
deterministic checks: 16 PASS + 1 DEFERRED
HG-01: PASS
HG-02: PASS
HG-03: DEFERRED
HG-04: PASS
HG-05: PASS
HG-06: PASS
```

The validator runs independently from the model that produced the cards. It verifies Git blob bindings, semantic stable IDs, exact typed links, payload-first rendering, epistemic honesty, UNKNOWN-safe precision, action fields, cross-card redundancy, source-shaped batch coverage and series payload contracts.

The following v7.1 Quality Gates are currently supported by deterministic evidence:

```text
QG-01  Evidence Coverage      QG-12  Actionability
QG-02  Exactness              QG-13  Coverage
QG-03  Locator Integrity      QG-15  Injection Safety
QG-07  Stable Identity        QG-16  Version Consistency
QG-08  Typed Links            QG-17  No Orphan Evidence
QG-09  Conflict Preservation  QG-18  Narrative / Series Yield
QG-10  Test Honesty           QG-20  Reader Efficiency
QG-11  Source Independence    QG-21  Batch Balance
                              QG-23  No Absolute Overreach
```

`QG-02`, `QG-03`, `QG-13`, `QG-15` and `QG-17` are evidenced against
[`evidence-ledger.json`](evidence-ledger.json) and the subject retained under
`sources/CvRngaQZQ3Y/`. `QG-04`, `QG-05`, `QG-06`, `QG-14` and `QG-19` are
`HUMAN_ADMITTED_QG_IDS` in the validator - a fixed property of those five
gates, not a per-report field; `QG-22` and `QG-24` remain `qg_not_run`.

This is a partial external-QG implementation. It does not turn the remaining QG states into PASS.

## Reproduce the validator

```bash
python tools/validate_semantic_yield_artifacts.py \
  --target evals/semantic-yield/CvRngaQZQ3Y \
  --output evals/semantic-yield/CvRngaQZQ3Y/semantic-validator-report.json \
  --created-at 2026-08-14T01:15:00Z \
  --check
```

## Regenerate the evidence ledger

`evidence-ledger.json` is generated, not hand-edited. Its 16 entries are
re-derived from `sources/CvRngaQZQ3Y/` on every run and every field is
asserted against retained bytes before the file is written.

```bash
python tools/materialize_evidence_ledger.py --check   # verify only, exit 1 on drift
python tools/materialize_evidence_ledger.py            # regenerate after a
                                                          # table entry or a
                                                          # retained source changes
```

## Contract

```text
prompt: governance/CARD_PROTOCOL_V7_1.md
prompt Git blob: 7f3019f4b41a90728cd48a523d742c7c59721bf6
prompt modified: false
source dependency: youtube-video:CvRngaQZQ3Y
source type: secondary auto-generated transcript
card count: 10
status: CONTINUE
```

## Honesty boundary

- No claim is marked `CORROBORATED`.
- The Practice card remains `UNTESTED`.
- The Verification card is `PARTIAL`, not a completed production experiment.
- Unknown benchmark values and model revisions remain `UNKNOWN`.
- Diagrams are host-side relation projections, not reconstructed source slides.
- Original visual evidence remains deferred until an authorized frame or creator-slide artifact is available.
- The deterministic validator verifies persisted artifacts, not source-video visual fidelity.
- QG-01 through QG-24 are not all complete.
