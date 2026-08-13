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

### S-model-harness-task-fit-iteration｜先證明可行，再把 Model、Harness、Task 一起 Fit

- **核心命題**：Agent 改進不應只換 model；更可靠的策略是固定 task/eval，先用高能力 model 證明可行，再以 traces 調整 harness、測試較低成本 model，於 harness ceiling 後才考慮 narrow fine-tuning。
- **為什麼重要**：這條路徑同時處理品質、成本與迭代速度，並避免把 model leaderboard 當成產品成效。

- **Objective**：在固定 task 與 guardrails 下，提高可重播的品質指標，同時量測 inference cost、latency、human-review burden 與 failure taxonomy。
- **Preconditions**：
  - 已啟用可追蹤的 Agent execution。
  - 有 frozen eval、holdout 與明確 oracle。
  - model、prompt、tools、skills、memory 與 dataset 版本可辨識。
  - 可以保留 baseline 與 rollback artifact。
- **策略邏輯**：
  1. 先用能力較強的 model 測試 task 是否可完成。
  2. 讀取成功與失敗 traces，找出 model intelligence 與 harness guidance 的邊界。
  3. 在相同 eval 上測試較低成本或 open model，透過 harness 補足可補足的差距。
  4. 當 harness 修改連續無法再提升時，才針對 narrow vertical task 建立 fine-tuning candidate。
  5. Fine-tuning 後再次做 harness engineering，而不是把 weights 視為終點。
- **Ecological Context**：
  - 主角做法：[[D-harness-finetune-harness-sandwich]]
  - 環境常態：[[D-four-stage-trace-improvement-loop]]
  - 競對做法：UNKNOWN；來源未提供可比較的競對流程。
- **Trade-offs**：
  - 高能力 model 可快速判斷 feasibility，但成本較高。
  - Open/smaller model 可能降低成本，但需要更強的 harness 與 regression control。
  - Fine-tuning 可提高 narrow-task fit，卻增加 dataset governance、deployment 與 model drift 負擔。
  - 高 inference volume 可能把經濟模型從 token cost 改成 hardware-cluster cost。
- **Pre-mortem Glitches**：
  - Eval 被 Agent gaming：held-out cases 同步上升前不得接受改動。
  - Harness overfit：不同 task slice 或新時間窗立即退化。
  - Trace leakage：訓練資料含 eval answer 或 reviewer hints。
  - 成本假象：只比較 token price，忽略 cluster utilization、latency 與人類審查。
  - Model 名稱或版本被 auto-caption 誤辨：由 [[K-auto-caption-identifiers-unverified]] 阻擋精確選型結論。
- **Success Criteria**：
  - 同一 frozen eval 與 task mix 可重播。
  - 主要品質指標改善，且 safety/reliability guardrail 無退化。
  - 成本與 latency 使用同一口徑記錄。
  - 改動能綁定到 model、harness、dataset 與 artifact digest。
  - 失敗時可回到上一個已驗證組合。
- **Implementation Path**：[[P-trace-driven-agent-improvement-cycle]]

- **證據與狀態**：NORMATIVE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-model-cost-path]]：00:07:53–00:10:25；來源描述 strongest-model feasibility、open model/harness、fine-tuning 與 token-to-hardware economics。
  - [[EV-cvrngaqzq3y-fit-function]]：00:12:57–00:14:28；來源提出 model–harness–task fit。
- **反證／限制**：這是由演講實務編譯出的策略，不是本次環境已執行的 optimization experiment。
- **Typed Links**：
  - ROOT ← [[C-model-harness-task-fit]]
  - ROOT ← [[D-harness-finetune-harness-sandwich]]
  - FLOW → [[P-trace-driven-agent-improvement-cycle]]
  - VALIDATED_BY → [[V-trace-improvement-procedure-replay]]

