### T-four-independent-harnesses｜四套獨立 harness 各自買到不同的保證，不是同一件事做四次

- **核心命題**：TCL、TH3、SLT、dbsqlfuzz 四套 harness 各自獨立設計與維護，規模與所買到的保證都不同；把它們當成備援副本會誤判剩餘風險。
- **為什麼重要**：決定要從這個規制借用哪一段時，得先知道每一段各自買到什麼：分支覆蓋、跨引擎答案一致、還是對惡意輸入的韌性。

- **Decision Use**：判斷自家測試體系缺的是覆蓋、是差分比對、還是對抗性輸入。
- **Comparison Contract**：
  - 同一時間範圍：同一份文件所述的同一版本期（SQLite 3.42.0 前後）。
  - 同一測量口徑：各 harness 自報的案例數與執行規模，口徑不互通，僅供區辨用途。
  - 缺值規則：UNKNOWN。
- **Dimensions**：擁有者、實作語言、案例數、單次全跑規模、所買到的保證。
- **Structured Table**：
  | Harness | 案例數 | 全跑規模 | 買到的保證 |
  |---|---|---|---|
  | TCL | 51445 distinct test cases | 全跑達數百萬次分離測試 | 開發期主測試面 |
  | TH3 | 50362 distinct test cases | 全覆蓋跑約 2.4 million instances | 核心 100% branch 與 MC/DC |
  | SLT | UNKNOWN | 7.2 million queries | 與 PostgreSQL、MySQL、SQL Server、Oracle 10g 的答案一致 |
  | dbsqlfuzz | 336 seed files | 每日約 10 億次 mutation | 對惡意 SQL 與資料庫檔的韌性 |
- **Interpretation**：案例數彼此不可比（TCL 與 TH3 皆高度參數化，SLT 以查詢計、fuzzer 以 mutation 計）；可比的是各自買到的保證彼此不重疊。
- **Decision Threshold**：若只想要一項，先問缺的是哪一種保證；四者不能互相替代。

- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · HIGH
  - [[EV-sqlite-testing-four-harnesses]]：「There are four independent test harnesses used for testing the」
  - [[EV-sqlite-testing-tcl-cases]]：「51445 distinct test cases, but many of the test」
  - [[EV-sqlite-testing-th3-cases]]：「of C code implementing 50362 distinct test cases.」
  - [[EV-sqlite-testing-slt-queries]]：「SLT runs 7.2 million queries comprising」
  - [[EV-sqlite-testing-dbsqlfuzz-rate]]：「runs about one billion test mutations per day.」
- **反證／限制**：四個數字的量測口徑不同，本表不主張它們之間可換算；若文件改以統一口徑重報，表格的相對印象會改變。
- **Typed Links**：ROOT ← [[N-open-source-reliability-doubt]]

<!-- CARD_META
{
  "canonical_key": "T | four-sqlite-test-harnesses | compared-on | scale-and-guarantee | release-gate | source-digest:1f255420",
  "confidence_basis": "每一格都對應文件中的具體數字；口徑不可比這件事在 Interpretation 明說，而不是靠讀者自行折算。",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "How SQLite Is Tested, sqlite.org/testing.html, retrieved 2026-08-31; SQLite 3.42.0 era figures",
  "series": "T",
  "source_dependency_key": "article:sqlite.org/testing.html",
  "source_provenance": [
    "artifact:sources/sqlite-testing/article.txt",
    "sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24",
    "TEXT_MATCH::There are four independent test harnesses used for testing the",
    "TEXT_MATCH::51445 distinct test cases, but many of the test",
    "TEXT_MATCH::of C code implementing 50362 distinct test cases.",
    "TEXT_MATCH::SLT runs 7.2 million queries comprising",
    "TEXT_MATCH::runs about one billion test mutations per day."
  ],
  "stable_id": "T-four-independent-harnesses",
  "unresolved_links": []
}
-->
