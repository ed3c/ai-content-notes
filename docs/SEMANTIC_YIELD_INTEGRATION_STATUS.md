# Semantic Yield Integration Status｜整合現況與需求 SSOT

> Status snapshot for Agents and reviewers. Read-back artifacts are authority; this document is a maintained navigation and responsibility map, not completion evidence by itself.

## 1. Current outcome｜目前產物

The modified Semantic Yield flow has been applied to exactly one content item:

```text
content_id: CvRngaQZQ3Y
source_dependency_key: youtube-video:CvRngaQZQ3Y
source: secondary auto-generated transcript
prompt: governance/CARD_PROTOCOL_V7_1.md
prompt Git blob: 7f3019f4b41a90728cd48a523d742c7c59721bf6
prompt modified: false
card directory: evals/semantic-yield/CvRngaQZQ3Y/cards/
card count: 10
state: CONTINUE
```

The complete card list is maintained in [`../evals/semantic-yield/README.md`](../evals/semantic-yield/README.md). The earlier 12-card artifact under `evals/live/CvRngaQZQ3Y/` is a retained transcript-only v7.1 baseline, not a modified-flow batch.

## 2. Integration layers｜整合分層

| Layer | Repository paths | Current state | Authority / limitation |
|---|---|---|---|
| Immutable protocol | `governance/CARD_PROTOCOL_CURRENT.json`, `governance/CARD_PROTOCOL_V7_1.md` | `MATERIALIZED` | Prompt bytes are immutable; host adapters may not patch them. |
| Acquisition | `tools/ai_video_transcriber_*`, `tools/youtube_*`, acquisition workflows | `PARTIAL` | Transcript acquisition exists; rights and platform access remain source-specific. |
| Normalization | `tools/normalize_rolling_transcript.py` | `MATERIALIZED` | Removes deterministic rolling-caption duplication; does not repair semantics or names. |
| First v7.1 batch | `evals/live/CvRngaQZQ3Y/` | `RETAINED_BASELINE` | Pre-Semantic-Yield 12-card output. |
| Semantic Yield cards | `evals/semantic-yield/CvRngaQZQ3Y/cards/` | `MATERIALIZED` | Current 10-card source-driven batch. |
| Knowledge projections | `knowledge-views.md` in the batch directory | `MATERIALIZED` | Grounded host projections, not original-slide reconstructions. |
| Deterministic validator | `tools/validate_semantic_yield_artifacts.py`, report/schema/tests | `MATERIALIZED_PARTIAL_QG` | Validates persisted artifacts, the retained subject and its evidence ledger, and 17 QGs; cannot validate the A/B baseline or a re-run compile. |
| Evidence ledger | `evals/semantic-yield/CvRngaQZQ3Y/evidence-ledger.json` | `MATERIALIZED` | 16 anchors bound to retained bytes by digest; declares anchor kind so an artifact anchor is not read as a missing locator. |
| Live provider compiler | provider-neutral invocation + raw-response receipt | `NOT_MATERIALIZED` | A prompt/model display name is not a reproducible run identity. |
| Visual evidence runtime | authorized frame/slide extraction, bbox/OCR/chart topology | `NOT_MATERIALIZED_FOR_THIS_SOURCE` | No authorized frame or creator-slide artifact exists for this run. |
| Source-dependency resolver | independent-origin graph across articles/reports/releases | `NOT_MATERIALIZED` | Current run has one explicit dependency key only. |
| Google Docs/Sheets transaction | write/read-back/CAS/rollback adapter | `NOT_MATERIALIZED` | Documented target flow is not an executed transaction pipeline. |
| Downstream Atlas/Skill admission | external repositories | `OUT_OF_SCOPE` | This repository emits review candidates only. |

## 3. Current deterministic evidence｜目前已驗證

The host validator reports:

```text
overall: PASS_WITH_DEFERRED_VISUAL_AND_PARTIAL_QG
failures: 0
HG-01: PASS
HG-02: PASS
HG-03: DEFERRED
HG-04: PASS
HG-05: PASS
HG-06: PASS
```

Automated QG subset (17 of 24):

