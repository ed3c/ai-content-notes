### K-visual-and-identifier-gap｜投影片、圖表與產品識別字仍不可驗證

- **核心命題**：本批次全部由自動字幕推導，投影片、圖表與若干專有名詞未取得可驗證來源，因此不得當作精確識別依據。
- **為什麼重要**：把自動字幕的拼寫當成產品名或方法名，會把轉錄誤差寫進知識庫。

- **Unknown**：影片中 slide 的實際內容、legal benchmark 圖表數值、產品名稱正確拼寫，以及被字幕寫成 `OPD, OPSD, trySFT` 的 RL 方法名稱。
- **Why Unresolved**：權利依據為 user-directed-evaluation，沒有取得授權的本機影片、creator slides 或人工校對稿。
- **Impact**：`T-trace-judge-cost-comparison` 的精確欄位必須維持 UNKNOWN；產品名稱不得寫入任何下游 claim。
- **Evidence Needed**：授權影片檔、frame SHA-256、timestamp 加 bbox、人工校對的轉錄稿與術語表。
- **Retrieval / Test Plan**：取得可驗證的媒體權利 → 依 `frame_sampling_plan.py` 抽 frame 並保存 digest → 依 `visual-evidence-receipt@1` 記錄 bbox 與標註。
- **Unblock Criteria**：`governance/RIGHTS_ALLOWLIST.json` 出現該影片的 `verified` 記錄，且存在人工校對稿。
- **Priority**：HIGH
- **證據與狀態**：OBSERVATION · SUPPORTED · HIGH
- **Typed Links**：ROOT ← [[N-autonomy-shifts-evidence-to-traces]]

<!-- CARD_META
{
  "stable_id": "K-visual-and-identifier-gap",
  "canonical_key": "K | visual-and-identifier-evidence | blocks | exact-slide-and-name-reconstruction | cvrngaqzq3y-v2-run | run-local-2026-08-14",
  "series": "K",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y English auto-generated caption track retrieved 2026-08-14; user-directed evaluation only",
  "confidence_basis": "字幕本身即顯示不確定拼寫；缺席的媒體與校對稿由本次取材收據直接佐證。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:10:27.920..00:11:03.200",
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:14:08.680..00:14:33.440",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
