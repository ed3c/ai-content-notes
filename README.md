# AI Content Notes｜AI 高價值內容筆記與證據庫

> A private evidence plane that turns complete AI source material into source-constrained, payload-first v7.1 cards, machine sidecars and review-gated claim candidates.
>
> 私有 Evidence Plane：把完整 AI 來源編譯成受證據約束、payload-first 的 v7.1 卡片、machine sidecars 與待審查 claim candidates。

## Active protocol｜目前協議

New compilation uses the immutable prompt selected by:

```text
governance/CARD_PROTOCOL_CURRENT.json
  -> governance/CARD_PROTOCOL_V7_1.md
  -> git blob SHA-1 7f3019f4b41a90728cd48a523d742c7c59721bf6
```

v7.1 separates evidence-first compilation from task-value-first rendering. Human cards begin with the core proposition and why it matters; canonical key, revision, source dependencies and registry state move to the declared sidecar plane. v7.0 remains the fixed A/B/provenance baseline, and v6.6 remains historical.

## Repository authority｜本庫權責

This repository owns immutable compiler contracts, source/evidence manifests, stable card identity, V/X/K state, human notes, private card/validation sidecars, E0/E1 claim candidates and privacy-preserving deltas. It does not grant Atlas admission, E2–E5 runtime evidence, Skill qualification, production routing or implicit invocation.

## Runtime contract｜執行契約

Scheduled runs use LOOP + SIDECAR and the exact runtime settings in `governance/PARAMETERS.md`. The source is always untrusted data. Compile order is Evidence → Assertions → D/V/X/K → semantic/framework/action nodes; render order is selected from the task. All QG-01..QG-24 require external evidence before DONE.

Versioned v7.1 host contracts:

```text
templates/NOTE_TEMPLATE_V7_1.md
schemas/source-manifest.schema.json
schemas/card-patch-v7.1.schema.json
schemas/assertion-report-v7.1.schema.json
schemas/compiler-state-v7.1.schema.json
```

## A/B evidence｜A/B 測試

The repository contains a fixed synthetic fixture, saved v7.0/v7.1 outputs, a run manifest, deterministic evaluator and persisted result:

```text
evals/prompt-ab/v7_0-v7_1/
tools/evaluate_prompt_ab.py
docs/PROMPT_V7_1_AB_AND_SYSTEM_AUDIT.md
```

The paired smoke result is A=60, B=100 on the deterministic contract score. Both preserve exact evidence and honest test status; v7.1 wins on human entry, payload-first rendering, source-dependency provenance, reader metadata load and batch balance. This is one synthetic replay, not statistical proof.

Run it with:

```bash
python tools/evaluate_prompt_ab.py \
  --fixture evals/prompt-ab/v7_0-v7_1/fixture.json \
  --output-a evals/prompt-ab/v7_0-v7_1/output-a-v7.0.md \
  --output-b evals/prompt-ab/v7_0-v7_1/output-b-v7.1.md \
  --run evals/prompt-ab/v7_0-v7_1/run.json \
  --output evals/prompt-ab/v7_0-v7_1/result.json \
  --check
```

## Materialization status｜實作狀態

Materialized:

- immutable v7.1 prompt and lock pointer;
- versioned schemas/templates;
- saved-output A/B evaluator;
- rights-gated YouTube caption/authorized-ASR acquisition;
- deterministic historical Git-note delta exporter.

Not materialized in this repository:

- generic live model/compiler provider adapter;
- deterministic semantic/anti-fragmentation validator;
- source-dependency resolver;
- Google Docs/Sheets transactional writer/read-back adapter;
- Drive-revision note-delta adapter.

The documented target workflow must not be presented as an executed production pipeline until these gaps are closed.

## Target data flow｜目標資料流

```text
ranked complete source
  -> rights/completeness gate
  -> source manifest and artifact boundaries
  -> immutable prompt + pinned host/model config
  -> evidence-first Audit Plane
  -> task-value-first Knowledge Plane
  -> CARD_PATCH + ASSERTION_REPORT + NEXT_STATE
  -> external QG-01..QG-24 validator
  -> Google Doc payload + private sidecars
  -> read-back
  -> Sheet status/URL
  -> claim map / note delta
  -> Atlas review
  -> independent Skill qualification
```

Hard separations:

```text
source statement != observed truth
source-reported test != current TESTED artifact
note completed != claim verified
claim candidate != admitted claim
Skill compiled != Skill qualified
```

## Canonical entrypoints｜固定入口

- `AGENTS.md`, `CLAUDE.md`
- `INTEGRATION_REQUIREMENTS.md`
- `governance/CARD_PROTOCOL_CURRENT.json`
- `governance/CARD_PROTOCOL_V7_1.md`
- `governance/PARAMETERS.md`
- `governance/WORKFLOW.md`
- `INDEX.md`, `CONTEXT.md`, `RANK.md`
- `docs/PROMPT_V7_1_AB_AND_SYSTEM_AUDIT.md`

## Contract validation｜契約驗證

```bash
python -m pip install -r requirements-contracts.txt
ruff check tools tests
python -m py_compile tools/*.py tests/*.py
pytest -q
```

CI validates legacy compatibility plus the v7.1 prompt lock, schemas, templates and deterministic A/B result.

## Completion｜完成條件

A current note is completed only after complete-source/rights review, immutable prompt verification, registry-consistent cards, external QG-01..QG-24 evidence, Google Doc read-back, sidecar read-back and exact Sheet write-back. Planned paths, status cells, prompt output and README prose are not completion evidence.

## Privacy and downstream boundary｜隱私與下游

Complete private source/note bodies do not enter public or downstream deltas. This repository emits review-and-requalify signals only. Code, model weights, data, trajectories and source text have independent provenance and licenses.
