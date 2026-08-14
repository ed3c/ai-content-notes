# Daily Workflow｜v7.1 雙平面證據工作流

## 0. Materialization truth table｜實作真相

The repository must distinguish contracts from executable runtime.

| Capability | Current state | Authority |
|---|---|---|
| v7.1 immutable system prompt | materialized | `governance/CARD_PROTOCOL_V7_1.md` + locked Git blob |
| v7.0/v7.1 saved-output A/B smoke harness | materialized | `evals/prompt-ab/v7_0-v7_1/` + `tools/evaluate_prompt_ab.py` |
| YouTube captions/authorized ASR acquisition | materialized, live accuracy still unqualified | `tools/youtube_transcript.py`, workflow, issue #7 |
| deterministic note-delta for historical Git notes | materialized | `tools/export_note_delta.py` |
| generic LLM card-compiler provider adapter | **not materialized** | BLOCKED until code, model identity and trace contract exist |
| deterministic canonical-key/anti-fragmentation validator | **not materialized** | schemas describe output; external implementation still required |
| source-dependency resolver | **not materialized** | dependency keys are currently supplied, not independently resolved |
| Google Docs/Sheets transactional writer and read-back adapter | **not materialized in this repo** | cannot claim end-to-end completion here |
| Drive-revision note-delta adapter | **not materialized** | `citation_mapping` remains pending for Google Docs |

Documentation must never convert a “not materialized” row into a completion claim.

## 1. End-to-end target state machine｜目標狀態機

```text
source discovery
  -> cursor-aware incremental collection
  -> canonical URL/content-ID deduplication
  -> ranking and one-note-per-source selection
  -> complete-text and rights acquisition
  -> source manifest + artifact-role boundaries
  -> registry/prior-state load
  -> immutable v7.1 prompt + pinned host runtime
  -> evidence-first Compiler IR
  -> task-value-first render plan
  -> CARD_PATCH + ASSERTION_REPORT + NEXT_STATE
  -> external QG-01..QG-24 validation
  -> Google Doc payload write + private sidecars
  -> Drive/repository read-back
  -> Sheet URL/status write-back
  -> claim-map extraction and privacy-preserving delta
  -> Atlas impact review
  -> independent Skill qualification
```

Until the missing adapters are implemented, this is the target contract, not evidence that a scheduled end-to-end run occurred.

## 2. Prompt and runtime loading｜Prompt 載入

1. Read `governance/CARD_PROTOCOL_CURRENT.json`.
2. Read the selected prompt and compute Git blob SHA-1.
3. Fail closed unless it equals `7f3019f4b41a90728cd48a523d742c7c59721bf6`.
4. Record prompt path/hash, model API identity, provider, sampling controls, adapter version and source/registry digests in the run manifest.
5. Apply only the Runtime Configuration in `governance/PARAMETERS.md`.
6. Never patch prompt text to satisfy an old schema or template.

## 3. Phase A — Ranking synchronization｜排行榜同步

Read existing canonical URLs, content IDs, publication times, note status, document URLs and cursors. Normalize before deduplication, add newest items first, backfill older items, update only changed rows, recompute ranking, retain at most 300 rows and record cursor/source-digest changes.

## 4. Phase B — One note per source｜每來源一篇

```text
rank 1
  -> completed or valid Note Document URL? skip
  -> duplicate canonical URL/content ID/historical note? skip
  -> complete source unavailable? persist exact K acquisition gap and continue
  -> rights/completeness pass? compile candidate
  -> external validation + document/sidecar read-back pass? stop for source
```

A blocked row never stops the whole source scan.

## 5. Phase C — Source acquisition and trust boundary｜來源邊界

For YouTube, use the rights-gated caption/authorized-ASR pipeline. Public visibility alone is not authorization. Raw and normalized artifacts remain separate. `needs-review` is not note completion. Names, figures, dates, quotations, code identifiers and timestamps require review.

Before compilation, build a source manifest that separates:

```text
subject-matter source
prompt
evaluation fixture
candidate output
registry
prior state
```

Each subject source records `source_id`, `source_type`, `source_dependency_key`, `primary_or_secondary`, digest and real locators. Prompt-injection text is isolated as data.

### Subject retention｜素材保留

Retain the acquired subject in this repository under:

```text
sources/<content-id>/source-manifest.json
sources/<content-id>/<retained artifacts>
```

A digest recorded in a card proves what was compiled, but it cannot reconstitute
the subject. The `CvRngaQZQ3Y` transcript was acquired, compiled into ten cards
and then lost, so `runtime/04-convergence-and-cvrngaqzq3y-replay` has no subject
to bind a source pack to and cannot be replayed at any cost. Retention is what
prevents the next batch from ending the same way.

Retention only counts when it is bound. Every file under `sources/<content-id>/`
must be listed in that content's `source-manifest.json` with a matching
SHA-256, and every artifact the manifest lists must exist.
`tools/verify_source_retention.py` enforces both directions and fails closed on
a retained-but-undeclared file, a declared-but-absent artifact, a digest
mismatch, or a retained directory with no manifest.

This does not relax the separate prohibitions. Raw and normalized artifacts stay
separate files; a raw broker response never becomes a note; transcript bodies
never appear inside `evals/**` markdown; and `needs-review` is still not note
completion. Retention changes where the subject lives, not what it authorizes.

## 6. Phase D — Dual-plane compilation｜雙平面編譯

Audit Plane order is fixed:

