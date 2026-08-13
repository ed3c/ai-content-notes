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
