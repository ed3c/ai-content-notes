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
12. Evidence-ledger anchor resolution, verbatim exactness, orphan evidence,
    high-signal coverage disposition and source-instruction safety, all against
    the subject retained under `sources/<content-id>/`.
13. Every card and evidence id that `visual-ledger.json` names resolves inside
    this batch.

## Why the visual ledger gets its own reader

`tools/semantic_artifacts.py` reads `visual-ledger.json` for `visual_id` and
`disposition` only, so HG-03 counts the visuals and never looks at the ids each
item cites. `SV-18-high-signal-coverage` does that cross-check, but only for
`coverage-manifest.json`. The ledger therefore had no reader for its own
references, and both of its `card_ids` plus one `evidence_ids` entry named
identifiers that resolve only in `cards.fixture.md` and `evals/live/` — the
retired fixture and the transcript-only baseline this repository's AGENTS.md
explicitly says not to confuse with the modified-flow batch. They stayed wrong
across two landings because nothing was looking.

`SV-20-visual-ledger-id-integrity` applies SV-18's denominator to that file:
card ids against this batch, evidence ids against `evidence-ledger.json`. It is
deliberately not mapped to a QG gate — QG-13 already belongs to the coverage
manifest, and this is a referential-integrity reader rather than a new external
gate — but it does contribute to `failures` and `overall_status`, so a stale id
fails the report rather than being reported and ignored.

## The evidence ledger

`evals/semantic-yield/<content-id>/evidence-ledger.json` is required. Without
it the validator refuses to produce a report at all, because five of the gates
below cannot be evidenced and a silently smaller subset is the failure this
validator exists to prevent.

Its entries reuse `schemas/card-registry.schema.json#/$defs/evidenceEntry`
rather than defining a second evidence shape. Its envelope adds what the entry
shape cannot carry: per-source **anchor kind**, retained path and pinned digest.

```text
TRANSCRIPT_TIMESTAMP  locator  timestamp:HH:MM:SS..HH:MM:SS
                      resolves to a run of retained cues; the verbatim must
                      occur inside that run
ARTIFACT_STATE        locator  json-pointer:/path/into/the/artifact
                      resolves inside the named retained artifact; the verbatim
                      must equal the value at that pointer
```

That distinction is the whole reason QG-03 was previously deferred: the `K`
card's two anchors cite the source manifest and the normalization report, and
neither has a timestamp. A locator rule without a declared anchor kind cannot
tell a missing locator from a legitimate artifact anchor, so it would fail
correct cards.

The ledger is bound to bytes in three places, and a mismatch in any of them is
a FAIL rather than a skipped check:

- the declared `sha256` against the bytes actually on disk;
- the same digest against `sources/<content-id>/source-manifest.json`;
- `declared_source_id` against `card-manifest.json`'s `source.source_id`, so a
  ledger cannot be bound to a transport the cards were not compiled from.

## Current QG mapping

The validator provides automated evidence for seventeen gates:

```text
QG-01 QG-02 QG-03 QG-07 QG-08 QG-09
QG-10 QG-11 QG-12 QG-13 QG-15 QG-16
QG-17 QG-18 QG-20 QG-21 QG-23
```

Five are `HUMAN_ADMITTED_QG_IDS` in the validator, and two remain
`qg_not_run`. The three sets partition QG-01…QG-24 with no gate in two of
them — asserted once against the validator's constants
(`tests/test_semantic_yield_validator.py`), since which five gates are
human-admitted does not vary between subjects and so is not a per-report
field. The report must never be used to claim that QG-01 through QG-24 all
passed.

### What each newly automated gate actually proves

| Gate | Mechanism | Deliberately not proven |
|---|---|---|
| QG-02 Exactness | every ledger `verbatim` occurs byte-exactly at its own locator, after whitespace collapse | numbers a card states outside a quoted anchor |
| QG-03 Locator Integrity | every locator resolves in the retained bytes, and every card-side timestamp gloss equals the ledger locator | whether the anchor supports the claim it is attached to |
| QG-13 Coverage | the coverage manifest enumerates exactly the fixture's high-signal units, and every card and evidence id it names exists | whether that enumeration is complete against the source |
| QG-15 Injection Safety | source instructions detected in the retained subject must be declared in the retention manifest and must not be repeated by a card | instruction shapes the pattern set does not recognize |
| QG-17 No Orphan Evidence | every entry is cited by at least one card, and `supports` matches the citing set exactly | whether the citation is load-bearing for the claim |

`QG-15` passes vacuously on a subject containing no injection, so the negative
control plants one in a copied subject, re-pins every digest that binds it, and
requires the gate to fire anyway.

### Human-admitted judgement gates

| Gate | Why a person owns it |
|---|---|
| QG-04 Atomicity | "one primary case per card" is a semantic judgement. |
| QG-05 Anti-Fragmentation | needs a judgement about whether a split card can produce value alone. Canonical-key uniqueness is a necessary condition only, and is already covered by QG-07. |
| QG-06 Entity Fission | semantic judgement about entity identity. |
| QG-14 No Hidden Compression | semantic judgement. |
| QG-19 Insight Delta | semantic judgement about whether a card restates the source. |

`HUMAN_ADMITTED_QG_IDS` is a distinct constant from the report's `qg_not_run`
field: a gate a person owns and a gate nobody has run are different states,
and collapsing them was what made the previous report unreadable.

### Still not run

| Gate | Blocker |
|---|---|
| QG-22 Baseline Guard | needs frozen v6.6 outputs and predeclared thresholds. |
| QG-24 Idempotency | needs a re-run of the compile against the same source, which needs a model invocation — the Codex CLI lane in `ed3c/ai-content-notes#40`. |

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
