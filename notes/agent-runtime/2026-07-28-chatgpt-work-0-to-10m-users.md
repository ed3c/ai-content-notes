---
id: latent-space:chatgpt-work-0-to-10m-users
title: Codex from 0 to 10M Users: Building ChatGPT Work — Akshay Nathan, OpenAI
source: Latent Space
source_url: https://www.latent.space/p/chatgpt-work
published_at: '2026-07-28'
monetization_score: 100
category: agent-runtime
language: zh-TW
note_format: zettelkasten-v6.6-cyberpunk
storage: private-github-markdown
repository: ed3c/ai-content-notes
path: notes/agent-runtime/2026-07-28-chatgpt-work-0-to-10m-users.md
citation_mapping: pending
library_mapping: pending
---

### N1：Coding Agent 逃出 IDE，開始吞掉 Knowledge Work
- **核心衝突**：Coding Agent 的能力已足以處理非程式工作，但使用者心智模型、權限模型與 UX 還停在「寫程式工具」。真正的產品戰不是再加一個模型，而是把 Agent harness 重新包裝成一般知識工作者可理解、可授權、可監督的工作環境。
- **關鍵人物/實體**：OpenAI Codex / ChatGPT Work vs. 傳統 Chat UI 與單點 SaaS 工具。
- **衝擊力錨點 (Impact Anchors)**：
  - 2026-07-28：Latent Space 發布 1:09:27 訪談。
  - Codex MAU 相較 2026 年 1 月成長超過 10 倍。
  - ChatGPT Work 與 Codex 在 2026-07-21 已被公開稱達到合計 10M users。
  - OpenAI 先前披露 knowledge workers 約佔 Codex user base 的 20%，且其增長速度超過 developers 的 3 倍。
  - 訪談前言指出：會「使用 code」的人可能約為「會寫 code」者的 100 倍。
- **劇情轉折**：OpenAI 不是另外打造一套 knowledge-work Agent，而是保留 Codex 的核心 harness，把 Git-first、diff-first 的工程 UX 抽掉，再換成 artifacts、Sites、plugins、local files、persistent computer、memory 與 scheduled tasks。
- **生態背景**：模型能力快速上升後，產品差異從「哪個模型最強」轉移到 context acquisition、tool access、artifact lifecycle、permission boundary 與 human supervision。
- **連結**：→ [[D1]], [[D2]], [[D3]], [[D4]], [[G1]]；≈ [[N2：Harness becomes the product]]

### N2：Super App Merge 不是品牌合併，而是 Harness Consolidation
- **核心衝突**：同一個 Agent 能力若被拆在 Chat、Codex、Work 多個產品，使用者會被迫學習工具邊界；但若全部合併，developer 又會失去 Git、diff、repo、sandbox 等精細控制。
- **關鍵人物/實體**：ChatGPT core chat / Codex / ChatGPT Work。
- **衝擊力錨點 (Impact Anchors)**：
  - 訪談中明確指出 Codex 與 Work 使用 shared harness。
  - Codex UX 假設 repo、Git、diff；Work UX 隱藏檔案變更細節，優先呈現工作成果。
  - Classic ChatGPT harness 仍存在，並持續針對 latency、personality、search、learning 等需求最佳化。
- **劇情轉折**：產品不再用「一種 UI 對應一個 Agent architecture」，而是用同一 harness 配多個 opinionated UX surface。
- **生態背景**：Agent 基礎能力逐漸商品化後，UX abstraction 會成為市場分層器。
- **連結**：→ [[C1]], [[D2]], [[D5]], [[T1]], [[S1]]