<!-- CARD_META
{
  "stable_id": "S-model-harness-task-fit-iteration",
  "canonical_key": "S | agent-team | applies | model-harness-task-fit-iteration | production-agent-improvement | source-digest:bf993b8d",
  "series": "S",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "策略順序由來源直接支持；success criteria、rollback 與 contamination controls 是 compiler 的 bounded normative extension。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:07:53..00:16:59",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->

### P-trace-driven-agent-improvement-cycle｜可回滾的 Trace-Driven Agent 改進程序

- **核心命題**：把 trace-driven improvement 落地時，必須把每次 model/harness/data 變更封裝成單一、可重播、可驗收、可 rollback 的實驗。
- **為什麼重要**：沒有版本、oracle 與 rollback 的「看 traces 後改 prompt」無法區分真正改善、偶然波動與 eval contamination。

- **Scenario**：已有可執行 Agent、可保存 traces，且需要改善品質、成本或 long-horizon behavior。
- **Value**：把模糊的「Agent 犯錯」轉成 decision-relevant cases、frozen eval、單變量 patch 與 production feedback。
- **Prerequisites**：
  - Trace schema 能保存 input、tool calls、messages、outcome、model/harness identity 與時間。
  - 有資料處理權限、PII/secrets policy 與 retention rule。
  - 有 baseline release、registry snapshot、eval oracle 與 canary/rollback path。
- **Inputs**：
  - 一個明確 decision question。
  - 綁定 source digest 的 trace cohort。
  - Baseline model/harness/task configuration。
  - Frozen eval、holdout、cost/latency counters 與 guardrails。
- **Exploit / Procedure**：
  1. 在受控 cohort 啟用 tracing，保存 raw trace 與 immutable digest。
     - Validation：每個 run 可回讀 model、prompt/tools、task、outcome 與 trace ID。
     - Failure Signal：缺少 tool call、版本、terminal outcome 或 trace span。
  2. 定義一個 decision question，例如 failure cluster、compaction 後退化或 model counterfactual。
     - Validation：問題能映射到 oracle 與會被改變的決策。
     - Failure Signal：問題只能產生泛化摘要，不能改變 action。
  3. 對 cohort 執行 trace mining，保留 selected cases、rejected cases、query/config 與 reviewer decisions。
     - Validation：相同 input/digest 可重播 selection。
     - Failure Signal：只輸出結論，沒有 case ID、locator 或 rejection reason。
  4. 由 traces 建立或更新 eval；隔離 training、development 與 held-out slices。
     - Validation：每個 case 有 provenance，且 eval answer 未進入訓練資料。
     - Failure Signal：duplicate、leakage、source drift 或 label 無法追溯。
  5. 先以 baseline 與高能力 model 建立 feasibility/capability ceiling，再提出單一 harness 或 model patch。
     - Validation：一次只改一個主要 decision variable；其他條件固定。
     - Failure Signal：同時換 model、prompt、tools 與 dataset，無法 attribution。
  6. 在 frozen eval 重播 patch，記錄品質、failure taxonomy、cost、latency 與 guardrails。
     - Validation：結果綁定到完整 artifact digests，且 held-out slice 同方向。
     - Failure Signal：只報 aggregate score、無失敗樣本或 safety regression。
  7. Harness ceiling 明確出現後，才建立 narrow-task fine-tuning dataset 與獨立 qualification。
     - Validation：dataset license/provenance、train/eval separation 與 base-model identity 完整。
     - Failure Signal：用同一 traces 同時訓練與宣告通過。
  8. 以 canary 部署被接受的組合，持續收集新 traces；production evidence 與 offline eval 分開記錄。
     - Validation：canary 指標與 rollback trigger 可觀察。
     - Failure Signal：線上異常但無法定位到 release/model/harness revision。
- **Expected Output**：
  - Trace cohort manifest。
  - Decision question 與 oracle。
  - Case set／eval set 與 provenance。
  - Model/harness patch。
  - Reproducible evaluation report。
  - Canary receipt、rollback trigger 與下一輪 cursor。
- **Rollback**：恢復上一個 model/harness/registry snapshot；停止 contaminated dataset；保留失敗 artifact，以 `SUPERSEDES` 記錄而非刪除歷史。
- **Failure Handling**：
  - Trace 不完整 → 阻擋 mining，先修 instrumentation。
  - Eval leakage → 廢棄受污染結果，重建 holdout。
  - Patch 無 attribution → 拆成單變量 experiments。
  - Production regression → 觸發 canary rollback，將新 traces 建成 X/V work。
- **Security / Privacy Constraints**：最小權限、PII/secret redaction、tenant isolation、retention、review access 與 training eligibility 必須分開治理。
- **Toolset**：trace store、query/mining agent、eval runner、model/harness registry、dataset lineage、canary deployment；來源未指定固定工具版本。
- **Execution Status**：UNTESTED
- **Validated By**：[[V-trace-improvement-procedure-replay]]

- **證據與狀態**：NORMATIVE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-recipe]]：00:00:44–00:02:17；來源提供 ship、collect、mine、experiment 的基本順序。
  - [[EV-cvrngaqzq3y-dense-feedback]]：00:14:58–00:15:58；來源認為 pass/fail 太稀疏，traces 可提供下一步所需的 dense feedback。
