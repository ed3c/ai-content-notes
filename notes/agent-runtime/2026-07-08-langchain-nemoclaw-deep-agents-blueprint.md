---
id: langchain:nemoclaw-deep-agents-blueprint
source: LangChain Blog
canonical_url: https://www.langchain.com/blog/langchain-and-nvidia-launch-the-nemoclaw-deep-agents-blueprint
published_at: 2026-07-08
collected_at: 2026-08-11T09:22:10+08:00
repository: ed3c/ai-content-notes
path: notes/agent-runtime/2026-07-08-langchain-nemoclaw-deep-agents-blueprint.md
protocol: v6.6-cyberpunk
---

### N1：Agent Moat 從 Model 移到 System Stack
- **核心衝突**：企業買到更強 model，卻不代表 agent 更可靠。真正會累積成 proprietary IP 的是 memory、workflow、trace、eval dataset、harness config、runtime policy。
- **關鍵人物/實體**：LangChain Deep Agents + NVIDIA Nemotron 3 Ultra + NVIDIA OpenShell vs closed one-size-fits-all agent stack。
- **衝擊力錨點 (Impact Anchors)**：
  - 2026-07-08：LangChain 與 NVIDIA 發布 NemoClaw for LangChain Deep Agents blueprint。
  - LangChain eval suite：Nemotron 3 Ultra + tuned Deep Agents harness aggregate score **0.86**，成本 **$4.48**；next closest performing model 成本 **$43.48**，約 **10x** 差距。
- **劇情轉折**：Model benchmark 不再是終點。低 inference cost 反過來允許跑更大 eval suite、更多 variants、更多 specialized agents，形成 engineering flywheel。
- **生態背景**：Long-running agent 的 unit economics 由多次 model calls、tool loops、sandbox time、eval frequency 共同決定。
- **連結**：→ [[D1.1]], [[D2.1]], [[G1]]

### Q1：如果便宜 10x，真正多買到的是 Token，還是 Learning Velocity？
- **核心疑問 (The Doubt)**：低 inference cost 最重要的作用是否不是降低帳單，而是允許團隊提高 experimentation/evaluation frequency？
- **現狀反差 (Reality Gap)**：理想是「便宜模型 = 更低成本」；現實是 agent 系統會把省下來的 budget 重新投入 eval、variant search、specialization。
- **思維實驗 (Simulation)**：同樣 $43.48 budget，如果 candidate stack 每輪只需 $4.48，能否把單次 benchmark 升級成多版本 regression gate？
- **連結**：← [[D2.1]], → [[S2]]

### C1：Model–Harness–Eval–Runtime Co-Optimization
- **定義**：把 agent quality 視為四層耦合系統，而非單一 model property。
- **演化**：Prompt tuning → harness tuning → runtime/policy/eval 一起 versioned。
- **本質**：Agent performance 是 system function：`f(model, context, tools, harness, evals, runtime, policy)`。
- **結構特徵**：open model layer、tuned harness、governed runtime、continuous eval。
- **連結**：→ [[D1.1]], [[D1.2]], [[D1.3]], [[E1]]

### D1.1：Open Model Layer — Nemotron 3 Ultra
- **操作手法**：允許 enterprise 自行 run、customize、optimize model layer。
- **獨特特徵**：企業能把 model weights 與自己的 workload requirements 綁定，而不是固定接受 closed endpoint behavior。
- **影子證據**：Blueprint 指定 **NVIDIA Nemotron 3 Ultra**。
- **連結**：↔ [[D1.2]], [[D1.3]] ⟨S1⟩

### D1.2：Tuned Harness — Deep Agents Code
- **操作手法**：Harness 管 planning、tool use、memory、task execution，並對 Nemotron 3 Ultra 調整 tool use、context management、intermediate eval。
- **獨特特徵**：不是只改 system prompt；harness 本身成為可版本化的 performance layer。
- **影子證據**：官方描述的 tuned profile 對長時間 agent tasks 做 workload-specific adaptation。
- **連結**：↔ [[D1.1]], [[D1.3]] ⟨S1⟩

### D1.3：Governed Runtime — OpenShell
- **操作手法**：在 sandboxed agent execution 中套用 tools、systems、data interaction policies。
- **獨特特徵**：把「agent 可以呼叫 tool」與「agent 被允許在哪裡執行」拆開。
- **影子證據**：Blueprint 將 **NVIDIA OpenShell** 明確放在 governed runtime layer。
- **連結**：↔ [[D1.1]], [[D1.2]] ⟨G1⟩