### Q1：如果 Harness 相同，真正的產品 moat 還剩什麼？
- **核心疑問 (The Doubt)**：當 model + harness 可被多個 surface 共用，產品是否只剩 UI？
- **現狀反差 (Reality Gap)**：表面上 Work 與 Codex 只是不同介面；實際上使用者看到的資訊量、sandbox 預設、artifact 呈現、權限提示、任務時間尺度都不同，這些差異直接改變 Agent 行為的可控性與採用率。
- **思維實驗 (Simulation)**：把完全相同的 retirement-calculator 任務送進 Codex 與 Work：前者暴露 repo/diff/file-edit，後者直接輸出可用 spreadsheet。若企業 KPI 是任務完成，不是程式碼透明度，哪個 surface 會贏？
- **連結**：← [[D2]]；→ [[S1]], [[P1]]

### Q2：Agent 有「全部 context」時，誰是 permissions layer？
- **核心疑問 (The Doubt)**：當 Work 能讀 plugins、local files、Docs、Slack-like context 與個人 memory，答案是否可能正確但不應被某位同事看到？
- **現狀反差 (Reality Gap)**：多人協作想共享 Agent rollout；但 context 本身高度個人化，使用者甚至不知道自己「不知道哪些資訊」。
- **思維實驗 (Simulation)**：A 問 Agent 後把結果轉傳給 B。A 無意間成為人工 access-control proxy。若直接改成 shared hosted artifact，原本由 A 承擔的 permission judgment 必須由系統接手。
- **連結**：← [[D6]]；→ [[G1]], [[P4]]

### Q3：Token、PR、Story Point 都失效後，Knowledge Work 如何量測？
- **核心疑問 (The Doubt)**：Agent 讓 output volume 爆增時，傳統 productivity proxy 是否會反向鼓勵 busywork？
- **現狀反差 (Reality Gap)**：tokens、pull requests、lines of code、story points 都可以上升，但團隊目標不一定更接近完成。
- **思維實驗 (Simulation)**：兩個團隊都產生 10 倍 artifact；一個每週完成 30 次高品質 idea→build→feedback→validation loop，另一個只堆 prompt 與 dashboard。哪個是真的變快？
- **連結**：← [[D10]]；→ [[S6]], [[T3]], [[P6]]

### C1：Shared Harness / Segmented UX
- **定義**：把 context、tool calling、computer use、artifact generation、sub-agent orchestration 等 Agent runtime 能力做成共享底層，再依 personas 暴露不同控制面。
- **演化**：`Model-specific UI` → `Agent harness` → `shared harness + persona surface`。
- **本質**：能力重用，認知負擔分流。
- **結構特徵**：shared execution core、UX policy、sandbox policy、artifact renderer、permission projection、task routing。
- **連結**：→ [[D2]], [[D5]]；→ [[E1]]

### C2：Artifact-Native Knowledge Work
- **定義**：Agent 不只回覆文字，而是直接建立 spreadsheet、slides、site、code、research dashboard 等可持續操作的 work product。
- **演化**：Chat answer → generated file → hosted interactive artifact → persistent collaborative workspace。
- **本質**：把「答案」升級成「可執行狀態」。
- **結構特徵**：filesystem、renderer/editor、hosting、versioning、share boundary、data connector。
- **連結**：→ [[D3]], [[D4]], [[P2]]；→ [[E2]]

### C3：Persistent Personal Computer Primitive
- **定義**：Agent 擁有跨 session 保留的 filesystem、scheduled tasks、memory 與可重用 context，使一次性 chat 變成長期 operating process。
- **演化**：stateless prompt → session memory → durable workspace → proactive scheduled Agent。
- **本質**：持久狀態使 Agent 從 function call 變成 operating system process。
- **結構特徵**：durable storage、scheduler、memory index、tool credentials、task history、permission state。
- **連結**：→ [[D7]], [[D8]], [[P3]]；→ [[E3]]

### C4：Goal-Oriented Productivity
- **定義**：以是否靠近業務/個人目標作為成果，而不是以中間產出量作為 proxy。
- **演化**：LOC / tickets / PR count → cycle time → validated progress toward goal。
- **本質**：Agent 讓「產出」變便宜後，稀缺資源轉為選題、驗證與 feedback quality。
- **結構特徵**：goal state、hypothesis、attempt、feedback、decision、next attempt。
- **連結**：→ [[D10]], [[T3]], [[E5]]

