### N-trace-data-to-agent-improvement-loop｜從 Agent 犯錯到可重播的改進閉環

- **核心命題**：Agent 的執行資料只有在「上線 → 收集 traces → 資料挖掘 → 受控實驗 → 更新系統」形成閉環時，才會從 observability 轉成 continual learning。
- **為什麼重要**：單純保存 log 不會自動改善 Agent；閉環把失敗變成可定位、可比較、可 rollback 的工程訊號。

- **核心衝突**：Agent 取得更多 autonomy 後，行為由 prompt、tools、skills、hooks、middleware 與多 Agent orchestration 共同生成；人類卻愈難像閱讀一般程式碼那樣預測變更後果。
- **角色矩陣**：
  - 主角：負責上線與改善 Agent 的工程團隊。
  - 對立面：非確定性、長 trace、資料規模與有限 context window。
  - 次要變量：model、harness、eval、成本、memory 與人類審查。
- **Impact Anchors**：
  - [[EV-cvrngaqzq3y-four-stage-loop]]：00:00:44–00:02:17；來源依序描述 ship、collect traces、data mining、data-driven experiments。
  - [[EV-cvrngaqzq3y-trace-scale]]：00:06:21–00:07:22；來源提出 millions of traces、millions of tokens per trace 與超長 context 無法直接放入另一個 Agent。
- **完整劇情鏈**：
  1. 起始狀態：Agent 上線、執行任務並產生 mistakes 與 traces。
  2. 壓力累積：Agent stack 比單一程式碼路徑更難推理；trace 數量、長度與 input-token cost 同時上升。
  3. 決策／事件：團隊把 traces 視為可查詢的外部物件，針對明確問題進行 mining，而不是把全部資料直接塞回 context。
  4. 轉折：trace 中的 dense feedback 被轉成 harness 修改、model 選擇、fine-tuning data、eval 與 memory update。
  5. 結果：來源提出一個可持續 hill-climbing 的改進迴圈；但沒有提供本演講方法在固定 benchmark 上的完整實驗 artifact。
- **生態背景**：來源認為 observability 與 continual learning 緊密耦合，因為 Agent 在環境中採取行動時會持續產生可回饋到自身狀態的資料。
- **未解段落**：每一層更新對品質、成本與安全的因果貢獻尚未被獨立量化。

- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-observability-learning]]：00:02:17–00:03:17；來源把 traces 描述為 continual learning 的必要輸入。
- **反證／限制**：若在固定 task、相同 eval 與相同成本口徑下，trace-driven 迴圈無法穩定優於無迴圈 baseline，這張卡的策略價值會被削弱。
- **Typed Links**：
  - ROOT ← [[D-four-stage-trace-improvement-loop]]
  - FLOW → [[S-model-harness-task-fit-iteration]]
  - DEPENDS_ON → [[K-auto-caption-identifiers-unverified]]

<!-- CARD_META
{
  "stable_id": "N-trace-data-to-agent-improvement-loop",
  "canonical_key": "N | agent-improvement | converts | traces-into-closed-loop-learning | agent-systems | source-digest:bf993b8d",
  "series": "N",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "單一 secondary auto-caption transcript 直接支持事件順序；閉環因果是 bounded inference，未有獨立實驗 corroboration。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:00:44..00:07:22",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->

### C-trace-mining-feedback-substrate｜Trace Mining 是回饋基材，不是 Log 搜尋

- **核心命題**：Trace mining 是針對決策問題，從 Agent 執行軌跡中提取行為模式、反例、counterfactual 與可供下一輪更新的資料產品。
- **為什麼重要**：這個定義把「有 tracing」和「能改進 Agent」分開；前者是儲存，後者需要 question、selection、evaluation 與 update contract。

- **定義**：對保留 tool calls、messages、API／CLI interaction 與結果的 traces，使用可重播查詢找出 good/bad interactions、compaction 後退化、model counterfactual、dense feedback 與可訓練案例。
- **Non-Goals**：
  - 不是把完整 trace 無差別塞進 model context。
  - 不是把同一影片經不同 transport 取得的文字當成獨立 corroboration。
  - 不是看到 correlation 後直接宣告某個 prompt 或 model 造成結果。
  - 不是以 summary 取代 raw trace 與 source digest。
- **演化**：UNKNOWN；來源描述目前實務，未提供可驗證的版本演化時間線。
- **底層機制**：
  1. Trace 捕捉使用者實際看見的 Agent behavior。
  2. Mining query 將大量 traces 壓縮成 decision-relevant cases。
  3. Cases 被轉成 eval、fine-tuning／distillation data 或 human-review queue。
  4. 更新後以同一 evaluation contract 重播，形成 feedback loop。
- **Invariants**：
  - 原始 trace、normalized derivative 與 interpretation 必須分層。
  - 每個 case 綁定 task、model、harness、時間與 source digest。
  - 訓練集、eval set 與 holdout 不得靜默互相污染。
  - 長 trace 需被當成外部物件查詢，而非假設能完整進入 context。
- **Boundary Conditions**：
  - 缺少完整 trace、privacy authority、穩定 task definition 或可重播 oracle 時，mining 只能產生 hypothesis。
  - trace volume 很大時，input-token cost 與 context limit 會成為系統瓶頸。
- **正例**：[[D-four-stage-trace-improvement-loop]]
- **反例**：只存 traces、不定義問題、不建立 eval、也不把結果回寫到 model／harness／memory 的被動 logging。

- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-trace-questions]]：00:04:48–00:05:50；來源列出 good/bad interactions、compaction degradation 與 model counterfactual 等查詢用途。
  - [[EV-cvrngaqzq3y-trace-outputs]]：00:10:55–00:12:57；來源描述 distillation/SFT data、evals/environments 與 human-review content。
- **反證／限制**：來源沒有提供 mining query 的 precision/recall、標註一致性、成本或資料污染率。
- **Typed Links**：
  - ROOT ← [[D-four-stage-trace-improvement-loop]]
  - FLOW → [[S-model-harness-task-fit-iteration]]
  - DEPENDS_ON → [[K-auto-caption-identifiers-unverified]]

<!-- CARD_META
{
  "stable_id": "C-trace-mining-feedback-substrate",
  "canonical_key": "C | trace-mining | defines | decision-shaped-feedback-substrate | agent-execution-traces | source-digest:bf993b8d",
  "series": "C",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "定義與機制由多個同源 timestamp span 支持；尚無獨立來源或 runtime quality measurements。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:04:48..00:12:57",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->
