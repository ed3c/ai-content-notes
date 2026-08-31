### E-coverage-measures-the-suite｜覆蓋率描述的是測試套件，不是被測程式

- **核心命題**：覆蓋率量測的對象是「套件走過了哪些路徑」，不是「程式在這些路徑上是對的」；要讓數字談論程式，必須另外證明每個被走過的分支都會改變輸出。
- **為什麼重要**：這條界線決定了覆蓋率能當什麼證據：它能否證「未測到」，不能證「已正確」；把兩者混用會讓一個 100% 的數字買到它沒有賣的東西。

- **Law**：覆蓋率是測試套件的性質；只有當每個分支都被證明會影響輸出時，該數字才開始描述被測程式。
- **Scope**：以執行路徑為單位的覆蓋率量測（statement／branch／MC-DC）。不涵蓋以輸出正確性為單位的差分測試。
- **Derivation**：量測執行本身是對套件的 meta-test；而 mutation testing 之所以被視為「更好」的量測，正是因為它問的是分支是否影響輸出，而非是否被走過。
- **Implications**：100% 覆蓋率不排除「該分支被走過但沒有任何斷言在看」；補上這一層需要 mutation 或等價的機制。
- **Falsifier**：找到一種路徑覆蓋率量測，其數值會在測試套件的斷言被移除、而執行路徑不變時下降。
- **Known Exceptions**：純為效能而存在、不改變輸出的分支，在 mutation testing 下會產生 false positive，需以明示標記排除，因此本法則在該類分支上不可直接套用。

- **證據與狀態**：HYPOTHESIS · UNCHECKED · LOW
  - [[EV-sqlite-testing-meta-test]]：「The gcov run is a test of the test - a meta-test.」
  - [[EV-sqlite-testing-false-positives]]：「Such branches generate false-positives during mutation testing.」
- **反證／限制**：本卡由單一來源歸納，依 v7.1 對 E Card 的要求維持 HYPOTHESIS；要升級需要至少兩個獨立來源的 D 或 V 支撐，本批次沒有。
- **Typed Links**：DEPENDS_ON → [[C-coverage-run-is-a-meta-test]] · VALIDATED_BY → [[V-mutation-testing-branch-usefulness]]

<!-- CARD_META
{
  "canonical_key": "E | a-coverage-number | describes | the-test-suite-not-the-program | derived-from-sqlite | source-digest:1f255420",
  "confidence_basis": "單一來源歸納，明確標為 HYPOTHESIS 且未使用「唯一」「永遠」等絕對詞；falsifier 為可執行的實驗。",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "How SQLite Is Tested, sqlite.org/testing.html, retrieved 2026-08-31; SQLite 3.42.0 era figures",
  "series": "E",
  "source_dependency_key": "article:sqlite.org/testing.html",
  "source_provenance": [
    "artifact:sources/sqlite-testing/article.txt",
    "sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24",
    "TEXT_MATCH::The gcov run is a test of the test - a meta-test.",
    "TEXT_MATCH::Such branches generate false-positives during mutation testing."
  ],
  "stable_id": "E-coverage-measures-the-suite",
  "unresolved_links": []
}
-->
