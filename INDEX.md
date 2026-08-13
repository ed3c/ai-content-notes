# Notes Index｜筆記索引

## Authority boundary｜權威邊界

This file is navigation only. Repository paths, document revisions, sidecar digests and read-back determine existence/completion. A stale index entry is never authority.

## Active compiler contract｜目前編譯契約

```text
governance/CARD_PROTOCOL_CURRENT.json
  -> governance/CARD_PROTOCOL_V7_1.md
  -> git blob SHA-1 7f3019f4b41a90728cd48a523d742c7c59721bf6
```

- Active note template: `templates/NOTE_TEMPLATE_V7_1.md`
- Runtime schemas: `schemas/*v7.1.schema.json` plus `schemas/source-manifest.schema.json`
- A/B evidence: `evals/prompt-ab/v7_0-v7_1/`
- System audit: `docs/PROMPT_V7_1_AB_AND_SYSTEM_AUDIT.md`
- v7.0: retained A/B/provenance baseline
- v6.6: historical note provenance

## Canonical storage｜固定儲存

```text
Google Doc: current human-readable note, one document per content item
source-manifests/<source-id>/<content-id>.source-manifest.json
card-registries/<source-id>.card-registry.json
card-patches/<source-id>/<content-id>/<batch>.card-patch.json
compiler-state/<source-id>/<content-id>.compiler-state.json
assertion-reports/<source-id>/<content-id>.assertion-report.json
claim-maps/<technical-category>/<slug>.claim-map.json
notes/<technical-category>/<yyyy-mm-dd>-<slug>.md  # historical Git notes
```

## Technical categories｜技術類別

| Category | Scope | Atlas Domain |
|---|---|---|
| `agent-runtime` | MCP, gateway, context routing, memory, runtime policy | `agent-runtime` |
| `evaluation` | benchmark, judge, regression, baseline | `evaluation` |
| `security-governance` | safeguards, jailbreak, secret, OAuth, policy | `security-governance` |
| `retrieval-rag` | retrieval, citation, GraphRAG, source anchoring | `retrieval-rag` |
| `ai-infrastructure` | accelerator, inference capacity, FinOps, SLO | `ai-infrastructure` |
| `model-serving` | quantization, batching, cache, compatibility | `model-serving` |
| `data-trajectory` | provenance, dataset, trajectory, contamination | `data-trajectory` |
| `frontier-models` | model release and capability evidence | claim-sidecar mapped |
| `full-stack` | API, database, frontend/backend integration | `full-stack` |
| `android-kotlin` | Android SDK, Kotlin/KMP, Gradle, Jetpack, WebRTC | `android-kotlin` |

Machine consumers use claim maps and note-delta manifests rather than scraping this Markdown file. Note completion, claim admission and Skill qualification remain separate.

## Known gaps｜已知缺口

- Issue #2 tracks incomplete legacy note materialization.
- Issue #7 tracks live authorized YouTube transcript accuracy qualification.
- The v7.1 audit documents missing live compiler, validator, dependency resolver and Google Docs/Sheets adapters.
