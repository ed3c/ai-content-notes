### C-continual-learning-state-planes｜Continual Learning 必須更新三個 State Plane

- **核心命題**：長期 Agent 的 continual learning 不只更新 weights；來源把可更新狀態分成 observational/training data、harness 與 memory 三個平面。
- **為什麼重要**：若所有學習都塞進單一 memory file 或單一 fine-tune，系統會失去更新權責、驗證邊界與 rollback 能力。

- **定義**：
  - Data Plane：Agent 在環境中執行後形成的 observational/training data。
  - Harness Plane：prompt、tools、skills、orchestration 與 execution scaffolding 的更新。
  - Memory Plane：跨 run 保留、整理、淘汰與重組的長期狀態。
- **Non-Goals**：
  - 不是把所有歷史 append 到一個無限成長的檔案。
  - 不是每次觀察都立即寫回 weights。
  - 不是未經 eval 就把 trace-derived inference 當成 memory fact。
- **演化**：來源描述面向 year、5-year、decade、lifetime 的長期 Agent 假設，但沒有已驗證的版本演化資料。
- **底層機制**：
  1. Agent 在環境採取 actions，產生 traces。
  2. Trace mining 決定哪些觀察應成為 training data、harness patch 或 memory candidate。
  3. Sleep-time／dreaming 類背景處理重新整理全生命週期 traces。
  4. 每個 plane 使用不同 admission、validation、retention 與 rollback contract。
- **Invariants**：
  - 三個 plane 的 authority、version 與 evidence grade 分離。
  - Memory update 必須支援 supersession、forgetting 與 conflict handling。
  - Production observations 不得自動升級成 verified truth 或 training eligibility。
- **Boundary Conditions**：
  - 來源未定義 sleep-time/dreaming 的具體 algorithm、頻率、成本或 oracle。
  - 長期記憶涉及 privacy、staleness、tenant boundary 與錯誤累積。
- **正例**：[[D-four-stage-trace-improvement-loop]]
- **反例**：把 Agent 視為 append-only log，永遠只追加、不淘汰、不重寫、不記錄 supersession。

- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-three-state-planes]]：00:16:59–00:18:30；來源依序描述 observational/training data、harness updates 與 memory。
  - [[EV-cvrngaqzq3y-memory-not-append-only]]：00:17:59–00:19:00；來源明確排除長期 Agent 只使用巨大 append-only file。
- **反證／限制**：三平面架構在來源中是設計主張，沒有 longitudinal experiment 或 failure-rate artifact。
- **Typed Links**：
  - ROOT ← [[N-trace-data-to-agent-improvement-loop]]
  - ROOT ← [[D-four-stage-trace-improvement-loop]]
  - DEPENDS_ON → [[K-auto-caption-identifiers-unverified]]

<!-- CARD_META
{
  "stable_id": "C-continual-learning-state-planes",
  "canonical_key": "C | continual-learning | separates | data-harness-memory-state-planes | long-lived-agents | source-digest:bf993b8d",
  "series": "C",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "三個平面由來源直接陳述；authority/retention/rollback 分離是為避免狀態污染而做的 bounded systems inference。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:16:59..00:19:00",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->
