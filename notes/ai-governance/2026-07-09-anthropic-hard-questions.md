---
id: anthropic:hard-questions
title: Inviting hard questions
source: Anthropic Newsroom
source_url: https://www.anthropic.com/news/hard-questions
published_at: '2026-07-09'
monetization_score: 94
category: ai-governance
language: zh-TW
note_format: zettelkasten-v6.6-cyberpunk
storage: private-github-markdown
repository: ed3c/ai-content-notes
path: notes/ai-governance/2026-07-09-anthropic-hard-questions.md
citation_mapping: pending
library_mapping: pending
---

### N1：從「回答 AI 爭議」轉成公開 Accountability Loop
- **核心衝突**：AI 公司面對工作流失、人類 agency、創作價值、濫用與科學醫療機會等問題時，最容易掉進 PR 回答；Anthropic 試圖把問題轉成可追蹤的 public commitment。
- **關鍵人物/實體**：Anthropic、Anthropic Institute、公眾、Claude users、Long-Term Benefit Trust。
- **衝擊力錨點 (Impact Anchors)**：
  - 文章發布於 2026-07-09。
  - Anthropic Public Record 第一輪蒐集 52,000 名美國人的希望與擔憂。
  - Anthropic Interviewer 調查 81,000 名 Claude users，橫跨 159 個國家與 70 種語言。
  - Anthropic 宣布公開追蹤回答 hard questions 所採取的具體行動，並承諾說明未達成目標之處。
- **劇情轉折**：問題從「公司如何說明自己」變成「公司能否把外部疑問編譯成 action、owner、evidence、status 與 failure disclosure」。
- **生態背景**：Frontier labs 正面對更高的公共責任壓力。單次 policy statement 很快過期；可追蹤 commitment system 才能與快速變化的 capability 對齊。
- **連結**：→ [[D1.1]], [[D1.2]], [[D2.1]], [[G1]]；≈ [[N2：Public Questions as Governance Inputs]]

### N2：Public Questions as Governance Inputs
- **核心衝突**：治理通常從公司內部 risk taxonomy 出發，但外部社會在意的問題可能完全不同。
- **關鍵人物/實體**：Internal safety/governance teams vs workers、families、creators、researchers、international users。
- **衝擊力錨點 (Impact Anchors)**：
  - Anthropic 明列四類 hard questions：誰決定 AI 規則、AI 是否給下一代更好未來、AI 是否讓世界更危險、AI 是否能幫科學家治療疾病。
  - 文章同時提及 job loss、creative work devaluation、human agency、meaning、misuse 與 scientific progress。
- **劇情轉折**：若 public concern 只停在 survey，它是研究資料；若能綁定政策、產品、研究與 outcome evidence，它才成為 governance input。
- **生態背景**：AI governance 的 Bug 往往不是「沒有規則」，而是規則的問題空間由供應商單方面定義。
- **連結**：→ [[C1]], [[C2]], [[S1]], [[G1]]

### Q1：公開承諾如何避免變成不可驗證的 PR backlog？
- **核心疑問 (The Doubt)**：承諾「公開追蹤行動」之後，什麼才算完成？
- **現狀反差 (Reality Gap)**：文章提出透明承諾，但真正可信需要 stable question ID、owner、deadline、evidence、counter-evidence、status transition 與 archived history。
- **思維實驗 (Simulation)**：半年後隨機抽 100 個 public questions；是否能從每個問題追到政策/產品/research action、evidence URL、未完成原因與下一個 review date？
- **連結**：← [[D2.1]], → [[S2]], [[P1]], [[G1]]

### Q2：52,000 美國人與 81,000 Claude Users 能代表誰？
- **核心疑問 (The Doubt)**：大型 sample 不等於代表性。
- **現狀反差 (Reality Gap)**：Public Record 的 52,000 人聚焦美國；Anthropic Interviewer 的 81,000 users 跨 159 國、70 語言，但仍是 Claude users，而非整體人口。
- **思維實驗 (Simulation)**：將 stakeholder 分成 users、non-users、workers、children/parents、creators、scientists、regulated sectors、low-connectivity regions；比較問題分布與優先序是否一致。
- **連結**：← [[D1.1]], [[D1.2]], → [[S1]], [[T1]]

