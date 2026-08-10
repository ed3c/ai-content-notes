---
id: sequoia:sable-diffusion-gap
title: Partnering with Sable: Closing the Diffusion Gap
source: Sequoia Capital
source_url: https://sequoiacap.com/article/partnering-with-sable-closing-the-diffusion-gap/
published_at: '2026-07-16'
monetization_score: 99
category: vertical-agents
language: zh-TW
note_format: zettelkasten-v6.6-cyberpunk
storage: private-github-markdown
repository: ed3c/ai-content-notes
path: notes/vertical-agents/2026-07-16-sable-diffusion-gap.md
citation_mapping: pending
library_mapping: pending
---

### N1：Diffusion Gap 變成 AI Employee 的切入口
- **核心衝突**：Frontier AI capability 每月前進，但 Fortune 500 的實際部署速度遠落後；真正 bottleneck 不只是模型 intelligence，而是讓客戶理解 AI 能替他完成什麼工作。
- **關鍵人物/實體**：Sable vs 傳統產品銷售與 demo 流程。
- **衝擊力錨點 (Impact Anchors)**：
  - Sequoia 文章發布於 2026-07-16。
  - Sable 創立不到 1 年。
  - 「Aidan」能以 vision、voice、video、real-time browser interaction 主持 customer calls。
  - Notion custom agents、Decagon agent-building platform 與大型 public enterprises 已被列為使用案例。
  - +150 companies 已在 Sable waitlist。
- **劇情轉折**：AI adoption 問題從「模型能不能做到」轉為「能不能在客戶現場即時展示、理解需求、回答問題並完成互動」。
- **生態背景**：傳統 SaaS demo 依賴 solution engineer / sales engineer；multimodal agent 開始把 product expertise 壓縮成可無限複製的 runtime employee。
- **連結**：
  - 證據支撐：→ [[D1.1]], [[D1.2]], [[D2.1]]
  - 歷史鏡像：≈ [[N2：Sales Engineer → Software Agent]]
  - 治理建立：→ [[G1：AI Employee Production Gate]]

### N2：Sales Engineer → Software Agent
- **核心衝突**：最佳產品專家無法同時服務所有 prospect；AI employee 嘗試把 expertise、demo、adaptive conversation 與 browser execution 合併成 software-scalable labor。
- **關鍵人物/實體**：Human product expert vs Aidan AI employee。
- **衝擊力錨點 (Impact Anchors)**：
  - Aidan 被描述為可自行主持 customer calls，而不是只提供 chat assistance。
  - 核心 technical requirements 包含 low-latency browser use、real-time vision、simultaneous human-agent interaction。
- **劇情轉折**：從「回答產品問題」升級到「在同一 interaction 內看、說、操作 browser、示範結果」。
- **生態背景**：Agentic sales / customer success 競爭不再只比 LLM response quality，而是比 multimodal latency、tool reliability、session state 與 handoff governance。
- **連結**：→ [[C1]], [[C2]], [[S1]]

### Q1：AI Employee 的 moat 是模型，還是 interaction runtime？
- **核心疑問 (The Doubt)**：當所有競爭者都能使用相近 frontier model 時，Aidan 類產品如何形成不可快速複製的優勢？
- **現狀反差 (Reality Gap)**：市場容易把 AI employee 當成「更好的 chatbot」，但文章列出的 hard problems 都在 multimodal runtime：browser use、vision、latency、simultaneous interaction。
- **思維實驗 (Simulation)**：固定同一模型，替換掉 session orchestration、browser stack、latency control、knowledge graph 與 customer-call UX；若效果大幅下降，真正 moat 在 harness/runtime。
- **連結**：← [[D1.1]], [[D1.2]], → [[S1]]

### Q2：+150 waitlist 是需求證據，還是 deployment debt 的前兆？
- **核心疑問 (The Doubt)**：強烈 market pull 是否能轉成 reliable enterprise deployment？
- **現狀反差 (Reality Gap)**：waitlist 證明 demand，卻不能證明 call completion、browser success、policy compliance、handoff quality 或 ROI。
- **思維實驗 (Simulation)**：若 150 個企業同時 onboarding，哪個資源先飽和：FDE、eval creation、browser compatibility、identity integration、security review 或 customer knowledge ingestion？
- **連結**：← [[D2.1]], → [[R1]], [[G1]]

