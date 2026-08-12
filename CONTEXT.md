# CONTEXT.md｜Technical Trigger and Production-Stack Mapping

> Canonical terminology, lifecycle, evidence, and capability mapping contract for converting private card notes into auditable implementation context.  
> 將私有卡片筆記轉換成可稽核技術實作上下文的固定術語、生命週期、證據與 Capability 映射契約。

## 1. Boundary｜邊界

This repository is the canonical **note body and research evidence store**. It does not decide that a Skill is sandbox-qualified or production-routable.

本庫是完整筆記正文與研究證據的 Source of Truth，不負責宣告 Skill 已通過 sandbox qualification 或可進入 production routing。

```text
complete source / transcript
  -> private v6.6 card note
  -> atomic claim map
  -> authenticated note-delta manifest
  -> tech-implementation-atlas impact review
  -> Skill compilation candidate
  -> independent agent-skills-repo qualification
```

Hard invariant:

```text
note completed != claim admitted
claim source-anchored != runtime reproduced
Skill compiled != Skill qualified
signed receipt != lifecycle admission
```

## 2. Canonical classification axes｜固定分類軸

Do not encode all axes into nested directories. A note has one storage category, while machine-readable sidecars carry orthogonal metadata.

不要把所有分類維度塞進巢狀目錄。筆記只使用一個主要儲存類別；其他維度放入機器可讀 sidecar。

| Axis | Canonical values | Purpose |
|---|---|---|
| Domain | `agent-runtime`, `evaluation`, `security-governance`, `retrieval-rag`, `ai-infrastructure`, `model-serving`, `data-trajectory`, `full-stack`, `android-kotlin` | 技術領域 |
| Engineering lifecycle | `discover`, `learn`, `specify`, `design`, `implement`, `verify`, `secure`, `deploy`, `operate`, `observe`, `migrate`, `retire` | 使用者目前要完成的工程階段 |
| Claim kind | `fact`, `inference`, `assumption`, `invariant` | 區分可直接驗證內容與推演 |
| Evidence grade | `E0`–`E6` | 來源與 runtime 成熟度 |
| Skill impact | `none`, `new-candidate`, `update-candidate`, `invalidate`, `deprecate`, `review-and-requalify` | 下游處理，不是自動 admission |
| Artifact plane | `code`, `model`, `data`, `trajectory` | 授權與 provenance 分離 |
| Risk tier | `R0`–`R4` | 權限、網路、秘密與 production 風險 |

### Evidence grades

```text
E0 discovered
E1 primary-source-anchored
E2 independently cross-checked
E3 locally reproduced
E4 sandbox-attested
E5 production-observed
E6 stale or invalidated
```

`E6` is a warning state, not a higher-quality score.

## 3. Domain trigger map｜Domain 觸發映射

The following terms are discovery triggers. They are not approval signals. The downstream router must combine user intent, repository signals, lifecycle, evidence freshness, host compatibility, risk, and qualification state.

以下術語只負責 discovery，不能單獨觸發 production Skill。下游 Router 必須同時檢查 intent、repository signal、lifecycle、evidence freshness、host compatibility、risk 與 qualification。

### agent-runtime

**Trigger phrases**: MCP, Model Context Protocol, tool server, `tools/list`, `tools/call`, Streamable HTTP, agent memory, context routing, model gateway, LLM gateway, fallback, rate limit, spend cap, runtime policy, Claude Code, Codex CLI.

**Capability candidates**:

| Capability ID | Trigger outcome | Required principles | Minimum note evidence |
|---|---|---|---|
| `agent-runtime.mcp-gateway` | MCP transport, OAuth boundary, tool schema, contract tests | schema-first, least-privilege, fail-closed | E1 |
| `agent-runtime.llm-gateway` | model routing, budget, fallback, tenant policy, redaction | policy-before-routing, tenant isolation, evidence-first | E1 |
| `agent-runtime.context-routing` | context selection, working set, prompt distribution | least-context, provenance, deterministic routing | E1 |
| `agent-runtime.agent-memory` | episodic memory, provenance, staleness, contamination | source anchoring, expiry, reversible migration | E1 |

### evaluation