### D1：10M Users 是 Harness Distribution 的證據，不只是 Growth 指標
- **操作手法**：把原本服務 developers 的 Codex harness 嵌入 ChatGPT Work，直接借用 ChatGPT distribution，而不是重新教育一個獨立市場。
- **獨特特徵**：非 developer 不需要先理解 repo、terminal 或 Git；仍然使用同一類 Agent runtime。
- **影子證據**：2026-07-21 公開 10M combined users；Codex MAU 自 2026-01 起超過 10x；knowledge workers 約 20% user base 且增長 >3x developers。
- **連結**：↔ [[D2]] ⟨S2⟩

### D2：Codex 與 Work 共用 Harness，但故意暴露不同 Runtime 細節
- **操作手法**：Codex 顯示 Git repo、diff、file edit、reasoning trace 等工程細節；Work 隱藏相同執行過程，直接呈現 spreadsheet/site/artifact。
- **獨特特徵**：不是能力閹割，而是 abstraction policy。
- **影子證據**：訪談 00:09:49–00:10:42；同一 retirement-calculator spreadsheet 任務在兩個 surface 呈現不同。
- **連結**：↔ [[D5]] ⟨S1⟩

### D3：Artifacts 把 Chat Output 轉成 Work Product
- **操作手法**：模型直接編輯 Excel-like files、生成 spreadsheet、hosted site 與其他 artifacts；使用者不必把文字答案再手工搬進 Office 工具。
- **獨特特徵**：artifact quality 同時依賴 model capability 與 product renderer/editor，不是單純 prompt engineering。
- **影子證據**：訪談 00:20:04 起示範 retirement calculator；受訪者指出 GPT‑5.6 相較 GPT‑5.5 / GPT‑5.4 的 artifact quality 顯著提升。
- **連結**：↔ [[D4]] ⟨S3⟩

### D4：Sites 是「無固定 Schema 的 Artifact Runtime」
- **操作手法**：使用 Site 直接做 interactive prototype、knowledge artifact、research dashboard；若需求超出一般 spreadsheet/slides schema，就用 web runtime 表達。
- **獨特特徵**：傳統 Office artifact 有功能邊界；Site 可由 Agent 動態生成任何 UI/interaction。
- **影子證據**：GPT‑5.6 model slider 的產品 prototyping 幾乎全部先在 Site 中完成；訪談案例以約 30 張照片、約 1.7B tokens 建出可互動 board-game research site。
- **連結**：↔ [[D3]] ⟨P2⟩

### D5：Classic Chat 與 Work 的 Divergence / Convergence Cycle
- **操作手法**：Chat harness 針對 low-latency、personality、search、learning；Codex harness 針對 flexible computer environment、longer tasks、files/tools；再逐步把能力互相帶回。
- **獨特特徵**：不是一次性平台統一，而是持續 divergence→convergence。
- **影子證據**：訪談 00:14:02–00:15:10；受訪者直接描述此循環。
- **連結**：↔ [[D2]] ⟨S1⟩

### D6：Human Message Forwarding 暴露 Collaboration 與 Permission Glitch
- **操作手法**：員工收到問題後讓 Work 查完整 context，再把自己的解讀回傳同事。
- **獨特特徵**：人類同時是 context selector、permission gate、compression layer；效率高但資訊會 loss。
- **影子證據**：訪談 00:22:48–00:24:22；Work 可能連接 plugins、local files，context 被形容為 deeply personal。
- **連結**：→ [[G1]], [[P4]]

### D7：OpenClaw 啟發 Persistent Computer，而不是單一 Feature Copy
- **操作手法**：Work 的 web/mobile runtime 保留 persistent files、scheduled tasks 與跨 session state，讓 agent 可持續追蹤 workout、meal、calendar 等工作或個人 productivity flow。
- **獨特特徵**：核心移植的是 primitive：durable filesystem + scheduler + tool access，而不是 OpenClaw 的 UI。
- **影子證據**：訪談 00:44:38 起；受訪者提到家中 OpenClaw 會建立 calendar events，Work 團隊成員已把既有 OpenClaw workflow 遷移到 Work。
- **連結**：→ [[C3]], [[P3]]

