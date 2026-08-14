### C-model-harness-task-fit｜Agent 能力是 Model、Harness、Task/Data 的 Joint Fit

- **核心命題**：Agent 的任務表現不是 model 的單一屬性，而是 model、harness 與 task/data 在同一 evaluation contract 下的 joint fit。
- **為什麼重要**：它能把 base capability、context、tools、memory 與 task distribution 分開診斷，避免把所有失敗都歸因於 model。

```text
Data / Traces
      |
      v
fit(Model, Harness, Task / Distribution) -> Agent Performance
             |
             +-- Prompt / Context
             +-- Tools / Skills
             +-- Hooks / Middleware
             +-- Memory / Compaction
             +-- Orchestration / Policies
```

- **定義**：Model 提供基礎 capability；Harness 改變可見 context、可採取 actions 與 execution path；Task/Data 定義目標、分布、成本與 guardrails；Traces 暴露三者 mismatch。
- **Non-Goals**：
  - 不用單一 general benchmark 取代 production task contract。
  - 不在一次 experiment 同時更換 model、prompt、tools 與 dataset 後宣稱已找到原因。
  - 不把 eval score 上升自動等同 production value。
- **Invariants**：
  - 比較使用同一 task distribution、eval、時間範圍與成本口徑。
  - Training、development、eval 與 holdout 分離。
  - 更新綁定 model、harness、dataset、task mix 與 artifact digest。
- **Boundary Conditions**：Task drift 會讓既有 fit 失效；缺乏 stable task definition 時，fit 可能只是 overfit。
- **正例**：先用能力較高 model 建立 feasibility ceiling，再固定 eval 比較 harness patch、較低成本 model 與 narrow fine-tuning。
- **反例**：只修改 system prompt 語氣，卻不處理 tool、memory 或 context interface。

- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-fit-concept]]：`00:12:57–00:14:28`；來源把 fit 概念套用到 model、harness 與 task。
  - [[EV-cvrngaqzq3y-auto-research-risk]]：`00:14:28–00:14:58`；來源指出自動提高 score 仍可能利用評測漏洞。
- **反證／限制**：來源沒有提供可直接重跑的 joint-fit algorithm、公開 dataset 或 production causal attribution。
- **Typed Links**：
  - ROOT ← [[N-autonomy-trace-mining]]
  - FLOW → [[S-harness-finetune-harness]]
  - FLOW → [[T-trace-judge-comparison]]
  - VALIDATED_BY → [[V-semantic-yield-replay]]

<!-- CARD_META
{
  "stable_id": "C-model-harness-task-fit",
  "canonical_key": "C | model-harness-task-fit | defines | joint-agent-performance-function | agent-development | source-digest:bf993b8d",
  "series": "C",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "Agent optimization under a fixed task/evaluation contract",
  "confidence_basis": "Source-supported fit analogy plus bounded engineering constraints.",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": ["youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:12:57..00:14:58"],
  "projection_kind": "equation",
  "unresolved_links": []
}
-->
