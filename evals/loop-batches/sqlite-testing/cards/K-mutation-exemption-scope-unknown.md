### K-mutation-exemption-scope-unknown｜被 mutation testing 豁免的分支有多少，來源沒說

- **核心命題**：文件說明純效能分支會以 `/*OPTIMIZATION-IF-TRUE*/` 之類的註解豁免於 mutation 檢查，但沒有給出這類註解的數量，也沒有給出被豁免分支佔全部分支的比例。
- **為什麼重要**：缺了這個數字，「每個分支都會影響輸出」這句話的實際涵蓋範圍就無法界定，也就無法判斷 mutation testing 在此專案買到多少保證。

- **Unknown**：豁免註解的總數，以及被豁免分支佔全體分支指令的比例。
- **Why Unresolved**：來源文件提供了 testcase() 與 assert() 的使用次數，卻沒有提供豁免註解的對應數字。
- **Impact**：無法為 V 卡的結論給出涵蓋率下界；也無法比較本方法與其他專案的 mutation 結果。
- **Evidence Needed**：在 SQLite 原始碼中對兩種豁免註解計數，並取得同一份建置的分支指令總數。
- **Retrieval / Test Plan**：取得對應版本的原始碼樹，對註解字串計數，並以覆蓋率建置輸出的分支總數作分母。
- **Unblock Criteria**：同時取得豁免註解數與分支總數，且兩者來自同一版本；任一缺失即維持本卡開啟。
- **Priority**：MEDIUM

- **證據與狀態**：OBSERVATION · UNCHECKED · MEDIUM
  - [[EV-sqlite-testing-optimization-comment]]：「to tell the mutation testing script to ignore some branch」
  - [[EV-sqlite-testing-assert-count]]：「The SQLite core contains 6754 assert()」
- **反證／限制**：若來源另有一份文件公布豁免數量，本缺口即關閉；本卡只主張這份文件沒有給出該數字。
- **Typed Links**：DEPENDS_ON → [[V-mutation-testing-branch-usefulness]]

<!-- CARD_META
{
  "canonical_key": "K | mutation-exemption-list | unknown | size-and-share-of-branches | sqlite-testing-doc | source-digest:1f255420",
  "confidence_basis": "缺口本身由「文件給了 assert 與 testcase 的計數、卻沒給豁免計數」這個對比支撐，非臆測。",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "How SQLite Is Tested, sqlite.org/testing.html, retrieved 2026-08-31; SQLite 3.42.0 era figures",
  "series": "K",
  "source_dependency_key": "article:sqlite.org/testing.html",
  "source_provenance": [
    "artifact:sources/sqlite-testing/article.txt",
    "sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24",
    "TEXT_MATCH::to tell the mutation testing script to ignore some branch",
    "TEXT_MATCH::The SQLite core contains 6754 assert()"
  ],
  "stable_id": "K-mutation-exemption-scope-unknown",
  "unresolved_links": []
}
-->