**Trigger phrases**: benchmark, eval, judge, rubric, no-Skill baseline, paired comparison, regression, route regret, trigger precision, trigger recall, task success.

**Capability candidates**: `evaluation.task-contract`, `evaluation.judge-calibration`, `evaluation.skill-baseline`, `evaluation.regression-triage`.

### security-governance

**Trigger phrases**: prompt injection, jailbreak, secret leakage, OAuth, destructive command, policy downgrade, least privilege, sandbox, attestation, cleanup proof, risk tier.

**Capability candidates**: `security.secret-output-guard`, `security.prompt-injection-boundary`, `security.oauth-review`, `security.destructive-command-policy`.

### retrieval-rag

**Trigger phrases**: RAG, retrieval, citation, source anchoring, chunking, embedding, GraphRAG, code graph, AST, LSP, provenance, contradiction.

**Capability candidates**: `retrieval.source-anchored-rag`, `retrieval.citation-verifier`, `retrieval.index-migration`, `retrieval.evidence-graph`.

### ai-infrastructure

**Trigger phrases**: inference gateway, GPU, accelerator, capacity, batching, latency, throughput, observability, FinOps, autoscaling, SLO.

**Capability candidates**: `infrastructure.inference-capacity`, `infrastructure.model-gateway`, `infrastructure.cost-latency-slo`, `infrastructure.observability`.

### model-serving

**Trigger phrases**: quantization, KV cache, continuous batching, speculative decoding, vLLM, TensorRT-LLM, model server, rollback, compatibility.

**Capability candidates**: `serving.quantization`, `serving.batch-cache-policy`, `serving.compatibility`, `serving.rollback`.

### data-trajectory

**Trigger phrases**: dataset, trajectory, trace, provenance, contamination, leakage, synthetic data, license, fine-tuning corpus, replay.

**Capability candidates**: `data.provenance-ledger`, `trajectory.capture`, `data.license-gate`, `data.contamination-guard`.

### full-stack

**Trigger phrases**: API contract, database migration, backend, frontend, authentication, integration test, deployment, rollback, observability.

**Capability candidates**: `full-stack.api-contract`, `full-stack.database-migration`, `full-stack.integration-verification`, `full-stack.release-safety`.

### android-kotlin

**Trigger phrases**: Android SDK, API level, Kotlin, Kotlin Multiplatform, Gradle Kotlin DSL, Jetpack, Compose, WebRTC, emulator, real device, instrumentation test.

**Capability candidates**: `android.sdk-migration`, `android.gradle-kotlin-dsl`, `android.kmp-compatibility`, `android.device-test-orchestration`, `android.webrtc`.

## 4. Principle triggers｜底層原理觸發

| Principle ID | Trigger | Implementation invariant |
|---|---|---|
| `schema-first` | API/tool/event/config contract | 先固定 schema、版本、錯誤形狀，再實作 |
| `least-privilege` | OAuth, token, scope, filesystem, network | 權限按 capability 與 task 收斂 |
| `fail-closed` | stale source, missing evidence, failed assertion | 缺證據或驗證失敗時停止，不自動降級 |
| `idempotency` | replay, retry, incremental sync | 相同輸入與 commit 不產生重複 side effect |
| `evidence-first` | completion, ranking, qualification | 完成宣告必須指向 claim、assertion 與 receipt |
| `source-anchoring` | citation, official docs, transcript | Claim 必須回到 canonical URL、版本、anchor 與 digest |
| `policy-before-routing` | fallback, provider switch, model selection | data/safety/tool/cost policy 先於 availability routing |
| `reversibility` | migration, rollout, deprecation | 變更需要 rollback、supersession 與 invalidation path |

## 5. Card-to-contract compiler map｜卡片到契約的映射

| Card series | Machine use | Downstream artifact |
|---|---|---|
| N | scenario and failure narrative | use case / pre-mortem |
| Q | unknown and contradiction detector | research gap / fallback trigger |
| C | ontology and definition | glossary / capability definition |
| D | atomic evidence | claim entries / source anchors |
| S | decision strategy | workflow branch |
| P | executable practice | Skill steps / scripts / assertions |
| T | comparison matrix | stack selector / compatibility matrix |
| R | lifecycle sequence | migration and phase state machine |
| G | governance | risk, permission, approval, abort policy |
| E | invariant | executable assertion candidate |

