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

Google Sheet stores ranking, cursor, status, timestamps and the exact Note Document URL. Google Docs stores the human-facing payload. This private repository stores immutable prompts, manifests, registries, compiler state, assertion reports, card patches, claim maps and historical notes. It does not store runtime qualification evidence.

## Canonical prompt｜固定 Prompt

The authority is the locked pointer, not a copied prompt fragment:

```text
governance/CARD_PROTOCOL_CURRENT.json
  -> governance/CARD_PROTOCOL_V7_1.md
  -> git blob SHA-1 7f3019f4b41a90728cd48a523d742c7c59721bf6
```

Protocol identifier:

```text
zettelkasten-v7.1-evidence-first-narrative-alive-dual-plane
```

`CARD_PROTOCOL_V7_0.md` remains the A/B baseline. No host may edit v7.1 to resolve an adapter mismatch; the adapter or versioned contract must be fixed instead.

## Scheduled Runtime override｜排程覆寫

Only documented Runtime Configuration is supplied by the host:

```yaml
RUN_MODE: LOOP
OUTPUT_LANGUAGE: zh-TW
STYLE_PROFILE: CYBERPUNK_PRECISE
INTELLIGENT_COMPRESSION: OFF
GRANULARITY: MAXIMUM
MAX_CARDS_PER_BATCH: 12
MAX_SELF_REPAIR_PASSES: 3
COMPILE_ORDER: EVIDENCE_FIRST
RENDER_ORDER: TASK_VALUE_FIRST
RENDER_MODE: PAYLOAD_FIRST
METADATA_MODE: COMPACT_WITH_HTML_SIDECAR
BATCH_COVERAGE_POLICY: BALANCED
STATE_CHANNEL: SIDECAR
EXTERNAL_KNOWLEDGE: DISALLOW
TOOL_EXECUTION: DISALLOW
QUOTE_POLICY: MINIMUM_NECESSARY
LINK_POLICY: EXACT_TYPED_LINKS
ID_POLICY: STABLE_CANONICAL_KEY
LOCATOR_FALLBACK: TEXT_MATCH_OR_LOCATOR_MISSING
SOURCE_DEPENDENCY_CHECK: ON
ANTI_FRAGMENTATION: ON
BASELINE_GUARD: V6_6_SEMANTIC_RICHNESS
```

In LOOP mode, “HTML sidecar” in the presentation contract is mapped to the private SIDECAR channel. The host must not place `CARD_META`, `ASSERTION_REPORT`, or `NEXT_STATE` inside Google Docs.

## Versioned host contracts｜版本化 Host Contract

```text
templates/NOTE_TEMPLATE_V7_1.md
schemas/source-manifest.schema.json
schemas/card-patch-v7.1.schema.json
schemas/assertion-report-v7.1.schema.json
schemas/compiler-state-v7.1.schema.json
templates/SOURCE_MANIFEST_TEMPLATE_V7_1.json
templates/CARD_PATCH_TEMPLATE_V7_1.json
templates/ASSERTION_REPORT_TEMPLATE_V7_1.json
templates/COMPILER_STATE_TEMPLATE_V7_1.json
```

The unversioned v7.0 schemas/templates remain compatibility artifacts for existing tests and historical state. New v7.1 state must not be coerced into those older contracts.

## Required source classes｜來源類型

At least YouTube (`@showoffer`, `@aidotengineer`, `@langchain`, `@sequoiacapital`), official OpenAI/Anthropic material, representative Substack/Podcast sources, primary technical specifications, official docs, release notes and security advisories.

## Ranking｜排行

Each item receives a 1–100 knowledge-monetization score from scarcity, transformation effort, commercial implementation surface, evidence quality, technical depth, reusability and production relevance. Tie-break: newer publication time first. Retain at most 300 rows per source.

## Incremental synchronization｜增量同步

- Read existing URL, content ID, publication time, note status, Note Document URL and cursor.
- Add new content first, then backfill older content.
- Update only changed rows; never overwrite a whole source page to simulate synchronization.
- Bind each cursor to the source digest. A changed digest invalidates or rebases the cursor.
- Deduplicate by canonical URL + source content ID + Note Document URL, plus a historical GitHub path when present.

## Source-text threshold｜完整文本門檻

YouTube/Podcast needs complete transcript or sufficiently complete reviewed captions; an article needs the complete body; official material needs the complete page/version. Search snippets, titles, previews and model memory are prohibited as note sources.

## Note selection｜筆記選擇

For each source, scan rank 1 downward until one eligible uncompleted item succeeds. A blocked row records the exact reason and continues to the next row; a successful, read-back-verified note stops that source for the current run.

## Storage｜儲存

```text
Human-readable note:
  Google Doc, one document per content item, source-specific folder

Private compiler artifacts:
  source-manifests/<source-id>/<content-id>.source-manifest.json
  card-registries/<source-id>.card-registry.json
  card-patches/<source-id>/<content-id>/<batch>.card-patch.json
  compiler-state/<source-id>/<content-id>.compiler-state.json
  assertion-reports/<source-id>/<content-id>.assertion-report.json
  claim-maps/<technical-category>/<slug>.claim-map.json

Historical notes:
  notes/<technical-category>/<yyyy-mm-dd>-<slug>.md
```

A new note is `completed` only after source/rights review, full card write, Google Drive read-back, sidecar persistence/read-back, external QG-01..QG-24 validation, baseline guard, and Sheet write-back.

## Status values｜狀態

```text
pending | processing | completed | blocked | error | superseded
```

Note status, card compilation, claim admission and Skill qualification remain separate state machines.
