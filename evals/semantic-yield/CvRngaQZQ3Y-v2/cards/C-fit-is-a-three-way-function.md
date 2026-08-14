### C-fit-is-a-three-way-function｜任務表現是 model、harness 與 task 的共同擬合

- **核心命題**：agent 的任務表現是 model、harness 與 task/資料分布三者共同擬合的結果，因此不能把回歸單獨歸因於模型。
- **為什麼重要**：把退步歸因於「換了模型」會讓團隊改錯變因；來源主張的工作變成「找好的 fit function」與「找好的資料」。

- **定義**：借用 scikit-learn 的 fit 概念——把資料、harness 與 model 一起擬合，使目標任務通過。
- **Non-Goals**：不宣稱存在單一最佳模型；不宣稱 harness 可以取代模型能力。
- **演化**：來源把「classical machine learning」定位在約六年前，並主張其擬合原則仍適用於 agent-first 世界。
- **底層機制**：演算法形式改變，但「取資料、取 harness、取模型、一起擬合」的流程未變。
- **Invariants**：三個變因中任一改變，任務表現都可能改變。
- **Boundary Conditions**：來源以 vertical、窄任務為主要場景；未涵蓋通用任務全分布。
- **正例**：把 base model 在特定垂直任務上 fine-tune，可達到甚至超越 frontier 表現（來源陳述）。
- **反例**：只看模型排行榜就預期任務表現同步提升。
- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
- **反證／限制**：若任務表現在 harness 與任務分布固定時，仍能單由模型排名預測，本概念的解釋力即失效。
- **Typed Links**：ROOT ← [[N-autonomy-shifts-evidence-to-traces]] · FLOW → [[S-harness-then-tune-then-harness]]

<!-- CARD_META
{
  "stable_id": "C-fit-is-a-three-way-function",
  "canonical_key": "C | task-performance | is-jointly-determined-by | model-harness-task-fit | agent-first-engineering | source-digest:304e9a05",
  "series": "C",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y English auto-generated caption track retrieved 2026-08-14; user-directed evaluation only",
  "confidence_basis": "來源直接提出 model harness task fit 並以 scikit-learn 類比；三因共同性為 inference，未給量化分解。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:12:45.960..00:14:33.440",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