- **反證／限制**：本次沒有 Agent runtime、frozen eval、model registry 或 canary artifact；所有步驟尚未執行。
- **Typed Links**：
  - ROOT ← [[S-model-harness-task-fit-iteration]]
  - VALIDATED_BY → [[V-trace-improvement-procedure-replay]]
  - DEPENDS_ON → [[K-auto-caption-identifiers-unverified]]
  - DEPENDS_ON → [[K-rights-and-note-completion-authority]]

<!-- CARD_META
{
  "stable_id": "P-trace-driven-agent-improvement-cycle",
  "canonical_key": "P | agent-operator | executes | trace-driven-improvement-cycle | controlled-agent-runtime | source-digest:bf993b8d",
  "series": "P",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "流程骨架由來源支持；validation、failure handling、security 與 rollback 是 compiler 為可執行性補上的 normative contract，尚未測試。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:00:44..00:16:59",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->

### C-model-harness-task-fit｜Agent 能力是 Joint Fit，不是單一 Model 屬性

- **核心命題**：Task performance 應被建模為 model、harness 與 task/data 的 joint fit；任何一層變動都可能改寫 Agent 行為。
- **為什麼重要**：這能避免把 prompt/tool/orchestration 的不足錯判成 model intelligence 不足，也避免只靠換 model 解決可由 harness 修復的問題。

- **定義**：在固定 task contract 下，選擇 model，配置 prompt/tools/skills/memory/orchestration 的 harness，並用資料與 eval 反覆 fit，使目標行為通過驗收。
- **Non-Goals**：
  - 不是用單一 leaderboard score 選 model。
  - 不是假設更大的 model 在所有 task 都最划算。
  - 不是將 eval score 上升直接等同 production value。
- **演化**：來源以 scikit-learn 的 fit 概念作類比，但未提供版本化歷史；時間演化為 UNKNOWN。
- **底層機制**：
  1. Model 提供基礎 capability。
  2. Harness 改變 context、tool affordance、feedback 與 execution path。
  3. Task/data 定義要 hill-climb 的目標與分布。
  4. Traces 揭示三者的 mismatch，eval 則提供可重播 oracle。
- **Invariants**：
  - 比較時保持 task、eval、time window 與 measurement contract 一致。
  - Model/harness/data identity 必須可追溯。
  - Auto-research 產生的 score improvement 必須防止 cheating 與 holdout regression。
- **Boundary Conditions**：
  - 沒有 stable task definition 或 held-out data 時，fit 可能只是 overfit。
  - Harness 已飽和且錯誤來自缺失 capability 時，weights update 才可能合理。
- **正例**：[[D-harness-finetune-harness-sandwich]]
- **反例**：不固定 task/eval 就直接比較兩個 model，或一次同時改 model、prompt、tools 與 dataset。

- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-fit-concept]]：00:12:57–00:14:28；來源將 classical ML fit 類比到 model–harness–task fit。
  - [[EV-cvrngaqzq3y-auto-research-risk]]：00:14:28–00:14:58；來源指出 Agent 能讓 score 上升，但可能作弊。
- **反證／限制**：來源未提供一個可直接重跑的 joint-fit algorithm、資料集或統計檢定。
- **Typed Links**：
  - ROOT ← [[D-harness-finetune-harness-sandwich]]
  - FLOW → [[S-model-harness-task-fit-iteration]]
  - VALIDATED_BY → [[V-trace-improvement-procedure-replay]]

