### K-visual-identifier-evidence-gap｜投影片圖表與專有名詞仍缺少可回讀的一手 Anchor

- **核心命題**：此次輸出改善了 relation graph、equation、comparison 與 dataflow，但這些是 transcript-grounded host projections，不是對原始 slide/frame 的精確重建。
- **Unknown**：
  - 影片中的 slide boundary、bbox、chart axis、legend、table cells 與 diagram topology。
  - Auto-caption 中的人名、產品、model version、benchmark 與 acronym 的 canonical spelling。
  - Open-model/Opus 比較的完整 score、sample size、cost table 與 model revision。
- **Why Unresolved**：目前 authority 是 secondary auto-generated transcript；沒有 verified local media、creator slides、raw VTT/SRT 或 reviewed frame annotations。
- **Impact**：
  - [[T-trace-judge-comparison]] 只能保留 UNKNOWN-safe matrix。
  - Diagram 是 relation projection，不能標成原始投影片重製。
  - 精確 model selection 與 benchmark claim 保持 provisional。
- **Evidence Needed**：已授權 frames/slides、frame SHA-256、timestamp+bbox、reviewed OCR、chart/table annotation、canonical identifier receipt。
- **Retrieval / Test Plan**：
  1. 取得可驗證的 media/slide rights。
  2. 對 high-signal timestamps抽 frame並保存 digest。
  3. 由 reviewer 標註 OCR、nodes、edges、axes、legend、table/equation。
  4. 重跑 visual coverage；受影響卡片以 revision/SUPERSEDES 更新。
- **Unblock Criteria**：所有會改變 entity identity、數值或圖表 topology 的內容都有可回讀的一手 anchor。
- **Priority**：HIGH
- **證據與狀態**：OBSERVATION · TESTED · HIGH
  - [[EV-cvrngaqzq3y-source-manifest]]：來源狀態為 needs-review，raw platform caption/frame identity 不可用。
  - [[EV-cvrngaqzq3y-normalization-report]]：正規化只移除可證明的重複與 transport metadata，未修正詞彙。
- **反證／限制**：取得合法且可回讀的 frame/slide artifacts 後，此 gap 可部分解除；外部 benchmark 仍需獨立驗證。
- **Typed Links**：ROOT ← [[T-trace-judge-comparison]] · ROOT ← [[C-continual-learning-state-planes]] · VALIDATED_BY → [[V-semantic-yield-replay]]

<!-- CARD_META
{"stable_id":"K-visual-identifier-evidence-gap","canonical_key":"K | visual-and-identifier-evidence | blocks | exact-slide-and-entity-reconstruction | CvRngaQZQ3Y | transcript-only-run","series":"K","lifecycle":"ACTIVE","revision":1,"source_dependency_key":"youtube-video:CvRngaQZQ3Y","unresolved_links":[]}
-->
