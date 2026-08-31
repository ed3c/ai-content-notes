### P-oom-failure-injection-loop｜以「第 N 次配置失敗」遞增迴圈把 OOM 路徑逐一走完

- **核心命題**：替換 malloc 為可設定在第 N 次配置時失敗的版本，從 N=1 起跑同一段操作並檢查錯誤處理，N 遞增到整段操作不再遇到模擬失敗為止；整個迴圈跑兩次，一次只失敗一次，一次首次失敗後持續失敗。
- **為什麼重要**：這把「錯誤處理路徑有沒有被測到」從抽樣變成窮舉，而且同一個骨架可原樣套到 I/O 錯誤與崩潰模擬。

- **Scenario**：需要驗證失敗路徑而非成功路徑，且失敗點數量有限可枚舉。
- **Value**：把失敗處理的覆蓋從「試幾個點」變成「走完所有注入點」。
- **Prerequisites**：被測系統允許替換資源配置實作；測試 harness 能安裝插樁版本。
- **Inputs**：一段待測操作；一個可設定失敗計數的資源配置器。
- **Exploit / Procedure**：
  1. 安裝可在第 N 次配置失敗的插樁 malloc，設 N=1。
     - Validation：該次操作確實遇到一次模擬失敗。
     - Failure Signal：整段操作完全沒有觸發失敗，表示注入未生效。
  2. 執行待測操作並檢查系統是否正確處理該次失敗。
     - Validation：回傳錯誤碼與資源狀態符合預期。
     - Failure Signal：崩潰、資源洩漏，或錯誤被吞掉。
  3. N 遞增一，重複，直到整段操作跑完而未遇到任何模擬失敗。
     - Validation：迴圈自然終止，代表注入點已窮舉。
     - Failure Signal：迴圈不終止，代表操作的配置次數不收斂。
  4. 以「首次失敗後持續失敗」的設定重跑整個迴圈。
     - Validation：兩種模式都跑完。
     - Failure Signal：僅單次失敗模式通過，表示串聯失敗未被覆蓋。
- **Expected Output**：每一個注入點都有一次被驗證過的錯誤處理行為。
- **Rollback**：移除插樁配置器，restore 原本的實作；本流程不改動被測資料。
- **Failure Handling**：任一注入點失敗即停在該 N 值，該值就是最小重現案例。
- **Security / Privacy Constraints**：僅在測試組態啟用；插樁配置器不得進入交付版本。
- **Toolset**：可替換的資源配置介面；同型作法亦用於 I/O 錯誤注入，並在關閉注入後以完整性檢查確認未留下損壞。
- **Execution Status**：SOURCE_REPORTED
- **Validated By**：來源文件所述之 TCL 與 TH3 harness；本批次未執行。

- **證據與狀態**：SOURCE_STATEMENT · UNCHECKED · MEDIUM
  - [[EV-sqlite-testing-oom-rigged-malloc]]：「inserting a modified version of malloc() that can be rigged to fail」
  - [[EV-sqlite-testing-oom-loop]]：「on the instrumented malloc is increased by one and the test is」
  - [[EV-sqlite-testing-integrity-check]]：「PRAGMA integrity_check to make sure that the I/O error has not」
- **反證／限制**：本流程只窮舉「第幾次配置失敗」這一個維度；配置順序本身改變時的失敗組合不在其覆蓋範圍內，複合失敗需另行設計。
- **Typed Links**：INSTANCE_OF → [[T-four-independent-harnesses]]

<!-- CARD_META
{
  "canonical_key": "P | out-of-memory-handling | exercised-by | incrementing-failure-injection-loop | tcl-and-th3 | source-digest:1f255420",
  "confidence_basis": "步驟與兩種失敗模式皆為文件原文所述；Execution Status 標為 SOURCE_REPORTED，因為本批次沒有執行過它。",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "How SQLite Is Tested, sqlite.org/testing.html, retrieved 2026-08-31; SQLite 3.42.0 era figures",
  "series": "P",
  "source_dependency_key": "article:sqlite.org/testing.html",
  "source_provenance": [
    "artifact:sources/sqlite-testing/article.txt",
    "sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24",
    "TEXT_MATCH::inserting a modified version of malloc() that can be rigged to fail",
    "TEXT_MATCH::on the instrumented malloc is increased by one and the test is",
    "TEXT_MATCH::PRAGMA integrity_check to make sure that the I/O error has not"
  ],
  "stable_id": "P-oom-failure-injection-loop",
  "unresolved_links": []
}
-->
