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