<!-- CARD_META
{
  "stable_id": "C-model-harness-task-fit",
  "canonical_key": "C | model-harness-task-fit | defines | joint-agent-performance-function | agent-development | source-digest:bf993b8d",
  "series": "C",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "概念由來源直接提出；invariants 與 anti-cheating boundary 是由來源風險陳述推導的 bounded inference。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:12:57..00:16:59",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->

### C-continual-learning-state-planes｜Continual Learning 必須更新三個 State Plane

- **核心命題**：長期 Agent 的 continual learning 不只更新 weights；來源把可更新狀態分成 observational/training data、harness 與 memory 三個平面。
- **為什麼重要**：若所有學習都塞進單一 memory file 或單一 fine-tune，系統會失去更新權責、驗證邊界與 rollback 能力。

- **定義**：
  - Data Plane：Agent 在環境中執行後形成的 observational/training data。
  - Harness Plane：prompt、tools、skills、orchestration 與 execution scaffolding 的更新。
  - Memory Plane：跨 run 保留、整理、淘汰與重組的長期狀態。
- **Non-Goals**：
  - 不是把所有歷史 append 到一個無限成長的檔案。
  - 不是每次觀察都立即寫回 weights。
  - 不是未經 eval 就把 trace-derived inference 當成 memory fact。
- **演化**：來源描述面向 year、5-year、decade、lifetime 的長期 Agent 假設，但沒有已驗證的版本演化資料。
- **底層機制**：
  1. Agent 在環境採取 actions，產生 traces。
  2. Trace mining 決定哪些觀察應成為 training data、harness patch 或 memory candidate。
  3. Sleep-time／dreaming 類背景處理重新整理全生命週期 traces。
  4. 每個 plane 使用不同 admission、validation、retention 與 rollback contract。
- **Invariants**：
  - 三個 plane 的 authority、version 與 evidence grade 分離。
  - Memory update 必須支援 supersession、forgetting 與 conflict handling。
  - Production observations 不得自動升級成 verified truth 或 training eligibility。
- **Boundary Conditions**：
  - 來源未定義 sleep-time/dreaming 的具體 algorithm、頻率、成本或 oracle。
  - 長期記憶涉及 privacy、staleness、tenant boundary 與錯誤累積。
- **正例**：[[D-four-stage-trace-improvement-loop]]
- **反例**：把 Agent 視為 append-only log，永遠只追加、不淘汰、不重寫、不記錄 supersession。

- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-three-state-planes]]：00:16:59–00:18:30；來源依序描述 observational/training data、harness updates 與 memory。
  - [[EV-cvrngaqzq3y-memory-not-append-only]]：00:17:59–00:19:00；來源明確排除長期 Agent 只使用巨大 append-only file。
- **反證／限制**：三平面架構在來源中是設計主張，沒有 longitudinal experiment 或 failure-rate artifact。
- **Typed Links**：
  - ROOT ← [[N-trace-data-to-agent-improvement-loop]]
  - ROOT ← [[D-four-stage-trace-improvement-loop]]
  - DEPENDS_ON → [[K-auto-caption-identifiers-unverified]]

<!-- CARD_META
{
  "stable_id": "C-continual-learning-state-planes",
  "canonical_key": "C | continual-learning | separates | data-harness-memory-state-planes | long-lived-agents | source-digest:bf993b8d",
  "series": "C",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "三個平面由來源直接陳述；authority/retention/rollback 分離是為避免狀態污染而做的 bounded systems inference。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:16:59..00:19:00",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->

### D-four-stage-trace-improvement-loop｜Ship、Collect、Mine、Experiment 的四階段 Case

- **核心命題**：來源提出一個 decision-relevant case：先讓 Agent 在真實環境運作，再收集 traces、挖掘資料，最後用既有 traces 驗證新 prompt/tool/orchestration/loop 是否改善。
- **為什麼重要**：它提供整個演講的最小可操作骨架，並把 offline analysis 接回 deployment decision。

- **Entity**：負責 production Agent 的工程團隊。
- **Behavior / Case**：以四階段迴圈把 execution data 轉成下一版 Agent 的實驗輸入。
- **操作手法**：
  1. Ship Agent，讓它在環境中執行。
  2. Collect traces，保存 tool calls、output messages、API 與 CLI interactions。
  3. Mine trace data；來源指出資料量可能達 gigabytes 或 terabytes。
  4. 以既有 traces 執行 data-driven experiments，比較 prompt、tool、orchestration 或 loop patch。
- **獨特特徵**：最後一步不是閱讀摘要，而是要求變更在歷史 traces/eval 上產生可比較結果。
- **Shadow Evidence**：
  - [[EV-cvrngaqzq3y-stage-ship]]：00:00:44–00:01:17。
  - [[EV-cvrngaqzq3y-stage-collect]]：00:01:17–00:01:47。
  - [[EV-cvrngaqzq3y-stage-mine-experiment]]：00:01:47–00:02:17。
- **Outcome**：來源將此迴圈作為改善 recipe；沒有提供本次四階段流程的 observed benchmark result，因此 outcome 為 SOURCE_REPORTED。
- **Comparison Target**：N/A；來源沒有同口徑的 passive-logging control case。

- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-four-stage-loop]]：00:00:44–00:02:17；同一演講中的連續描述。
- **反證／限制**：四階段順序可能是必要但不充分；資料品質、oracle、privacy 或 feedback latency 失敗仍會讓閉環無效。
- **Typed Links**：
  - FLOW → [[N-trace-data-to-agent-improvement-loop]]
  - FLOW → [[P-trace-driven-agent-improvement-cycle]]
  - INSTANCE_OF → [[C-trace-mining-feedback-substrate]]