### D8：Memory 的價值不是「永遠不忘」，而是比人更容易撈回被遺忘的 Context
- **操作手法**：專案可把 learnings 寫入 notes.md，再由 global context 拉回；Chronicle 類系統則把 computer activity 變成 memory input。
- **獨特特徵**：不要求 perfect recall。只要 retrieval 能找回人類已遺忘但與當前任務相關的資訊，就形成超額價值。
- **影子證據**：訪談 00:39:50–00:40:41 與 00:57:55–01:00:14；案例會找回約四個月前專案筆記。
- **連結**：→ [[C3]], [[P3]], [[G2]]

### D9：Sub-Agents 的 UX 問題是「可觀測性 vs. 認知負擔」
- **操作手法**：複雜或可平行任務由 sub-agents 拆分；產品顯示其存在，但預設隱藏大量 transcript。
- **獨特特徵**：power users 想看每個 sub-agent；一般知識工作者只需要知道任務在平行執行與最終結果。
- **影子證據**：訪談 00:50:23–00:51:39；hidden-by-default 是當前設計取捨。
- **連結**：→ [[S4]], [[P5]]

### D10：At-Bats 取代 Output Volume
- **操作手法**：追蹤團隊能否更快完成 idea→build→feedback→validate/invalidate→next idea 的完整循環，而不是 token、PR、LOC、story points。
- **獨特特徵**：把產出量移出核心 KPI，改看 learning velocity 與 validated progress。
- **影子證據**：訪談 01:05:44–01:08:09；受訪者明確指出 tokens、PR 等 proxy 與真正目標的相關性正在下降。
- **連結**：→ [[C4]], [[S6]], [[T3]]

### S1：One Harness, Multiple Control Surfaces
- **策略邏輯**：Agent runtime 能力集中；使用者控制面分層。不要為每個 persona 重建 execution stack。
- **生態位對照 (Ecological Context)**：
  - 主角表現：Codex 暴露 Git/diff；Work 暴露 artifact/goal。
  - **環境/競對參照**：傳統 SaaS 常把每個 persona 做成獨立產品，導致 context、tool、eval stack 分裂。
- **反面教材 (Pre-mortem)**：把 UX abstraction 誤做成 capability fork，最後兩個產品逐漸行為不一致、eval 不能共用。
- **理論基礎**：← [[D2]], [[D5]]
- **實踐路徑**：→ [[P1]]
- **支撐框架**：← [[T1]]

### S2：Distribution Exploit：把 Developer Agent 嵌進既有 Chat Surface
- **策略邏輯**：使用者已懂 ChatGPT，不要要求 10x–100x 更大的 non-developer market 先學 terminal。
- **生態位對照 (Ecological Context)**：
  - 主角表現：ChatGPT Work 借用 ChatGPT distribution。
  - **環境/競對參照**：新 Agent startup 必須自己建立 acquisition、trust、identity、billing 與 connector ecosystem。
- **反面教材 (Pre-mortem)**：只把 CLI 包成 chat，卻沒有改 permissions、artifact rendering、error recovery，會得到「比較難用的 terminal」。
- **理論基礎**：← [[D1]]
- **實踐路徑**：→ [[P1]], [[P2]]
- **支撐框架**：← [[R1]]

### S3：Artifact First，Chat Second
- **策略邏輯**：對 work task，最終交付物應是可用 artifact，而非解釋如何做 artifact 的文字。
- **生態位對照 (Ecological Context)**：
  - 主角表現：spreadsheet、Sites、files 直接由 Agent 操作。
  - **環境/競對參照**：傳統 chatbot 仍要求使用者 copy/paste 至 Excel、Docs、IDE。
