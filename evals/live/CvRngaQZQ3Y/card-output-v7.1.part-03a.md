### C-model-harness-task-fit｜Agent 能力是 Joint Fit，不是單一 Model 屬性

- **核心命題**：Task performance 應被建模為 model、harness 與 task/data 的 joint fit；任何一層變動都可能改寫 Agent 行為。
- **為什麼重要**：這能避免把 prompt/tool/orchestration 的不足錯判成 model intelligence 不足，也避免只靠換 model 解決可由 harness 修復的問題。

- **定義**：在固定 task contract 下，選擇 model，配置 prompt/tools/skills/memory/orchestration 的 harness，並用資料與 eval 反覆 fit，使目標行為通過驗收。
- **Non-Goals**：
  - 不是用單一 leaderboard score 選 model。
  - 不是假設更大的 model 在所有 task 都最划算。
  - 不是將 eval score 上升直接等同 production value。
- **演化**：來源以 scikit-learn 的 fit 概念作類比，但未提供版本化歷史；時間演化為 UNKNOWN。
- **底層機制**：
  1. Model 提供基礎 capability。
  2. Harness 改變 context、tool affordance、feedback 與 execution path。
  3. Task/data 定義要 hill-climb 的目標與分布。
  4. Traces 揭示三者的 mismatch，eval 則提供可重播 oracle。
- **Invariants**：
  - 比較時保持 task、eval、time window 與 measurement contract 一致。
  - Model/harness/data identity 必須可追溯。
  - Auto-research 產生的 score improvement 必須防止 cheating 與 holdout regression。
- **Boundary Conditions**：
  - 沒有 stable task definition 或 held-out data 時，fit 可能只是 overfit。
  - Harness 已飽和且錯誤來自缺失 capability 時，weights update 才可能合理。
- **正例**：[[D-harness-finetune-harness-sandwich]]
- **反例**：不固定 task/eval 就直接比較兩個 model，或一次同時改 model、prompt、tools 與 dataset。

- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-fit-concept]]：00:12:57–00:14:28；來源將 classical ML fit 類比到 model–harness–task fit。
  - [[EV-cvrngaqzq3y-auto-research-risk]]：00:14:28–00:14:58；來源指出 Agent 能讓 score 上升，但可能作弊。
- **反證／限制**：來源未提供一個可直接重跑的 joint-fit algorithm、資料集或統計檢定。
- **Typed Links**：
  - ROOT ← [[D-harness-finetune-harness-sandwich]]
  - FLOW → [[S-model-harness-task-fit-iteration]]
  - VALIDATED_BY → [[V-trace-improvement-procedure-replay]]

<!-- CARD_META
{
  "stable_id": "C-model-harness-task-fit",
  "canonical_key": "C | model-harness-task-fit | defines | joint-agent-performance-function | agent-development | source-digest:bf993b8d",
  "series": "C",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "概念由來源直接提出；invariants 與 anti-cheating boundary 是由來源風險陳述推導的 bounded inference。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:12:57..00:16:59",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->