<!-- CARD_META
{
  "stable_id": "D-four-stage-trace-improvement-loop",
  "canonical_key": "D | agent-team | executes | ship-collect-mine-experiment-loop | production-agent-improvement | source-digest:bf993b8d",
  "series": "D",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "四個連續階段由單一 secondary transcript 直接陳述；未有 independent outcome artifact。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:00:44..00:02:17",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->

### D-open-model-trace-judge-cost-claim｜Open Model 接近 Opus Trace Judging 的來源主張

- **核心命題**：來源陳述：在與 Harvey 相關的 legal benchmark 工作中，較便宜的 open model 經 model trials 與 harness engineering 後，可大致接近 Opus 的 trace-judging capability，成本低約 1 或 2 個數量級。
- **為什麼重要**：若可重現，trace mining 不必全部使用 frontier model，會直接改變大量 traces 的 unit economics。

- **Entity**：來源所稱的 LangChain–Harvey trace-judging experiment。
- **Behavior / Case**：以 Opus 作 capability reference，再測試 open model 與 trace-informed harness。
- **操作手法**：
  1. 先以高能力 model 判斷 task feasibility。
  2. 在 traces 上觀察 reasoning mismatch。
  3. 測試多個 open models。
  4. 用較明確 guidance/harness 補足可補足的差距。
- **獨特特徵**：比較目標是 trace judging，而不是一般聊天 benchmark；成本主張為「1 或 2 個數量級」。
- **Shadow Evidence**：
  - [[EV-cvrngaqzq3y-harvey-open-model]]：00:07:53–00:08:55。
- **Outcome**：SOURCE_REPORTED；來源回答大致可行，但未附 model revision、dataset、score、sample size、cost table 或 runtime artifact。
- **Comparison Target**：Opus trace judging。

- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · LOW
  - [[EV-cvrngaqzq3y-open-model-cost-claim]]：00:08:25–00:08:55；精確保留「1 或 2 個數量級」的成本尺度。
- **反證／限制**：只要固定 benchmark、相同 judge contract 與完整成本口徑下無法重現 capability/cost 結果，此 claim 即被削弱或 falsified；專有名詞亦受 [[K-auto-caption-identifiers-unverified]] 阻擋。
- **Typed Links**：
  - FLOW → [[C-model-harness-task-fit]]
  - FLOW → [[S-model-harness-task-fit-iteration]]
  - DEPENDS_ON → [[K-auto-caption-identifiers-unverified]]

<!-- CARD_META
{
  "stable_id": "D-open-model-trace-judge-cost-claim",
  "canonical_key": "D | langchain-harvey-experiment | compares | open-model-vs-opus-trace-judging-cost | legal-benchmark | source-digest:bf993b8d",
  "series": "D",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "只有單一 secondary auto-caption transcript 的 source statement；沒有 benchmark artifact，且若干 model/product identifiers 待校對。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:07:53..00:08:55",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->

### D-harness-finetune-harness-sandwich｜Harness → Fine-Tune → Harness 的介入順序

- **核心命題**：來源建議先用 harness engineering 取得快速 feedback；在 harness ceiling 飽和後才做 narrow-task fine-tuning，必要時再回到 harness engineering。
- **為什麼重要**：這個順序把低成本、可快速 rollback 的外部調整放在較重的 weights update 之前。

- **Entity**：來源所描述的 LangChain customer-improvement practice。
- **Behavior / Case**：依 feedback speed 與 capability ceiling 選擇 harness 或 fine-tuning。
- **操作手法**：
  1. 優先取得 human labels 或 Agent execution feedback。
  2. 用 harness engineering 快速迭代 prompt/context/tool guidance。
  3. 當 eval 顯示 harness ceiling 飽和，再針對 narrow vertical task fine-tune。
  4. Fine-tuning 後繼續調整 harness。
- **獨特特徵**：來源把 harness feedback latency 描述為可能約 **2 分鐘**，並稱許多團隊只靠 harness 已能滿足 customer use case。
- **Shadow Evidence**：
  - [[EV-cvrngaqzq3y-two-minute-feedback]]：00:15:58–00:16:29。
  - [[EV-cvrngaqzq3y-sandwich]]：00:16:29–00:16:59。
- **Outcome**：SOURCE_REPORTED；沒有提供團隊數量、task distribution 或 fine-tuning lift。
- **Comparison Target**：在尚未量測 harness ceiling 前直接 fine-tune。

- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-harness-ceiling]]：00:08:55–00:09:55；來源描述 prompt/harness improvement 達到 intelligence threshold 後再轉向 fine-tuning。
- **反證／限制**：對需要新增基礎 capability、嚴格 latency 或固定 device constraints 的 task，harness-first 未必是最佳順序；「2 分鐘」沒有環境與分布說明。
- **Typed Links**：
  - FLOW → [[C-model-harness-task-fit]]
  - FLOW → [[S-model-harness-task-fit-iteration]]
  - FLOW → [[P-trace-driven-agent-improvement-cycle]]

