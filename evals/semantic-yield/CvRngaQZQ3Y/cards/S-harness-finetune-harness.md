### S-harness-finetune-harness｜Harness → Ceiling → Model Update → Re-Harness

- **核心命題**：先調整可快速回復的 Harness；只有在固定評測顯示能力瓶頸後，才進入模型更新，完成後重新調整 Harness。
- **為什麼重要**：低成本、可歸因的外部調整應先於較重的資料與模型變更。
- **Objective**：在固定 task/eval 下提高品質，同時控制 latency、cost 與 rollback 風險。
- **Preconditions**：Traces 可回讀；model/harness/data 版本可辨識；存在 frozen eval、held-out slices、baseline 與 rollback path。
- **策略邏輯**：
  1. 用高能力 model 建立 task feasibility ceiling。
  2. 從 traces 找出 prompt、context、tools、memory 或 orchestration 可修復的 mismatch。
  3. 量測 harness ceiling；只有缺失 capability 仍阻塞任務時才建立模型更新候選。
  4. 更新後重新適配 Harness，並用同一 eval 重播。
- **Ecological Context**：
  - 主角做法：先用 Harness 建立低成本回饋，再以固定 eval 判定 ceiling。
  - 環境常態：prompt、tool、model 與 dataset 常被同時改動，導致 attribution 消失。
  - 競對做法：UNKNOWN；來源未提供同口徑 competitor workflow。
- **Trade-offs**：Harness 易回復但受 base capability 限制；模型更新增加資料治理、訓練與部署負擔。
- **Pre-mortem Glitches**：eval leakage、一次改太多變量、只保留成功 traces、held-out 或 safety 退化。
- **Success Criteria**：同一 eval 可重播；主要指標改善；guardrails 無不可接受退化；成本同口徑；可恢復上一組 artifact。
- **Implementation Path**：[[P-trace-driven-improvement-cycle]]
- **證據與狀態**：NORMATIVE · SUPPORTED · MEDIUM
  - [[EV-cvrngaqzq3y-harness-ceiling]]：`00:08:55–00:09:55`。
  - [[EV-cvrngaqzq3y-sandwich]]：`00:15:58–00:16:59`。
- **反證／限制**：嚴格 device/latency 約束或明確缺失基礎 capability 的任務，harness-first 未必最佳。
- **Typed Links**：ROOT ← [[C-model-harness-task-fit]] · FLOW → [[P-trace-driven-improvement-cycle]] · VALIDATED_BY → [[V-semantic-yield-replay]]

<!-- CARD_META
{"stable_id":"S-harness-finetune-harness","canonical_key":"S | agent-team | sequences | harness-ceiling-model-update-reharness | narrow-agent-tasks | source-digest:bf993b8d","series":"S","lifecycle":"ACTIVE","revision":1,"source_dependency_key":"youtube-video:CvRngaQZQ3Y","source_provenance":["youtube:CvRngaQZQ3Y:youtube-transcript-ai#timestamp:00:08:55..00:16:59"],"unresolved_links":[]}
-->