### C1：Diffusion Gap
- **定義**：Frontier capability 與企業實際理解、部署、治理、變現之間的時間差。
- **演化**：早期 gap 來自模型能力不足；現在更多來自 integration、workflow、security、UX、change management 與 proof-of-value。
- **本質**：市場機會存在於「把已有 capability 編譯成客戶可以使用的工作流」。
- **結構特徵**：capability discovery、demo translation、workflow fit、trust、deployment latency。
- **連結**：→ [[D2.1]], [[S2]], [[E1]]

### C2：Multimodal AI Employee Runtime
- **定義**：把 voice、vision、video、browser control、customer context、session memory 與 tool execution 統一到 real-time agent loop 的 runtime。
- **演化**：Chatbot → voice assistant → computer-use agent → synchronous multimodal worker。
- **本質**：價值來自 interaction-to-action latency，而不只是 text generation quality。
- **結構特徵**：streaming ASR/TTS、screen/browser state、vision frame selection、tool/action policy、interrupt handling、handoff、audit trace。
- **連結**：→ [[D1.1]], [[P1]], [[G1]], [[E2]]

### D1.1：Aidan 的 Real-Time Customer Call Runtime
- **操作手法**：在 customer call 中同時處理 voice、vision、video 與 browser interaction；依 prospect goals 調整 demo 與回答。
- **獨特特徵**：不是 async back-office agent，而是 synchronous customer-facing agent，失敗會直接暴露在對話現場。
- **影子證據**：文章點名 Aidan、vision、voice、video、real-time browser interaction 四個 runtime surface。
- **連結**：↔ [[D1.2]] ⟨S1⟩

### D1.2：Low-Latency Browser + Vision + Human-Agent Concurrency
- **操作手法**：在真人 speaking turn 與 agent browser execution 同時維持 shared task state，避免 UI action 與口語說明脫節。
- **獨特特徵**：傳統 chatbot latency 只影響等待感；AI employee latency 會破壞 demo continuity、turn-taking 與 trust。
- **影子證據**：Sequoia 將 low-latency browser use、real-time vision、simultaneous human-agent interaction 明列為 frontier technical breakthroughs。
- **連結**：↔ [[D1.1]] ⟨P1⟩

### D2.1：Market Pull 與 +150 Companies Waitlist
- **操作手法**：Sable 以 frontier startup 與 enterprise deployment 作為 demand signal，並把 product demo/customer explanation 作為 wedge。
- **獨特特徵**：需求跨高速成長公司與大型企業，不局限於單一 vertical。
- **影子證據**：+150 companies on waitlist；Notion、Decagon 與大型 public enterprises 被文章列為已使用或部署情境。
- **連結**：↔ [[D3.1]] ⟨S2⟩

### D3.1：Founding Team / Talent Density
- **操作手法**：創辦團隊聚焦 post-training、reinforcement learning、multimodality；早期 hiring 偏 applied AI researchers 與 customer-obsessed engineers。
- **獨特特徵**：Sequoia 把 technical research depth 與 customer obsession 視為同一 deployment capability 的兩面。
- **影子證據**：四位 founders 皆為 Harvard friends；經歷包含 SpaceX、Google、Meta、Together AI；早期團隊含 10 位 Harvard alumni、former quantitative traders、International Math Olympiad winners。
- **連結**：↔ [[D2.1]] ⟨S3⟩

### S1：Sell the Demonstration, Not the Description
- **策略邏輯**：Agentic GTM 的核心不是產生更漂亮的產品文案，而是在客戶會議中直接操作產品、展示能力、根據對方情境改變路徑。
- **生態位對照 (Ecological Context)**：
  - 主角表現：Aidan 即時說明 + browser action + multimodal feedback。
  - **環境/競對參照**：傳統 chatbot / copilot 多數停在 Q&A，無法在同一 session 完成可見操作。
