### V-projection-replay-v2｜本次投影重播的驗證結果

- **核心命題**：本批次的五個知識投影可由已保留的字幕素材與已提交的 relation graph 確定性重播。
- **為什麼重要**：若不可重播，投影就只是一次性輸出，無法用於後續比較。

- **Target Assertion**：相同 source pack 與相同 relation graph 會產出相同的 projection bundle 與 knowledge views。
- **Verification Method**：以保留素材重建 source pack、relation graph、projection bundle，並比對摘要。
- **Oracle**：`relation-graph.json` 的 `graph_subject_digest` 與 `projection-bundle.json` 的 `source_graph_digest`。
- **Environment / Fixture**：本機執行；素材保留於 `sources/CvRngaQZQ3Y/` 並由 `verify_source_retention.py` 綁定。
- **Procedure**：取材 → 保留並驗證綁定 → source pack → relation graph → projection plan → knowledge views → HG 評估。
- **Expected Result**：五種投影全部渲染，來源未給的數值維持 UNKNOWN。
- **Observed Result**：PARTIAL
- **Verdict**：PARTIAL
- **Artifacts**：`source-pack.json`、`relation-graph.json`、`projection-bundle.json`、`knowledge-views.md`、`semantic-yield.result.json`。
- **Limitations**：未做跨執行的位元級重播比對；視覺模態全部封鎖；外部 QG 僅涵蓋既有子集。
- **證據與狀態**：OBSERVATION · TESTED · MEDIUM
- **反證／限制**：若以相同輸入重跑而 thesis 排序、節點 ID 或投影內容改變，重播宣稱即失效。
- **Typed Links**：ROOT ← [[P-four-step-trace-improvement-recipe]] · DEPENDS_ON → [[K-visual-and-identifier-gap]]

<!-- CARD_META
{
  "stable_id": "V-projection-replay-v2",
  "canonical_key": "V | projection-bundle | verifies | deterministic-replay-from-retained-source | cvrngaqzq3y-v2-run | not-run",
  "series": "V",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y English auto-generated caption track retrieved 2026-08-14; user-directed evaluation only",
  "confidence_basis": "本次確實執行了完整鏈路並保留 artifacts；但未做第二次獨立重跑比對，故為 PARTIAL。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:00:01.309..00:20:00.683",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
