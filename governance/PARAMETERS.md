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
current_note_document_store: Google Docs
private_evidence_and_state_store: ed3c/ai-content-notes
legacy_markdown_note_store: ed3c/ai-content-notes/notes
qualification_store: ed3c/agent-skills-repo
implementation_atlas: ed3c/tech-implementation-atlas
```

Google Sheet stores ranking, cursor, status, timestamps, and the exact Note Document URL. Google Docs stores the current human-readable card body. This private repository stores the canonical protocol, source/evidence manifests, card registry, compiler state, assertion reports, claim maps, and historical GitHub Markdown notes. It does not store runtime qualification evidence.

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

- Read existing URL, content ID, publication time, note status, Note Document URL, and cursor.
- Add new content first, then backfill older content.
- Update only changed rows.
- Never overwrite a whole source page to simulate synchronization.
- Recompute rank after mutations.

Deduplication key:

```text
canonical URL + source content ID + Note Document URL
```

Historical private GitHub Markdown paths remain additional deduplication evidence and must never be rematerialized as duplicate Google Docs.

## Note selection｜筆記選擇

For each source, scan rank 1 downward until one eligible, uncompleted item succeeds.

```text
completed or valid Note Document URL -> skip
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

## Current note and sidecar storage｜目前筆記與 Sidecar 儲存

```text
Human-readable note:
  Google Doc, one document per content item, source-specific folder

Private compiler sidecars:
  card-registries/<source-id>.card-registry.json
  compiler-state/<source-id>/<content-id>.compiler-state.json
  assertion-reports/<source-id>/<content-id>.assertion-report.json
  source-manifests/<source-id>/<content-id>.source-manifest.json
  claim-maps/<technical-category>/<slug>.claim-map.json

Historical notes:
  notes/<technical-category>/<yyyy-mm-dd>-<slug>.md
```

A new Google Doc note becomes `completed` only after document creation, full card write, Drive read-back, v7 Quality Gate validation, sidecar persistence, and Sheet write-back. A historical Markdown note remains completed only after commit and GitHub read-back. Do not write an expected URL before the corresponding authority can read it back.

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

Canonical prompt:

```text
governance/CARD_PROTOCOL_V7_0.md
```

Default interactive runtime is defined by that prompt. The scheduled daily workflow overrides it with:

```yaml
protocol: zettelkasten-v7.0-evidence-first-loop-safe
RUN_MODE: LOOP
OUTPUT_LANGUAGE: zh-TW
STYLE_PROFILE: CYBERPUNK_LOW_NOISE
INTELLIGENT_COMPRESSION: OFF
GRANULARITY: MAXIMUM
MAX_CARDS_PER_BATCH: 12
STATE_CHANNEL: SIDECAR
EXTERNAL_KNOWLEDGE: DISALLOW
TOOL_EXECUTION: DISALLOW
QUOTE_POLICY: MINIMUM_NECESSARY
LINK_POLICY: EXACT_TYPED_LINKS
ID_POLICY: STABLE_CANONICAL_KEY
```

Required invariants:

```text
Evidence Before Narrative
One Case, One Card
stable canonical identity
exact evidence anchors
typed links only
explicit epistemic state
V/X/K representation
lossless cursor batching
idempotent patch output
honest test status
QG-01 through QG-14 before DONE
```

Legacy policy:

```text
v6.6 notes remain historical and immutable by default
no bulk renumbering
no silent rewrite
explicit migration uses governance/CARD_PROTOCOL_MIGRATION_V6_6_TO_V7_0.md
```

## Completion evidence｜完成證據

Every daily run reports:

```text
ranking rows added / updated / deduplicated
current row count per source
source-tab classification
notes completed / blocked
processed rank and title per source
Note Document links
Top 5 content items
spreadsheet link
card patch / registry / compiler-state status
Quality Gate assertion report
claim-map and Atlas impact status when available
```
