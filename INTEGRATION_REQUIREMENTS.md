# Agent Integration Requirements｜Notes Evidence Plane

> Status: canonical human/agent handoff for `ed3c/ai-content-notes`.
>
> 本文件定義本庫如何把完整來源內容轉成可供 `ed3c/tech-implementation-atlas` 審查的 evidence 與 claim candidates。它不授予 Claim admission、Skill qualification、production routability 或 implicit invocation authority。

## 0. Mandatory read order｜強制閱讀順序

任何 Agent 在建立筆記、更新 claim mapping、修改 daily workflow、同步 Google Sheet 或串接 Atlas 前，必須依序讀取：

1. `INTEGRATION_REQUIREMENTS.md`
2. `AGENTS.md` 或 `CLAUDE.md`
3. `README.md`
4. `governance/PARAMETERS.md`
5. `governance/WORKFLOW.md`
6. `governance/CARD_PROTOCOL_V6_6.md`
7. `governance/CITATION_MAPPING.md`
8. `governance/LICENSE_POLICY.md`
9. `governance/SHEET_CONTRACT.md`
10. `CONTEXT.md`、`INDEX.md`、`RANK.md`
11. 受影響的 schemas、templates、note、claim-map 與 exporter tests

若路徑不存在、內容無法 read-back 或與 README 宣告不一致，必須回報為 materialization gap；不得把預期路徑或 Sheet URL 當成已存在檔案。

## 1. Repository role｜本庫唯一責任

本庫是每日 AI 情報工作流的 **canonical note body and research evidence store**：

```text
完整文章 / transcript / captions / official document
  → canonical URL and content identity
  → deduplication
  → v6.6 N/Q/C/D/S/P/T/R/G/E cards
  → atomic claim candidates
  → Domain / Capability / Lifecycle / Principle mappings
  → code / model / data / trajectory mappings
  → privacy-preserving note delta
  → Atlas ingestion review
```

本庫可以產生：

- 完整 Markdown 卡片筆記；
- source provenance、version、retrieval time、digest 與 anchors；
- `Fact | Invariant | Inference | Assumption` claim candidates；
- Domain、Capability、Engineering Lifecycle、Principle 與 artifact-plane mappings；
- freshness、contradiction、review、license metadata；
- Google Sheet control-plane status；
- privacy-preserving downstream delta。

本庫不得產生或宣告：

- admitted Atlas Claim；
- E3/E4/E5 runtime evidence，除非有獨立可核對的相應執行證據且仍須下游審查；
- sandbox-qualified Skill；
- production-routable Skill；
- implicit invocation permission；
- Arena ranking eligibility。

## 2. Source completeness gate｜完整來源 Gate

每篇 completed note 必須來自足夠完整的 source text：

- YouTube / Podcast：完整 transcript、captions 或可核對的完整逐字內容；
- Article：完整正文；
- Official Newsroom / docs：完整頁面正文與版本／日期資訊；
- Code / specification：可定位的 file、symbol、line、tag、commit 或 section anchor。

禁止使用：

- title only；
- search snippet；
- summary-only feed；
- 未核對的模型記憶；
- 無法對應 canonical source 的二手摘錄。

若完整文本不足：

```text
note_status = blocked
note_error = exact retrieval/completeness failure
```

同一來源的 daily workflow 應繼續檢查下一順位，直到成功完成一篇或沒有其他 eligible item。

## 3. Note completion contract｜筆記完成條件

一篇 note 只有在全部成立時才是 `completed`：

1. `notes/<category>/<file>.md` 存在於 declared ref；
2. frontmatter 有唯一 ID、canonical source URL、source identity、repository/path；
3. 內容遵守 v6.6、One Case One Card、D/P/N protection 與 Shadow Evidence rules；
4. source completeness gate 通過；
5. Git commit 成功；
6. GitHub read-back 成功；
7. Google Sheet 對應列已回寫 exact repository URL、status 與 timestamp；
8. canonical URL + content ID + note path 去重通過；
9. note body 未被錯誤複製到不應包含全文的 downstream artifact。

Daily content note writes 依既有運行契約可直接 atomic commit 到 `main`；schema、governance、exporter、security 或 cross-repository contract 變更應使用獨立 branch/PR，除非使用者明確要求其他流程。

## 4. Card-to-implementation mapping｜卡片到技術實作

卡片系列在下游的語義：

| Series | Downstream meaning |
|---|---|
| N | scenarios, incidents, negative examples, failure triggers |
| Q | knowledge gaps, unknown-domain fallback questions |
| C | glossary, Domain ontology, Capability definitions |
| D | atomic evidence and source anchors |
| S | strategy and workflow decision branches |
| P | executable procedures, tools, commands, parameters |
| T | comparison matrices and stack selection |
| R | lifecycle and migration plans |
| G | governance, permission and policy rules |
| E | invariants and candidate assertions |

編譯規則：

```text
D → evidence candidates
E + G → assertion / policy candidates
P → executable workflow candidates
S + T → selection logic candidates
R → lifecycle state-machine candidates
Q → unknown-domain fallback candidates
C → ontology and Capability candidates
N → scenarios and failure examples
```

每一篇 note 不等於一個 Skill。新 note 必須先判定：

```text
new Capability
| update existing Capability
| evidence-only addition
| stale/invalidate an existing claim or Skill
| no runtime impact
```

## 5. Atomic claim contract｜原子主張

每個 claim candidate 必須包含：