- **反面教材 (Pre-mortem)**：Artifact 沒有 versioning、schema validation、preview 或 rollback，錯誤會比文字 hallucination 更昂貴。
- **理論基礎**：← [[D3]], [[D4]]
- **實踐路徑**：→ [[P2]]
- **支撐框架**：← [[T2]], [[G1]]

### S4：Progressive Agent Observability
- **策略邏輯**：預設顯示 goal、progress、cost、blocked state；把 sub-agent transcript、tool trace、filesystem diff 放進 drill-down。
- **生態位對照 (Ecological Context)**：
  - 主角表現：sub-agent details hidden by default。
  - **環境/競對參照**：developer agent 常把所有 terminal/tool trace 全開；consumer UI 則可能完全黑箱。
- **反面教材 (Pre-mortem)**：完全隱藏會失去 trust/debuggability；全部展開會讓非工程使用者被 log 淹沒。
- **理論基礎**：← [[D9]]
- **實踐路徑**：→ [[P5]]
- **支撐框架**：← [[T1]]

### S5：Context Is a Privileged Capability
- **策略邏輯**：context 越完整，Agent 越強；同時 data leakage blast radius 越大。Connector 數量不是單向 KPI。
- **生態位對照 (Ecological Context)**：
  - 主角表現：plugins/local files/memory/persistent files 帶來長期 utility。
  - **環境/競對參照**：很多 RAG 系統只優化 recall，不把 authorization provenance 納入 retrieval。
- **反面教材 (Pre-mortem)**：把「能找到」誤當「有權使用與分享」。
- **理論基礎**：← [[D6]], [[D8]]
- **實踐路徑**：→ [[P4]]
- **支撐框架**：← [[G1]], [[G2]]

### S6：Measure Learning Velocity, Not Agent Activity
- **策略邏輯**：當 Agent 讓輸出近乎免費，管理指標必須聚焦 hypothesis throughput 與 validated progress。
- **生態位對照 (Ecological Context)**：
  - 主角表現：以 at-bats 描述高品質完整迭代。
  - **環境/競對參照**：傳統工程管理容易回到 PR/LOC/story point/token dashboards。
- **反面教材 (Pre-mortem)**：Agent 活動越多，dashboard 越漂亮，但 customer/business state 沒變。
- **理論基礎**：← [[D10]]
- **實踐路徑**：→ [[P6]]
- **支撐框架**：← [[T3]]

### T1：Shared Harness Surface Matrix
- **用途**：決定哪些能力應共用，哪些細節應依 persona 隱藏。
- **結構內容**：
  | 維度 | Developer / Codex | Knowledge Work / Work | Shared Runtime |
  |---|---|---|---|
  | Primary object | repo / diff | artifact / task | filesystem + tools |
  | Execution detail | high | progressive disclosure | trace store |
  | Sandbox | explicit | abstracted | isolated execution |
  | Context | code + repo | plugins + local/work files | connector layer |
  | Output | code + diff | spreadsheet/site/slides/docs | artifact engine |
  | Orchestration | visible | simplified | sub-agent scheduler |
- **連結**：→ [[S1]], [[S4]], [[P1]]

### T2：Artifact Production Gate
- **用途**：避免 Agent 產生漂亮但不可交付的工作物。
- **結構內容**：
  | Gate | 檢查 |
  |---|---|
  | Source | context provenance / permissions |
  | Build | schema / file validity |
  | Render | preview 是否與內容一致 |
  | Test | formulas / links / interactions |
  | Review | human approval threshold |
  | Publish | share scope / access control |
  | Rollback | version / restore path |
- **連結**：→ [[S3]], [[P2]], [[G1]]

### T3：At-Bat Metrics Matrix
- **用途**：把 Agent productivity 從 output vanity metric 切換到 learning velocity。
- **結構內容**：
  | 維度 | Vanity | Executable Metric |
  |---|---|---|
  | Coding | LOC / PR count | validated change lead time |
  | Research | token count | hypotheses invalidated/validated |
  | Product | artifacts created | user-observed behavior change |
  | Team | tasks closed | goal distance reduced |
  | Agent | tool calls | successful autonomous task completion |