<!-- CARD_META
{
  "stable_id": "D-harness-finetune-harness-sandwich",
  "canonical_key": "D | langchain-practice | sequences | harness-finetune-harness | narrow-agent-tasks | source-digest:bf993b8d",
  "series": "D",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "介入順序與 2 分鐘說法由單一 secondary transcript 直接支持；缺少 sample、environment 與 outcome artifacts。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:08:55..00:09:55",
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:15:58..00:16:59",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": []
}
-->

### V-trace-improvement-procedure-replay｜Trace-Driven 改進程序的重播驗證

- **核心命題**：[[P-trace-driven-agent-improvement-cycle]] 只有在 frozen eval、相同 task mix 與完整 artifact identity 下重播，才能判斷是否真正改善。
- **為什麼重要**：來源提出 feedback loop，但本次只有逐字稿與 acquisition artifacts，沒有 Agent runtime 或 evaluation result。

- **Target Assertion**：[[P-trace-driven-agent-improvement-cycle]] 能提高 Agent 品質並維持可接受的成本與 guardrails。
- **Verification Method**：runtime replay + controlled evaluation + canary observation。
- **Oracle**：
  - Frozen eval 的主要 task metric。
  - Held-out failure taxonomy。
  - Safety/reliability guardrails。
  - Cost、latency 與 human-review burden。
  - Production canary rollback triggers。
- **Environment / Fixture**：NOT_PROVIDED；需要固定 model revision、harness revision、trace cohort digest、task distribution、eval/holdout 與 infrastructure profile。
- **Procedure**：
  1. 對 baseline model/harness 執行 frozen eval，保存 artifacts。
  2. 僅套用一個主要 patch，重跑同一 eval。
  3. 比較 aggregate 與 per-slice result，檢查 held-out、safety 與成本。
  4. 通過 offline gate 後進入 canary，觀察真實 traces 與 rollback trigger。
- **Expected Result**：主要目標改善，且 held-out、guardrail、cost/latency contract 無不可接受退化；所有結果可綁定到 exact artifacts。
- **Observed Result**：NOT_RUN
- **Verdict**：NOT_RUN
- **Artifacts**：NONE
- **Limitations**：本次執行只驗證 transcript acquisition、normalization 與 v7.1 compilation artifact；沒有執行任何 Agent improvement experiment。

- **證據與狀態**：HYPOTHESIS · UNCHECKED · LOW
  - [[EV-cvrngaqzq3y-verification-need]]：來源提供 procedure rationale，但沒有可直接檢查的 benchmark output。
- **反證／限制**：即使 offline eval PASS，也不能單獨證明 production causality；需要 canary/production evidence 與 contamination review。
- **Typed Links**：
  - ROOT ← [[P-trace-driven-agent-improvement-cycle]]
  - VALIDATED_BY → N/A：本卡本身是待執行 validator。
  - DEPENDS_ON → [[K-auto-caption-identifiers-unverified]]