```text
QG-01 Evidence Coverage      QG-12 Actionability
QG-02 Exactness              QG-13 Coverage
QG-03 Locator Integrity      QG-15 Injection Safety
QG-07 Stable Identity        QG-16 Version Consistency
QG-08 Typed Links            QG-17 No Orphan Evidence
QG-09 Conflict Preservation  QG-18 Narrative / Series Yield
QG-10 Test Honesty           QG-20 Reader Efficiency
QG-11 Source Independence    QG-21 Batch Balance
                             QG-23 No Absolute Overreach
```

Declared `qg_human_admitted` — judgement gates a person owns, which is a
different state from a gate nobody has run:

```text
QG-04 Atomicity   QG-05 Anti-Fragmentation   QG-06 Entity Fission
QG-14 No Hidden Compression                  QG-19 Insight Delta
```

Still `qg_not_run`: `QG-22` needs frozen v6.6 outputs and predeclared
thresholds, `QG-24` needs a model invocation to re-run the compile.

## 4. Active blockers｜尚未解除

1. **Authorized visual source** — no frame/slide artifact with rights, timestamp, digest and reviewed annotation.
2. **Identifier review** — speaker, product, model version, benchmark and acronym spellings are not all canonicalized.
3. **Remaining QG evidence** — QG-22 needs a frozen v6.6 baseline with predeclared thresholds; QG-24 needs the provider invocation lane (#40). QG-04/05/06/14/19 are human-admitted judgement, not a missing artifact.
4. **Provider/model run receipt** — no exact provider API model ID, sampling contract and raw-response digest for the original compilation.
5. **Generic compiler host** — no provider-neutral runtime that produces and persists `CARD_PATCH`, `ASSERTION_REPORT` and `NEXT_STATE` from arbitrary source packs.
6. **Transactional persistence** — Google Doc, sidecar and Sheet updates are not one verified transaction.

## 5. Required path for the next content item｜下一個內容的最低流程

```text
complete and authorized source
  -> source dependency + exact artifact digest
  -> transcript/visual modality inventory
  -> deterministic normalization only
  -> immutable v7.1 prompt + exact host/model receipt
  -> evidence/assertion/relation graph
  -> central-thesis selection
  -> source-driven card batch
  -> host projections with UNKNOWN-safe fields
  -> deterministic HG/QG validator
  -> persisted card directory + manifest + state
  -> read-back before any completion claim
```

A new batch is discoverable only after it is added under `evals/semantic-yield/<content-id>/` and linked from `evals/semantic-yield/README.md`.

## 6. State machine summary｜狀態機摘要

```text
DISCOVERED
  -> RIGHTS_AND_COMPLETENESS_REVIEW
  -> ACQUIRED
  -> NORMALIZED
  -> EVIDENCE_BOUND
  -> SEMANTIC_MODELED
  -> CARD_BATCH_RENDERED
  -> HOST_VALIDATED
  -> PERSISTED_AND_READ_BACK
  -> CONTINUE | DONE | BLOCKED | FAILED
```

Current `CvRngaQZQ3Y` state:

```text
PERSISTED_AND_READ_BACK
  -> CONTINUE
```

Reason: the card batch and deterministic validator are persisted, while visual evidence, identifier review, remaining QGs and provider/model receipt are incomplete.

## 7. Historical delivery trace｜歷史交付索引

| PR | Result | Relationship |
|---|---|---|
| #9 | v7.1 prompt lock, A/B harness and system audit | protocol/evaluator foundation |
| #11/#12 | transcript acquisition and complete first v7.1 output | pre-Semantic-Yield baseline materialization |
| #15 | regenerated 10-card Semantic Yield batch | current card output |
| #16 | deterministic Semantic Yield artifact validator | current host validation |
| #13 | open draft grounded runtime | monolithic draft; not authority for current `main` and must be decomposed before merge |

Issue #17 owns the discoverability, Agent routing, README state-machine and Git Town-compatible stacked-delivery documentation work.

## 8. Completion boundary｜完成邊界

Do not replace `CONTINUE` with `DONE` until the active v7.1 Completion Contract is met. Documentation, a green subset validator, a PR body, a status string or a host projection is never sufficient on its own.
