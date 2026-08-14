### P-four-step-trace-improvement-recipe｜四步 trace 改進程序

- **核心命題**：持續改進 agent 的可執行程序是：先上線、收集 trace、對 trace 做 data mining、再以資料驅動方式跑實驗。
- **為什麼重要**：缺少任一步，改進就退回成無法歸因的 prompt 微調。

- **Scenario**：已有 agent 可投入真實環境運作。
- **Value**：把散落的執行結果轉成可比較、可重播的實驗輸入。
- **Prerequisites**：tracing 已開啟；trace 集中在一個 tracing project（來源說可以 per agent 或跨 agent 集中）。
- **Inputs**：trace 資料、要回答的 decision question、模型與 harness 版本資訊。
- **Exploit / Procedure**：
  1. 上線 agent，使其在環境中運作並產生回饋。
  2. 保存每次操作產生的 trace（tool call、輸出訊息、API、CLI）。
  3. 對 trace 做 mining，產出 eval／資料集／給人閱讀的內容。
  4. 以先前 trace 為基準跑實驗，判斷新 prompt、工具或編排是否真的改善。
- **Expected Output**：可重播的 eval、可比較的實驗結果、供人審閱的摘要。
- **Rollback**：若實驗結果不可歸因，退回上一版 harness／模型設定並保留失敗紀錄。
- **Failure Handling**：trace 不完整時先修 instrumentation，不以殘缺資料下結論。
- **Security / Privacy Constraints**：來源提及 legal、medical 等高信任場域仍需人審；本 repo 另要求取材權利與素材保留。
- **Toolset**：tracing project、trace mining agent、eval runner；來源提及的產品名稱未能確認拼寫。
- **Execution Status**：UNTESTED
- **Validated By**：[[V-projection-replay-v2]]
- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · HIGH
- **Typed Links**：ROOT ← [[N-autonomy-shifts-evidence-to-traces]] · VALIDATED_BY → [[V-projection-replay-v2]] · DEPENDS_ON → [[D-trace-reading-cost-bottleneck]]

<!-- CARD_META
{
  "stable_id": "P-four-step-trace-improvement-recipe",
  "canonical_key": "P | improvement-team | executes | ship-collect-mine-experiment | production-agent-improvement | source-digest:304e9a05",
  "series": "P",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y English auto-generated caption track retrieved 2026-08-14; user-directed evaluation only",
  "confidence_basis": "四個步驟由來源逐一列出並命名；步驟間的必要性為來源主張，未經本次執行驗證。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:01:11.520..00:02:21.440",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
