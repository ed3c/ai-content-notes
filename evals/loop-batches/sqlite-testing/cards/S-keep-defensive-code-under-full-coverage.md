### S-keep-defensive-code-under-full-coverage｜用三種編譯期定義把防禦性程式碼留下，同時仍拿到 100% branch coverage

- **核心命題**：以 ALWAYS()／NEVER() 標記那些實務上恆真或恆假的防禦性條件，並讓同一份原始碼在三種巨集定義下各跑一次：release 為 pass-through、測試期會在真值不符時觸發 assert、量測期為常數而不產生分支指令。
- **為什麼重要**：這解掉「要不要為了 100% 覆蓋率刪掉防禦性程式碼」的兩難：不刪，而是讓量測看不到它、讓測試盯著它。

- **Objective**：保留防禦性條件的同時，不讓它們在覆蓋率量測中變成永遠打不到的分支。
- **Preconditions**：防禦性條件可被明確標記；建置系統能以三組不同巨集定義各跑一次完整測試套件。
- **策略邏輯**：把「這是防禦性程式碼」從註解升級成編譯期事實，讓三種身分各自對應一種定義。
- **Ecological Context**：
  - 主角做法：保留防禦性程式碼，以巨集切換其在量測中的可見性。
  - 環境常態：為了讓覆蓋率數字好看而刪除或改寫防禦性分支。
  - 競對做法：接受低於 100% 的覆蓋率並在報告中標註豁免清單。
- **Trade-offs**：多出兩次完整測試執行的成本；巨集本身成為必須被驗證的機制。
- **Pre-mortem Glitches**：三次執行結果不一致而被當成 flaky；部署版本誤用非 pass-through 定義。
- **Success Criteria**：三次執行輸出完全相同；並有 run-time 檢查可確認部署版本使用的是 pass-through 形式。
- **Implementation Path**：標記防禦性條件 → 定義三組巨集 → 三次執行並比對輸出 → 以 run-time 檢查確認部署組態。

- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · MEDIUM
  - [[EV-sqlite-testing-always-never]]：「macros called ALWAYS() and NEVER(). The ALWAYS() macro」
  - [[EV-sqlite-testing-three-runs]]：「The test suite is designed to be run three times, once for each of」
- **反證／限制**：此策略只讓防禦性分支不干擾覆蓋率數字，不使它們被實際測試過；若把它讀成「防禦性程式碼也被覆蓋了」，即為誤用。
- **Typed Links**：MITIGATES → [[X-mcdc-versus-fuzz-tension]]

<!-- CARD_META
{
  "canonical_key": "S | defensive-conditionals | retained-under | full-branch-coverage | always-never-macros | source-digest:1f255420",
  "confidence_basis": "三種巨集定義與三次執行的要求皆為文件原文；成功條件取自文件明列的「三次結果應完全相同」與 run-time 檢查。",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "How SQLite Is Tested, sqlite.org/testing.html, retrieved 2026-08-31; SQLite 3.42.0 era figures",
  "series": "S",
  "source_dependency_key": "article:sqlite.org/testing.html",
  "source_provenance": [
    "artifact:sources/sqlite-testing/article.txt",
    "sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24",
    "TEXT_MATCH::macros called ALWAYS() and NEVER(). The ALWAYS() macro",
    "TEXT_MATCH::The test suite is designed to be run three times, once for each of"
  ],
  "stable_id": "S-keep-defensive-code-under-full-coverage",
  "unresolved_links": []
}
-->
