# v7.1 Prompt A/B Test and Prompt-External System Audit

Date: 2026-08-13 (Asia/Taipei)  
Repository: `ed3c/ai-content-notes`  
Branch: `agent/v7-1-prompt-ab-harness`

## 1. Change under test

The B prompt is the user-supplied `CARD_PROTOCOL_V7_1.md`, stored verbatim and locked to Git blob SHA-1:

```text
7f3019f4b41a90728cd48a523d742c7c59721bf6
```

The prompt is not edited by templates, schemas, tests or adapters. `CARD_PROTOCOL_CURRENT.json` selects it. A uses the retained v7.0 prompt. Prompt text and candidate output are evaluation artifacts, not subject-matter evidence.

## 2. A/B method

Controlled inputs:

- one fixed synthetic transcript fixture;
- identical task and runtime intent;
- external knowledge disabled;
- tool execution disabled;
- maximum 12 cards;
- same model session and one reviewer;
- saved outputs evaluated by a deterministic, standard-library-only script.

The fixture deliberately tests:

- exact figures and identifiers (`12 分鐘`, `84 張卡`, `CASE-FRAG-001`, `E_CARD_SPLIT`, `17 張卡`, `3 段訪談`, `41%`);
- one source-dependency origin repeated by two speakers;
- a source-reported test with no command artifact;
- an explicit command and required LOOP channels;
- a prompt-injection string;
- a missing locator;
- a same-event fragmentation case.

Artifacts:

```text
evals/prompt-ab/v7_0-v7_1/fixture.json
evals/prompt-ab/v7_0-v7_1/output-a-v7.0.md
evals/prompt-ab/v7_0-v7_1/output-b-v7.1.md
evals/prompt-ab/v7_0-v7_1/run.json
evals/prompt-ab/v7_0-v7_1/result.json
tools/evaluate_prompt_ab.py
```

## 3. Deterministic result

| Check | A: v7.0 | B: v7.1 | Interpretation |
|---|---:|---:|---|
| Exact Shadow Evidence recall | 100% | 100% | No gain on fidelity in this fixture |
| Fabricated timestamp | 0 | 0 | Tie |
| Test honesty | PASS | PASS | Both keep source-reported testing non-TESTED |
| Source-independence rule | PASS | PASS | Neither marks one dependency key CORROBORATED |
| Dependency key visible/auditable | FAIL | PASS | v7.1 makes origin dependence inspectable |
| Typed-link integrity | PASS | PASS | Tie |
| First card | D | N | v7.1 begins with a human entry card |
| Payload-first | FAIL | PASS | v7.1 separates visible payload from Audit metadata |
| Visible administrative metadata ratio | 39.3% | 0.0% | v7.0 template exceeds the 25% reader-load ceiling |
| Balanced first batch | FAIL | PASS | v7.1 contains N/C/P/V/D/K rather than bookkeeping-only entry |
| Deterministic score | **60/100** | **100/100** | B +40 on this smoke fixture |

Human rubric mean: A `3.714/5`, B `4.857/5`. The multiplicative five-factor score is A `0.1152`, B `1.0`; this value is reviewer judgment, not a calibrated benchmark statistic.

## 4. What the result does and does not show

Supported on this fixture:

1. v7.1 fixes the visible compile-order leak: evidence still compiles first, but the reader sees Narrative/Concept/Action before low-level bookkeeping.
2. v7.1 reduces visible metadata load by moving canonical registry fields to a sidecar.
3. v7.1 makes source dependency provenance explicit.
4. v7.1 produces a balanced first batch without sacrificing exact figures or test honesty.

Not established:

- general reduction of fragmentation across a real corpus;
- statistical superiority across models, providers or sampling conditions;
- live runtime wiring;
- provider reproducibility, because model API identifier, seed and token trace are unavailable;
- independent human-review agreement;
- production Google Docs/Sheets completion.

The A/B result is a regression smoke test. It must not be upgraded into a universal claim.

## 5. Prompt-external defects and bottlenecks

### P0 — No executable card compiler/model adapter

The repository had a detailed workflow but no code that loads the canonical prompt, invokes a model, captures exact model/provider/sampling identity, parses LOOP channels and persists a card patch. Replacing a Markdown prompt alone therefore could not change a scheduled runtime reliably.

Required fix: implement a provider-neutral adapter with prompt/model/config digests, timeout/retry policy, output-channel parser and preserved raw response artifact.

### P0 — v7.0 template/schema can override v7.1 behavior

The existing unversioned note template forces the full Common Header on every card; the existing compiler-state schema fixes protocol v7.0 and QG-01..QG-14. A host following those files would turn v7.1 back into metadata-first output or reject its state.

Applied fix: versioned v7.1 template and state/patch/report schemas. Operational entrypoints now select them without editing the prompt.

### P0 — Quality Gates are self-reported, not externally evidenced

The old compiler-state schema stored `PASS | FAIL | NOT_RUN` strings. A model could write PASS without an artifact, and DONE could validate structurally.

