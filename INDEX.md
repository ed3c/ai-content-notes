# Notes Index｜筆記索引

## Authority boundary｜權威邊界

This file is a navigation entrypoint. Repository paths, note frontmatter, Git blob identity, and GitHub read-back determine whether a note exists and is complete. A missing or stale index entry never proves that a note is absent.

本文件是導航入口，不是 completeness authority。筆記是否存在，以 repository path、frontmatter、Git blob 與 GitHub read-back 為準。

## Canonical storage｜固定儲存

```text
notes/<technical-category>/<yyyy-mm-dd>-<slug>.md
claim-maps/<technical-category>/<yyyy-mm-dd>-<slug>.claim-map.json
```

## Technical categories｜技術類別

| Category | Scope | Atlas Domain |
|---|---|---|
| `agent-runtime` | MCP, model gateway, context routing, memory, runtime policy | `agent-runtime` |
| `evaluation` | benchmark, judge, regression, no-Skill baseline | `evaluation` |
| `security-governance` | safeguards, jailbreak, secret, OAuth, policy | `security-governance` |
| `retrieval-rag` | retrieval, citation, GraphRAG, source anchoring | `retrieval-rag` |
| `ai-infrastructure` | accelerator, inference capacity, FinOps, SLO | `ai-infrastructure` |
| `model-serving` | quantization, batching, cache, compatibility | `model-serving` |
| `data-trajectory` | provenance, dataset, trajectory, contamination | `data-trajectory` |
| `frontier-models` | model release and capability evidence | mapped by claim sidecar |
| `full-stack` | API, database, frontend/backend integration | `full-stack` |
| `android-kotlin` | Android SDK, Kotlin/KMP, Gradle, Jetpack, WebRTC | `android-kotlin` |

## Navigation contract｜導航契約

A valid note contains:

```yaml
id: unique repository identity
source_url: canonical source
category: one storage category
repository: ed3c/ai-content-notes
path: exact repository path
note_format: zettelkasten-v6.6-cyberpunk
citation_mapping: pending|completed|blocked
library_mapping: pending|completed|blocked
```

Use repository code search or the `notes/` tree for current navigation. Machine consumers must use note-delta manifests and claim maps rather than scrape this Markdown file.

## Known migration gap｜已知遷移缺口

Issue `#2 materialize-ai-content-notes-migration` tracks 22 legacy canonical notes and related files that the Google Sheet references but this repository has not yet fully materialized. Do not mark those paths complete until file read-back succeeds.

## Current contract example｜目前契約範例

The first machine-bound example is:

```text
note:
  notes/agent-runtime/2026-07-30-langsmith-llm-gateway-runtime-controls.md
claim map:
  examples/claim-maps/langsmith-llm-gateway.claim-map.json
```

The example remains a claim candidate source. It does not make a downstream Skill qualified or routable.