- **連結**：→ [[S6]], [[P6]]

### R1：Knowledge-Work Agent Migration Roadmap
- **總體目標**：把現有 chatbot/coding agent 轉成可服務 non-developer 的 durable work runtime。
- **階段劃分**：
  - **Phase 1 Shared Harness**：統一 tool calling、filesystem、artifact、trace、eval。
  - **Phase 2 Surface Split**：developer 保留 diff/terminal；knowledge worker 顯示 goal/artifact。
  - **Phase 3 Context Expansion**：加入 work connectors、local files、permission-aware retrieval。
  - **Phase 4 Durable State**：persistent files、memory、scheduled tasks。
  - **Phase 5 Parallelism**：sub-agents、programmatic tool calling、long-running tasks。
  - **Phase 6 Goal Metrics**：以 at-bat 與 validated outcome 取代 output count。
- **系統風險 (Glitches)**：surface 分裂造成 capability drift；context 擴張造成 authorization leak；artifact 執行造成 silent corruption。
- **連結**：→ [[G1]], [[G2]], [[S1]], [[S6]]

### R2：Enterprise Adoption Loop
- **總體目標**：不用 training manual 教 Agent capability，而是在使用者任務現場讓產品展示能力。
- **階段劃分**：
  - **Phase 1 Observe**：找出高頻重複 work requests。
  - **Phase 2 Show-in-Context**：在任務時刻推薦 Work/Artifact，而非泛用 onboarding。
  - **Phase 3 Capture**：保存成功 artifact、workflow、memory。
  - **Phase 4 Reuse**：把成功 path 轉成 scheduled task/template/skill。
  - **Phase 5 Team Diffusion**：以 shared artifact 展示，不只靠文章教學。
- **系統風險 (Glitches)**：過度 proactive 導致干擾；成功案例缺少 permission metadata 無法安全分享。
- **連結**：→ [[G1]], [[P3]], [[P4]]

### G1：Context / Artifact Permission Protocol
- **核心協議 (Protocol)**：每一段 context 與每一個 artifact 都要攜帶可執行 authorization metadata；Agent 不得用「使用者能讀」推導「任何收件者都能讀」。
- **具體條款/機制**：
  - Context provenance：保存來源、principal、scope、retrieval time。
  - Derived artifact：紀錄支撐來源與最嚴格 share scope。
  - Cross-user share：重新做 recipient authorization，而非沿用 creator 權限。
  - Connector secrets：使用短生命週期 scoped credential。
  - Sensitive workflow：人類 approval gate 前不得 publish/send。
- **決策流程**：Task → Context Resolve → Per-source Authorization → Execute → Artifact Taint/Provenance → Recipient Check → Share。
- **違規後果**：blocked share、audit event、credential rotation、artifact quarantine。
- **連結**：← [[R1]], [[R2]]；→ [[S5]], [[P4]]

### G2：Memory Governance Protocol
- **核心協議 (Protocol)**：Memory 是 persistent privileged data，不是便利 cache。
- **具體條款/機制**：
  - 每筆 memory 保存 source、timestamp、confidence、sensitivity、retention class。
  - 支援 user-visible delete / correct / export。
  - retrieval 必須受當前 task 與 principal policy 限制。
  - Chronicle/computer-observation 類資料預設 opt-in，建立清楚 capture indicator。
  - 由 memory 自動生成 skill 前必須做 policy scan，避免把 secret 轉成 reusable instruction。
- **決策流程**：Capture → Classify → Store → Retrieve → Use → Review/Expire。
- **違規後果**：停止 proactive retrieval、刪除衍生 skill、觸發 privacy incident review。
- **連結**：← [[R1]]；→ [[S5]], [[P3]]

