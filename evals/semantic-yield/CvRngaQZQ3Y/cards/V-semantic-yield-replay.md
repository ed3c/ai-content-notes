### V-semantic-yield-replay｜修改後流程的重播驗證

- **核心命題**：修改後的輸出 artifacts 可以由獨立於產生模型的 deterministic host validator 重播檢查；這不等同於完成原始影片視覺驗證或 production Agent 實驗。
- **為什麼重要**：它把「輸出結構與 epistemic contract 已驗證」和「來源真實性、multimodal fidelity、完整 QG 已驗證」分開。
- **Target Assertion**：新版流程能保留中心命題、implicit relations、comparison structure 與 dataflow，同時不增加無來源精確值。
- **Verification Method**：回讀 manifest、cards、typed links、knowledge views、result 與 state；驗證 Git blob SHA、stable IDs、payload-first、uncertainty、series contracts、HG 與可自動化 QG 子集。
- **Oracle**：Grounded semantic yield、relation recall、visual coverage、unsupported precision、redundancy、mental-model utility。
- **Environment / Fixture**：`CvRngaQZQ3Y` secondary normalized transcript；單一 dependency；沒有已授權 frame artifact。
- **Procedure**：Read-back → blob/hash contract → IDs/links → payload/series fields → views/UNKNOWN policy → HG/QG subset → persisted-report comparison。
- **Expected Result**：Autonomy → lower static predictability → traces → trace mining；未知比較欄位保持 UNKNOWN；status 為 CONTINUE。
- **Observed Result**：PARTIAL
- **Verdict**：PARTIAL
- **Artifacts**：GitHub card batch、index、semantic result、`semantic-validator-report.json`。
- **Limitations**：Multimodal frame validation、independent human review 與完整 external QG 尚未執行。
- **證據與狀態**：OBSERVATION · TESTED · MEDIUM
- **反證／限制**：相同 source pack 重跑若無證據地改變 thesis、ID 或 projection，則 idempotency 失敗。
- **Typed Links**：ROOT ← [[N-autonomy-trace-mining]] · DEPENDS_ON → [[K-visual-identifier-evidence-gap]]

<!-- CARD_META
{"stable_id":"V-semantic-yield-replay","canonical_key":"V | semantic-yield-runtime | verifies | grounded-relations-and-projections | CvRngaQZQ3Y | regenerated-run","series":"V","lifecycle":"ACTIVE","revision":2,"source_dependency_key":"youtube-video:CvRngaQZQ3Y","unresolved_links":[]}
-->
