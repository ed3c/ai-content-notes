---
id: latent-space:aiewf26trends
source: Latent Space
canonical_url: https://www.latent.space/p/aiewf26trends
published_at: 2026-07-14
collected_at: 2026-08-11T09:22:10+08:00
repository: ed3c/ai-content-notes
path: notes/agent-engineering/2026-07-14-aiewf-2026-five-trends.md
protocol: v6.6-cyberpunk
---

### N1：AI Engineering 從「做 Agent」轉成「做 Agent 周邊系統」
- **核心衝突**：2023 的問題是 LLM 能否成為 agent；2026 的問題是如何讓 agent 在 production 裡可靠、可治理、可觀測、可持續改善。
- **關鍵人物/實體**：AI Engineer World’s Fair 2026 ecosystem vs 2023 AutoGPT / prompt-engineering era。
- **衝擊力錨點 (Impact Anchors)**：
  - 文章發布於 **2026-07-14**，回顧 AIEWF 2026 的五個趨勢。
  - AI Engineer 這個 framing 可追溯到 **2023-06**；三年後焦點已移到 coding agents、harness engineering、context、evals、loops、enterprise orchestration 與 skills。
- **劇情轉折**：Agent autonomy 不再被視為「把人移除」；human engineer 逐漸移到 outer loop，負責方向、評估、控制與 exception handling。
- **生態背景**：Claude Code、Codex、Gemini CLI、Cursor、Warp 等把 developer interface 從 autocomplete 推向 goal-level agents。
- **連結**：→ [[D1.1]], [[D2.1]], [[D4.1]], [[D5.1]]

### Q1：真正的 Agent Architect 是寫更多 Agent，還是設計更好的 Outer Loop？
- **核心疑問 (The Doubt)**：當 inner execution loop 越來越自主，人類工程師的 leverage 是否轉移到 objective、eval、policy、context、review 與 feedback loop？
- **現狀反差 (Reality Gap)**：autonomy marketing 講「少人」；production engineering 講「更好的 control loop」。
- **思維實驗 (Simulation)**：如果 agent 可以自行改 code、跑 test、部署，但沒有人定義 acceptable evidence、rollback、risk tier，它是 automation 還是高速 Bug generator？
- **連結**：← [[D2.1]], → [[S1]], [[G1]]

### C1：Harness Engineering
- **定義**：圍繞 model 建立 workflow、context、permissions、evaluation、persistent state、continuous-improvement 的工程層。
- **演化**：Prompt → agent loop → production harness。
- **本質**：Model intelligence 需要被 bounded system 轉成 repeatable outcome。
- **結構特徵**：context routing、tool policy、state/memory、eval、trace、feedback、sandbox、human gate。
- **連結**：→ [[D1.1]], [[P1]], [[E1]]

### D1.1：從 Lilian Weng 2023 Agent Anatomy 到 2026 Harness Engineering
- **操作手法**：把 focus 從 planning/memory/tool-use 的 agent anatomy，移到 agent 周邊的 workflow/context/permission/eval/state/self-improvement system。
- **獨特特徵**：2023 是 proof-of-concept；2026 是 reliability architecture。
- **影子證據**：文章對照 Lilian Weng 的 2023 agent essay 與 2026 harness-engineering essay。
- **連結**：↔ [[D1.2]] ⟨S1⟩

### D1.2：Coding Agents 成為 Developer Interface
- **操作手法**：Agents 接收 broader objective、探索 codebase、修改多檔、run tests、debug、iterate，再把結果交還工程師。
- **獨特特徵**：Developer interface 從「下一行 autocomplete」升級成「委派一段有驗證循環的工作」。
- **影子證據**：文章列出 Claude Code、Codex、Gemini CLI、Cursor、Warp。
- **連結**：↔ [[D1.1]] ⟨C1⟩