### D2.1：0.86 / $4.48 vs $43.48
- **操作手法**：在相同 agent eval suite 中比較 aggregate performance 與 inference cost。
- **獨特特徵**：用 cost-aware evaluation 而非只看 quality score。
- **影子證據**：aggregate **0.86**；成本 **$4.48**；next closest **$43.48**；約 **10x lower inference cost**。
- **連結**：→ [[S2]], [[T1]]

### D2.2：低成本讓 Eval 變成 Continuous Control Loop
- **操作手法**：pre-deployment 測 prompts、harnesses、tools、models、data；post-deployment 監控 behavior，把 failure 轉成 regression tests。
- **獨特特徵**：Inference economics 直接控制 eval coverage。
- **影子證據**：LangChain 明確列出 larger eval suites、更多 model/harness/tool variants、specialized agents 三種被低成本解鎖的行為。
- **連結**：→ [[S2]], [[P2]]

### D3.1：Enterprise IP 不只在 Data
- **操作手法**：把 agent memory、workflows、traces、eval datasets、harness configuration、tuning data 視為公司專有知識資產。
- **獨特特徵**：Context/harness/eval 會隨 production use 累積，比單一 prompt 更接近 operational moat。
- **影子證據**：官方逐項列出 memory、workflows、traces、eval datasets、harness configuration、tuning data。
- **連結**：→ [[G2]], [[E2]]

### S1：把 Agent Stack 當 Compiler Target，而不是 SDK Collection
- **策略邏輯**：Canonical capability 應先定義，再編譯到 model/harness/runtime adapters。否則 host-specific config 會變成 source of truth。
- **生態位對照 (Ecological Context)**：
  - 主角表現：NemoClaw 把 model、harness、runtime 分層。
  - **環境/競對參照**：典型 agent demo 把 model API + tools 寫在一個 script，沒有 lifecycle/evidence boundary。
- **反面教材 (Pre-mortem)**：只換 model 就宣稱 stack 升級；生成 dist artifacts 卻沒有 canonical capability spec。
- **理論基礎**：← [[D1.1]], [[D1.2]], [[D1.3]]
- **實踐路徑**：→ [[P1]]
- **支撐框架**：← [[G1]]

### S2：Cost-Aware Eval Flywheel
- **策略邏輯**：省下的 inference budget 應被重新投資到更多 eval repetitions、variants、edge cases，而不是只當 gross-margin optimization。
- **生態位對照 (Ecological Context)**：
  - 主角表現：低成本 open stack 讓 larger eval suites 更實際。
  - **環境/競對參照**：高單次 inference 成本會誘導團隊少跑 regression、少做 ablation。
- **反面教材 (Pre-mortem)**：只比較每 token 價格，不比較 task success、turn count、latency、review cost。
- **理論基礎**：← [[D2.1]], [[D2.2]]
- **實踐路徑**：→ [[P2]]
- **支撐框架**：← [[T1]]

### P1：Open Agent Stack Build Contract
- **場景 (Scenario)**：建立可在 Claude Code/Codex/自有 runtime 之間遷移的 production Skill/Agent stack。
- **價值 (Value)**：讓 knowledge、harness、runtime policy 可獨立版本化與替換。
- **漏洞利用 (Exploit/How)**：
  1. 定義 canonical capability：inputs、outputs、tools、assertions、risk tier。
  2. Model adapter 只描述 model/profile，不保存 business invariant。
  3. Harness adapter 管 context、memory、planning、tool loop。
  4. Runtime adapter 管 sandbox、network、filesystem、secret policy。
  5. Eval contract 綁定 model/harness/runtime digests，避免 moving-target benchmark。
  6. Compiler 產生 host-specific artifacts；generated files 不得反向成 canonical source。
- **工具集 (Toolset)**：SKILL.md、AGENTS.md/CLAUDE.md、OpenShell-like sandbox、eval harness、artifact digest、Decision Trace。
- **影子技巧**：Model、harness、runtime 任一變更都應觸發 impact analysis；不要只在 model release 時 requalify。
- **連結**：← [[S1]]

