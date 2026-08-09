# AI Content Notes｜AI 高價值內容筆記庫

> A private, evidence-first Markdown knowledge base that turns complete AI source material into v6.6 card notes, atomic claim candidates, implementation impacts, and license-aware artifact rankings.  
> 一個私有、證據優先的 Markdown 知識庫，把完整 AI 原始內容轉成 v6.6 卡片筆記、atomic claim candidate、技術實作 impact 與授權感知的資產排名。

## Repository authority｜Repository 權責

`ed3c/ai-content-notes` is the canonical **note-body and research-evidence store** for the daily AI intelligence workflow. It is not a bookmark archive, summary-only reading list, runtime sandbox, or Skill qualification authority.

`ed3c/ai-content-notes` 是每日 AI 情報工作流的**筆記正文與研究證據 Source of Truth**。它不是書籤庫、摘要清單、runtime sandbox 或 Skill qualification authority。

A completed note must be grounded in a sufficiently complete article, transcript, caption set, official document, source tree, paper, or release artifact. It preserves exact figures, dates, identifiers, short quotations, causal chains, executable procedures, and explicit unknowns.

This repository owns:

1. **Card-based knowledge modeling** with the v6.6 Cyberpunk N/Q/C/D/S/P/T/R/G/E protocol and One Case, One Card.
2. **Atomic claim candidates** that distinguish Fact, Invariant, Inference, and Assumption.
3. **Technical context mapping** from terminology to Domain, capability, lifecycle, principle, risk, and artifact planes.
4. **Privacy-preserving note deltas** bound to a private note path and Git blob SHA.
5. **License-aware artifact ranking** across code, model, data, and trajectory planes.
6. **Google Sheet synchronization**, with the Sheet as the ranking/cursor/status control plane.

It does **not** own E2–E5 runtime evidence, sandbox qualification, production observation, Skill lifecycle admission, or production routability.

## End-to-end data flow｜端到端資料流

```text
High-value source / complete official material
  -> cursor-aware incremental collection and deduplication
  -> monetization scoring and source ranking
  -> highest-ranked eligible unnoted item per source
  -> complete-text acquisition
  -> v6.6 private Markdown card note
  -> atomic commit and GitHub read-back
  -> Google Sheet canonical URL/status write-back
  -> atomic claim-map sidecar
  -> deterministic ai-content-note-delta@1
  -> tech-implementation-atlas impact review
  -> capability / assertion / Skill candidate delta
  -> independent agent-skills-repo qualification
```

Hard invariant:

```text
note completed != claim admitted
claim source-anchored != runtime reproduced
Skill compiled != Skill qualified
signed receipt != lifecycle admission
```

## Cross-repository authority｜跨庫權責

| Repository | Canonical authority |
|---|---|
| `ed3c/ai-content-notes` | complete note, private note blob, source mapping, E0/E1 claim candidate |
| `ed3c/tech-implementation-atlas` | admitted claim ledger, capability graph, routing, assertions, compilation, Claude/Codex distribution |
| `ed3c/agent-skills-repo` | independent runtime evidence, qualification, Arena evaluation, lifecycle admission |

No repository may infer another repository's authority from a status string, expected URL, or file-format conformance alone.

## Canonical entrypoints｜固定入口

### Knowledge and workflow

- [All notes navigation｜筆記導航](INDEX.md)
- [Technical trigger and stack mapping｜術語觸發與技術堆疊](CONTEXT.md)
- [Open-source artifact ranking｜開源資產排名](RANK.md)
- [Operating parameters｜固定執行參數](governance/PARAMETERS.md)
- [Daily workflow｜每日工作流](governance/WORKFLOW.md)
- [Card protocol v6.6｜卡片協議](governance/CARD_PROTOCOL_V6_6.md)
- [Citation and claim contract｜引用與 Claim 契約](governance/CITATION_MAPPING.md)
- [License policy｜授權 Gate](governance/LICENSE_POLICY.md)
- [Google Sheet contract｜試算表契約](governance/SHEET_CONTRACT.md)

### Machine contracts

- [Atomic claim-map schema](schemas/claim-map.schema.json)
- [Privacy-preserving note-delta schema](schemas/note-delta.schema.json)
- [Exact-version rank-entry schema](schemas/rank-entry.schema.json)
- [Deterministic note-delta exporter](tools/export_note_delta.py)
- [Complete-note claim-map example](examples/claim-maps/langsmith-llm-gateway.claim-map.json)

### Templates and migration

- [Note template｜筆記模板](templates/NOTE_TEMPLATE.md)
- [Library candidate template｜開源候選模板](templates/LIBRARY_CANDIDATE_TEMPLATE.md)
- [Migration manifest｜遷移清單](MIGRATION_MANIFEST.json)

