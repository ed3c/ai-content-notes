# Citation Mapping Contract｜v7 卡片、Evidence 與 Claim Admission 契約

## Purpose｜目的

Convert complete private notes and v7 machine sidecars into atomic, source-anchored claim candidates without copying the complete note or source body into downstream public artifacts.

## Source priority｜來源優先序

```text
1. official specification
2. official documentation
3. official source code and release note
4. research paper or reproducible benchmark
5. complete first-party article/transcript
6. substantive secondary analysis
7. search result or snippet — discovery only, never evidence
```

Source priority does not replace verification. `SOURCE_STATEMENT` means the source says something; it does not mean the statement is independently true.

## v7 epistemic model｜卡片知識狀態

Every card assertion carries all three dimensions:

```text
Claim Kind:
SOURCE_STATEMENT | OBSERVATION | INFERENCE | HYPOTHESIS | NORMATIVE

Verification:
UNCHECKED | SUPPORTED | CORROBORATED | TESTED | CONTESTED | FALSIFIED

Confidence:
HIGH | MEDIUM | LOW + confidence basis
```

No percentage confidence is accepted. Exact evidence, scope, method, independence, counterevidence, and limitations determine the label.

## Downstream claim kinds｜下游 Claim 類型

The current `claim-map@1` vocabulary remains:

| Kind | Meaning | Default review |
|---|---|---|
| `fact` | One falsifiable source statement or observation | ingestion review; source statement remains scope-limited |
| `invariant` | One implementation/governance condition to preserve | policy review required |
| `inference` | One implication derived from evidence | review required |
| `assumption` | One unverified condition or hypothesis | explicit and unresolved |

### Epistemic mapping

| v7 Claim Kind | claim-map candidate | Required preservation |
|---|---|---|
| `SOURCE_STATEMENT` | `fact` | source identity, exact wording/anchor, `SUPPORTED` at most unless independently checked |
| `OBSERVATION` | `fact` | observation method, environment, fixture/artifact and scope |
| `INFERENCE` | `inference` | derivation links and falsifier |
| `HYPOTHESIS` | `assumption` | evidence needed, test plan and unblock criteria |
| `NORMATIVE` | `invariant` only after review, otherwise no claim | authority, decision use, trade-offs and policy scope; never map to fact |

A `FALSIFIED` card remains in history and produces invalidation/supersession impact rather than an active factual candidate.

## Evidence anchor contract｜Evidence ID

Every evidence item has a stable ID and exact locator:

```yaml
evidence_id: EV-<source_id>-<locator_slug>
source_id: <stable-source-id>
source_type: transcript | article | paper | code | log | issue | interview | dataset | observation
locator: page/line/timestamp/section/path/commit-or-LOCATOR_MISSING
evidence_kind: quote | datum | code | event | observation | experiment | counterexample
verbatim: <minimum necessary exact text or datum>
context: <minimum context that prevents meaning drift>
supports: [assertion_or_card_id]
challenges: [assertion_or_card_id]
```

Rules:

- Never fabricate a locator.
- One anchor may support multiple compatible assertions.
- One assertion may require multiple independent anchors.
- Repeated secondary retellings are not independent corroboration.
- Every evidence anchor is used by a card/assertion or marked pending; orphan evidence fails QG-14.
- Complete transcripts/articles are never copied into downstream manifests.

## One claim, one statement｜一個 Claim 一個陳述

A claim must be independently falsifiable and share one scope/time/version.

Bad:

```text
The gateway returns HTTP 402, has a strong moat, and should replace every provider SDK.
```

Good:

```text
claim:gateway.spend-cap-http-402
claim:gateway.policy-state-moat
claim:gateway.centralize-enforcement-strategy
```

Split when actors, versions, time ranges, evidence quality, causal branches, outcomes, or falsifiers differ.

## Required binding｜必要綁定

Every claim must bind:

```text
Note Document ID/revision or historical private note path/Git blob
source manifest ID and digest
canonical source URL/publisher/version/retrieval date
Evidence IDs and exact locators
card stable ID/canonical key/revision/lifecycle
card Claim Kind/Verification/Confidence/Confidence Basis
Domain/capability/lifecycle/principle mappings
evidence grade/freshness/license state
supersession/contradiction relations
review status
```

Canonical downstream schema remains `schemas/claim-map.schema.json`. Card registry and compiler state use `schemas/card-registry.schema.json` and `schemas/compiler-state.schema.json`.

## Card extraction map｜卡片抽取映射

| Cards | Extraction behavior |
|---|---|
| D | direct atomic evidence candidates; preserve one entity/case/scope/time and exact Shadow Evidence |
| V | verification plan or observation; `NOT_RUN` is work, not evidence; actual artifacts remain required |
| X | contradiction relation, contested state, decision impact and resolution test |
| K | explicit assumption/gap, evidence need and retrieval/test plan |
| E | invariant or inference candidate; fewer than two independent D/V supports means HYPOTHESIS |
| G | policy/invariant candidate; authority and auditability required |
| P | executable-step candidate; inputs, version, validation, rollback, failure handling and execution status required |
| S/T/R | decision/comparison/lifecycle candidates; normally inference or normative invariant |
| Q | unresolved question/experiment request; does not become fact |
| N/C | scenario/ontology context; not automatically an implementation assertion |

## Verification honesty｜V 系列邊界

```text
V Verdict = NOT_RUN
  -> no runtime evidence
  -> no TESTED verification state
  -> no Evidence Grade increase

V Verdict = PASS/FAIL/PARTIAL
  -> requires actual environment, oracle, observed result and artifact
  -> may become an observation candidate
  -> still requires downstream review for runtime Evidence Grade
```

A model-written test plan or expected result is not execution evidence.

## Conflict and supersession｜X 與歷史保留

A new claim never silently replaces an existing claim.

```text
new source/version/evidence
  -> update or create atomic card
  -> X card when claims conflict
  -> V resolution test when answerable
  -> SUPERSEDES relation when conclusion changes
  -> preserve both source anchors and historical revisions
  -> emit review-and-requalify impact
```

Unresolved conflict remains `CONTESTED`. Do not select one side merely to simplify a narrative.

## Evidence grades｜Evidence Plane

- `E0`: discovered, synthesized, hypothetical or normative; not sufficient for factual implementation assertion.
- `E1`: sufficiently complete source anchored; runtime remains unverified.
- Higher grades belong to independent reproduction, sandbox and production observation planes.
- This repository cannot self-issue E2–E5.
- Stale, superseded, invalidated, contradicted or falsified claims lose downstream eligibility until reviewed.

Card `Verification: TESTED` and downstream Evidence Grade are separate dimensions.

## Privacy boundary｜隱私邊界

Downstream manifests may include identity, path/document revision, digests, card/claim/Evidence IDs, locators, mappings and statuses. They must not include complete note bodies, complete transcripts/articles, private code, credentials, session traces or unpublished research material.

## Export sequence｜匯出順序

Historical Markdown path:

```text
note committed
  -> GitHub read-back
  -> claim-map Git blob binding
  -> schemas validate
  -> deterministic note delta
  -> Atlas review
```

Current Google Doc path:

```text
Google Doc complete
  -> Drive read-back and revision binding
  -> registry/state/assertion/source-manifest read-back
  -> Drive-aware claim-map adapter validates
  -> privacy-preserving delta
  -> Atlas review
```

Until the Drive-aware adapter is materialized and validated, Google Doc notes keep `citation_mapping: pending`; no fabricated Git blob or downstream authority is allowed.

Existing Markdown command:

```bash
python tools/export_note_delta.py \
  --note <notes/...md> \
  --claim-map <claim-maps/...json> \
  --source-commit <40-char-sha> \
  --readback-verified \
  --check \
  --output <note-delta.json>
```