### D2.1：Inner Loop / Outer Loop
- **操作手法**：Inner loop 執行主要工作；outer loop 觀察、評估、維護、調整 primary system。
- **獨特特徵**：Human leverage 不是每一步手動介入，而是設計高品質 feedback signals 和 intervention points。
- **影子證據**：Introspection 的 autoresearch framing、Addy Osmani 與 Peter Steinberger 都把 outer loop 指向 engineering responsibility。
- **連結**：→ [[S1]], [[P2]]

### D2.2：Loop Debate — Deterministic Control vs Frontier Thinking
- **操作手法**：AIEWF debate 直接質疑 fully autonomous loops 是否已足夠可靠。
- **獨特特徵**：支持 loops 的人也承認 production discipline 尚未完全成熟。
- **影子證據**：Dex Horthy 把 Kubernetes control loops 與 agent loops 做區分：前者 deterministic；Geoffrey Huntley 把 agent-loop practice 描述為 frontier thinking。
- **連結**：↔ [[D2.1]] ⟨G1⟩

### D3.1：FDE 成為 Enterprise Agent 的 Delivery Interface
- **操作手法**：Forward Deployed Engineers 直接進組織，把 agents、integrations、long-running automations 與 SDK applications 接到真實流程。
- **獨特特徵**：成功標準不是 demo，而是 FDE 離開後 customer 還會繼續使用，且能看到 strict ROI。
- **影子證據**：Cursor 的 AIEWF 分享把 cloud agents、long-running agents、automations、Cursor SDK apps 都放進 FDE engagement output。
- **連結**：→ [[S2]], [[P3]]

### D3.2：Software Factory 的 Automation Boundary
- **操作手法**：企業選 repositories、要 automate 的 software lifecycle segments、human review points。
- **獨特特徵**：不同 codebase/risk profile 不應共享同一 autonomy level。
- **影子證據**：Warp 將 fully automated code review vs high-risk human review 明確列為組織要自行選擇的 control point。
- **連結**：↔ [[D3.1]] ⟨G2⟩

### D3.3：Context Engineering 變成 Company-Brain Routing
- **操作手法**：Business systems → shared company brain → agents/copilots/apps，透過 MCP、APIs、retrieval 分發 context。
- **獨特特徵**：企業 Agent 的 bottleneck 不只是 model，而是 context 如何流動、被授權與被更新。
- **影子證據**：Atlan 的 conference framing 直接描述這條 context flow。
- **連結**：→ [[P4]], [[E2]]

### D4.1：Agent 是一種新的 Software Form
- **操作手法**：Agent framework 要處理更動態、更不可預測的 interaction/output，並提供 secure code execution 與 long-running job infrastructure。
- **獨特特徵**：Web app infrastructure 的部分基礎可重用，但 agent execution 需要新的 sandbox/state/observability layer。
- **影子證據**：Vercel 的 Andrew Qu 表示一年前仍低估了 sandbox 與 secure long-running execution 的重要性。
- **連結**：→ [[S3]], [[P1]]

### D4.2：Factory vs Orchestra
- **操作手法**：Factory framing 強調長時間 agents 執行 lifecycle；orchestra framing 強調 human conductor 持續控制方向。
- **獨特特徵**：這不是文案差異，而是 authority distribution 的架構選擇。
- **影子證據**：Conductor 的 Charlie Holtz 反對把未來完全建成 factories；Geoffrey Huntley 也警告下一年可能出現大量 factory/loop failure retrospectives。
- **連結**：↔ [[D3.2]] ⟨Q1⟩

### D5.1：Skills 從 Tool Description 升級成 Portable Operating Knowledge
- **操作手法**：用 declarative Markdown 等 artifacts 編碼 workflows、quality gates、best practices，按需載入 agent context。
- **獨特特徵**：Skill 是可版本化、可分發的 know-how，而非固定 orchestration code。
- **影子證據**：AIEWF 上出現「from agent tools to agent skills」；Philipp Schmid 以 Markdown/files 展示低 orchestration-code 的 agent capability extension。
- **連結**：→ [[S4]], [[P5]], [[E3]]