### Q3：Public Input 何時能真正改變 Product / Safety Decision？
- **核心疑問 (The Doubt)**：feedback 是 advisory 還是具有 governance authority？
- **現狀反差 (Reality Gap)**：收集意見很容易；證明它導致不同的 model policy、product boundary 或 deployment decision 才困難。
- **思維實驗 (Simulation)**：每個 high-priority concern 必須至少綁定一個 decision record；若 decision 不採納 concern，也必須留下理由與 evidence。
- **連結**：← [[C2]], → [[G2]], [[P2]]

### C1：Public Accountability Loop
- **定義**：把外部問題轉成可追蹤 claim、action、evidence、decision 與 follow-up 的治理閉環。
- **演化**：PR statement → consultation → public record → executable commitment ledger。
- **本質**：透明不是公開更多文字，而是讓外部觀察者能驗證承諾與行動是否一致。
- **結構特徵**：question ID、stakeholder provenance、theme、priority、owner、commitment、evidence、status、review date、failure disclosure。
- **連結**：→ [[D2.1]], [[P1]], [[G1]], [[E1]]

### C2：Stakeholder Coverage
- **定義**：治理輸入是否涵蓋受 AI 影響但不一定是產品使用者的群體。
- **演化**：user feedback → public consultation → stratified stakeholder sampling。
- **本質**：只看 active users 會形成 selection bias；non-users 與 indirect stakeholders 也可能承受重大 externalities。
- **結構特徵**：population frame、language、country、user/non-user、occupation、age/guardian status、exposure level、sampling method。
- **連結**：→ [[D1.1]], [[D1.2]], [[T1]], [[E2]]

### D1.1：Anthropic Public Record 的 52,000-Person US Sample
- **操作手法**：蒐集美國公眾對 AI 的希望與擔憂，形成 public-record input。
- **獨特特徵**：規模大，但地理範圍集中美國，不能自動代表全球社會。
- **影子證據**：第一輪 52,000 名 Americans。
- **連結**：↔ [[D1.2]] ⟨S1⟩

### D1.2：Anthropic Interviewer 的 Global User Sample
- **操作手法**：對 Claude users 進行大規模 multilingual survey/interview，蒐集使用者對 AI 的觀點。
- **獨特特徵**：地理與語言覆蓋廣，但 sample frame 仍是 Claude users。
- **影子證據**：81,000 Claude users、159 countries、70 languages。
- **連結**：↔ [[D1.1]] ⟨T1⟩

### D2.1：Hard Questions Website → Public Action Tracking
- **操作手法**：邀請公眾提交最困難的 AI questions，並承諾公開追蹤具體 actions 與 shortfalls。
- **獨特特徵**：把「回答問題」與「證明採取行動」放到同一公開流程。
- **影子證據**：文章明確承諾 publicly track and report specific actions，並說明可能未達成 stated goals 的地方。
- **連結**：↔ [[D3.1]] ⟨G1⟩

### D3.1：Anthropic Institute + Long-Term Benefit Trust 的制度層
- **操作手法**：Anthropic Institute 專注 AI 對社會重大挑戰的研究；Long-Term Benefit Trust 提供公司公共利益 mission 的 impartial oversight。
- **獨特特徵**：把 research function 與 governance oversight 放在 public-question initiative 背後，而不是只交給 marketing channel。
- **影子證據**：文章將 Anthropic Institute 與自公司早期即存在的 Long-Term Benefit Trust 一併列為治理基礎。
- **連結**：↔ [[D2.1]] ⟨G2⟩

### S1：Separate Sample Size from Stakeholder Coverage
- **策略邏輯**：任何 public-input dashboard 都同時報 `N` 與 coverage gaps；禁止只用大數字暗示代表性。
- **生態位對照 (Ecological Context)**：
  - 主角表現：52,000 US public + 81,000 users / 159 countries / 70 languages 提供多種視角。
  - **環境/競對參照**：單一 opt-in survey 容易被 heavy users 與特定地區主導。
