### T-trace-judge-comparison｜Frontier Reference 與 Open-Model Candidate 的可驗證比較框架

- **核心命題**：來源支持建立 Trace Judge 的比較框架，但不足以填滿精確 model revision、benchmark score 或完整成本表；未知欄位應保留為 UNKNOWN，而不是取消整張比較卡或補造數字。
- **為什麼重要**：大量長 traces 的 judge 成本可能成為主要瓶頸；比較介面能把 source-reported claim 與真正待驗證欄位分開。
- **Decision Use**：決定何時用高能力 model 建立 capability reference，何時測試較低成本 model 作規模化 judge。
- **Comparison Contract**：相同 task cohort、judge rubric、time window、output contract 與成本口徑；缺值規則為 UNKNOWN。

| Dimension | Frontier reference | Open-model candidate |
|---|---|---|
| 主要角色 | 建立 task feasibility / capability ceiling | 測試較低成本的規模化 judging |
| Exact model revision | UNKNOWN | UNKNOWN |
| Benchmark artifact | UNKNOWN | UNKNOWN |
| Quality result | 來源作為 reference | 來源稱可大致接近；未有可回讀 score artifact |
| Cost result | 未提供完整表 | 來源稱低約 1 或 2 個數量級；未驗證 |
| Harness dependency | 仍需 task contract | 來源強調 trace-informed guidance / harness |
| 決策狀態 | PROVISIONAL | PROVISIONAL |

- **Interpretation**：來源提出的方向是用強 model 證明可行，再測試 open/smaller model 與 harness 是否能在同一 task 上降低成本；這不是對所有 workload 的 universal law。
- **Decision Threshold**：來源沒有提供可靠的固定 volume threshold；切換條件應由實測 quality、cost、latency 與 review burden 決定。
- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · LOW
  - [[EV-cvrngaqzq3y-open-model-cost-claim]]：`00:08:25–00:08:55`；來源保留「1 或 2 個數量級」的成本尺度。
  - [[EV-cvrngaqzq3y-model-cost-path]]：`00:07:53–00:10:25`；來源描述 strongest-model reference、較低成本 model、harness 與後續更新路徑。
- **反證／限制**：固定 benchmark、相同 rubric 與完整成本口徑若無法重現品質/成本結果，來源主張會被削弱或 falsified。
- **Typed Links**：ROOT ← [[C-model-harness-task-fit]] · FLOW → [[P-trace-driven-improvement-cycle]] · DEPENDS_ON → [[K-visual-identifier-evidence-gap]]

<!-- CARD_META
{"stable_id":"T-trace-judge-comparison","canonical_key":"T | trace-judge-selection | compares | frontier-reference-and-open-model-candidate | trace-mining | source-digest:bf993b8d","series":"T","lifecycle":"ACTIVE","revision":1,"source_dependency_key":"youtube-video:CvRngaQZQ3Y","source_provenance":["youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:07:53..00:10:25"],"projection_kind":"comparison-matrix","unresolved_links":[]}
-->