Applied contract fix: every v7.1 gate includes status, evidence references and failures; PASS requires at least one evidence reference. Remaining work: implement the independent validator that emits those references.

### P0 — Missing generic manifest, patch and assertion contracts

Only a YouTube transcript manifest was materialized. Generic source boundaries, candidate-output boundaries, source dependencies, card-patch operations and assertion evidence had no enforceable schema.

Applied fix: `source-manifest.schema.json`, `card-patch-v7.1.schema.json` and `assertion-report-v7.1.schema.json`.

### P0 — No deterministic canonical-key implementation

“Deterministic semantic slug” is a prompt instruction, not an algorithm. Different model runs can normalize entities, scope or object phrases differently, creating identity drift even when the source is unchanged.

Required fix: host-side canonicalization with normalized entity IDs, predicate vocabulary, version/scope normalization, collision detection and registry reconciliation. The model may propose keys; it must not be the sole authority.

### P1 — Source dependency is supplied, not resolved

A `source_dependency_key` field makes dependence visible but does not prove two URLs have independent origins. Syndication, copied reports and company reposts need a resolver and human override path.

Required fix: provenance graph from canonical origin IDs, citation chains, publisher/release identity and explicit override evidence.

### P1 — `TEXT_MATCH` uniqueness is not externally verified

The prompt allows the shortest unique text match, but no host validator checks uniqueness against the exact source digest. A repeated phrase can resolve to multiple spans.

Required fix: locator resolver returns source digest, normalized match, occurrence count and byte/character span; occurrence count must equal one.

### P1 — Cursor was not source-digest-bound

A paragraph/item cursor without source digest can skip or duplicate content when captions or an article change between batches.

Applied contract fix: v7.1 compiler state binds cursor to `source_digest`. Remaining work: rebase policy and mutation tests.

### P1 — Google Docs/Sheets transaction adapter is absent

The workflow describes create/write/read-back/Sheet write-back, but no implementation exists in this repository. The historical delta exporter binds Git blobs only, and the workflow itself acknowledges that Google Docs need a Drive-revision adapter.

Required fix: idempotency key, document revision precondition, append/write receipt, sidecar commit receipt, compensating rollback and final Sheet compare-and-set.

### P1 — No live multi-run A/B harness

The current evaluator compares saved outputs. There is no provider adapter, seed capture, repeated runs, blind reviewers, confidence intervals or cross-domain corpus.

Required fix: authorized benchmark corpus covering transcript, article, paper, code/log, multi-source conflict and action tasks; repeated model runs; two independent reviewers; deterministic and semantic scores.

### P1 — v6.6 Baseline Guard has no executable benchmark

`BASELINE_GUARD: V6_6_SEMANTIC_RICHNESS` names a policy but lacks fixed v6.6 outputs, dimensions, thresholds and adjudication.

Required fix: freeze representative v6.6 notes/outputs, define narrative/concept/action/reader-flow thresholds and fail upgrades that regress beyond the predeclared margin.

### P2 — Version references drift across docs, tests and issues

Operational files previously pointed to v7.0; issue #7 still mentions v6.6 note generation. Version drift can silently route agents to the wrong contract.

Applied partial fix: README, integration entrypoints, parameters, workflow, agent contracts and index now select v7.1. Remaining fix: audit all historical docs/issues and label legacy references explicitly rather than rewriting provenance.

### P2 — Sidecar terminology is ambiguous across modes

The prompt says `METADATA_MODE: COMPACT_WITH_HTML_SIDECAR`, while scheduled LOOP uses `STATE_CHANNEL: SIDECAR`. The prompt need not change: the host must map HTML-sidecar presentation fields into the private SIDECAR artifact in LOOP mode.

Applied fix: this mapping is explicit in parameters, workflow and v7.1 note template.

### P2 — “Hard Gate” classification is undefined

The prompt says any Hard Gate failure blocks DONE but does not enumerate a hard subset; the Completion Contract separately requires all gates PASS.

Host interpretation: treat all QG-01..QG-24 as blocking until an explicit, versioned gate policy exists. This avoids weakening the immutable prompt.

## 6. Remediation order

1. **Lock and route prompt** — completed in this change.
2. **Version host contracts** — completed in this change.
3. **External deterministic validator** — next P0 implementation.
4. **Provider-neutral live compiler adapter** — next P0 implementation.
5. **Canonical-key and dependency resolvers** — P0/P1.
6. **Google Docs/Sheets transactional adapter** — P1.
7. **Authorized repeated corpus benchmark and v6.6 baseline** — P1.
8. **Version-drift audit and legacy labeling** — P2.

## 7. Current honest status

```text
v7.1 prompt stored and locked: DONE
operational pointers switched on branch: DONE
saved A/B smoke artifacts: DONE
deterministic evaluator and regression check: DONE
v7.1 host schemas/templates: DONE
live model A/B execution: NOT_RUN (adapter unavailable)
production card compiler wiring: BLOCKED
external semantic gate validator: BLOCKED
Google Docs/Sheets transactional completion: BLOCKED in this repository
```