- **反面教材 (Pre-mortem)**：把 user sentiment 當 society sentiment，導致 governance priorities 對高曝光但非使用者群體失真。
- **理論基礎**：← [[D1.1]], [[D1.2]]
- **實踐路徑**：→ [[P2]]
- **支撐框架**：← [[T1]]

### S2：Convert Questions into an Evidence Ledger
- **策略邏輯**：每個 public commitment 必須有 stable identity、owner、evidence 與 lifecycle；否則透明度會退化成網頁更新。
- **生態位對照 (Ecological Context)**：
  - 主角表現：公開提交問題 + tracking specific actions。
  - **環境/競對參照**：傳統 corporate transparency report 通常是年度 snapshot，難追單一問題的演化。
- **反面教材 (Pre-mortem)**：問題持續新增，沒有 dedup、priority、status 或 stale rule，最後變成無限 backlog。
- **理論基礎**：← [[D2.1]]
- **實踐路徑**：→ [[P1]]
- **支撐框架**：← [[G1]]

### S3：Make Non-Adoption a First-Class Decision
- **策略邏輯**：外部意見不需要全部被採納，但不採納必須留下 rationale、evidence 與 review trigger。
- **生態位對照 (Ecological Context)**：
  - 主角表現：承諾說明 shortfalls 可形成更完整的 decision trail。
  - **環境/競對參照**：只公開「我們做了什麼」會產生 survivorship bias，看不到被拒絕的高價值 concerns。
- **反面教材 (Pre-mortem)**：公司只選容易回答的 questions，hard questions 被永久標記 research ongoing。
- **理論基礎**：← [[D2.1]], [[D3.1]]
- **實踐路徑**：→ [[P2]]
- **支撐框架**：← [[G2]]

### P1：Public Commitment Ledger
- **場景 (Scenario)**：把 public hard questions 轉成可驗證治理 work items。
- **價值 (Value)**：讓透明承諾可以被外部 audit，而不是只靠敘事。
- **漏洞利用 (Exploit/How)**：
  1. 每個問題建立 immutable `question_id`，保留原文、來源、日期、stakeholder metadata。
  2. 用 taxonomy 標記 jobs、agency、creative work、misuse、science/health、family/children 等 themes。
  3. 為每個 accepted concern 指派 owner、commitment、deadline、evidence type。
  4. Status 限定為 `received → scoped → action-planned → evidence-published → reviewed → closed/reopened`。
  5. 每個 close 必須附 evidence URL 與 reviewer；每個 overdue item 自動標 stale。
  6. 版本化公開 changelog；不得覆寫歷史狀態。
- **工具集 (Toolset)**：Git-backed Markdown/JSON ledger、issue tracker、schema validation、public dashboard、content digests。
- **影子技巧**：把「我們不同意」作合法 final state，但必須附 rationale 與 next-review trigger。
- **連結**：← [[S2]]

### P2：Stakeholder Coverage & Decision Audit
- **場景 (Scenario)**：驗證 consultation 是否覆蓋實際受影響群體，且輸入能追到 decision。
- **價值 (Value)**：降低 user-only sampling 與 performative consultation。
- **漏洞利用 (Exploit/How)**：
  1. 建 coverage matrix：country、language、user/non-user、occupation、age/guardian、AI exposure。
  2. 每輪 survey 公開 sampling frame、missing groups、known bias。
  3. 對 top concerns 建 `concern → policy/product/research decision` mapping。
  4. 抽樣 audit decision record，檢查 concern 是否被引用、採納或有 explicit rejection rationale。
  5. 每季比較 concern distribution 與 action allocation，找出 systematic under-response。
- **工具集 (Toolset)**：survey metadata、coverage dashboard、decision log、statistical weighting、audit samples。
- **影子技巧**：把 `coverage gap` 當正式 governance Bug，而不是 footnote。
- **連結**：← [[S1]], [[S3]]