### D5.2：Skills Hell
- **操作手法**：Skill 數量、大小、結構如果失控，agent retrieval 與 context selection 會反而變差。
- **獨特特徵**：技能不是越多越好；需要 routing、evaluation、lifecycle、requalification。
- **影子證據**：文章引用 Matt Pocock 對 fewer/smaller/better-structured skills 的方向，並把問題稱為 “skills hell”。
- **連結**：↔ [[D5.1]] ⟨G3⟩

### S1：Outer Loop First
- **策略邏輯**：先設 eval、observation、rollback、approval，再提高 inner-loop autonomy。
- **生態位對照 (Ecological Context)**：
  - 主角表現：AIEWF 2026 的主流討論從 autonomous hype 轉向 loop engineering。
  - **環境/競對參照**：2023 AutoGPT 類系統先追求 autonomy，再補 reliability。
- **反面教材 (Pre-mortem)**：Agent 可以一直做事，但沒有人能定義「做對了」或知道何時停止。
- **理論基礎**：← [[D2.1]], [[D2.2]]
- **實踐路徑**：→ [[P2]]
- **支撐框架**：← [[G1]]

### S2：FDE 用 ROI Closure 取代 Demo Completion
- **策略邏輯**：交付的 Definition of Done 應是 workflow 在真組織內持續工作，而非 demo 能跑一次。
- **生態位對照 (Ecological Context)**：
  - 主角表現：FDE 把 cloud agents、long-running agents、automation 接進 customer lifecycle。
  - **環境/競對參照**：PoC 常停在模型能力展示，沒有 adoption champion、integration ownership、maintenance loop。
- **反面教材 (Pre-mortem)**：FDE 離場後 integrations 無 owner、skill stale、token cost 無人負責。
- **理論基礎**：← [[D3.1]], [[D3.2]]
- **實踐路徑**：→ [[P3]]
- **支撐框架**：← [[G2]]

### S3：Sandbox 是 Agent Framework 的 Core Primitive
- **策略邏輯**：當 agent 能修改 code、run commands、持續數小時，secure execution 不是 plugin，而是 runtime foundation。
- **生態位對照 (Ecological Context)**：
  - 主角表現：AIEWF discussion 明確把 secure code execution、long-running jobs 放進 framework evolution。
  - **環境/競對參照**：chat-only assistant 沒有相同 physical-action surface。
- **反面教材 (Pre-mortem)**：把 prompt permission 當 isolation；把 host machine 當 sandbox。
- **理論基礎**：← [[D4.1]]
- **實踐路徑**：→ [[P1]]
- **支撐框架**：← [[G1]]

### S4：Skill 要被評測，不是被收藏
- **策略邏輯**：Skill 是 executable knowledge，因此每次 model/harness 變更都可能讓 skill behavior drift。
- **生態位對照 (Ecological Context)**：
  - 主角表現：AIEWF 把 skills 視為 portable on-demand knowledge。
  - **環境/競對參照**：技能目錄很容易退化成 Markdown dump。
- **反面教材 (Pre-mortem)**：沒有 no-skill baseline、沒有 negative triggers、沒有 requalification，最後進入 skills hell。
- **理論基礎**：← [[D5.1]], [[D5.2]]
- **實踐路徑**：→ [[P5]]
- **支撐框架**：← [[G3]]

### P1：Agent Runtime Minimum Contract
- **場景 (Scenario)**：Coding/operations agent 需要長時間執行與 tool access。
- **價值 (Value)**：建立可預測的 physical-action boundary。
- **漏洞利用 (Exploit/How)**：
  1. 每次 run 建 disposable workspace。
  2. Filesystem/network/secrets default deny，按 capability 開放。
  3. 所有 elevated actions 走 review policy。
  4. 綁定 model/harness/policy/tool digests。
  5. Run 結束驗證 cleanup/destruction，再出 receipt。
