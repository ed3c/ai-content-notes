### X-mcdc-versus-fuzz-tension｜100% MC/DC 與 fuzz 韌性互相拉扯，而且兩者都要

- **核心命題**：追求 100% MC/DC 會壓抑帶有不可達分支的防禦性程式碼，而少了防禦性程式碼，fuzzer 更容易走到出問題的路徑；反之，fuzz 表現好的程式碼通常遠低於 100% MC/DC。
- **為什麼重要**：這是同一份程式碼上兩個都想要的目標互相扣減，不是工具選型問題；任何「全面測試」的規劃若沒有為這一項編預算，會在其中一側悄悄退讓。

- **Claim A**：100% MC/DC 讓改動一處不致在他處造成非預期後果，是正常使用下的健壯性來源。
- **Claim B**：MC/DC 壓抑防禦性程式碼，而防禦性程式碼正是抵擋惡意輸入的那一層。
- **Conflict Type**：METHOD
- **Scope Delta**：Claim A 的範圍是正常使用下的正確性；Claim B 的範圍是對抗性輸入下的韌性。兩者不是同一個受測條件。
- **Possible Reconciliation**：同時維持兩者，但把大部分測試 CPU 週期分配給 fuzzing，並以既有的 100% MC/DC 讓 fuzzer 找到的問題能被快速且低風險地修掉。
- **Resolution Test**：在同一份程式碼上移除一批防禦性分支，量測 MC/DC 與 fuzz 發現率的變化方向是否相反。
- **Current State**：PARTIALLY_RESOLVED
- **Decision Impact**：把「100% 覆蓋」與「抗 fuzz」寫進同一個驗收條件時，必須明列各自的預算與可接受的退讓幅度。

- **證據與狀態**：OBSERVATION · SUPPORTED · MEDIUM
  - [[EV-sqlite-testing-tension]]：「Fuzz testing and 100% MC/DC testing are in tension with」
  - [[EV-sqlite-testing-defensive-discouraged]]：「This is because MC/DC testing discourages defensive code with」
  - [[EV-sqlite-testing-cycles-to-fuzzing]]：「100% MC/DC of the core SQLite code, but most testing CPU cycles are」
- **反證／限制**：文件未給出量化的拉扯幅度；若有專案能同時維持 100% MC/DC 與零 fuzz 發現，本卡的張力主張在該情境下不成立。
- **Typed Links**：ROOT ← [[N-open-source-reliability-doubt]] · CONFLICT → [[S-keep-defensive-code-under-full-coverage]]

<!-- CARD_META
{
  "canonical_key": "X | full-mcdc-coverage | conflicts-with | fuzz-robustness | same-codebase | source-digest:1f255420",
  "confidence_basis": "兩個 claim 都取自文件同一節的直述，且文件自陳兩者同時做到很困難，非本卡外推。",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "How SQLite Is Tested, sqlite.org/testing.html, retrieved 2026-08-31; SQLite 3.42.0 era figures",
  "series": "X",
  "source_dependency_key": "article:sqlite.org/testing.html",
  "source_provenance": [
    "artifact:sources/sqlite-testing/article.txt",
    "sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24",
    "TEXT_MATCH::Fuzz testing and 100% MC/DC testing are in tension with",
    "TEXT_MATCH::This is because MC/DC testing discourages defensive code with",
    "TEXT_MATCH::100% MC/DC of the core SQLite code, but most testing CPU cycles are"
  ],
  "stable_id": "X-mcdc-versus-fuzz-tension",
  "unresolved_links": []
}
-->
