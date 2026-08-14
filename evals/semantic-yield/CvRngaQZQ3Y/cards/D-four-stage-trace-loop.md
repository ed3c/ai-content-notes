### D-four-stage-trace-loop｜Ship、Collect、Mine、Experiment 的最小案例

- **核心命題**：先讓 Agent 執行，再收集 traces、挖掘 decision-relevant cases，最後以相同 evaluation contract 比較新的 prompt、tool 或 orchestration patch。
- **為什麼重要**：它把 observability 接回 deployment decision，提供改進系統的最小可操作骨架。
- **Entity**：負責 production Agent 的工程團隊。
- **Behavior / Case**：Execution data 成為下一版 Agent 的 experiment input。
- **操作手法**：
  1. Ship：在環境中執行 Agent。
  2. Collect：保存 tool calls、messages、interactions 與 outcome。
  3. Mine：針對明確問題建立 selected/rejected cases。
  4. Experiment：在相同 eval 下比較 patch。
- **獨特特徵**：最後一步要求可比較結果，而不是只讀摘要或依直覺修改。
- **Shadow Evidence**：
  - [[EV-cvrngaqzq3y-stage-ship]]：`00:00:44–00:01:17`。
  - [[EV-cvrngaqzq3y-stage-collect]]：`00:01:17–00:01:47`。
  - [[EV-cvrngaqzq3y-stage-mine-experiment]]：`00:01:47–00:02:17`。
- **Outcome**：SOURCE_REPORTED；來源把此流程作為 improvement recipe，但未提供可直接檢查的 benchmark output。
- **Comparison Target**：只保存 logs、沒有 question/eval/update 的 passive observability。
- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · MEDIUM
- **反證／限制**：資料品質、oracle、privacy 或 feedback latency 失敗仍會讓閉環無效。
- **Typed Links**：FLOW → [[N-autonomy-trace-mining]] · FLOW → [[P-trace-cycle]] · FLOW → [[C-model-harness-task-fit]]

<!-- CARD_META
{"stable_id":"D-four-stage-trace-loop","canonical_key":"D | agent-team | executes | ship-collect-mine-experiment | production-agent-improvement | source-digest:bf993b8d","series":"D","lifecycle":"ACTIVE","revision":1,"source_dependency_key":"youtube-video:CvRngaQZQ3Y","source_provenance":["youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:00:44..00:02:17"],"unresolved_links":[]}
-->