## Storage and completion contract｜儲存與完成契約

A note is `completed` only when all conditions are true:

1. `notes/<category>/<file>.md` exists at an immutable commit.
2. The file has valid frontmatter with a unique `id`, canonical source URL, repository, and exact path.
3. The note was generated from sufficiently complete source text, not a title, search snippet, or model memory.
4. GitHub read-back succeeds after commit.
5. The Google Sheet row points to the verified private GitHub Markdown path.

Deduplication key:

```text
canonical URL + source content ID + canonical GitHub note path
```

Private URL format:

```text
https://github.com/ed3c/ai-content-notes/blob/main/notes/<category>/<file>.md
```

A claim map has a separate completion contract:

```text
note frontmatter/path/id validate
note Git blob SHA matches sidecar
claim-map schema validates
Fact/Invariant/Inference/Assumption are separated
source/version/anchor/freshness/license mappings exist
non-facts retain review state
GitHub read-back is verified
delta action remains review-and-requalify
```

## Deterministic note-delta export｜確定性增量匯出

```bash
python tools/export_note_delta.py \
  --note notes/agent-runtime/2026-07-30-langsmith-llm-gateway-runtime-controls.md \
  --claim-map examples/claim-maps/langsmith-llm-gateway.claim-map.json \
  --source-commit <40-character-commit-sha> \
  --readback-verified \
  --check \
  --output /tmp/note-delta.json
```

The delta contains note identity, path, blob SHA, source URL, Domain, trigger terms, claim IDs, capability IDs, lifecycle, principles, artifact planes, and `review-and-requalify`. It contains no full note body or private transcript.

## Contract validation｜契約驗證

```bash
python -m pip install -r requirements-contracts.txt
ruff check tools tests
python -m py_compile tools/export_note_delta.py tests/test_contracts.py
pytest -q
```

CI runs the same contracts on Python 3.11 and 3.13 and performs an end-to-end deterministic delta export.

## Repository layout｜目錄結構

```text
.
├── README.md
├── INDEX.md
├── CONTEXT.md
├── RANK.md
├── MIGRATION_MANIFEST.json
├── governance/
│   ├── PARAMETERS.md
│   ├── WORKFLOW.md
│   ├── CARD_PROTOCOL_V6_6.md
│   ├── CITATION_MAPPING.md
│   ├── LICENSE_POLICY.md
│   └── SHEET_CONTRACT.md
├── schemas/
│   ├── claim-map.schema.json
│   ├── note-delta.schema.json
│   └── rank-entry.schema.json
├── templates/
│   ├── NOTE_TEMPLATE.md
│   └── LIBRARY_CANDIDATE_TEMPLATE.md
├── examples/claim-maps/
├── tools/export_note_delta.py
├── tests/test_contracts.py
├── claim-maps/<technical-category>/
└── notes/<technical-category>/*.md
```

`examples/claim-maps/` contains reviewed contract examples. Canonical production sidecars move to `claim-maps/<technical-category>/` after the corresponding extraction and review workflow is admitted.

## Operating rules｜運行規則

- Private repository; do not publish complete source text, private transcripts, or internal research artifacts without explicit review.
- Default branch: `main`.
- Daily note writes use one atomic commit directly to `main`; governance/compiler changes use reviewed branches and CI.
- Never write a GitHub URL to the Sheet before commit and read-back succeed.
- New Google Docs are disabled. Legacy Google Docs are historical artifacts, not canonical URLs.
- `CONTEXT.md` terms are discovery triggers, not approvals.
- `RANK.md` recommendations require exact-version license, compatibility, security, and evidence gates.
- Code, model weights, data, and trajectories have separate licenses and provenance.
- Search snippets never qualify as source text or E1 evidence.
- This repository cannot self-assert E2–E5, sandbox qualification, production observation, or production routability.

## Google Sheet control plane｜Google Sheet 控制面

```text
Name: AI高價值內容知識變現潛力排行榜
Spreadsheet ID: 1i1y4116id0l-CFYR0g1wPbYYMr6bAU18I85yOAcaG0M
```

The Sheet stores ranking, source cursors, note status, timestamps, and verified private GitHub Markdown URLs. This repository stores complete notes and machine-readable research contracts.

## Known migration Glitch｜已知遷移 Glitch

Issue `#2 materialize-ai-content-notes-migration` tracks 22 legacy canonical notes and related artifacts that still require path-level materialization and read-back. `MIGRATION_MANIFEST.json` deliberately remains `incomplete` with no fabricated entries until that evidence exists.
