### D-transport-locator-precision｜三條取材路徑內容一致，但 locator 精度差 4.6 倍

- **核心命題**：youtube-transcript-api、youtube-transcript.ai broker 與 AI-Video-Transcriber 在正規化後取得同一份內容，但每個證據錨所覆蓋的文字量分別是 207、959 與 385 字，且 broker 少收尾 19 秒。
- **為什麼重要**：內容一致會讓人以為取材路徑可以互換。就 Shadow Evidence 而言不能——指向 959 個字的 locator 無法支撐「精確引語」這件事。

- **Entity**：同一支影片的三條字幕取材路徑。
- **Behavior / Case**：以 v2 批次的 15 個證據錨，逐一在三份保留素材上解析。
- **操作手法**：對每個 `timestamp:start..end` 窗口計算命中 cue 數與窗內字數，取中位數比較。
- **獨特特徵**：
  - broker 只回 39 個 cue，單一 cue 可跨約 30 秒並攜帶滾動重複文字；
  - direct-caption 回 550 個 cue，正規化器對它是 no-op，因為它本來就沒有滾動重複；
  - AI-Video-Transcriber 回 543 個 cue，帶約兩倍重複。
- **Shadow Evidence**：`acquisition-comparison.json` 記錄 15 個錨在三條路徑上的解析結果；全部可解析，無一遺失。
- **Outcome**：卡片可跨路徑移植，但證據精度不可移植；預設路徑取 youtube-transcript-api。
- **Comparison Target**：把三條路徑視為等價可替換的作法。
- **證據與狀態**：OBSERVATION · TESTED · HIGH
- **反證／限制**：若在同一組錨上，broker 的窗口字數降到與 direct-caption 同級，此差異即消失；本卡不主張任何一條路徑的轉錄品質較高，只主張定位精度不同。
- **Typed Links**：ROOT ← [[N-autonomy-shifts-evidence-to-traces]] · CONFLICT → [[V-cross-transport-convergence]]

<!-- CARD_META
{
  "stable_id": "D-transport-locator-precision",
  "canonical_key": "D | caption-transports | differ-in | evidence-locator-precision | cvrngaqzq3y-comparison | source-digest:304e9a05",
  "series": "D",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y three retained caption transports compared 2026-08-15; user-directed evaluation only",
  "confidence_basis": "每個數字都由保留素材上的確定性量測得出，非估計；三份素材皆已入庫並經 verify_source_retention.py 綁定。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "artifact:evals/semantic-yield/CvRngaQZQ3Y-v2/acquisition-comparison.json",
    "artifact:sources/CvRngaQZQ3Y/source-manifest.json",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
