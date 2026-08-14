### D-trace-scale-bottleneck｜Trace 規模同時撞上成本與 Context 上限

- **核心命題**：大量、超長 Agent traces 不能被當成普通短日誌完整塞回另一個 model；資料量、input cost 與 context window 會同時成為瓶頸。
- **為什麼重要**：系統必須把 trace 視為外部資料物件，先做 query、selection 與 case construction，再送入 evaluator。
- **Entity**：Long-horizon Agent 與 trace-mining pipeline。
- **Behavior / Case**：單次執行產生長 tool/message trajectory，大量 runs 疊加成大規模 corpus。
- **操作手法**：直接 review 全量資料時，成本近似 `trace_count × average_trace_tokens × input_unit_cost`。
- **獨特特徵**：同一 trace可能被多個 judges/queries 重讀；完整軌跡又可能超出 context，compaction 可能刪除 decision-relevant state。
- **Shadow Evidence**：[[EV-cvrngaqzq3y-trace-scale]]：`00:06:21–00:07:22`。
- **Outcome**：架構轉向 digest-bound cohort、外部查詢、case selection 與 frozen eval，而不是無差別 context stuffing。
- **Comparison Target**：短 request/response 日誌。
- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · MEDIUM
- **反證／限制**：即使 context 變長或價格下降，資料選擇、provenance 與 contamination 問題仍存在。
- **Typed Links**：ROOT ← [[N-autonomy-trace-mining]] · FLOW → [[P-trace-driven-improvement-cycle]] · FLOW → [[C-model-harness-task-fit]]

<!-- CARD_META
{"stable_id":"D-trace-scale-bottleneck","canonical_key":"D | long-horizon-traces | create | cost-and-context-bottleneck | trace-mining | source-digest:bf993b8d","series":"D","lifecycle":"ACTIVE","revision":1,"source_dependency_key":"youtube-video:CvRngaQZQ3Y","source_provenance":["youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:06:21..00:07:22"],"unresolved_links":[]}
-->
