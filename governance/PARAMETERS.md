# Operating Parameters｜固定執行參數

## Schedule｜排程

```yaml
timezone: Asia/Taipei
daily_run: "09:00"
source_limit: 50
per_source_row_limit: 300
notes_per_source_per_run: 1
maximum_notes_per_run: 50
```

## Control plane｜控制面

```yaml
spreadsheet_name: AI高價值內容知識變現潛力排行榜
spreadsheet_id: 1i1y4116id0l-CFYR0g1wPbYYMr6bAU18I85yOAcaG0M
body_store: ed3c/ai-content-notes
qualification_store: ed3c/agent-skills-repo
implementation_atlas: ed3c/tech-implementation-atlas
```

Google Sheet stores ranking, cursor, status, timestamps, and canonical private GitHub URLs. It does not store the complete note body or runtime qualification evidence.

## Required source classes｜來源類型

At least:

```text
YouTube: @showoffer, @aidotengineer, @langchain, @sequoiacapital
Official: OpenAI Newsroom, Anthropic Newsroom
Representative Substack and Podcast sources
Primary technical specifications, official docs, release notes, and security advisories
```

## Ranking｜排行

Each item receives a 1–100 knowledge monetization score from:

```text
scarcity
transformation effort
commercial implementation surface
evidence quality
technical depth
reusability
production relevance
```

Tie-break: newer publication time first. Over 300 rows per source, retain the highest-scoring 300 using the same tie-break.

## Incremental synchronization｜增量同步

- Read existing URL, content ID, publication time, note status, note path, and cursor.
- Add new content first, then backfill older content.
- Update only changed rows.
- Never overwrite a whole source page to simulate synchronization.
- Recompute rank after mutations.

Deduplication key:

```text
canonical URL + source content ID + canonical GitHub note path
```

## Note selection｜筆記選擇

For each source, scan rank 1 downward until one eligible, uncompleted item succeeds.

```text
completed or valid note URL -> skip
blocked -> record exact reason and continue
insufficient complete text -> blocked, never summarize from title/snippet
success -> stop for this source in this run
```

## Source-text threshold｜完整文本門檻

```text
YouTube / Podcast: complete transcript or sufficiently complete captions
Article: complete body
Official newsroom: complete article
Search snippet, title, social preview, or model memory: prohibited as note source
```

## Storage｜儲存

```text
notes/<technical-category>/<yyyy-mm-dd>-<slug>.md
claim map: claim-maps/<technical-category>/<same-slug>.claim-map.json
```

A note becomes `completed` only after commit and GitHub read-back. Do not write a canonical URL to Google Sheet before read-back succeeds.

## Status values｜狀態

```text
pending
processing
completed
blocked
error
superseded
```

Claim admission and Skill qualification use separate state machines and must not reuse note status.

## Card protocol｜卡片協議

```yaml
protocol: zettelkasten-v6.6-cyberpunk
intelligent_compression: false
granularity: maximum
one_case_one_card: true
D_series_summary: forbidden
P_series_summary: forbidden
N_series_outline_reduction: forbidden
output_only_cards: true
```

## Completion evidence｜完成證據

Every daily run reports:

```text
ranking rows added / updated / deduplicated
current row count per source
source-tab classification
notes completed / blocked
processed rank and title per source
canonical note links
Top 5 content items
spreadsheet link
claim-map and Atlas impact status when available
```
