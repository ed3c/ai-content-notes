### D-branch-versus-statement-coverage｜同一行 C 條件式：一個測試給 100% statement，要三個才給 100% branch

- **核心命題**：對 `if( a>b && c!=25 ){ d++; }` 這一行，任一個測試案例都能讓 statement coverage 達 100%，但要 `a<=b`、`a>b && c==25`、`a>b && c!=25` 三個案例才能達到 100% branch coverage。
- **為什麼重要**：「XX% 覆蓋率」在沒有限定詞時通常指 statement coverage；這個案例給出兩者強度差距的下界，讓人知道未限定的數字買到了什麼。

- **Entity**：單行 C 條件式 `if( a>b && c!=25 ){ d++; }`。
- **Behavior / Case**：同一行程式碼在兩種覆蓋率定義下所需的測試案例數不同。
- **操作手法**：以短路運算子拆解決策，逐一列出每個子條件的真假組合。
- **獨特特徵**：
  - 條件式可能永遠為假、`d` 從未被遞增，statement coverage 仍計為已測試；
  - branch coverage 要求每個機器碼分支指令的兩個方向都被走過；
  - 100% branch 蘊含 100% statement，反向不成立。
- **Shadow Evidence**：文件以同一行程式碼並列兩種定義，並明列三個必要案例。
- **Outcome**：讀到未限定的覆蓋率數字時，預設它是三者中最弱的那個。
- **Comparison Target**：把 statement coverage 的百分比當成 branch coverage 的作法。

- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · HIGH
  - [[EV-sqlite-testing-statement-coverage]]：「Any one of the above test cases would provide 100% statement coverage」
  - [[EV-sqlite-testing-branch-stricter]]：「Branch coverage is more rigorous than statement coverage. Branch」
- **反證／限制**：此案例只界定 statement 與 branch 的差距；不涵蓋 MC/DC 與 branch 在布林向量測試上的差異，該差異另見 T 與 X 卡的範圍。
- **Typed Links**：ROOT ← [[N-open-source-reliability-doubt]] · DEPENDS_ON → [[C-coverage-run-is-a-meta-test]]

<!-- CARD_META
{
  "canonical_key": "D | one-c-conditional | distinguishes | statement-from-branch-coverage | sqlite-example | source-digest:1f255420",
  "confidence_basis": "案例與三個必要測試案例皆為文件原文列舉，未做任何外推。",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "How SQLite Is Tested, sqlite.org/testing.html, retrieved 2026-08-31; SQLite 3.42.0 era figures",
  "series": "D",
  "source_dependency_key": "article:sqlite.org/testing.html",
  "source_provenance": [
    "artifact:sources/sqlite-testing/article.txt",
    "sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24",
    "TEXT_MATCH::Any one of the above test cases would provide 100% statement coverage",
    "TEXT_MATCH::Branch coverage is more rigorous than statement coverage. Branch"
  ],
  "stable_id": "D-branch-versus-statement-coverage",
  "unresolved_links": []
}
-->
