### V-cross-transport-convergence｜三條路徑正規化後收斂，且重現了先前判定遺失的 v1 產物

- **核心命題**：三條取材路徑經滾動字幕正規化後收斂到同一份內容；其中 broker 路徑重現的 digest 與先前記錄為遺失的 v1 逐字稿位元完全相同。
- **為什麼重要**：先前把 v1 素材判為不可挽回，因而把 leaf 04 判為永久受阻。該判斷被本次執行推翻。

- **Target Assertion**：`youtube-transcript.ai` 取材經 `normalize_rolling_transcript.py` 後，可重現 v1 記錄的 `normalized_transcript_sha256`。
- **Verification Method**：重新取材、正規化、計算 SHA-256，與 `evals/live/CvRngaQZQ3Y/card-manifest.json` 記錄值比對。
- **Oracle**：`bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462`。
- **Environment / Fixture**：本機執行 2026-08-15；三份素材保留於 `sources/CvRngaQZQ3Y/` 並經綁定驗證。
- **Procedure**：三條路徑各取材一次 → 各自正規化 → 比對 digest 與詞袋重疊 → 以 15 個 v2 錨逐一解析。
- **Expected Result**：內容收斂；v1 digest 重現。
- **Observed Result**：PASS
- **Verdict**：PASS
- **Artifacts**：`acquisition-comparison.json`、`sources/CvRngaQZQ3Y/broker/normalization-report.json`、`sources/CvRngaQZQ3Y/source-manifest.json`。
- **Limitations**：三條路徑共用同一個 `youtube-video:CvRngaQZQ3Y` 依賴與同一份自動字幕，因此彼此一致只是傳輸保真度，**不構成獨立佐證**；另有兩條需要真實 rights basis 的路徑未執行。
- **證據與狀態**：OBSERVATION · TESTED · HIGH
- **反證／限制**：若同一流程再次執行而 digest 不再吻合，重現宣稱即失效。
- **Typed Links**：ROOT ← [[D-transport-locator-precision]] · DEPENDS_ON → [[K-visual-and-identifier-gap]]

<!-- CARD_META
{
  "stable_id": "V-cross-transport-convergence",
  "canonical_key": "V | three-caption-transports | verifies | normalized-content-convergence | cvrngaqzq3y-comparison | run-local-2026-08-15",
  "series": "V",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y three retained caption transports compared 2026-08-15; user-directed evaluation only",
  "confidence_basis": "digest 比對為位元級相等，非相似度判斷；比對雙方皆可回讀。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "artifact:evals/semantic-yield/CvRngaQZQ3Y-v2/acquisition-comparison.json",
    "artifact:evals/live/CvRngaQZQ3Y/card-manifest.json",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
