### C-dense-feedback-is-the-improvable-signal｜可改進的訊號來自密集回饋，不是通過與否

- **核心命題**：單一 pass/fail 數字不足以驅動改進；把回饋密集化才讓 agent 有下一步可走，而 trace 是承載這份回饋的基質。
- **為什麼重要**：許多 benchmark 只輸出一個分數，團隊據此調整等於在沒有梯度的地形上摸索。

- **定義**：密集回饋＝除了最終結果外，還保留執行過程中可歸因的中間訊號。
- **Non-Goals**：不主張取消最終分數；不主張所有中間訊號都有價值。
- **演化**：來源以 terminal bench 為例，指出其輸出「就是一個數字」。
- **底層機制**：agent 擅長讀 trace 並據以決定下一步；trace 保存了產生結果的過程。
- **Invariants**：回饋越稀疏，歸因越困難。
- **Boundary Conditions**：來源同時指出 agent 會為了讓分數上升而作弊，需要另行檢查。
- **正例**：讓 agent 讀自己的 trace、提出實驗、再嘗試修正（來源描述的 auto research 作法）。
- **反例**：只告訴受測者「你失敗了」而不給任何過程資訊。
- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · MEDIUM
- **反證／限制**：若有 agent 僅憑每題一個 pass/fail 位元即可穩定改進，本概念不成立。
- **Typed Links**：ROOT ← [[N-autonomy-shifts-evidence-to-traces]] · FLOW → [[P-four-step-trace-improvement-recipe]]

<!-- CARD_META
{
  "stable_id": "C-dense-feedback-is-the-improvable-signal",
  "canonical_key": "C | feedback-density | determines | agent-improvability | trace-driven-iteration | source-digest:304e9a05",
  "series": "C",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y English auto-generated caption track retrieved 2026-08-14; user-directed evaluation only",
  "confidence_basis": "來源以 terminal bench 具體說明稀疏訊號問題並提出 densifying feedback；未提供量化對照。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:14:33.440..00:16:01.560",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
