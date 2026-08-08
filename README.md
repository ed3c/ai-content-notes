# AI Content Notes｜AI 高價值內容筆記庫

> A private, evidence-first Markdown knowledge base that turns high-value AI source material into structured card notes, implementation mappings, and license-aware open-source rankings.  
> 一個私有、證據優先的 Markdown 知識庫，把高價值 AI 原始內容轉成卡片盒筆記、技術落地映射與授權優先的開源資產排名。

## Repository purpose｜Repository 用途

### 中文（繁體）

`ed3c/ai-content-notes` 是每日 AI 情報工作流的**正文與研究資產 Source of Truth**。它不是一般文章收藏夾，也不是只有摘要的閱讀清單。每一篇完成筆記都必須由可取得的完整正文、逐字稿或字幕生成，保留具體數字、日期、引語、代號、因果鏈與可執行步驟。

本庫承擔五個工作：

1. **卡片盒知識建模**：使用 v6.6 Cyberpunk 協議產生 N/Q/C/D/S/P/T/R/G/E 系列卡片，遵守 One Case, One Card。
2. **技術觀點映射**：把帶 cite 的原子技術主張映射到 `code / model / data / trajectory` 四個平面。
3. **Production stack 對齊**：透過 `CONTEXT.md` 將術語觸發為可落地能力契約、等價技術堆疊、部署層與驗證需求。
4. **開源資產排名**：透過 `RANK.md` 評估新發現的開源庫、模型、資料集與 trajectory assets，涵蓋 Hackathon MVP、Commercial、Research、Production、Compatibility 與 Evidence。
5. **Google Sheet 索引同步**：Google Sheet 保留排行、同步游標、狀態與 URL；完整正文固定存於本 private repository。

### English

`ed3c/ai-content-notes` is the canonical body store and research asset base for a daily AI intelligence workflow. It is not a bookmark archive and not a summary-only reading list. A completed note must be grounded in a sufficiently complete article, transcript, or caption set and must preserve concrete figures, dates, quotations, identifiers, causal chains, and executable procedures.

The repository has five responsibilities:

1. **Card-based knowledge modeling** using the v6.6 Cyberpunk N/Q/C/D/S/P/T/R/G/E protocol and One Case, One Card.
2. **Technical claim mapping** from cited atomic claims to code, model, data, and trajectory planes.
3. **Production-stack translation** through `CONTEXT.md`, which turns terminology into capability contracts, equivalent implementation stacks, deployment layers, and validation requirements.
4. **Open-source artifact ranking** through `RANK.md`, covering Hackathon MVP, Commercial, Research, Production, Compatibility, and Evidence dimensions.
5. **Google Sheet synchronization**, where the Sheet remains the ranking and cursor control plane while this private repository remains the note-body source of truth.

## Data flow｜資料流

```text
High-value source / 完整原始內容
  → incremental collection and deduplication
  → monetization score and source ranking
  → highest-ranked unnoted item per source
  → v6.6 Markdown card note
  → one atomic commit directly to main
  → GitHub readback verification
  → private blob URL written to Google Sheet
  → Markdown & cite claim mapping
  → Code / Model / Data / Trajectory candidates
  → versioned license and evidence gates
  → RANK.md
```

## Canonical links｜固定入口

- [All notes index｜全部筆記索引](INDEX.md)
- [Technical trigger and stack mapping｜術語觸發與技術堆疊](CONTEXT.md)
- [Open-source artifact ranking｜開源資產排名](RANK.md)
- [Operating parameters｜固定執行參數](governance/PARAMETERS.md)
- [Daily workflow｜每日工作流](governance/WORKFLOW.md)
- [Card protocol v6.6｜卡片協議](governance/CARD_PROTOCOL_V6_6.md)
- [Citation mapping contract｜引用映射契約](governance/CITATION_MAPPING.md)
- [License policy｜授權 Gate](governance/LICENSE_POLICY.md)
- [Google Sheet contract｜試算表契約](governance/SHEET_CONTRACT.md)
- [Note template｜筆記模板](templates/NOTE_TEMPLATE.md)
- [Library candidate template｜開源候選模板](templates/LIBRARY_CANDIDATE_TEMPLATE.md)
- [Migration manifest｜遷移清單](MIGRATION_MANIFEST.json)

## Storage and completion contract｜儲存與完成契約

A note is `completed` only when all conditions are true:

1. `notes/<category>/<file>.md` exists on `main`.
2. The file has valid frontmatter with unique `id`, canonical source URL, repository, and path.
3. GitHub readback succeeds after the commit.
4. The Google Sheet row is `completed` and its note URL points to this repository.
5. The note was generated from sufficiently complete source text, not from a title or search snippet.

Deduplication key:

```text
Canonical URL + Content ID + GitHub note path
```

Private URL format:

```text
https://github.com/ed3c/ai-content-notes/blob/main/notes/<category>/<file>.md
```

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
│   └── rank-entry.schema.json
├── templates/
│   ├── NOTE_TEMPLATE.md
│   └── LIBRARY_CANDIDATE_TEMPLATE.md
└── notes/<technical-category>/*.md
```

## Operating rules｜運行規則

- Private repository; do not publish source text or internal research artifacts without an explicit review.
- Default branch: `main`.
- Daily note writes use one atomic commit directly to `main`; no feature branch and no PR unless explicitly requested.
- Never write a GitHub URL to the Sheet before the commit and readback succeed.
- New Google Docs are disabled. Legacy Google Docs may remain historical artifacts but are not canonical URLs.
- `CONTEXT.md` candidates are discovery leads, not approvals.
- `RANK.md` scores are valid only after exact-version license and evidence gates pass.
- Code, model weights, data, and trajectories have separate licenses and provenance.
- Search snippets never qualify as source text.

## Google Sheet control plane｜Google Sheet 控制面

The operational ranking sheet remains:

`AI高價值內容知識變現潛力排行榜`  
Spreadsheet ID: `1i1y4116id0l-CFYR0g1wPbYYMr6bAU18I85yOAcaG0M`

The Sheet stores ranking, source cursors, note status, timestamps, and private GitHub Markdown URLs. This repository stores complete notes and the technical mapping/ranking contracts.
