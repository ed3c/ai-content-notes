### N-open-source-reliability-doubt｜「開源所以不可靠」的懷疑，被一份把測試量體攤開的文件正面回應

- **核心命題**：SQLite 面對「開源軟體不如商業軟體可靠」的預設懷疑，回應方式不是宣稱品質，而是把測試規模、方法與其代價逐項寫出來讓人自行判斷。
- **為什麼重要**：這決定了讀者該用什麼證據要求任何一份「我們測得很徹底」的宣稱：可查的數量、可名的方法、以及作者自己承認的代價與矛盾。

- **核心衝突**：可靠性宣稱無法由宣稱本身支撐，但揭露測試細節同時會揭露測試策略內部的矛盾。
- **角色矩陣**：
  - 主角：SQLite 開發者與其四套獨立測試 harness。
  - 對立面：「開源＝未經嚴格測試」的預設印象。
  - 次要變量：2014 年後出現的 profile-guided fuzzer，改變了測試資源的分配。
- **Impact Anchors**：測試碼是產品碼的 590 倍；核心程式在 as-deployed 組態下達 100% branch coverage。
- **完整劇情鏈**：
  1. 起始狀態：SQLite 以 100% MC/DC 為長期焦點，測試碼量體遠大於產品碼。
  2. 壓力累積：2014 年 AFL 出現後，fuzzer 在同一份程式上找到大量問題。
  3. 決策／事件：策略沒有二選一，而是同時維持 100% MC/DC 與大規模 fuzzing。
  4. 轉折：文件明說兩者互相拉扯，且大多數測試 CPU 週期已轉向 fuzzing。
  5. 結果：可靠性宣稱改由「可數的量體 ＋ 具名的方法 ＋ 承認的代價」承載。
- **生態背景**：SQLite 是被廣泛部署的基礎設施函式庫，作者自陳這種投入對一般應用並不划算。
- **未解段落**：文件未給出缺陷率、外部回報數或事故數，因此「高可靠」在本卡內仍只有測試投入這一側的證據。

- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · MEDIUM
  - [[EV-sqlite-testing-ratio-590x]]：「590 times as much」
  - [[EV-sqlite-testing-cycles-to-fuzzing]]：「100% MC/DC of the core SQLite code, but most testing CPU cycles are」
  - [[EV-sqlite-testing-not-cost-effective]]：「is probably not cost effective for a typical application.」
- **反證／限制**：若能取得同期缺陷率或事故統計，本卡的敘事重心會從「投入」移到「產出」；目前不主張測試投入與實際可靠度之間的因果強度。
- **Typed Links**：FLOW → [[X-mcdc-versus-fuzz-tension]] · FLOW → [[T-four-independent-harnesses]]

<!-- CARD_META
{
  "canonical_key": "N | sqlite | answers | open-source-reliability-doubt | testing-regime-2026 | source-digest:1f255420",
  "confidence_basis": "劇情鏈每一環都對應文件中的具名段落；未取得的缺陷率明確標為未解段落而非以常識補齊。",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "How SQLite Is Tested, sqlite.org/testing.html, retrieved 2026-08-31; SQLite 3.42.0 era figures",
  "series": "N",
  "source_dependency_key": "article:sqlite.org/testing.html",
  "source_provenance": [
    "artifact:sources/sqlite-testing/article.txt",
    "sha256:1f25542077e5729da5ab9c024e95cefe723b15622a03a08f8b3e40d9b7d15f24",
    "TEXT_MATCH::590 times as much",
    "TEXT_MATCH::100% MC/DC of the core SQLite code, but most testing CPU cycles are",
    "TEXT_MATCH::is probably not cost effective for a typical application."
  ],
  "stable_id": "N-open-source-reliability-doubt",
  "unresolved_links": []
}
-->