### T1：Public Input Coverage Matrix
- **用途**：分離「sample 很大」與「stakeholder 真的被覆蓋」。
- **結構內容**：
  | 維度 | Public Record | Anthropic Interviewer | 必須補的 Blind Spot |
  |---|---|---|---|
  | Sample size | 52,000 | 81,000 | 不以 N 取代代表性 |
  | Geography | United States | 159 countries | country-level imbalance |
  | Language | 未由文章完整列出 | 70 languages | low-resource languages |
  | User status | broader public | Claude users | non-users / affected third parties |
  | Concern type | hopes + concerns | user views/experience | workers、children、creators、regulated sectors |
  | Governance link | Public Record | Interviewer research | decision/evidence mapping |
- **連結**：→ [[S1]], [[P2]]

### R1：Public Accountability System Roadmap
- **總體目標**：把「hard questions」從 campaign 升級成持續運行的 governance evidence system。
- **階段劃分**：
  - **Phase 1 Intake**：stable IDs、dedup、stakeholder metadata、theme taxonomy。
  - **Phase 2 Coverage**：coverage matrix、blind-spot sampling、bias disclosure。
  - **Phase 3 Commitments**：owner、action、deadline、evidence requirement。
  - **Phase 4 Decision Mapping**：concern → product/policy/research decisions。
  - **Phase 5 Audit**：external review、stale detection、reopen rules、historical changelog。
- **系統風險 (Glitches)**：selection bias、PR cherry-picking、unbounded backlog、no owner、evidence without outcome、silent policy reversal。
- **連結**：→ [[G1]], [[G2]]

### G1：Public Commitment Evidence Protocol
- **核心協議 (Protocol)**：公開承諾不是 statement，而是可 version、可追蹤、可 audit 的 governance object。
- **具體條款/機制**：
  - Stable question/commitment ID。
  - Source provenance 與 submission date。
  - Named owner / accountable function。
  - Deadline 或 review cadence。
  - Evidence requirement 與 status lifecycle。
  - Closure/rejection rationale。
  - Immutable history + reopen trigger。
- **決策流程**：Question → Dedup → Scope → Prioritize → Commit/Reject → Action → Evidence → Review → Close/Reopen。
- **違規後果**：無 evidence 的 completion claim 標記 `unverified`；過期未處理標記 `stale`。
- **連結**：← [[R1]], → [[S2]]

### G2：Public Input to Decision Protocol
- **核心協議 (Protocol)**：consultation 的價值由「是否改變或明確支持 decision」衡量，而非 participation count。
- **具體條款/機制**：
  - High-priority concern 必須映射至少一個 decision record。
  - Adoption 與 rejection 都保留 rationale。
  - Governance body 可抽樣 review mapping quality。
  - Material policy reversal 必須回鏈原 concerns 與新 evidence。
- **決策流程**：Concern Cluster → Decision Candidate → Evidence Review → Adopt/Reject → Publish Rationale → Monitor Outcomes。
- **違規後果**：沒有 decision/evidence mapping 的 public-input program 不得宣稱已形成 governance feedback loop。
- **連結**：← [[R1]], → [[S3]], [[P2]]

### E1：Transparency Is a Traceability Property
- **法則內容**：公開更多文字不等於透明；只有能從 question 追到 action、evidence、decision 與 failure 的系統才具可驗證透明度。
- **推論/啟示**：AI lab transparency 最終需要 ledger 與 lifecycle，而不只是報告。
- **支撐證據**：← [[C1]], [[D2.1]], [[P1]], [[G1]]

### E2：Large Samples Do Not Eliminate Selection Bias
- **法則內容**：52,000 或 81,000 的大樣本仍可能因 geography、user status、language、exposure 而系統性漏掉重要 stakeholders。
- **推論/啟示**：每個 governance survey 都應把 coverage gap 與 sample size 並列為 headline metric。
- **支撐證據**：← [[C2]], [[D1.1]], [[D1.2]], [[T1]]

### E3：Public Input Matters Only When It Can Reach Decisions
- **法則內容**：意見蒐集若沒有 `concern → decision → evidence` 路徑，只是 sentiment telemetry，不是 governance。
- **推論/啟示**：最值得變現的治理產品不是 survey SaaS，而是可稽核的 stakeholder-to-decision trace system。
- **支撐證據**：← [[Q3]], [[S3]], [[P2]], [[G2]]
