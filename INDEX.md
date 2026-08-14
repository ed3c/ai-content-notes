# Notes Index｜筆記與卡片索引

## Authority boundary｜權威邊界

This file is navigation only. Repository paths, Git blobs, manifests, validator reports, document revisions, sidecar digests and read-back determine existence/completion. A stale index entry is never authority.

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
- Integration status: [`docs/SEMANTIC_YIELD_INTEGRATION_STATUS.md`](docs/SEMANTIC_YIELD_INTEGRATION_STATUS.md)
- v7.0: retained A/B/provenance baseline
- v6.6: historical note provenance

## Semantic Yield cards｜修改後流程卡片

Canonical catalog:

- [`evals/semantic-yield/README.md`](evals/semantic-yield/README.md)

Current coverage on `main`:

| Content ID | Card path | Count | State | Validator |
|---|---|---:|---|---|
| `CvRngaQZQ3Y` | [`evals/semantic-yield/CvRngaQZQ3Y/cards/`](evals/semantic-yield/CvRngaQZQ3Y/cards/) | 10 | `CONTINUE` | `PASS_WITH_DEFERRED_VISUAL_AND_PARTIAL_QG` |

Important distinction:

```text
evals/live/CvRngaQZQ3Y/
  = retained first transcript-only v7.1 batch

evals/semantic-yield/CvRngaQZQ3Y/
  = modified Semantic Yield flow with thesis ranking, projections,
    source-driven cards and deterministic host validation
```

Only the ten cards listed in the Semantic Yield catalog have run the modified flow.

## Legacy v6.6 corpus｜遷移語料

The 22 legacy Google-Doc notes are materialized under `notes/` from the pinned
bootstrap payload (`sha256:b3a80dd4…`). `MIGRATION_MANIFEST.json` is the record;
`tools/materialize_legacy_migration.py --check` is the replay authority.

Only `notes/**` was restored. The archived `README.md`, `INDEX.md`, `RANK.md`,
`CONTEXT.md`, `governance/`, `schemas/` and `templates/` members predate the
v7.1 contracts on `main` and are not authority. These notes stay `v6.6`,
`citation_mapping: pending`, and are review candidates only — materialization
does not mark any Sheet row completed and does not raise Atlas admission.

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

evals/semantic-yield/<content-id>/
├── README.md
├── cards/
├── card-manifest.json
├── knowledge-views.md
├── semantic-validator-report.json
├── semantic-yield.result.json
└── run-state.md
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

Machine consumers use manifests, validator reports, claim maps and note-delta manifests rather than scraping this Markdown file. Note completion, claim admission and Skill qualification remain separate.

## Materialized capabilities｜已實作

- immutable v7.1 prompt lock and versioned contracts;
- deterministic v7.0/v7.1 saved-output A/B replay;
- rights-gated YouTube transcript acquisition and deterministic caption normalization;
- first transcript-only v7.1 output under `evals/live/`;
- regenerated Semantic Yield cards, knowledge projections and source-driven batch under `evals/semantic-yield/`;
- deterministic Semantic Yield artifact validator with partial QG evidence;
- deterministic privacy-preserving historical Git-note delta export.

## Known gaps｜已知缺口

- Issue #2 tracks incomplete legacy note materialization.
- Issue #7 tracks live authorized YouTube transcript accuracy qualification.
- Issue #10 tracks generic compiler host, remaining validators, dependency resolution and transactional persistence.
- Issue #17 tracks card discoverability, Agent routing, state-machine/data-flow documentation and Git Town-compatible stacked delivery.
- Provider-neutral live model invocation and raw-run receipt are not materialized.
- Authorized video-frame/slide evidence is absent for `CvRngaQZQ3Y`; HG-03 remains `DEFERRED`.
- Google Docs/Sheets transactional write/read-back is not materialized.