### P2：Cost-per-Success Evaluation Loop
- **場景 (Scenario)**：比較 open/closed model 或多個 agent profiles。
- **價值 (Value)**：避免 benchmark score 與 production economics 分家。
- **漏洞利用 (Exploit/How)**：
  1. 固定 task pool、host、tools、policy、timeout。
  2. 每 candidate 執行同樣 repetitions。
  3. 記錄 success、cost、latency、turns、tool failures、human review time。
  4. 計算 `cost_per_success = total_cost / successful_tasks`。
  5. 對品質差距做 confidence interval；沒有統計 eligibility 不排名。
  6. 將 regression case 回寫 task pool，建立 continuous eval flywheel。
- **工具集 (Toolset)**：paired eval runner、cost telemetry、signed receipts、leaderboard eligibility gate。
- **影子技巧**：$4.48 vs $43.48 的價值只有在 task envelope 可比時成立；不同 harness/profile 不可偷換成單純「model 價格比較」。
- **連結**：← [[S2]]

### T1：Agent Stack Optimization Matrix
- **用途**：把 quality、cost、latency、governance 放在同一 decision surface。
- **結構內容**：
  | Layer | 可調參數 | 主要證據 |
  |---|---|---|
  | Model | weights / reasoning profile | task success / cost |
  | Harness | context / tools / memory / planning | trajectory / regression eval |
  | Eval | task pool / thresholds / repetitions | uncertainty / failure taxonomy |
  | Runtime | sandbox / policy / permissions | execution receipt / cleanup proof |
- **連結**：→ [[S1]], [[S2]], [[P1]], [[P2]]

### R1：Open Agent Production Roadmap
- **總體目標**：從可跑 demo 升級到可 ownership、可治理、可 requalify 的 agent stack。
- **階段劃分**：
  - **Phase 1 Canonicalize**：能力、assertions、risk、sources 先寫成 machine-readable contracts。
  - **Phase 2 Compile**：生成 model/harness/runtime adapters。
  - **Phase 3 Evaluate**：paired cost/performance eval + negative tests。
  - **Phase 4 Sandbox**：真 runtime execution + cleanup proof。
  - **Phase 5 Admit**：human/policy review 後才提升 lifecycle/routability。
  - **Phase 6 Feedback**：production failures 轉 regression cases，再跑 requalification。
- **系統風險 (Glitches)**：generated-artifact drift、benchmark leakage、runtime policy mismatch、cost-only optimization。
- **連結**：→ [[G1]], [[G2]]

### G1：Runtime Independence Protocol
- **核心協議 (Protocol)**：Harness 不能授予自己 runtime authority；runtime policy 是獨立 enforcement plane。
- **具體條款/機制**：default deny、scoped tools、network/secret boundaries、immutable policy digest、cleanup receipt。
- **決策流程**：capability → compile → runtime profile → execution → receipt → verification → admission。
- **違規後果**：qualification_eligible=false；禁止 production routing。
- **連結**：← [[R1]], → [[S1]]

### G2：Agent IP Provenance Protocol
- **核心協議 (Protocol)**：Memory、trace、eval data、harness config 皆視為可治理資產，不與 public model license 混在一起。
- **具體條款/機制**：分開 code/model/data/trajectory provenance；版本與 retention policy；敏感 traces 不進 public exports。
- **決策流程**：capture → classify → redact → version → evaluate → admit/reject。
- **違規後果**：quarantine artifact；禁止進 downstream training/eval。
- **連結**：← [[R1]], → [[S2]]

### E1：Agent Performance 是 Stack Property
- **法則內容**：Production agent 的表現不能只歸因於 model；model、harness、eval、runtime 必須一起看。
- **推論/啟示**：Agent architecture review 應追蹤跨層 digest 與 causal change，而非只記 model name。
- **支撐證據**：← [[C1]], [[D1.1]], [[D1.2]], [[D1.3]]

### E2：低 Inference Cost 的真正槓桿是更多實驗
- **法則內容**：當單次 iteration 便宜，團隊可以增加 eval density，進而提高 learning velocity。
- **推論/啟示**：成本優勢應用在更多 ablation、regression、specialized-agent experiments，而非只降低 serving bill。
- **支撐證據**：← [[D2.1]], [[D2.2]], [[S2]]

### E3：企業 Agent Moat 是可重播的 Operational Knowledge
- **法則內容**：能被 replay、eval、govern、改善的 memory/workflow/trace/harness 才能形成可累積 moat。
- **推論/啟示**：Skill.md / capability contracts 若沒有 evidence + eval + runtime state，就只是文件，不是 production intelligence asset。
- **支撐證據**：← [[D3.1]], [[G2]], [[P1]]