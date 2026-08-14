### C-continual-learning-state-planes｜Continual Learning 需要分離三個 State Plane

- **核心命題**：長期 Agent 的 learning 不只更新 model；可更新狀態至少分成 Data、Harness 與 Memory 三個 plane，並使用不同 admission、validation、retention 與 rollback contract。
- **為什麼重要**：若所有學習都塞入一個 append-only memory 或一次模型更新，系統會失去權責、版本與錯誤回復能力。

```text
Data Plane -----+
Harness Plane --+--> Continual Learning --> Replay / Review
Memory Plane ---+
```

- **定義**：
  - Data Plane：執行後形成的 observational/training candidates。
  - Harness Plane：prompt、tools、skills、orchestration 與 execution policy。
  - Memory Plane：跨 run 保留、重組、淘汰與 supersede 的狀態。
- **Non-Goals**：不把所有歷史永遠 append；不讓每個 observation 直接進入 model 或 memory；不把 inference 自動升級成 verified fact。
- **演化**：來源描述 year、5-year、decade 與 lifetime 的長期方向，但沒有已驗證的版本演化時間線。
- **底層機制**：Agent action → trace → mining/adjudication → routing to data、harness 或 memory → replay。
- **Invariants**：三個 plane 的 authority、version 與 evidence grade 分離；memory 支援 forgetting、conflict 與 supersession。
- **Boundary Conditions**：來源未定義 sleep-time/dreaming 的 algorithm、頻率、成本或 oracle；長期狀態還受 privacy、staleness 與 tenant boundary 限制。
- **正例**：Trace-derived memory candidate 經 review、versioning 與 supersession 後才進入長期狀態。
- **反例**：把所有 observations 追加到單一無限成長檔案，既不淘汰也不處理衝突。
- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-three-state-planes]]：`00:16:59–00:18:30`。
  - [[EV-cvrngaqzq3y-memory-not-append-only]]：`00:17:59–00:19:00`。
- **反證／限制**：這是來源提出的架構方向，沒有 longitudinal experiment artifact。
- **Typed Links**：ROOT ← [[N-autonomy-trace-mining]] · DEPENDS_ON → [[K-visual-identifier-evidence-gap]]

<!-- CARD_META
{"stable_id":"C-continual-learning-state-planes","canonical_key":"C | continual-learning | separates | data-harness-memory-planes | long-lived-agents | source-digest:bf993b8d","series":"C","lifecycle":"ACTIVE","revision":1,"source_dependency_key":"youtube-video:CvRngaQZQ3Y","source_provenance":["youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:16:59..00:19:00"],"projection_kind":"state-planes","unresolved_links":[]}
-->