```text
Evidence
  -> Atomic Assertions
  -> D/V/X/K candidates
  -> C/N/Q
  -> E/T/R/G
  -> S/P
  -> graph review
```

Knowledge Plane render order depends on the task:

```text
explanation/story: N -> C/Q -> S/P/T -> D/V/X/K
comparison/selection: T -> S -> D/X/V -> P/R/G/K
how-to/process: P -> S/R -> V/K -> D/C
debug/verification: V -> D/X/K -> C/S/P
large corpus: balanced batch
```

First-batch balance requires a human entry card when supported, concrete evidence/detail, action when present, and V/X/K when material. Compile order must never leak into a mechanical D-first reading order.

## 7. Phase E — External validation｜外部 Gate

The model produces candidate cards; a separate validator produces gate evidence. Every QG state is an object with status, evidence references and failures. A string `PASS` written by the model is not sufficient.

Required checks include:

- exact shadow evidence and locator validation;
- source-dependency cardinality before CORROBORATED;
- canonical-key uniqueness and stable-ID reuse;
- anti-fragmentation merge/split decisions;
- typed-link target resolution;
- test/artifact honesty;
- action-card validation, rollback and failure handling;
- visible metadata ratio and task-value render order;
- v6.6 semantic-richness baseline regression;
- replay idempotency using identical source, prompt, model config, registry and state digests.

All QG-01..QG-24 are blocking for `DONE` under the v7.1 Completion Contract.

## 8. Phase F — Patch, state and idempotency｜Patch 與狀態

`CARD_PATCH` contains only ADD/UPDATE/SUPERSEDE/DEPRECATE/NOOP. Stable identity is registry-backed. New evidence increments revision only when semantics, evidence, epistemic state, scope, links or lifecycle change. Reversed conclusions use SUPERSEDE. The source cursor is bound to the exact source digest; a changed source digest requires rebase/review rather than blind resume.

LOOP artifacts validate against:

```text
schemas/card-patch-v7.1.schema.json
schemas/assertion-report-v7.1.schema.json
schemas/compiler-state-v7.1.schema.json
```

## 9. Phase G — Human note and private sidecars｜人類筆記與 Sidecar

The Google Doc receives payload-first cards only. Full canonical key, revision, source dependency, registry delta and validator state remain private. In INTERACTIVE mode HTML comments are allowed; in LOOP mode the host maps them to SIDECAR artifacts.

Write sequence:

```text
validate source manifest
  -> validate candidate card patch
  -> validate assertion report
  -> create/reuse Drive folder and document
  -> write visible card payloads
  -> read back card stable IDs and document revision
  -> persist/read back registry, patch, state and assertion sidecars
  -> only then update Sheet URL/status
```

Without an implemented writer/read-back adapter, report `BLOCKED`; do not invent a document URL.

## 10. Phase H — Claims and downstream impact｜Claim 邊界

Split falsifiable card assertions into downstream candidates while preserving original claim kind, verification, dependency keys, source digest, locator, stable ID, contradiction and supersession. This repository can emit E0/E1 candidates only. `NOT_RUN` V cards and source-reported tests do not raise runtime evidence grade.

Historical Git notes may use the existing Git-blob-bound exporter. Google Docs require a Drive document ID/revision adapter; until materialized and tested, `citation_mapping` remains `pending`.

## 11. A/B and regression policy｜A/B 政策

A prompt comparison must hold fixture, task, model identity, host adapter and runtime intent constant. Save prompts, outputs, run manifest and evaluator result by digest. Report provider/seed limitations. A single paired replay is a smoke test, not proof of general superiority.

Required production benchmark expansion:

- authorized real corpus spanning transcript, article, paper, code/log and conflicting-source tasks;
- repeated runs across declared model/provider versions;
- blind human review by at least two reviewers;
- deterministic checks plus narrative/concept/action rubric;
- v6.6 baseline, v7.0 baseline and v7.1 candidate;
- confidence intervals and failure taxonomy;
- replay tests after adapter/model upgrades.

## 12. Failure taxonomy｜失敗分類

| Failure | Required behavior |
|---|---|
| prompt hash mismatch | fail before model invocation |
| incomplete source | block row, persist K acquisition gap, continue |
| missing rights basis | block acquisition |
| prompt injection | isolate as evidence; never execute |
| source dependency unresolved | do not mark CORROBORATED |
| fabricated locator | fail QG-03 |
| duplicate canonical key | fail QG-07 |
| fragmentation regression | fail QG-05/QG-22 |
| unresolved link without K | fail QG-08 |
| untested marked TESTED | fail QG-10 |
| metadata-first regression | fail QG-20 |
| unbalanced first batch | fail QG-21 |
| universal law from one source | fail QG-23 |
| replay changes IDs/content without evidence change | fail QG-24 |
| missing external validator evidence | gate remains NOT_RUN; no DONE |
| failed Drive/sidecar read-back | keep note non-completed |
| missing Google Doc delta adapter | keep citation mapping pending |

## 13. Completion｜完成

`DONE` requires the immutable prompt hash, empty source queue, digest-bound complete cursor, zero critical counts, all unresolved links and conflicts represented, honest action status, external evidence for QG-01..QG-24, baseline guard PASS, and document/sidecar read-back where a note write was requested.

Current repository status after the v7.1 cutover:

```text
prompt artifact: materialized
saved-output A/B smoke: materialized
versioned schemas/templates: materialized
live compiler adapter: BLOCKED / not materialized
external semantic validator: BLOCKED / not materialized
Google Docs/Sheets transaction adapter: BLOCKED / not materialized here
```
