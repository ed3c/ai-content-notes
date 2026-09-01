# Modern Web Architecture PDF — Stage 3 Product Signal Canary

This directory is the Stage 3 canary for `#50`. It consumes the live PDF packet
from PR #53, which is now on `main` as
`0f7f551ebbca067a02621abd8a2d538189a8855b`; this Stage 3 packet merged after it
as PR #73 / `beefeb0e792a771638ad1968db126d302729256d`. Its stacked-child
framing is history; Stage 2 is read from `main`, not from a parent branch.

## State Machine

```text
STAGE2_SOURCE_INPUT_ADMITTED
→ ATOMIC_CLAIMS_BOUND
→ EVIDENCE_LINEAGE_VALIDATED
→ CONTRADICTIONS_PRESERVED
→ PRODUCT_SIGNALS_GROUPED
→ PRIVACY_AND_AUTHORITY_GATED
→ DETERMINISTIC_READ_BACK
→ HOSTED_VERIFIED | BLOCKED
```

## Data flow

```text
Stage 2 source-registry@1
+ exact PDF digest / dependency key / locators
→ claims.jsonl
→ evidence-ledger.json
→ contradictions.json
→ tools/product_signal.py
→ product-signal.json
→ exact Git blob read-back
```

## Epistemic boundary

The PDF is source evidence. Its reusable DSL/AST + constraint solver +
bidirectional canvas + deterministic-rendering pattern may be exported as a
`SOURCE_STATEMENT`. Named-company internals stay `HYPOTHESIS` or `UNKNOWN`
until independent primary or runtime evidence exists.

The canary deliberately retains the tension between the source's unconditional
"100% permissive" summary and its separate LGPL/MIT qualification for one
candidate time-stretch dependency. The compiler therefore emits a rights
validation gap instead of license PASS.

## Verification

```bash
python -m py_compile tools/product_signal.py tests/test_product_signal.py
python -m unittest -q tests/test_product_signal.py
python tools/product_signal.py \
  --claims evals/product-signal/modern-web-architecture/claims.jsonl \
  --evidence evals/product-signal/modern-web-architecture/evidence-ledger.json \
  --contradictions evals/product-signal/modern-web-architecture/contradictions.json \
  --source-registry evals/source-intake/modern-web-architecture/source-registry.json \
  --output evals/product-signal/modern-web-architecture/product-signal.json \
  --check
```

Maximum automated decision: `VALIDATE`. This packet does not establish product
internals, license truth, runtime quality, user value, paid demand, merge, or
release.
