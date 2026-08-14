### P-trace-cycle｜Trace 改進最小可重播程序

- **核心命題**：保存 trace digest、定義 decision question、建立 frozen eval、一次套用一個 patch、重播並保留 rollback receipt。
- **Scenario**：Agent 已產生可回讀 traces。
- **Value**：把錯誤轉成可比較的 case 與 experiment。
- **Prerequisites**：Baseline、oracle、版本資訊與 rollback path。
- **Inputs**：Trace cohort、task/eval contract、model/harness identity。
- **Exploit / Procedure**：
  1. 保存 raw trace 與 digest。Validation：可回讀 task/outcome。Failure Signal：缺少 terminal state。
  2. 建立 selected/rejected cases。Validation：相同 digest 可重播。Failure Signal：沒有 locator。
  3. 隔離 eval 與 holdout。Validation：provenance 完整。Failure Signal：資料重複或污染。
  4. 一次套用一個 patch並重播。Validation：結果綁定 artifact。Failure Signal：無法 attribution。
  5. 通過後 canary；失敗恢復 baseline。
- **Expected Output**：Cohort manifest、eval、patch、report、rollback receipt。
- **Rollback**：恢復上一個 model/harness snapshot並保留失敗歷史。
- **Failure Handling**：Trace 不完整先修 instrumentation；污染時廢棄結果；線上 regression 立即 rollback。
- **Execution Status**：UNTESTED
- **Validated By**：[[V-semantic-yield-replay]]
- **證據與狀態**：NORMATIVE · SUPPORTED · MEDIUM
- **Typed Links**：ROOT ← [[S-harness-cycle]] · DEPENDS_ON → [[K-visual-identifier-evidence-gap]]

<!-- CARD_META
{"stable_id":"P-trace-cycle","canonical_key":"P | agent-operator | executes | trace-improvement-cycle | agent-runtime | source-digest:bf993b8d","series":"P","lifecycle":"ACTIVE","revision":1,"source_dependency_key":"youtube-video:CvRngaQZQ3Y","unresolved_links":[]}
-->
