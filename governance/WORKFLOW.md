# Daily Workflow｜每日證據工作流

## End-to-end state machine｜端到端狀態機

```text
source discovery
  -> cursor-aware incremental collection
  -> canonical URL/content-ID deduplication
  -> monetization scoring and ranking
  -> highest-ranked unnoted selection per source
  -> complete-text acquisition
  -> v6.6 card-note generation
  -> note validation
  -> atomic GitHub commit
  -> GitHub read-back
  -> Sheet status/URL write-back
  -> atomic claim-map extraction
  -> deterministic note-delta export
  -> Atlas impact review
  -> Skill candidate compilation
  -> independent qualification
```

## Phase A — Ranking synchronization｜排行榜同步

1. Read every source tab's existing canonical URLs, content IDs, timestamps, note status, and cursor.
2. Fetch newest content first; then backfill older content.
3. Normalize canonical URLs before deduplication.
4. Score each item from 1–100 and record a concrete monetization path.
5. Add only new rows and update only changed rows.
6. Sort by score descending, then publication time descending.
7. Retain at most 300 rows per source.
8. Write an execution log with counts and cursor changes.

## Phase B — One note per source｜每來源一篇筆記

For each source:

```text
rank 1
  -> completed? skip
  -> duplicate note/path? skip
  -> complete text unavailable? mark blocked and continue
  -> complete text available? generate and validate note
  -> successful commit/read-back? stop for source
```

Do not stop at the first blocked row. Continue until one note succeeds or no eligible rows remain.

### YouTube complete-text acquisition｜YouTube 完整文本取得

For YouTube rows, use the rights-gated pipeline documented in
`docs/YOUTUBE_TRANSCRIPT_PIPELINE.md` and implemented by
`tools/youtube_transcript.py`.

```text
explicit rights basis
  -> single-video canonicalization
  -> manual captions
  -> platform automatic captions
  -> explicit authorized ASR fallback
  -> manifest + raw-source digest + timestamped artifacts
  -> human review
  -> complete-source decision
```

Rules:

- Public visibility alone is not a rights basis.
- Caption acquisition is the default. Audio download requires an explicit ASR gate.
- No cookie, proxy, browser-session, PO-token-provider, or anti-bot bypass is supported.
- `manifest.status = needs-review` is not note completion.
- `manual-caption`, `platform-auto-caption`, and `asr-unreviewed` all require review of technical proper nouns, figures, dates, quotations, and code identifiers.
- A `blocked` manifest must write the exact acquisition failure to the Sheet and the workflow must continue to the next ranked row.
- Full transcript/audio artifacts remain private and are never copied into public Skill exports.

## Phase C — Note validation｜筆記驗證

Required frontmatter:

```yaml
id: globally unique within repository
title: source title
source: source display name
source_url: canonical URL
published_at: YYYY-MM-DD
monetization_score: 1-100
category: technical category
language: zh-TW
note_format: zettelkasten-v6.6-cyberpunk
storage: private-github-markdown
repository: ed3c/ai-content-notes
path: notes/<category>/<file>.md
citation_mapping: pending|completed|blocked
library_mapping: pending|completed|blocked
```

Body rules:

- Output only N/Q/C/D/S/P/T/R/G/E cards.
- No general abstract, preface, dashboard, or M-series index.
- Preserve One Case, One Card.
- Preserve exact figures, dates, identifiers, and short source quotations.
- Expand executable tools, commands, parameters, and abort conditions.
- Long content remains in one Markdown note; do not compress D/P/N cards.

## Phase D — Commit and read-back｜Commit 與 Read-back

```text
validate path/frontmatter
  -> commit exactly the intended note and sidecars
  -> fetch the same path from the committed ref
  -> verify blob SHA/path/id
  -> only then write canonical GitHub URL and completed status to Sheet
```

A status cell, issue comment, or expected URL is not read-back evidence.

## Phase E — Claim mapping｜Claim 映射

1. Inspect D/E/G/P/S/T/R/Q cards.
2. Split each falsifiable statement into one claim.
3. Classify Fact, Invariant, Inference, or Assumption.
4. Bind source URL, version, retrieval date, source anchor, note path, and Git blob SHA.
5. Map Domain, capability, lifecycle, principles, artifact planes, and Skill impact.
6. Keep E0/E1 only in this repository.
7. Record contradiction and supersession relations.
8. Validate `schemas/claim-map.schema.json`.

## Phase F — Delta export and Atlas impact｜Delta 與 Atlas Impact

```bash
python tools/export_note_delta.py \
  --note <note-path> \
  --claim-map <claim-map-path> \
  --source-commit <commit-sha> \
  --readback-verified \
  --check \
  --output <note-delta.json>
```

The downstream action is always `review-and-requalify`. Note ingestion never raises evidence grade, Skill lifecycle, or production routability.

## Failure taxonomy｜失敗分類

| Failure | Required behavior |
|---|---|
| duplicate content | count as deduplicated; do not create another note |
| incomplete text | mark blocked with exact acquisition reason |
| YouTube rights basis missing | block acquisition; do not invoke caption/audio backend |
| YouTube caption unavailable | remain blocked or use separately authorized ASR; continue next row |
| YouTube ASR unreviewed | keep `needs-review`; do not mark note completed |
| invalid frontmatter/path | abort commit |
| failed commit | keep Sheet row non-completed |
| failed read-back | do not write canonical note URL |
| claim-map mismatch | block delta export |
| stale or contradictory source | queue review; do not overwrite active claim |
| license unknown | retain discovery-only status |
| sandbox evidence missing | keep Skill non-routable |

## Idempotency｜冪等性

The same canonical URL/content ID/note path/claim-map blob/source commit must produce the same result. Replaying a successful event must not create duplicate rows, notes, claims, or qualification requests.