- **工具集 (Toolset)**：container/sandbox、policy engine、artifact digest、execution receipt、audit log。
- **影子技巧**：長時間 agent 必須有 checkpoint 與 resume，不應以擴大 host permissions 解決中斷問題。
- **連結**：← [[S3]]

### P2：Outer-Loop Autoresearch Harness
- **場景 (Scenario)**：Agent 已能自主執行 code/research tasks，需要持續提升但不讓 self-improvement 直接進 production。
- **價值 (Value)**：把 improvement 變成 candidate → eval → admit 的 controlled loop。
- **漏洞利用 (Exploit/How)**：
  1. Inner loop 執行固定 production task envelope。
  2. Outer loop 只讀 traces、failures、metrics，提出 candidate patch。
  3. Candidate 在 fresh sandbox 跑 baseline/candidate paired eval。
  4. 通過 assertions 才進 review；production 不允許 self-write/self-admit。
  5. 每次 admission 保留 Decision Trace。
- **工具集 (Toolset)**：trace store、eval harness、sandbox、git diff、signed evidence。
- **影子技巧**：把「能自我修改」與「能自我升級 production」拆成兩種權限。
- **連結**：← [[S1]]

### P3：FDE ROI Closure Checklist
- **場景 (Scenario)**：把 agent 導入 enterprise team。
- **價值 (Value)**：確保 engagement 結束後仍可運作。
- **漏洞利用 (Exploit/How)**：
  1. 先記 baseline cycle time/cost/error rate。
  2. 找 internal champion + workflow owner。
  3. 建 integrations、context sources、permissions、fallback path。
  4. 定義 measurable ROI 與 adoption telemetry。
  5. 把 runbook、skills、evals、incident ownership 移交。
  6. FDE exit 前跑 failure simulation 與 owner handoff test。
- **工具集 (Toolset)**：workflow map、ROI dashboard、MCP/API connectors、runbook、skill registry。
- **影子技巧**：真正 DoD 是 customer 不會在 FDE 離開後關掉系統。
- **連結**：← [[S2]]

### P4：Company Context Router
- **場景 (Scenario)**：多個 agents/copilots/apps 要存取企業 knowledge。
- **價值 (Value)**：避免每個 Agent 自建一套 stale RAG。
- **漏洞利用 (Exploit/How)**：
  1. 建 source registry：system-of-record、owner、freshness、ACL。
  2. Context chunk 綁 source/version/citation。
  3. 透過 MCP/API/retrieval 分發，保留 identity-aware filtering。
  4. Agent response/decision 記錄實際使用的 context IDs。
  5. Source 更新觸發 downstream impact/re-eval。
- **工具集 (Toolset)**：knowledge graph、MCP gateway、retrieval service、ACL engine、citation ledger。
- **影子技巧**：Context flow 必須可以回答「哪個 source 讓 agent 做出這個決定」。
- **連結**：← [[D3.3]]

### P5：Skill Qualification Loop
- **場景 (Scenario)**：Claude Code/Codex/Deep Agents 共用 skills。
- **價值 (Value)**：把 Markdown knowledge 變成可測量 capability artifact。
- **漏洞利用 (Exploit/How)**：
  1. Skill 固定 ID、version、trigger、negative trigger、source claims。
  2. 建 no-skill baseline 與 skill candidate paired tasks。
  3. 測 invocation rate、pass rate、turns、cost、safety failures。
  4. Skill/model/harness 任何變更觸發 requalification。
  5. 只有 signed evidence + admission 才可 production routing。
- **工具集 (Toolset)**：SKILL.md、AGENTS.md/CLAUDE.md、task pool、sandbox runner、evidence receipts。
- **影子技巧**：Skill 太多會增加 routing collision；先做 bounded working set，再做 progressive disclosure。
- **連結**：← [[S4]]

