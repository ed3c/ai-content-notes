### V-mutation-testing-branch-usefulness｜「每個分支都會影響輸出」這件事的驗證方式，以及它在本批次未被執行

- **核心命題**：把原始碼編成組合語言後逐一將分支指令改成無條件跳躍或 no-op，重編並確認測試套件抓得到這個變異；抓不到就代表該分支要嘛可刪、要嘛沒被真正測試。
- **為什麼重要**：這是把覆蓋率從「走過」推進到「有用」的具體 oracle；但本批次只讀到它的描述，沒有執行過，所以在此僅登記為未執行。

- **Target Assertion**：測試套件能偵測到每一個分支指令的行為變異。
- **Verification Method**：組合語言層級的 mutation testing，逐一改寫分支指令後重編並重跑套件。
- **Oracle**：套件是否對變異版本轉紅；轉綠即為未偵測到的變異。
- **Environment / Fixture**：可輸出組合語言的編譯器工具鏈與完整測試套件。
- **Procedure**：編譯為組合語言 → 逐一將分支改為無條件跳躍或 no-op → 重編 → 跑套件 → 記錄未被偵測的變異。
- **Expected Result**：每個變異都被套件偵測到，或被標記為純效能分支而豁免。
- **Observed Result**：NOT_RUN
- **Verdict**：NOT_RUN
- **Artifacts**：NONE
- **Limitations**：純效能分支會產生 false positive，需要來源端的明示標記才能排除；因此此方法的結論強度取決於那份豁免清單的正確性，而豁免清單本身未被本批次讀到。

- **證據與狀態**：SOURCE_STATEMENT · UNCHECKED · MEDIUM
  - [[EV-sqlite-testing-mutation-flip]]：「instruction into either an unconditional jump or a no-op, compiles the」
  - [[EV-sqlite-testing-false-positives]]：「Such branches generate false-positives during mutation testing.」
  - [[EV-sqlite-testing-optimization-comment]]：「to tell the mutation testing script to ignore some branch」
- **反證／限制**：本卡不主張該方法在 SQLite 以外的專案可行；也不主張其結果，因為本批次未執行。
- **Typed Links**：IMPLEMENTS → [[E-coverage-measures-the-suite]]

<!-- CARD_META
{
  "canonical_key": "V | every-branch-affects-output | tested-by | assembly-level-mutation | not-run-here | source-digest:1f255420",
  "confidence_basis": "方法與限制皆為文件直述；Observed Result 與 Verdict 皆為 NOT_RUN，因為本批次沒有執行過任何 mutation。",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "How SQLite Is Tested, sqlite.org/testing.html, retrieved 2026-08-31; SQLite 3.42.0 era figures",
  "series": "V",
  "source_dependency_key": "article:sqlite.org/testing.html",
  "source_provenance": [
    "artifact:sources/sqlite-testing/article.txt",
    "sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24",
    "TEXT_MATCH::instruction into either an unconditional jump or a no-op, compiles the",
    "TEXT_MATCH::Such branches generate false-positives during mutation testing.",
    "TEXT_MATCH::to tell the mutation testing script to ignore some branch"
  ],
  "stable_id": "V-mutation-testing-branch-usefulness",
  "unresolved_links": []
}
-->
