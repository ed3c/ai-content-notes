# Citation Mapping Contract｜引用與 Claim Admission 契約

## Purpose｜目的

Convert complete private notes into atomic, source-anchored claim candidates without copying the note body into downstream public artifacts.

將完整私有筆記轉成具來源錨點的 atomic claim candidate，不把筆記正文複製到下游公開產物。

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

## Claim kinds｜Claim 類型

| Kind | Meaning | Default review |
|---|---|---|
| `fact` | Source directly states a falsifiable behavior or event | eligible for ingestion review |
| `invariant` | A rule that implementation or governance must preserve | policy review required unless normative source is direct |
| `inference` | Reasoned implication from one or more facts | review required |
| `assumption` | Unverified condition needed by a design or experiment | must remain explicit and unresolved |

## One claim, one statement｜一個 Claim 一個陳述

A claim must be independently falsifiable. Do not combine unrelated product behavior, business interpretation, and implementation advice in one claim.

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

## Required binding｜必要綁定

Every claim must bind:

```text
private note id/path/Git blob SHA
canonical source URL/publisher/version/retrieval date
source anchor
card or section anchor
Domain/capability/lifecycle/principle mappings
evidence grade/freshness/license state
supersession/contradiction relations
review status
```

Canonical schema: `schemas/claim-map.schema.json`.

## Card extraction map｜卡片抽取映射

| Cards | Extraction behavior |
|---|---|
| D | direct evidence candidates; preserve exact figures, dates, identifiers, and quotations |
| E | invariant candidates; verify whether the source is normative or the note is synthesizing |
| G | policy and approval candidates; never infer runtime enforcement from prose alone |
| P | executable step candidates; require command, parameter, prerequisite, and abort boundary |
| S/T/R | decision, comparison, and lifecycle candidates; usually inference or invariant |
| Q | unresolved unknown, contradiction, or experiment question |
| N/C | scenario and ontology context; not automatically an implementation assertion |

## Evidence rules｜證據規則

- `E0`: discovered or synthesized; not sufficient for production implementation assertion.
- `E1`: complete primary or first-party source anchored; runtime still unverified.
- Higher evidence grades belong to downstream reproduction, sandbox, and production observation planes.
- This repository cannot issue E2–E5 by itself.
- A stale, superseded, invalidated, or contradicted claim becomes E6 downstream until reviewed.

## Contradiction and supersession｜矛盾與取代

A new claim never silently replaces an existing claim.

```text
new source or version
  -> create a new claim candidate
  -> add supersedes / contradicts / invalidates relation
  -> preserve both source anchors
  -> require review
  -> emit review-and-requalify impact
```

## Privacy boundary｜隱私邊界

Downstream manifests may include note identity, path, blob SHA, claim IDs, source URL, mappings, and status. They must not include the complete note body, private transcript, session trace, credentials, or unpublished research material.

## Export sequence｜匯出順序

```text
note committed to main
  -> GitHub read-back succeeds
  -> claim-map blob binding verified
  -> schemas validate
  -> deterministic note delta emitted
  -> Atlas impact review
  -> no automatic lifecycle escalation
```

Command:

```bash
python tools/export_note_delta.py \
  --note <notes/...md> \
  --claim-map <claim-maps/...json> \
  --source-commit <40-char-sha> \
  --readback-verified \
  --check \
  --output <note-delta.json>
```