<!-- CARD_META
{
  "stable_id": "V-trace-improvement-procedure-replay",
  "canonical_key": "V | trace-driven-improvement-cycle | verifies | quality-cost-guardrail-lift | controlled-agent-runtime | not-run",
  "series": "V",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "來源沒有 runtime experiment artifacts；本卡是 compiler 建立的 verification plan，Observed Result 與 Verdict 均為 NOT_RUN。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:14:28..00:16:59",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": [],
  "execution_artifacts": []
}
-->

### K-auto-caption-identifiers-unverified｜Auto-Caption 的專有名詞與版本仍未解鎖

- **核心命題**：目前 transcript 足以支援概念與流程級編譯，但不足以對人㉩、產品、model version、benchmark 與 research acronym 做高信心 canonical naming。
- **為什麼重要**：錯一個 model version、產品名稱或 benchmark 名稱，就可能讓後續技術選型、搜尋與 claim mapping 指向錯誤實體。

- **Unknown**：
  - 影片標題使用「Vivek Trivedy」，caption 開場顯示「I'm Vic」；兩者是否為暱稱、截斷或 ASR error 未校對。
  - Candidate strings 包含 `GPT 5.5`／`55`、`GLM 5.2`、`Cloud Code`、`LangSplat engine`、`OPD`、`OPSD`、`trySFT` 與 `terminal benches`；canonical spelling/version 尚未確認。
  - Broker 未提供原始 YouTube VTT/SRT、caption track ID 或 punctuation provenance。
- **Why Unresolved**：取得的是 `en (auto-generated)` secondary transport；raw platform caption 不可回讀。正規化器只執行 exact duplicate removal 與 footer isolation，刻意不修正任何詞彙。
- **Impact**：
  - [[D-open-model-trace-judge-cost-claim]] 維持 LOW confidence。
  - 無法安全建立精確 model/product/benchmark entity graph。
  - Claim mapping 與外部搜尋必須等待 canonical spelling。
- **Evidence Needed**：
  - Creator slides、官方 agenda/description 或 creator-reviewed transcript。
  - 原始 VTT/SRT 或逐 timestamp 人工校對記錄。
  - 每個 identifier 的 canonical URL/version 與 reviewer receipt。
- **Retrieval / Test Plan**：
  1. 以 00:00:13–00:19:30 的 timestamp 對照影片畫面、字幕與官方活動資料。
  2. 為每個 high-impact identifier 記錄 raw token、canonical form、locator、reviewer 與 evidence digest。
  3. 重跑 canonical-key resolution，若實體改變則用 `SUPERSEDES` 更新受影響卡片。
- **Unblock Criteria**：所有會改變技術選型或 claim identity 的名稱、版本與 acronym 均有至少一個可回讀的一手 anchor。
- **Priority**：HIGH

- **證據與狀態**：OBSERVATION · TESTED · HIGH
  - [[EV-cvrngaqzq3y-normalization-report]]：GitHub Actions run `31698798606`；raw subject 11,290 words 正規化為 3,797 words，移除 7,214 個 adjacent duplicate tokens、279 個 cross-cue overlap tokens、542 次 exact collapse，並隔離 240 個 transport-footer characters。
  - [[EV-cvrngaqzq3y-source-manifest]]：source manifest 狀態為 `needs-review`，且明示 raw YouTube caption track identity 不可用。
- **反證／限制**：正規化測試只證明 deterministic transport-noise removal；不證明 auto-caption 的 lexical accuracy。
- **Typed Links**：
  - ROOT ← [[D-open-model-trace-judge-cost-claim]]
  - ROOT ← [[C-continual-learning-state-planes]]

<!-- CARD_META
{
  "stable_id": "K-auto-caption-identifiers-unverified",
  "canonical_key": "K | auto-caption-identifiers | blocks | canonical-entity-resolution | video-CvRngaQZQ3Y | run-31698798606",
  "series": "K",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "GitHub Actions normalization artifacts可直接檢查，因此 gap 的存在為 HIGH-confidence observation；具體 canonical spellings仍未知。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "actions-run:31698798606#normalized/normalization-report.json",
    "source-manifest:sm-youtube-CvRngaQZQ3Y-youtube-transcript-ai",
    "sha256:b14ef715744a2d5c0bab99da8bfe4fdcf46a90ebb513dc4a06e6e489177a2a0e",
    "sha256:bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462"
  ],
  "unresolved_links": [],
  "normalization_report_sha256": "sha256:363f2fd1285986330ad60950b84fc627b383c57c013a05cd89e67934ecffbced"
}
-->