- **反面教材 (Pre-mortem)**：browser automation 可靠度低、voice latency 高、vision context 過期，導致「會說不會做」。
- **理論基礎**：← [[D1.1]], [[D1.2]]
- **實踐路徑**：→ [[P1]]
- **支撐框架**：← [[T1]], [[G1]]

### S2：Exploit the Diffusion Gap
- **策略邏輯**：不要只等待模型再變強；把今天已存在但企業尚未 operationalize 的 capability 封裝成具 ROI 的 workflow。
- **生態位對照 (Ecological Context)**：
  - 主角表現：把 frontier multimodal/computer-use 能力轉成 customer-facing employee。
  - **環境/競對參照**：大量企業仍用去年 capability 的 deployment pattern。
- **反面教材 (Pre-mortem)**：demo 能力追著 frontier model 更新，但沒有 durable workflow、eval、security、integration，形成 permanent pilot。
- **理論基礎**：← [[C1]], [[D2.1]]
- **實踐路徑**：→ [[R1]]
- **支撐框架**：← [[T1]]

### S3：Research Depth + FDE Discipline
- **策略邏輯**：multimodal agent 的競爭不只在 research benchmark；需要 FDE-style customer loop 把 edge cases 快速回流 runtime/eval。
- **生態位對照 (Ecological Context)**：
  - 主角表現：research-heavy founding team + customer-obsessed engineering。
  - **環境/競對參照**：純 research team 可能缺 deployment context；純 integration team 可能無法解低延遲 multimodal primitives。
- **反面教材 (Pre-mortem)**：只堆 elite talent，但沒有 trace-to-eval / field feedback pipeline。
- **理論基礎**：← [[D3.1]]
- **實踐路徑**：→ [[P2]]
- **支撐框架**：← [[G2]]

### P1：Real-Time AI Employee Harness
- **場景 (Scenario)**：打造 customer call 中可操作 browser 的 multimodal agent。
- **價值 (Value)**：把產品 expertise 從稀缺的人力轉成可規模化 runtime。
- **漏洞利用 (Exploit/How)**：
  1. Voice stream 切成 turn-aware events；同步保留 transcript timecode。
  2. Browser state 每次 action 後產生 DOM/screenshot digest，避免 vision 使用 stale frame。
  3. 將「說明」與「執行」分成 plan/action channels；tool action 需顯式 policy gate。
  4. 在真人插話時立即 cancel / pause unsafe action，保持 shared session state。
  5. 對每個 demo flow 建 success invariant：page reached、field state、artifact created、customer confirmation。
  6. Full trace 保存 voice turn、vision snapshot、browser action、latency、approval、failure taxonomy。
- **工具集 (Toolset)**：WebRTC、browser automation、streaming ASR/TTS、vision model、policy engine、trace store、eval harness。
- **影子技巧**：用「action-to-explanation drift」作獨立 metric；agent 說的畫面與實際 browser state 不一致時直接 fail。
- **連結**：← [[S1]]

### P2：150-Account Deployment Stress Test
- **場景 (Scenario)**：在 waitlist 轉 enterprise onboarding 前，找出 FDE 與 runtime scaling bottleneck。
- **價值 (Value)**：防止 demand signal 被 deployment debt 吞掉。
- **漏洞利用 (Exploit/How)**：
  1. 依 identity/integration/security/browser complexity 將 account 分 tier。
  2. 每 tier 建 reference environment 與 standard onboarding pack。
  3. 追蹤 time-to-first-successful-call、tool failure rate、human takeover rate、p95 voice/action latency。
  4. 對 repeated FDE fixes 做 productization threshold；同一 workaround 出現 3 次以上即轉 canonical feature/eval。
  5. 對每個 account 建 kill switch 與 escalation owner。
- **工具集 (Toolset)**：feature flags、tenant isolation、session replay、customer-specific evals、SLO dashboard。
- **影子技巧**：把 FDE time 當 COGS；否則 waitlist growth 會掩蓋 delivery economics。
- **連結**：← [[S3]]

