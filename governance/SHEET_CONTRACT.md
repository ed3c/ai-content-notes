# Google Sheet Contract｜試算表控制面契約

## Canonical spreadsheet｜固定試算表

```text
Name: AI高價值內容知識變現潛力排行榜
ID: 1i1y4116id0l-CFYR0g1wPbYYMr6bAU18I85yOAcaG0M
```

## Responsibility boundary｜責任邊界

The Sheet is a ranking, cursor, and workflow-status control plane. It is not the canonical note body, claim ledger, session store, or qualification authority.

試算表只保存排行、游標與工作流狀態，不保存完整筆記正文、Claim Ledger、session trace 或 qualification authority。

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
| 筆記文件 URL | canonical private GitHub Markdown URL |
| 筆記建立時間 | successful commit/read-back time |
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
| Source Digest | content or source-manifest digest when available |
| Stale After | freshness deadline |
| License Gate | pass/fail/unknown/not-applicable by plane |
| Router Eligible | derived downstream; never inferred from note completion |

## Incremental mutation rules｜增量規則

1. Read existing rows and cursor before writes.
2. Normalize URL and content ID.
3. Insert new rows only.
4. Update changed cells only.
5. Preserve first-collected time.
6. Recompute ranking after writes.
7. Retain at most 300 rows per source.
8. Use score descending, publication time descending for retention and ranking.
9. Never replace an entire source tab to simulate a sync.

## Completion write-back｜完成回寫

Write `completed` only after:

```text
note path exists at committed ref
frontmatter/path/id validate
GitHub read-back returns the committed bytes/blob
canonical private URL points to that path
```

A planned URL or successful local file write is not sufficient.

## Blocked behavior｜Blocked 行為

When complete text is unavailable:

```text
status = blocked
error = exact acquisition or validation reason
note URL = empty
continue scanning lower-ranked eligible rows for the same source
```

## Deduplication｜去重

```text
canonical URL + source content ID + canonical GitHub note path
```

Claim maps additionally bind note blob SHA and source commit.

## Privacy｜隱私

Do not write complete note text, transcripts, private code, credentials, session traces, or unpublished claim evidence to Sheet cells.

## Run log｜執行紀錄

Each run records:

```text
run id
start/end time and timezone
source count
rows added/updated/deduplicated
notes completed/blocked
per-source cursor movement
claim maps completed/blocked
Atlas impacts emitted
errors and retry disposition
```
