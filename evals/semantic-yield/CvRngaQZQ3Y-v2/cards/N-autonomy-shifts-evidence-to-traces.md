### N-autonomy-shifts-evidence-to-traces｜自主性換走了靜態可預測性，證據面因此移到 runtime trace

- **核心命題**：過去四年以確定性換取自主性之後，agent 行為不再能靠讀原始碼推得，改進所依據的觀測面因而移到可重播的 runtime trace。
- **為什麼重要**：若團隊仍以「讀 prompt 與 orchestration 原始碼」作為主要判斷方式，就無法回答 compaction 之後是否退化、換模型會不會更好這類只在執行軌跡上成立的問題。

- **核心衝突**：
  - 讀程式碼可以在腦中推演函式如何互相呼叫（來源以左側 code block 為例）。
  - agent 由 prompt、tools、skills、hooks、middleware 與 agent 間編排共同構成，人難以推斷一次 prompt 變更在規模下如何影響行為。
  - 同一個 prompt 變更在 medical 與 law 兩個 domain 的效果並不相同。
- **角色矩陣**：
  - 主角：要持續改進 production agent 的工程團隊。
  - 對立面：自主執行帶來的不可預測性、跨 domain 差異。
  - 次要變量：tracing 是否開啟、trace 是否集中、誰去讀。
- **Impact Anchors**：
  - [[EV-cvrngaqzq3y-v2-determinism-for-autonomy]]：`00:04:19.600–00:04:43.280`；來源說自 ChatGPT moment 起的四年間「trading determinism for autonomy」。
  - [[EV-cvrngaqzq3y-v2-code-vs-agent-reasoning]]：`00:03:29.560–00:04:19.600`；來源對比讀 code 與讀 agent 的差異，並點名 domain 差異。
  - [[EV-cvrngaqzq3y-v2-observability-coupling]]：`00:02:21.800–00:03:08.600`；來源把 observability 與 continual learning 綁在同一個回饋系統。
- **完整劇情鏈**：
  1. 起始狀態：團隊把 agent 投入真實環境運作。
  2. 壓力累積：行為由多層元件共同生成，靜態閱讀不再足以解釋結果。
  3. 決策／事件：把每次操作產生的 trace 全部保存下來。
  4. 轉折：改進問題從「改哪一行」變成「查哪一段軌跡」。
  5. 結果：trace 成為改進的基質，而非事後除錯的附屬品。
- **生態背景**：來源將此描述為整個領域的位移，而非單一團隊的工程偏好。
- **未解段落**：來源未提供量化證據說明靜態審查在何種規模下開始失效。
- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
- **反證／限制**：若有團隊在不收集 trace 的情況下，仍能穩定且可量測地改進 production agent，本命題即被推翻。
- **Typed Links**：FLOW → [[C-fit-is-a-three-way-function]] · FLOW → [[P-four-step-trace-improvement-recipe]] · DEPENDS_ON → [[K-visual-and-identifier-gap]]

<!-- CARD_META
{
  "stable_id": "N-autonomy-shifts-evidence-to-traces",
  "canonical_key": "N | agent-autonomy | shifts | evidence-surface-to-runtime-traces | production-agent-systems | source-digest:304e9a05",
  "series": "N",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y English auto-generated caption track retrieved 2026-08-14; user-directed evaluation only",
  "confidence_basis": "來源明確陳述 determinism/autonomy 取捨與 code/agent 對比；因果鏈為 bounded inference，無獨立實驗佐證。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:02:21.800..00:04:43.280",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