### P1：建立 Shared Agent Harness + Surface Adapter
- **場景 (Scenario)**：同一套 Agent 要同時服務工程師與一般知識工作者。
- **價值 (Value)**：能力、eval、security patch 一次更新，多 surface 共用。
- **漏洞利用 (Exploit/How)**：
  1. 定義 runtime contract：`task`, `principal`, `context_refs`, `tools`, `artifact_target`, `budget`, `policy`。
  2. 把 model routing、tool calling、filesystem、sub-agent、trace 放進 shared runtime。
  3. Developer adapter 顯示 repo/diff/tool trace；Work adapter 顯示 goal/progress/artifact preview。
  4. 使用相同 eval corpus 比較 surface 是否造成 capability drift。
  5. 對每個 surface 建 cognitive-load test：使用者能否知道 Agent 現在做什麼、花多少、卡在哪。
- **工具集 (Toolset)**：Agent runtime、sandbox、trace store、artifact renderer、policy engine、feature flag。
- **影子技巧**：surface adapter 只改 presentation/policy defaults，不 fork core planner。
- **連結**：← [[S1]], [[S2]]

### P2：Artifact-First Delivery Patch
- **場景 (Scenario)**：任務最終需要 spreadsheet、slide、site、report 或 code，而不是文字建議。
- **價值 (Value)**：減少 copy/paste 與格式重建，把 Agent output 直接變成可驗證 work product。
- **漏洞利用 (Exploit/How)**：
  1. Prompt 首先解析 target artifact 與 acceptance criteria。
  2. 建立 isolated working copy，不直接覆寫 production file。
  3. 生成後跑格式 validator：xlsx formula、pptx structure、HTML links、code tests。
  4. 產生 preview + machine-readable diff。
  5. 高風險 mutation 要求人類 approve。
  6. Publish 後保存 source provenance、artifact version、rollback pointer。
- **工具集 (Toolset)**：filesystem sandbox、document SDK、browser renderer、schema validator、Git/object store、policy engine。
- **影子技巧**：把 Site 視為 escape hatch：當固定格式限制表達能力時，用動態 web artifact，但仍保留 data provenance 與 access policy。
- **連結**：← [[S3]]

### P3：Persistent Workspace Patch
- **場景 (Scenario)**：長期研究、meal/workout tracking、定期報告、跨 session 專案。
- **價值 (Value)**：讓 Agent 不必每次從零讀背景。
- **漏洞利用 (Exploit/How)**：
  1. 每個 project 建 durable directory：`/context`, `/artifacts`, `/memory`, `/runs`。
  2. 每次 run 寫 `run.json`：goal、inputs、tools、result、next_state。
  3. 可重複任務轉成 scheduler entry，不把 cron prompt 混在一般 chat history。
  4. 把 learnings 寫成 atomic Markdown memory，不直接存整段 conversation dump。
  5. Retrieval 時按 task + permissions + recency + confidence 選 memory。
  6. 定期 compact/expire，保留原始 provenance pointer。
- **工具集 (Toolset)**：object store/filesystem、scheduler、vector/keyword index、SQLite/Postgres、policy engine。
- **影子技巧**：先用簡單 `notes.md` 驗證 retrieval value，再投資複雜 memory infra。
- **連結**：← [[S5]], [[G2]]

### P4：Permission-Aware Context Broker
- **場景 (Scenario)**：Agent 同時讀 Slack/Docs/email/local files/CRM，並可能把答案分享給其他人。
- **價值 (Value)**：阻止「檢索正確、分享越權」。
- **漏洞利用 (Exploit/How)**：
  1. Connector 回傳內容時附 `source_id`, `owner`, `acl`, `sensitivity`。
  2. Agent context window 中保存 provenance tag，不移除 ACL metadata。
  3. 生成 artifact 時做 taint propagation：輸出繼承最嚴格來源 scope。
  4. Share 前以 recipient identity 重新 resolve authorization。
  5. 不可授權的句子做 redaction 或重新生成，不只彈 warning。
  6. Audit log 保存「哪個來源影響哪個輸出」。
- **工具集 (Toolset)**：MCP/connector gateway、OPA/Cedar-style policy、identity provider、lineage store、DLP。
- **影子技巧**：將「human forwarding」視為 threat model；若現在只有人能安全轉傳，代表系統缺少 explicit delegation policy。
- **連結**：← [[S5]], [[G1]]

