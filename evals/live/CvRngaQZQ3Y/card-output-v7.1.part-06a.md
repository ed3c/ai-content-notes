### K-auto-caption-identifiers-unverified｜Auto-Caption 的專有名詞與版本仍未解鎖

- **核心命題**：目前 transcript 足以支援概念與流程級編譯，但不足以對人㉩、產品、model version、benchmark 與 research acronym 做高信心 canonical naming。
- **為什麼重要**：錯一個 model version、產品名稱或 benchmark 名稱，就可能讓後續技術選型、搜尋與 claim mapping 指向錯誤實體。

- **Unknown**：
  - 影片標題使用「Vivek Trivedy」，caption 開場顯示「I'm Vic」；兩者是否為暱稱、截斷或 ASR error 未校對。
  - Candidate strings 包含 `GPT 5.5`／`55`、`GLM 5.2`、`Cloud Code`、`LangSplat engine`、`OPD`、`OPSD`、`trySFT` 與 `terminal benches`；canonical spelling/version 尚未確認。
  - Broker 未提供原始 YouTube VTT/SRT、caption track ID 或 punctuation provenance。
- **Why Unresolved**：取得的是 `en (auto-generated)` secondary transport；raw platform caption 不可回讀。正規化器只執行 exact duplicate removal 與 footer isolation，刻意不修正任何詞彙。
- **Impact**：
  - [[D-open-model-trace-judge-cost-claim]] 維持 LOW confidence。
  - 無法安全建立精確 model/product/benchmark entity graph。
  - Claim mapping 與外部搜尋必須等待 canonical spelling。
- **Evidence Needed**：
  - Creator slides、官方 agenda/description 或 creator-reviewed transcript。
  - 原始 VTT/SRT 或逐 timestamp 人工校對記錄。
  - 每個 identifier 的 canonical URL/version 與 reviewer receipt。
- **Retrieval / Test Plan**：
  1. 以 00:00:13–00:19:30 的 timestamp 對照影片畫面、字幕與官方活動資料。
  2. 為每個 high-impact identifier 記錄 raw token、canonical form、locator、reviewer 與 evidence digest。
  3. 重跑 canonical-key resolution，若實體改變則用 `SUPERSEDES` 更新受影響卡片。
- **Unblock Criteria**：所有會改變技術選型或 claim identity 的名稱、版本與 acronym 均有至少一個可回讀的一手 anchor。
- **Priority**：HIGH

- **證據與狀態**：OBSERVATION · TESTED · HIGH
  - [[EV-cvrngaqzq3y-normalization-report]]：GitHub Actions run `31698798606`；raw subject 11,290 words 正規化為 3,797 words，移除 7,214 個 adjacent duplicate tokens、279 個 cross-cue overlap tokens、542 次 exact collapse，並隔離 240 個 transport-footer characters。
  - [[EV-cvrngaqzq3y-source-manifest]]：source manifest 狀態為 `needs-review`，且明示 raw YouTube caption track identity 不可用。
- **反證／限制**：正規化測試只證明 deterministic transport-noise removal；不證明 auto-caption 的 lexical accuracy。
- **Typed Links**：
  - ROOT ← [[D-open-model-trace-judge-cost-claim]]
  - ROOT ← [[C-continual-learning-state-planes]]

<!-- CARD_META
{
  "stable_id": "K-auto-caption-identifiers-unverified",
  "canonical_key": "K | auto-caption-identifiers | blocks | canonical-entity-resolution | video-CvRngaQZQ3Y | run-31698798606",
  "series": "K",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "GitHub Actions normalization artifacts可直接檢查，因此 gap 的存在為 HIGH-confidence observation；具體 canonical spellings仍未知。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "actions-run:31698798606#normalized/normalization-report.json",
    "source-manifest:sm-youtube-CvRngaQZQ3Y-youtube-transcript-ai",
    "sha256:b14ef715744a2d5c0bab99da8bfe4fdcf46a90ebb513dc4a06e6e489177a2a0e",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": [],
  "normalization_report_sha256": "sha256:363f2fd1285986330ad60950b84fc627b383c57c013a05cd89e67934ecffbced"
}
-->