### T1：AIEWF 2026 五大趨勢矩陣
- **用途**：把 conference signals 編譯成 Agent Architect 的工程責任。
- **結構內容**：
  | 趨勢 | 表層變化 | Agent Architect Patch |
  |---|---|---|
  | Systems around agents | model → harness | context/eval/runtime contracts |
  | Loop engineering | autonomy → outer loop | feedback/admission boundary |
  | Enterprise/FDE | demo → workflow ROI | integration + ownership + telemetry |
  | Coding agents | IDE → goal interface | sandbox + long-running execution |
  | Skills | tools → portable knowledge | routing + eval + lifecycle |
- **連結**：→ [[S1]], [[S2]], [[S3]], [[S4]]

### R1：Agent Architect Competency Roadmap
- **總體目標**：從「會用 Agent SDK」升級成「能設計 evidence-aware agent system」。
- **階段劃分**：
  - **Phase 1 Harness**：context、tools、memory、state、traces。
  - **Phase 2 Runtime**：sandbox、permissions、long-running execution。
  - **Phase 3 Evals**：paired baseline、failure taxonomy、cost/latency。
  - **Phase 4 Enterprise**：FDE workflow mapping、ROI、ownership。
  - **Phase 5 Skills**：portable knowledge、routing、qualification。
  - **Phase 6 Outer Loop**：autoresearch、impact analysis、requalification。
- **系統風險 (Glitches)**：autonomy theater、skills hell、context drift、factory without controls、PoC without ROI closure。
- **連結**：→ [[G1]], [[G2]], [[G3]]

### G1：Outer-Loop Authority Protocol
- **核心協議 (Protocol)**：Inner loop 可以自主執行；不能自主提升自己的 production authority。
- **具體條款/機制**：candidate isolation、paired eval、human/policy admission、rollback、Decision Trace。
- **決策流程**：trace → candidate patch → sandbox eval → review → admission/reject → production update。
- **違規後果**：quarantine candidate；production version 不變。
- **連結**：← [[R1]], → [[S1]]

### G2：Enterprise Automation Boundary
- **核心協議 (Protocol)**：Automation level 按 lifecycle stage、repository、risk tier 分配，不做全域 autonomous toggle。
- **具體條款/機制**：low-risk auto、high-risk review、critical manual sign-off、owner + rollback。
- **決策流程**：task classify → risk → authority → execute → evidence → owner review。
- **違規後果**：降級自治、撤回 connector permission。
- **連結**：← [[R1]], → [[S2]]

### G3：Skill Lifecycle Governance
- **核心協議 (Protocol)**：`documented != evaluated != qualified != admitted != routable`。
- **具體條款/機制**：immutable digest、source anchoring、baseline eval、signed receipt、requalification triggers。
- **決策流程**：draft → source-anchored → evaluated → qualified → admitted → bounded routing。
- **違規後果**：stale/quarantine；禁止 implicit invocation。
- **連結**：← [[R1]], → [[S4]]

### E1：Agent Reliability 的主要工作發生在 Model 外面
- **法則內容**：當 model capability 足夠，差異化開始集中在 harness、context、eval、runtime、policy 與 feedback。
- **推論/啟示**：System design 能力比單純 prompt trick 更接近 Agent Architect 的 production value。
- **支撐證據**：← [[C1]], [[D1.1]], [[D4.1]]

### E2：Context Flow 是 Enterprise Agent 的資料平面
- **法則內容**：沒有可治理的 context routing，Agent 只會把 data silos 重新包裝成 prompt silos。
- **推論/啟示**：MCP/API/retrieval 應被統一放進 provenance + ACL + freshness graph。
- **支撐證據**：← [[D3.3]], [[P4]]

### E3：Skill 是可執行知識，因此必須有 Software Lifecycle
- **法則內容**：Skill 不是靜態文檔；它會改變 agent behavior，所以需要 version、eval、qualification、admission、rollback。
- **推論/啟示**：真正的 Skill Arena 應比較 outcome lift 與 safety，不是比較 README 美觀度。
- **支撐證據**：← [[D5.1]], [[D5.2]], [[P5]], [[G3]]