### P5：Sub-Agent Progressive Disclosure UI
- **場景 (Scenario)**：Agent 平行派生多個 research/coding/tool workers。
- **價值 (Value)**：保留可觀測性但不把一般使用者淹沒。
- **漏洞利用 (Exploit/How)**：
  1. 第一層只顯示 goal、worker count、elapsed time、budget、blocked state。
  2. 第二層顯示每個 sub-agent role 與輸出 artifact。
  3. 第三層顯示 tool trace / transcript / filesystem diff。
  4. 對 error 自動提升可見層級，不要求使用者自己翻 log。
  5. 允許 power user pin 某些 worker 到 always-visible。
- **工具集 (Toolset)**：trace graph、event stream、cost meter、artifact store、UI disclosure controls。
- **影子技巧**：不要把「reasoning transcript」當唯一 observability；tool event、artifact diff、policy decision 更可驗證。
- **連結**：← [[S4]]

### P6：At-Bat Productivity Instrumentation
- **場景 (Scenario)**：團隊導入 Agent 後 output 指標暴增，但管理者不知道是否真的變快。
- **價值 (Value)**：把 AI adoption 綁到可驗證的 learning velocity。
- **漏洞利用 (Exploit/How)**：
  1. 每個 initiative 建 `goal_state` 與 baseline。
  2. 每次 attempt 紀錄 hypothesis、artifact、feedback source、decision。
  3. 計算 `time_to_feedback`、`time_to_invalidate`、`validated_attempts/week`。
  4. 將 token/PR/tool-call 只當成本與診斷資料，不當主要成功 KPI。
  5. 每週抽查 5–10 個 at-bats，確認「完成」真的改變 goal state。
- **工具集 (Toolset)**：event log、product analytics、experiment tracker、issue tracker、cost ledger。
- **影子技巧**：若 AI dashboard 顯示 activity 成長但 at-bat cycle 沒縮短，立刻標記 automation theater。
- **連結**：← [[S6]]

### E1：Harness Surface Law
- **法則內容**：共享 Agent runtime 可以服務多種 persona；真正需要分裂的是 abstraction 與 policy defaults，不一定是能力核心。
- **推論/啟示**：Agent platform moat 會逐步從 model wrapper 移到 harness reliability、permission layer、artifact runtime 與 distribution。
- **支撐證據**：← [[D1]], [[D2]], [[D5]], [[S1]]

### E2：Artifact Supremacy Law
- **法則內容**：對知識工作，能直接交付可操作 artifact 的 Agent，價值高於只會解釋如何完成工作的聊天機器人。
- **推論/啟示**：文件格式、render/test、versioning、rollback 將變成 Agent 基礎設施，而不是 UI 細節。
- **支撐證據**：← [[D3]], [[D4]], [[P2]]

### E3：Persistence Converts Tool into Operator
- **法則內容**：filesystem、memory 與 scheduler 一旦持久化，Agent 就從一次性工具變成長期 operator。
- **推論/啟示**：persistent state 同時放大 utility 與 privacy/security blast radius。
- **支撐證據**：← [[D7]], [[D8]], [[G2]]

### E4：Context-Permission Coupling Law
- **法則內容**：Agent 能取得的 context 越多，authorization 必須越細；retrieval quality 與 access control 不能分開設計。
- **推論/啟示**：企業 Agent 的核心資料產品不是單純 RAG index，而是 permission-aware context graph。
- **支撐證據**：← [[D6]], [[G1]], [[P4]]

### E5：Cheap Output Makes Judgment Scarce
- **法則內容**：當 Agent 把產出成本壓低，稀缺資源會從「做東西」轉為「選對問題、拿到 feedback、判斷是否繼續」。
- **推論/啟示**：管理者應把 AI transformation 的 KPI 從 activity volume 改成 validated at-bat velocity。
- **支撐證據**：← [[D10]], [[S6]], [[P6]]
