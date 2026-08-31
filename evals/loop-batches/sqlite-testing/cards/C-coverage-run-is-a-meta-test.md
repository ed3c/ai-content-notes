### C-coverage-run-is-a-meta-test｜量覆蓋率的那一次執行，測的是測試套件，不是被測程式

- **核心命題**：以 gcov 量覆蓋率時，插樁選項讓編譯器產生不同的機器碼，所以那一次執行不是對產品的測試，而是對測試套件的測試；真正的測試是之後以交付組態重編再跑的第二次。
- **為什麼重要**：把量測執行當成測試執行，等於用一份不會出貨的二進位當作品質證據；而且兩次輸出若不一致，指向的是 undefined behavior 或編譯器錯誤，不是量測誤差。

- **定義**：coverage run 是對測試套件完備性的量測（meta-test）；delivery-configuration run 才是對程式的測試。
- **Non-Goals**：不主張覆蓋率高等於缺陷少，也不主張 gcov 之外的量測工具具有相同性質。
- **演化**：文件僅說明目前作法，未給出此作法的採用年代，故本卡不補時間線。
- **底層機制**：`-g -fprofile-arcs -ftest-coverage` 改變產生的組合語言；插樁後的執行路徑與交付版本不同。
- **Invariants**：兩次執行的輸出必須完全相同；差異即表示程式使用了 undefined／indeterminate behavior，或編譯器有錯。
- **Boundary Conditions**：僅適用於「量測本身會改變被測物」的工具鏈；不改變產物的量測不受此約束。
- **正例**：先跑插樁版確認 100% branch coverage，再以交付選項重編重跑，並比對兩次輸出。
- **反例**：只跑插樁版、看到 100% 就宣告通過，交付組態從未被執行過。

- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · HIGH
  - [[EV-sqlite-testing-meta-test]]：「The gcov run is a test of the test - a meta-test.」
  - [[EV-sqlite-testing-different-code]]：「the -fprofile-args and -ftest-coverage options cause the compiler to」
  - [[EV-sqlite-testing-second-run]]：「This second run is the actual test of SQLite.」
- **反證／限制**：若某個覆蓋率工具能證明其插樁不改變產生的機器碼，本卡對該工具不成立；本卡的範圍是會改變產物的插樁式量測。
- **Typed Links**：ROOT ← [[N-open-source-reliability-doubt]] · VALIDATED_BY → [[V-mutation-testing-branch-usefulness]]

<!-- CARD_META
{
  "canonical_key": "C | coverage-measurement-run | is | a-test-of-the-test-suite | sqlite-gcov | source-digest:1f255420",
  "confidence_basis": "三個錨都是文件對同一機制的直述，且彼此互為前後句；沒有跨來源推論。",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "How SQLite Is Tested, sqlite.org/testing.html, retrieved 2026-08-31; SQLite 3.42.0 era figures",
  "series": "C",
  "source_dependency_key": "article:sqlite.org/testing.html",
  "source_provenance": [
    "artifact:sources/sqlite-testing/article.txt",
    "sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24",
    "TEXT_MATCH::The gcov run is a test of the test - a meta-test.",
    "TEXT_MATCH::the -fprofile-args and -ftest-coverage options cause the compiler to",
    "TEXT_MATCH::This second run is the actual test of SQLite."
  ],
  "stable_id": "C-coverage-run-is-a-meta-test",
  "unresolved_links": []
}
-->
