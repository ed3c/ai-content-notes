### D-trace-reading-cost-bottleneck｜讀 trace 的成本與 context 上限構成瓶頸

- **核心命題**：讀 trace 的成本約等於 input token 成本 × trace 數量 × 平均 trace 大小，且單一長軌跡本身就塞不進另一個 agent 的 context，因此必須把 context 當成可查詢的外部物件。
- **為什麼重要**：這決定 mining 是「把資料丟進 context」還是「建一個能查詢的系統」。

- **Entity**：大量且超長的 agent trace。
- **Behavior / Case**：與 coding agent（來源點名 Claude Code、Codex、deep agents）的長互動所產生的軌跡。
- **操作手法**：把 trace 視為外部物件並對其查詢，而非整段餵入 context。
- **獨特特徵**：成本同時受 trace 數量與單筆長度影響，兩者都在成長。
- **Shadow Evidence**：來源以「input token cost × 數量 × 平均大小」描述估算方式。
- **Outcome**：需要建立能有效率地從其他 agent 資料中挖掘的 agent。
- **Comparison Target**：直接把整份 trace 餵進另一個模型的作法。
- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · HIGH
- **反證／限制**：若長 coding agent 軌跡能被另一個 agent 完整讀入並有效分析，此瓶頸不成立。
- **Typed Links**：ROOT ← [[P-four-step-trace-improvement-recipe]] · CONFLICT → [[C-dense-feedback-is-the-improvable-signal]]

<!-- CARD_META
{
  "stable_id": "D-trace-reading-cost-bottleneck",
  "canonical_key": "D | trace-corpus | is-bounded-by | reading-cost-and-context-limit | trace-mining-systems | source-digest:304e9a05",
  "series": "D",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y English auto-generated caption track retrieved 2026-08-14; user-directed evaluation only",
  "confidence_basis": "成本結構與 context 不足由來源直接描述並點名具體 coding agent。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:06:42.400..00:07:36.880",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
