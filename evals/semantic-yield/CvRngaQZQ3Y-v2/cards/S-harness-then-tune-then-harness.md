### S-harness-then-tune-then-harness｜依回饋延遲排序介入：先 harness、再微調、再回 harness

- **核心命題**：改進順序應由回饋延遲決定——harness engineering 約兩分鐘就能得到回饋，先做；等它的天花板飽和，再考慮 fine-tune；之後視需要再回到 harness。
- **為什麼重要**：反過來先微調，會用最慢的迴圈去試最不確定的假設。

- **Objective**：在最短時間內取得可據以決策的回饋。
- **Preconditions**：已有 trace，且有可重複的評估方式。
- **策略邏輯**：先用低延遲手段窮盡可得的提升，再動用高成本手段跨越門檻。
- **Ecological Context**：來源說很多團隊只做 harness engineering 就已滿足客戶場景。
- **Trade-offs**：fine-tune 把成本結構從 token cost 移到 hardware cost；在高推論量下來源認為跑叢集更便宜。
- **Pre-mortem Glitches**：在 harness 尚未飽和時就微調，會把提升誤歸因於權重更新。
- **Success Criteria**：harness 調整已無可量測提升，才啟動微調。
- **Implementation Path**：harness 調整 → 觀察飽和 → 在窄垂直任務上微調 → 視需要再做 harness。
- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · MEDIUM
- **反證／限制**：若某團隊在越過來源所述門檻後，仍持續從 prompt 調整取得可量測提升，此排序即不成立。
- **Typed Links**：ROOT ← [[C-fit-is-a-three-way-function]] · FLOW → [[T-trace-judge-cost-comparison]]

<!-- CARD_META
{
  "stable_id": "S-harness-then-tune-then-harness",
  "canonical_key": "S | improvement-effort | is-ordered-by | feedback-latency | harness-and-finetune-sandwich | source-digest:304e9a05",
  "series": "S",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y English auto-generated caption track retrieved 2026-08-14; user-directed evaluation only",
  "confidence_basis": "來源給出約兩分鐘的 harness 回饋時間與 sandwich 順序；門檻位置未量化。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:09:00.920..00:10:27.520",
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:16:01.560..00:16:51.600",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
