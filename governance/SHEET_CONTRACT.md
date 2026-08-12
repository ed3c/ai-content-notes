# Google Sheet Contract｜試算表控制面契約

## Canonical spreadsheet｜固定試算表

```text
Name: AI高價值內容知識變現潛力排行榜
ID: 1i1y4116id0l-CFYR0g1wPbYYMr6bAU18I85yOAcaG0M
```

## Responsibility boundary｜責任邊界

The Sheet is the ranking, cursor, configuration, and workflow-status control plane. It is not the complete note body, source corpus, card registry, compiler state, assertion report, Claim Ledger, private session store, or qualification authority.

Current human-readable notes use one Google Doc per content item. Historical private GitHub Markdown URLs remain valid legacy artifacts. Machine sidecars remain private in `ed3c/ai-content-notes`.

## System settings｜系統設定

The `系統設定` tab must identify:

```text
prompt version: 卡片盒記憶法知識編譯器 v7.0 — Evidence-First / Loop-Safe Cyberpunk Edition
canonical protocol URL: governance/CARD_PROTOCOL_V7_0.md
daily runtime: RUN_MODE=LOOP; STATE_CHANNEL=SIDECAR; MAX_CARDS_PER_BATCH=12
legacy policy: v6.6 notes are not bulk-renumbered or silently rewritten
```

A prompt-version cell is configuration, not proof that a note passed v7 Quality Gates.

## Required source-tab columns｜來源分頁欄位

| Column | Contract |
|---|---|
| 排名 | recomputed after incremental mutations |
| 標題 | source title |
| 來源管道 | source name/channel |
| 類型 | YouTube, Podcast, Article, Newsroom, Spec, Docs, Release, Advisory |
| URL | normalized canonical URL |
| 發布時間 | source publication time |
| 知識變現潛力評分 | integer 1–100 |
| 變現模式建議 | concrete offer or implementation path |
| 首次收錄時間 | immutable first discovery time |
| 最新更新時間 | last changed time |
| 筆記狀態 | pending/processing/completed/blocked/error/superseded |
| 筆記文件 URL | exact Google Doc URL or historical private GitHub Markdown URL |
| 筆記建立時間 | successful document/artifact read-back time |
| 筆記錯誤訊息 | exact failure reason |
| Domain | technical Domain |
| Capability IDs | comma-separated machine IDs |
| Principle IDs | bottom-layer principles |
| Engineering Lifecycle Impact | lifecycle stages |
| Claim Extraction Status | pending/completed/blocked |
| Evidence Grade | E0/E1 in notes plane; higher only by downstream authority |
| Skill Impact | none/new/update/invalidate/deprecate/review-and-requalify |
| Affected Skill IDs | downstream candidates |
| Requalification Required | true/false |
| Source Version | version or publication identifier |
| Source Digest | source-manifest digest when available |
| Stale After | freshness deadline |
| License Gate | pass/fail/unknown/not-applicable by plane |
| Router Eligible | derived downstream; never inferred from note completion |

## Incremental mutation rules｜增量規則

1. Read exact source rows and cursor before writes.
2. Normalize canonical URL and content ID.
3. Insert new rows only.
4. Update changed cells only.
5. Preserve first-collected time.
6. Recompute ranking after mutations.
7. Retain at most 300 rows per source.
8. Use score descending, publication time descending.
9. Never replace an entire source tab to simulate synchronization.

## Completion write-back｜完成回寫

For a current v7 Google Doc, write `completed` only after:

```text
complete-source and rights gates pass
source manifest is bound
all card patches are written
stable IDs/revisions are read back from the document
card registry and compiler state validate
QG-01 through QG-14 are PASS
no duplicate canonical key exists
unresolved links have K cards
contradictions have X cards or resolution
action execution status is honest
Google Doc and sidecars read back successfully
```

For a historical Markdown note, retain its Git commit/blob/path read-back contract.

A planned URL, generated title, local file, prompt output, or status cell is not sufficient.

## Blocked behavior｜Blocked 行為

When complete text, rights basis, locator, registry/state integrity, or required tool access is unavailable:

```text
status = blocked
error = exact failure
note URL = empty unless a prior valid artifact already exists
K acquisition/blocker record = exact evidence needed and unblock criteria
continue scanning lower-ranked eligible rows for the same source
```

## Deduplication｜去重

```text
canonical URL + source content ID + Note Document URL
+ historical private GitHub note path when present
```

Card/claim sidecars additionally bind source digest, stable IDs, canonical keys, document revision or Git blob, and source commit where applicable.

## Privacy｜隱私

Do not write complete note text, transcripts, private code, evidence verbatim beyond required control-plane fields, registry/state JSON, credentials, session traces, or qualification evidence to Sheet cells.

## Run log｜執行紀錄

Each run records:

```text
run ID and protocol version
start/end time and timezone
source count
rows added/updated/deduplicated
notes completed/blocked
per-source cursor movement
card patch counts
D/V/X/K counts
QG-01 through QG-14 summary
compiler status: CONTINUE/DONE/BLOCKED/FAILED
registry/state/assertion sidecar status
claim maps completed/blocked
Atlas impacts emitted
errors and retry disposition
```