### K-rights-and-note-completion-authority｜逐字稿可評估，但尚不能成為 Completed Note

- **核心命題**：本次取得的 transcript 只能用於 private transient evaluation；缺少已驗證 rights basis，因此不能把 full transcript 持久化公開、不能把 note 標記 completed，也不能自動提高 downstream claim/Skill authority。
- **為什麼重要**：技術上能取得字幕，不等於具備永久保存、再發布或訓練使用的權限。

- **Unknown**：影片與字幕是否屬於 owned、licensed、creator-permission、public-domain 或 user-provided-media 的哪一種可驗證權利基礎。
- **Why Unresolved**：本次 attestation 是 `user-directed-evaluation`，authorization status 為 `unverified-evaluation-only`；沒有 creator/license receipt。
- **Impact**：
  - `note_completion_allowed = false`。
  - Raw transcript 只保存在 7-day private Actions artifact，不提交 Git repository。
  - `may_raise_claim_evidence = false`、`may_enable_skill_routing = false`。
  - 本批卡片是 evaluation artifact，不是完成的 canonical note。
- **Evidence Needed**：
  - Ownership、license、creator permission、public-domain evidence，或使用者提供的合法 media/source。
  - 明確允許的 retention、transformation、sharing 與 training scope。
- **Retrieval / Test Plan**：
  1. 取得可回讀的 rights reference 與允許範圍。
  2. 重新執行 acquisition，將 authorization status 改為 `verified`。
  3. 完成人工 transcript review、v7.1 external QG-01..QG-24 validation、sidecar persistence 與 read-back。
  4. 最後才允許 Sheet/Note status compare-and-set 為 completed。
- **Unblock Criteria**：verified rights artifact、人工校對 receipt、external quality-gate evidence 與 storage read-back 全部存在。
- **Priority**：CRITICAL

- **證據與狀態**：OBSERVATION · TESTED · HIGH
  - [[EV-cvrngaqzq3y-chain-summary]]：GitHub Actions run `31698798606` 的 chain summary 記錄 `note_completion_allowed: false` 與 `independent_corroboration_count: 0`。
  - [[EV-cvrngaqzq3y-authorization]]：2026-08-13T12:10:47Z；authorization=`unverified-evaluation-only`、rights_basis=`user-directed-evaluation`。
- **反證／限制**：取得合法權利基礎後，這個 blocker 可被解除；但 transcript accuracy 與 external quality gates 仍需獨立通過。
- **Typed Links**：
  - ROOT ← [[P-trace-driven-agent-improvement-cycle]]
  - ROOT ← [[K-auto-caption-identifiers-unverified]]

<!-- CARD_META
{
  "stable_id": "K-rights-and-note-completion-authority",
  "canonical_key": "K | transcript-rights | blocks | completed-note-and-downstream-authority | video-CvRngaQZQ3Y | run-31698798606",
  "series": "K",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "影片 CvRngaQZQ3Y；2026-08-13 取得的 English auto-generated secondary transcript candidate；未完成人工校對",
  "confidence_basis": "Authorization、chain summary 與 authority flags 來自可回讀 GitHub Actions artifacts；未提供可驗證 rights receipt。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "actions-run:31698798606#chain-summary.json",
    "actions-run:31698798606#fallback-youtube-transcript-ai/manifest.json",
    "artifact-digest:sha256:2184ec48e49069fe8e7e5f7e4d6ad748e20bf1d65e7f9c82a0d5ac9d6f1ab225"
  ],
  "unresolved_links": []
}
-->

<!-- RUN_STATE
{
  "status": "CONTINUE",
  "next_cursor": "REVIEW::CvRngaQZQ3Y::identifiers-rights-external-gates",
  "remaining_work": [
    "human-review-proper-nouns-model-versions-and-acronyms",
    "obtain-verified-rights-basis",
    "obtain-raw-caption-or-creator-reviewed-transcript",
    "run-external-qg-01-through-qg-24-validator",
    "persist-canonical-registry-state-and-read-back"
  ],
  "registry_revision": 1
}
-->