`D`, `E`, and `G` cards have the highest priority for claim and assertion extraction. `P` cards may become executable workflow steps only when commands, parameters, prerequisites, and abort boundaries are explicit.

## 6. Atomic claim admission｜原子 Claim Admission

Every claim map must bind one private note to one or more atomic claims. Each claim must contain:

```text
claim id
claim kind
single falsifiable statement
canonical source URL and publisher
source publication/retrieval/version metadata
private note path and Git blob SHA
card/section anchor
Domain, capability, lifecycle, and principle mappings
evidence grade and freshness
artifact-plane license state
status and supersession/contradiction relations
```

Rules:

1. One claim, one falsifiable statement.
2. A search snippet, title, or model memory cannot produce E1.
3. `inference` and `assumption` require review before implementation use.
4. A contradiction creates review state; it never silently overwrites an active claim.
5. Changing the note blob, source version, or claim statement invalidates the previous downstream compile digest.
6. Note admission never raises Skill lifecycle or production routability.

Canonical schema: [`schemas/claim-map.schema.json`](schemas/claim-map.schema.json).

## 7. Note-delta export｜筆記增量匯出

The daily workflow emits a privacy-preserving manifest after the note commit and GitHub read-back succeed.

```text
note commit + claim-map sidecar
  -> verify note frontmatter
  -> recompute Git blob SHA
  -> validate claim-map binding
  -> emit ai-content-note-delta@1
  -> downstream impact review
```

The manifest includes no full note body. It carries note identity, repository/path/blob, source URL, Domain, terms, claim IDs, capability IDs, and the explicit downstream action `review-and-requalify`.

Canonical schema: [`schemas/note-delta.schema.json`](schemas/note-delta.schema.json).

Example:

```bash
python tools/export_note_delta.py \
  --note notes/agent-runtime/2026-07-30-langsmith-llm-gateway-runtime-controls.md \
  --claim-map examples/claim-maps/langsmith-llm-gateway.claim-map.json \
  --source-commit "$GITHUB_SHA" \
  --output /tmp/note-delta.json \
  --check
```

## 8. Trigger prompt contract｜技術實作觸發提示詞

Humans should state the goal, constraints, and expected evidence. They should not need to name a Prompt or Skill.

```text
Goal: <observable engineering outcome>
Repository/target: <path or component>
Constraints: <security, compatibility, production boundary>
Required evidence: <tests, sandbox, source version, receipt>
Unknowns: <what must be researched before implementation>
```

Examples:

```text
在這個 monorepo 建立 OAuth-protected MCP gateway，加入 tools/list、tools/call contract tests，禁止 token 進入 log，不要部署 production。

把這個 Agent 的 memory 遷移成有 provenance、expiry、rollback 的設計；先核對官方來源與現有 schema，再產生 migration assertions。

比較現有 Android Gradle/Kotlin stack 與最新支援矩陣；只在 primary sources 足夠時產生 migration Skill candidate。
```

The downstream Atlas decides Domain, lifecycle, risk, evidence, capability, assertions, host adapter, and unknown-domain fallback.

## 9. Unknown-domain workflow｜未知領域流程

When Domain confidence is low, sources are stale, or claims conflict:

```text
state the knowledge gap
  -> retrieve primary sources
  -> pin version and date
  -> extract atomic claims
  -> separate fact/inference/assumption/invariant
  -> create a minimal reproducible experiment
  -> record assertion output
  -> emit a draft capability or Skill candidate
  -> enter independent qualification
```

Do not persist hidden chain-of-thought. Persist an auditable Decision Trace containing facts, assumptions, unknowns, alternatives, exclusions, claim IDs, commands, assertions, artifacts, and outcome.

## 10. Cross-repository authority｜跨庫權責

| Repository | Authority |
|---|---|
| `ed3c/ai-content-notes` | complete note, note blob, source mapping, claim candidate |
| `ed3c/tech-implementation-atlas` | admitted claims, capability graph, routing, compilation, host distribution |
| `ed3c/agent-skills-repo` | independent runtime evidence, qualification, Arena evaluation, lifecycle admission |

No repository may infer another repository's authority from a status string alone.
