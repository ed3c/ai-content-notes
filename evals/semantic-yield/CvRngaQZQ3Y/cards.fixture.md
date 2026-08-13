### N-autonomy-trace-mining-paradigm｜Autonomy 讓 Runtime Trace 成為主要改進證據

- **核心命題**：Agent 以較低的靜態可預測性換取自主性，因此系統改進必須從只讀代碼轉向可重播的 Runtime Trace Mining。
- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-autonomy-determinism]]

### C-model-harness-task-fit｜Model、Harness、Task 必須共同擬合

- **核心命題**：Agent 的 Task Performance 是 Model、Harness 與 Task/Data Distribution 的共同函數，不能只歸因於模型排行榜。
- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-fit-function]]

### P-trace-driven-agent-improvement-cycle｜可重播的 Trace 改進程序

- **核心命題**：Trace 必須被轉成 Frozen Eval、單變量 Patch、Canary 與 Rollback Receipt，才構成可驗收的改進流程。
- **Execution Status**：UNTESTED
- **證據與狀態**：NORMATIVE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-four-stage-loop]]

### T-trace-judge-decision-matrix｜Trace Judge 比較框架

- **核心命題**：Frontier 與 Open-model Judge 應在同一 Task、Score Contract 與完整成本口徑下比較；未知欄位維持 UNKNOWN。
- **證據與狀態**：INFERENCE · SUPPORTED · LOW
  - [[EV-cvrngaqzq3y-open-model-cost-claim]]：來源宣稱成本可低 1–2 個數量級。

### D-trace-scale-cost-context-bottleneck｜Trace Scale 的成本與 Context 雙重瓶頸

- **核心命題**：Long-horizon Trace 的長度與數量會同時撞上 Context Window 與 Input-token Cost，迫使系統使用外部查詢而非完整塞入 Prompt。
- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-trace-scale]]

### C-continual-learning-state-planes｜Data、Harness、Memory 三個狀態平面

- **核心命題**：長期 Agent 必須分離 Data、Harness 與 Memory 的 Authority、Validation、Retention 與 Rollback。
- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-three-state-planes]]

### K-video-visual-evidence-unavailable｜投影片與圖表證據仍被阻擋

- **核心命題**：沒有授權的 Frame Artifact、Frame Digest 與 BBox Locator 時，公式與流程圖只能由文字關係投影，不得宣稱為精確投影片重建。
- **證據與狀態**：OBSERVATION · TESTED · HIGH
  - [[VIS-fit-equation]]：BLOCKED_WITH_K_CARD
  - [[VIS-harness-sandwich]]：BLOCKED_WITH_K_CARD