```text
claim_id
claim_kind: Fact | Invariant | Inference | Assumption
statement
source URL
source version/date
retrieval timestamp
source digest
quote/code/section anchor
note ID and Git blob SHA
review state
freshness / stale-after
contradiction links
Domain IDs
Capability IDs
Lifecycle stages
Principle IDs
artifact planes
separate license/provenance states
```

Claim rules：

- `Fact` 可在有 primary-source anchor 時成為 E1 candidate；
- `Inference`、`Invariant`、`Assumption` 預設需要 review，不得偽裝成 fact；
- 具體數字、日期、引語、代號不得模糊化；
- 多實體或多案例必須拆成 atomic claims；
- contradictory evidence 不得刪除，必須建立 relation；
- stale source 必須使 claim 失去 downstream eligibility，直到 refresh。

## 6. Notes → Atlas handoff｜下游輸出

Expected artifacts：

```text
claim-map@1
ai-content-note-delta@1
```

Delta 必須綁定：

- note ID、title、repository、path；
- Git blob SHA 與 source commit；
- canonical source URL；
- exact claim ID set；
- exact Capability、Lifecycle、Principle、artifact-plane mappings；
- downstream action，例如 `review-and-requalify`；
- read-back verification state。

Delta 不得包含：

- 完整 private note body；
- 完整 transcript／文章正文；
- secrets；
- private session traces；
- qualification 或 production-routing assertion。

所有 downstream bundle 必須保留：

```json
{
  "may_activate_claims": false,
  "may_raise_evidence_grade": false,
  "may_raise_skill_lifecycle": false,
  "may_enable_implicit_routing": false,
  "qualification_eligible": false
}
```

## 7. Google Sheet boundary｜控制面邊界

Google Sheet 是 ranking、cursor、status 與 URL control plane；GitHub Markdown 是完整 note body source of truth。

Sheet 至少維護：

```text
rank
title
source/channel/type
canonical URL
publish time
monetization score and mode
first seen / last updated
note status
note repository URL
note created time
note error
Domain
Capability IDs
Lifecycle impact
Claim extraction status
Evidence Grade candidate
Skill impact
Affected Skill IDs
Requalification required
Source version/digest
Stale after
License gate
Router eligible
```

禁止在 Git commit 與 GitHub read-back 完成前先寫入預期 note URL。

## 8. License and provenance｜授權與來源

Code、model weights、data、trajectory 與 source text 的 license/provenance 必須分開評估。整個 repository 或 project 的 MIT License 不會覆蓋第三方來源、資料、模型或軌跡。

Downstream ranking 或 implementation mapping 只有在 exact version/commit/license gate 通過後才可標示可用。`unknown` 應 fail closed，而不是視為 permissive。

## 9. Change-impact protocol｜新內容如何觸發技術工作流

新 note 或 source delta 的處理：

```text
source change
  → note/card delta
  → atomic claim delta
  → affected Domain / Capability / Principle / Lifecycle
  → affected assertions / prompts / compatibility
  → Skill impact: none | new | update | invalidate | deprecate
  → Atlas review
  → qualification/requalification queue where required
```

Security advisory、interface behavior change、source deprecation、license change 或 benchmark regression 必須標記 `requalification_required`，但本庫不得自行改變 Skill lifecycle。

## 10. Agent execution protocol｜Agent 執行步驟

1. 讀取 mandatory files 與 current source row。
2. 核對 canonical URL、content ID、published time 與 dedup key。
3. 取得完整 source text；不足則 blocked 並處理下一順位。
4. 依 v6.6 建立完整 card note，不縮減 D/P/N 系列。
5. 建立或更新 atomic claim-map；區分 Fact/Inference/Invariant/Assumption。
6. 驗證 source anchors、blob binding、privacy、schema、license/freshness metadata。
7. atomic commit；GitHub read-back exact path。
8. 只有在 read-back 成功後更新 Sheet。
9. 產生 privacy-preserving note delta。
10. 回報新增／更新／去重／blocked、note URLs、claim status 與 downstream impact。

## 11. Definition of Done｜整合完成條件

- complete source gate passed；
- note path exists and read-back succeeds；
- v6.6 card completeness passed；
- exact evidence preserved；
- canonical dedup passed；
- claim-map schema passed；
- note-delta schema and privacy gate passed；
- source/version/digest/anchor binding passed；
- Sheet row matches committed note identity；
- no unauthorized lifecycle/evidence/routing promotion；
- unresolved gaps recorded explicitly；
- completion report distinguishes note completion、claim candidate、Atlas admission、qualification and production routing。

## 12. Forbidden shortcuts｜禁止事項

- 不得用摘要、title 或 snippet 代替完整 source；
- 不得把 Sheet URL、expected path、issue checkbox 或 PR prose 當 GitHub materialization proof；
- 不得刪除矛盾 evidence 只保留支持既有結論的內容；
- 不得將 inference 寫成 fact；
- 不得把 private note body 放進 public exports；
- 不得從本庫提高 Skill lifecycle、production routability 或 implicit invocation；
- 不得把 license unknown 當 pass；
- 不得宣告 legacy migration completed，除非每個 exact path 都已 materialize 並 read-back。

## 13. Completion report template｜回報格式

```markdown
## Source
- source:
- canonical URL:
- completeness:
- source digest/version:

## Note
- note ID/path/blob:
- cards completed:
- read-back:
- Sheet row:

## Claims and mappings
- Fact:
- Invariant:
- Inference:
- Assumption:
- Domain/Capabilities/Lifecycle/Principles:

## Downstream impact
- Skill impact:
- affected Skills:
- requalification required:
- note delta:

## Status
- completed:
- blocked:
- unresolved gaps:
```
