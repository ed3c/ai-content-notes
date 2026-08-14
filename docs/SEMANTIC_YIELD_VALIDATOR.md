# Semantic Yield Artifact Validator

`tools/validate_semantic_yield_artifacts.py` is a deterministic host-side validator for persisted v7.1 card batches. It is separate from the model that generated the cards.

## Scope

The validator currently checks:

1. Git blob bindings for the immutable prompt and every card.
2. Semantic stable IDs, canonical keys and exact typed-link resolution.
3. Payload-first rendering with `核心命題` and `為什麼重要`.
4. One-source dependency honesty, no false `CORROBORATED`, `UNTESTED` Practice status and non-DONE state.
5. Coverage of causal flow, fit equation, intervention sequence, state planes and comparison matrix.
6. Explicit deferral of original-slide reconstruction when authorized visual evidence is absent.
7. UNKNOWN-safe comparison values and rejection of unsupported dollar, score and fixed-volume precision.
8. Practice rollback, failure handling, privacy constraints and toolset fields.
9. Cross-card core-proposition redundancy.
10. Source-shaped first-batch coverage rather than a fixed series counter.
11. Series-specific payload fields and no absolute overreach.

## Current QG mapping

The validator provides automated evidence for:

```text
QG-07 QG-08 QG-10 QG-11 QG-12
QG-16 QG-18 QG-20 QG-21 QG-23
```

All other QG states remain `NOT_RUN` for this validator. The report must never be used to claim that QG-01 through QG-24 all passed.

## Visual boundary

`HG-03` is `DEFERRED` when there is no authorized frame or creator-slide artifact. A host-generated Mermaid graph or comparison table is a relation projection, not evidence of the original slide layout, text, axis, legend or values.

## Reproduce

```bash
python tools/validate_semantic_yield_artifacts.py \
  --target evals/semantic-yield/CvRngaQZQ3Y \
  --output evals/semantic-yield/CvRngaQZQ3Y/semantic-validator-report.json \
  --created-at 2026-08-14T01:15:00Z \
  --check
```

The persisted report is schema-validated by:

```text
schemas/semantic-validator-report.schema.json
```

Tampered stable IDs, unresolved links, stale Git blob hashes, missing v7.1 payload fields and unsupported precision fail closed.
