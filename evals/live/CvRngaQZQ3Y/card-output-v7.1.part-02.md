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