### T1：AI Employee Production Matrix
- **用途**：把「會 demo」與「可 production」分開評估。
- **結構內容**：
  | 維度 | Demo-grade | Production-grade |
  |---|---|---|
  | Voice | 可對話 | interruption、jitter、latency SLO |
  | Vision | 偶發 screenshot | state freshness、frame policy、PII masking |
  | Browser | happy-path automation | rollback、idempotency、domain allowlist |
  | Customer context | prompt 注入 | tenant ACL、freshness、provenance |
  | Human handoff | 手動介入 | deterministic escalation + state transfer |
  | Audit | transcript | full multimodal/action trace |
  | Security | generic permissions | scoped credentials、network policy、approval gate |
  | Economics | demo 成本忽略 | cost per completed call / retained account |
- **連結**：→ [[S1]], [[S2]], [[P1]]

### R1：AI Employee 90-Day Deployment Roadmap
- **總體目標**：把 multimodal demo agent 轉成 repeatable enterprise deployment。
- **階段劃分**：
  - **Phase 1 Instrument**：建立 voice/browser/vision full trace 與 latency/error taxonomy。
  - **Phase 2 Guard**：domain allowlist、credential scope、approval、cancel、handoff、tenant isolation。
  - **Phase 3 Eval**：用真實 demo flows 建 deterministic success invariants 與 adversarial cases。
  - **Phase 4 Scale**：account tiering、reference environments、FDE productization loop。
  - **Phase 5 Monetize**：以 completed outcome、qualified pipeline 或 deployment ROI 衡量，而非 conversation count。
- **系統風險 (Glitches)**：stale vision、browser drift、voice interruption failure、cross-tenant leakage、FDE COGS explosion、unbounded tool permissions。
- **連結**：→ [[G1]], [[G2]]

### G1：AI Employee Production Gate
- **核心協議 (Protocol)**：Customer-facing autonomous action 必須比 text-only assistant 採用更硬的 execution boundary。
- **具體條款/機制**：
  - Browser domain allowlist。
  - Scoped per-session credentials。
  - Destructive/high-impact action human approval。
  - Voice interruption 即時 pause/cancel。
  - Tenant-isolated context/memory。
  - Full trace + replay。
- **決策流程**：Intent → Plan → Policy Check → Execute → Verify UI State → Explain → Continue/Handoff。
- **違規後果**：任一 verification 或 policy failure 立即停止 autonomy，切 human takeover。
- **連結**：← [[R1]], → [[S1]]

### G2：FDE-to-Product Admission Policy
- **核心協議 (Protocol)**：Repeated customer-specific patch 不能永遠留在 field engineering。
- **具體條款/機制**：
  - workaround 必須被分類與計數。
  - recurring failure 必須產生 canonical eval case。
  - 產品化 feature 必須通過 multi-tenant regression。
  - Customer-specific secrets/data 不可直接進 global prompt。
- **決策流程**：Field Incident → Reproduction → Generic Invariant → Eval → Product Patch → Canary → Admission。
- **違規後果**：無可泛化 evidence 的 patch 保持 tenant-local，不得升級 global behavior。
- **連結**：← [[R1]], → [[S3]]

### E1：The Diffusion Gap Is a Product Surface
- **法則內容**：當 frontier capability 進步快於企業 adoption，最大機會常在 capability translation，而不是再訓練一個更強模型。
- **推論/啟示**：FDE、workflow design、eval、security、UX 都能形成直接可變現產品。
- **支撐證據**：← [[C1]], [[D2.1]], [[S2]]

### E2：Real-Time Action Multiplies Both Value and Failure Cost
- **法則內容**：Agent 從回答問題升級成同步執行 browser action 後，interaction value 上升，但 latency、security、state drift 的 failure cost 也同步放大。
- **推論/啟示**：customer-facing AI employee 必須把 hard guardrails 與 verification 放進 runtime kernel。
- **支撐證據**：← [[C2]], [[D1.1]], [[D1.2]], [[G1]]
