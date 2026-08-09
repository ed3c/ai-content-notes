---
id: openai:improving-gpt-5-6-sol-chatgpt
title: Improving GPT‑5.6 Sol in ChatGPT—and expanding access to GPT-5.6 Luna for free users
source: OpenAI Newsroom
source_url: https://openai.com/index/improving-gpt-5-6-sol-in-chatgpt/
published_at: '2026-08-06'
monetization_score: 100
category: frontier-models
language: zh-TW
note_format: zettelkasten-v6.6-cyberpunk
storage: private-github-markdown
repository: ed3c/ai-content-notes
path: notes/frontier-models/2026-08-06-openai-gpt-5-6-sol-chatgpt-luna-free.md
citation_mapping: pending
library_mapping: pending
---

### N1：Frontier Model 競爭從「選哪個模型」變成「給多少思考權」
- **核心衝突**：使用者要更準確、更完整的回答，但不願每次理解 model catalog、reasoning mode、latency、cost。產品必須把 reasoning budget 壓縮成可理解的 control surface。
- **關鍵人物/實體**：GPT‑5.6 Sol / GPT‑5.6 Luna / ChatGPT routing vs. 傳統 model-picker UX。
- **衝擊力錨點 (Impact Anchors)**：
  - 2026-08-06：OpenAI 更新 GPT‑5.6 Sol in ChatGPT，並擴大 GPT‑5.6 Luna 給 free users。
  - Plus/Pro 使用者可用 slider 控制思考程度，在 speed/efficiency 與 quality/thoroughness 間調整。
  - Free tier 以 GPT‑5.6 Luna 為預設，提供 unlimited text chats；需要更深推理時可按 Think。
  - OpenAI 表示每週約 1 billion people 使用 ChatGPT。
  - 在 internal financial/medical/legal factual-detail evaluation 上，至少出現一個 factual error 的 response，相較 GPT‑5.5 Instant：Luna 少 62%，Sol 少 68%。
- **劇情轉折**：OpenAI 把 model capability improvement 同時變成 premium control（Sol + slider）與 distribution expansion（Luna free default），形成「高階付費深度 + 免費可靠度」雙軌產品策略。
- **生態背景**：當 frontier model family 內部差異逐漸由 routing、effort、tools、context 決定，單一型號 benchmark 對實際 UX 的解釋力下降。
- **連結**：→ [[D1]], [[D2]], [[D3]], [[D4]], [[S1]]；≈ [[N2：Reliability becomes funnel design]]

### Q1：Reasoning Slider 是真正的 Capability Control，還是成本節流器？
- **核心疑問 (The Doubt)**：使用者拉高 slider 時，產品到底改了模型、reasoning budget、tool policy、latency budget，還是多個參數一起變？
- **現狀反差 (Reality Gap)**：UI 刻意壓成單一維度；底層實際上可能是多維 routing problem。
- **思維實驗 (Simulation)**：若相同任務在 low/high slider 得到不同事實正確率、tool use、latency、token usage，企業能否把 slider 當可重現設定寫入 SOP？
- **連結**：← [[D1]], [[D5]]；→ [[T1]], [[P1]]

### Q2：Free Tier 的 Unlimited Text 是否其實是 Agent Funnel？
- **核心疑問 (The Doubt)**：免費使用者獲得更強文字模型，但 advanced tools 仍有 limits。這是否把 monetization 從「限制聊天」轉向「限制高成本工具與深度工作流」？
- **現狀反差 (Reality Gap)**：傳統 freemium 以 message cap 製造升級壓力；Luna free default 改用能力/工具邊界分層。
- **思維實驗 (Simulation)**：若免費文字足以完成 80% 日常需求，真正付費 conversion 是否會集中在 persistent work、tool execution、higher reasoning、artifact generation？
- **連結**：← [[D2]], [[D6]]；→ [[S2]], [[T2]], [[P2]]

### Q3：62% / 68% Factual-Error Reduction 能否外推到 Production？
- **核心疑問 (The Doubt)**：internal evaluation 涵蓋 financial/medical/legal factual detail，但企業自己的 domain、document freshness、tool context 可能完全不同。
- **現狀反差 (Reality Gap)**：headline improvement 很大；沒有 private eval 就無法知道 own workload 的 base rate 與 error distribution。
- **思維實驗 (Simulation)**：如果舊模型 factual-error rate 是 10%，減少 68% 很有價值；若 enterprise workflow 的主要錯誤其實來自 stale context/tool failure，model accuracy 改善可能只打到小部分問題。
- **連結**：← [[D3]]；→ [[G1]], [[P3]]

### C1：Effort-Conditioned Model UX
- **定義**：使用者不直接選複雜 model/routing parameter，而透過單一 effort control 指定 speed/quality preference，由系統決定底層 execution budget。
- **演化**：model dropdown → auto routing → user-adjustable effort → task-adaptive policy。
- **本質**：把 inference budget 變成 product primitive。
- **結構特徵**：latency target、reasoning budget、model route、tool budget、cost envelope、quality target。
- **連結**：→ [[D1]], [[T1]], [[P1]]；→ [[E1]]

### C2：Reliability-First Free Tier
- **定義**：免費層不以最弱模型作為主要降級，而是提供可靠主模型，再限制高成本 execution/tool surfaces。
- **演化**：message-capped weak model → strong default model + capability/tool limits。
- **本質**：免費體驗本身成為 adoption engine；付費價值移向 depth、tools、throughput、workflows。
- **結構特徵**：default model、unlimited/basic quota、tool caps、deep-reasoning switch、upsell triggers。
- **連結**：→ [[D2]], [[D6]], [[S2]]；→ [[E2]]

### C3：Factual-Detail Reliability
- **定義**：不是只看 benchmark score，而是量測回答是否包含至少一個可驗證 factual error，特別針對 financial/medical/legal 等高精度場景。
- **演化**：aggregate benchmark accuracy → error-rate under realistic response → workflow-specific eval。
- **本質**：長回答只要混入一個錯誤，就可能破壞整個 work product。
- **結構特徵**：claim extraction、ground truth、error severity、domain、response length、tool/context condition。
- **連結**：→ [[D3]], [[G1]], [[P3]]；→ [[E3]]

### D1：Sol Slider 把多維 Inference Tradeoff 投影成一條線
- **操作手法**：Plus/Pro 在 web/mobile/desktop 使用 slider 調整思考程度，UI 以 speed/efficiency ↔ quality/thoroughness 表達。
- **獨特特徵**：使用者不必知道底層 parameter；但 system 必須能穩定 mapping 至 execution policy。
- **影子證據**：2026-08-06 更新；slider 同時支援 web、mobile、desktop。
- **連結**：→ [[C1]], [[P1]], [[G2]]

### D2：Luna 成為 Free Default，Unlimited Text 把 Adoption Barrier 壓低
- **操作手法**：Free user 預設走 GPT‑5.6 Luna，文字聊天不限量；需要深度推理時以 Think 入口切換。
- **獨特特徵**：免費層的主要限制轉到 tools 等昂貴能力，不再以一般文字 chat 次數作唯一 gate。
- **影子證據**：Free rollout 在公告當週與下一週展開；tool limits 仍存在。
- **連結**：→ [[C2]], [[S2]], [[P2]]

### D3：Financial / Medical / Legal Eval 用「至少一個錯誤」測長答案可靠度
- **操作手法**：針對需要 factual detail 的回答，判斷整段 response 是否含至少一個 factual error，而不是只對單題選擇題計分。
- **獨特特徵**：更接近日常 professional use 中「一個錯誤就污染文件」的風險模型。
- **影子證據**：相較 GPT‑5.5 Instant，Luna response with ≥1 factual error 減少 62%；Sol 減少 68%。
- **連結**：→ [[C3]], [[G1]], [[P3]]

### D4：同一 Sol 串起 Instant 與 Deeper Reasoning
- **操作手法**：Plus/Pro 的 fast/instant 與 deeper reasoning experiences 使用相同 Sol family，由 product routing/effort決定執行方式。
- **獨特特徵**：model identity 與 user-perceived mode 開始解耦。
- **影子證據**：官方公告指出同一 GPT‑5.6 Sol 支撐快速與深度工作模式。
- **連結**：→ [[C1]], [[S1]], [[E1]]

### D5：Slider 是 UX 壓縮，底層仍需要可觀測 Execution Contract
- **操作手法**：表面只給一個 slider；enterprise/runtime 仍應保存實際 model version、effort、tools、latency、tokens、route。
- **獨特特徵**：consumer simplicity 與 auditability 必須同時存在。
- **影子證據**：公告以 user-facing speed/quality single axis 呈現，而產品其他 workload（如 Codex/Work）仍可能有不同 runtime policy。
- **連結**：→ [[G2]], [[P1]]

### D6：Work / Codex 的 Sol Version 未隨 ChatGPT Update 同步
- **操作手法**：ChatGPT product update 與 Codex/Work release channel 分離，避免同一 model family 的更新無條件穿透所有 agentic workloads。
- **獨特特徵**：產品明確指出 Work/Codex 中的 Sol version 沒有因此同步變更。
- **影子證據**：2026-08-06 公告中的 compatibility note。
- **連結**：→ [[G3]], [[P4]], [[E4]]

### D7：Teen Safety Boundaries 與 Model Rollout 綁定
- **操作手法**：新模型/新 routing rollout 同時套用 youth-specific safety boundaries 與 evaluations。
- **獨特特徵**：release decision 不是純 capability gate；user segment 也會改 policy。
- **影子證據**：公告明確提到 teen safety boundaries 與相關 evals。
- **連結**：→ [[G3]], [[P4]]

### S1：Hide Model Complexity, Preserve Execution Evidence
- **策略邏輯**：consumer UI 可以把推理選擇壓成一條 slider；enterprise logs 必須保留底層 route 與 effort evidence。
- **生態位對照 (Ecological Context)**：
  - 主角表現：Sol slider 降低 model-selection cognitive load。
  - **環境/競對參照**：model picker 暴露太多 SKU；完全 auto-route 又讓 power user 無法控制延遲/品質。
- **反面教材 (Pre-mortem)**：UI 簡化後沒有 reproducible metadata，使用者無法解釋為何昨天結果與今天不同。
- **理論基礎**：← [[D1]], [[D4]], [[D5]]
- **實踐路徑**：→ [[P1]]
- **支撐框架**：← [[T1]], [[G2]]

### S2：Monetize Expensive Work, Not Basic Intelligence
- **策略邏輯**：當 strong text model 可以大規模免費提供，付費牆應移向 expensive reasoning、tools、persistent workflows、high throughput 與 enterprise controls。
- **生態位對照 (Ecological Context)**：
  - 主角表現：Luna free default + unlimited text；advanced tools 仍有限制。
  - **環境/競對參照**：早期 chatbot freemium 常用 message cap 限制基本互動。
- **反面教材 (Pre-mortem)**：free tier 太弱導致使用者看不到價值；太強但沒有高價 work surface 則 conversion 崩。
- **理論基礎**：← [[D2]]
- **實踐路徑**：→ [[P2]]
- **支撐框架**：← [[T2]]

### S3：Private Eval Before Migration
- **策略邏輯**：官方 factual improvement 是 prior，不是 enterprise proof。每個高價工作流都要自己量 error rate、latency、cost、tool success。
- **生態位對照 (Ecological Context)**：
  - 主角表現：OpenAI 公布 domain-focused factual-detail eval。
  - **環境/競對參照**：企業常因 public benchmark headline 直接切 production model。
- **反面教材 (Pre-mortem)**：model factuality變好，但 retrieval/tool chain 是主要 failure source，migration ROI 不如預期。
- **理論基礎**：← [[D3]], [[D6]]
- **實踐路徑**：→ [[P3]], [[P4]]
- **支撐框架**：← [[G1]], [[G3]]

### T1：Reasoning Effort Contract
- **用途**：把 slider / effort 從 UX 偏好轉成可測 runtime contract。
- **結構內容**：
  | 欄位 | Low | Medium | High |
  |---|---|---|---|
  | Latency budget | low | medium | high |
  | Reasoning budget | low | medium | high |
  | Tool budget | constrained | normal | expanded |
  | Cost ceiling | low | medium | high |
  | Quality target | routine | professional | critical |
  | Audit | route metadata | route metadata | route + approval |
- **連結**：→ [[S1]], [[P1]], [[G2]]

### T2：Free-to-Paid Funnel Matrix
- **用途**：拆解 strong free model 下真正可賣的價值。
- **結構內容**：
  | Surface | Free Value | Paid Trigger |
  |---|---|---|
  | Text chat | broad/unlimited | not primary |
  | Deep reasoning | limited/explicit | higher effort |
  | Tools | quota | more tool capacity |
  | Artifacts | basic | advanced workflows |
  | Persistent work | limited | memory/schedules/projects |
  | Enterprise | none/basic | admin, privacy, audit |
- **連結**：→ [[S2]], [[P2]]

### R1：Model Family Migration Roadmap
- **總體目標**：導入新 frontier model，不讓 consumer rollout 自動污染 business-critical agent workflow。
- **階段劃分**：
  - **Phase 1 Inventory**：列所有 surface、model version、effort、tools。
  - **Phase 2 Offline Eval**：factuality、reasoning、tool use、safety。
  - **Phase 3 Shadow**：重放 production tasks，不影響使用者。
  - **Phase 4 Canary**：1–5% real traffic，固定 effort tier。
  - **Phase 5 Policy Rollout**：依 user/task segment 放大。
  - **Phase 6 Dynamic Effort**：完成 evidence 後才允許 auto routing / slider policy。
- **系統風險 (Glitches)**：model version drift、effort metadata missing、tool behavior regression、segment safety policy mismatch。
- **連結**：→ [[G1]], [[G2]], [[G3]], [[S3]]

### G1：Factual Reliability Gate
- **核心協議 (Protocol)**：高精度 domain 不能只接受「平均更強」；必須量測 atomic factual claims 與 error severity。
- **具體條款/機制**：
  - 建 domain-specific cases 與 fresh ground truth。
  - response 拆 atomic claims；每個 claim 標 correct/incorrect/unverifiable。
  - 同時計 `response_with_any_error_rate` 與 severe-error rate。
  - 將 retrieval/tool errors 與 model intrinsic errors 分類。
  - migration 需達指定 reduction threshold，不能只看 public benchmark。
- **決策流程**：Dataset → Run Old/New → Claim Audit → Failure Taxonomy → Cost/Latency → Release Decision。
- **違規後果**：保持舊 route、要求 citation/tool grounding、人工 review。
- **連結**：← [[R1]]；→ [[S3]], [[P3]]

### G2：Effort Reproducibility Protocol
- **核心協議 (Protocol)**：每個 business-critical response 必須能重建當時的 model + effort + tool policy。
- **具體條款/機制**：
  - log immutable model/version id。
  - log user slider position / normalized effort tier。
  - log actual route、reasoning/tool budget class、tool versions。
  - UI label 變更不得覆寫 historical meaning。
  - critical workflow 禁止 uncontrolled auto-upgrade。
- **決策流程**：Request → Resolve Effort → Route → Execute → Trace Manifest → Result。
- **違規後果**：result 不可用於 audit-sensitive automation；rollback route。
- **連結**：← [[R1]]；→ [[S1]], [[P1]]

### G3：Surface-Specific Release Protocol
- **核心協議 (Protocol)**：Chat、Work、Codex、API 等 surface 分開做 release gate；同 model family 不代表 same operational behavior。
- **具體條款/機制**：
  - 每個 surface 有自己的 eval suite。
  - agentic surface 額外測 tool calls、filesystem、long-horizon recovery。
  - youth/regulated segment 有獨立 safety policy。
  - release manifest 明確列 model build + surface + policy bundle。
- **決策流程**：Model Candidate → Surface Eval → Segment Safety Eval → Canary → Release。
- **違規後果**：只回滾受影響 surface，不做全域盲切。
- **連結**：← [[R1]]；→ [[P4]], [[S3]]

### P1：把 Reasoning Slider 轉成 Production Effort Tiers
- **場景 (Scenario)**：企業 UI 想提供「快 ↔ 深」控制，但要可重現、可控成本。
- **價值 (Value)**：使用者操作簡單，平台仍能治理。
- **漏洞利用 (Exploit/How)**：
  1. 定義 3–5 個 normalized tiers，不直接暴露 raw token budget。
  2. 每 tier 設 latency/cost/tool ceilings。
  3. 用 representative tasks 測各 tier quality gain curve。
  4. critical task minimum tier 由 policy 強制，不讓使用者降到不安全設定。
  5. trace 保存 tier + actual route。
  6. 每次 model update 重跑 tier calibration。
- **工具集 (Toolset)**：model gateway、policy engine、eval harness、trace store、cost ledger。
- **影子技巧**：slider calibration 是 model-version specific；不能假設一代的 medium 等於下一代 medium。
- **連結**：← [[S1]], [[G2]]

### P2：設計 Strong-Free-Model Monetization Funnel
- **場景 (Scenario)**：免費模型已足以處理大部分文字需求。
- **價值 (Value)**：避免用弱化核心 intelligence 破壞 acquisition。
- **漏洞利用 (Exploit/How)**：
  1. 把 feature 分為 cheap text、expensive reasoning、tools、persistent compute、enterprise governance。
  2. Free 提供足夠可靠文字體驗建立 daily habit。
  3. 在使用者真正觸發高成本 action 時顯示升級價值，例如 long-running research、files、scheduled tasks。
  4. 記錄 conversion by task intent，不只按 message count。
  5. 比較「限制 messages」與「限制 expensive surfaces」的 retention/LTV。
- **工具集 (Toolset)**：product analytics、cost attribution、experiment platform、feature gating。
- **影子技巧**：upsell 文案直接顯示「這個任務需要的能力」，不要泛稱 Plus 更強。
- **連結**：← [[S2]], [[T2]]

### P3：Factual-Detail Private Eval
- **場景 (Scenario)**：金融、醫療、法律、研究報告等長答案需要高事實準確率。
- **價值 (Value)**：驗證 62%/68% 類改善是否在 own workload 成立。
- **漏洞利用 (Exploit/How)**：
  1. 抽 100–500 個真實 historical tasks，去除敏感資訊。
  2. 保存當時 authoritative sources / expected facts。
  3. 跑 old/new model，固定 context/tool條件。
  4. 用 claim extractor 拆 atomic claims。
  5. 人工抽驗 automated judge；計 any-error rate、severe-error rate、unverifiable rate。
  6. 加入 cost、latency、citation coverage，產生 migration scorecard。
- **工具集 (Toolset)**：eval framework、claim extraction、human review UI、trace store、spreadsheet/BI。
- **影子技巧**：至少保留一組「no retrieval」與一組「production retrieval」以分離 model improvement 與 RAG improvement。
- **連結**：← [[S3]], [[G1]]

### P4：Surface Isolation Release Test
- **場景 (Scenario)**：ChatGPT 同模型更新，但 Codex/Work agentic workflow不一定同步。
- **價值 (Value)**：防止把 chat-quality improvement誤認成 tool-agent regression-free。
- **漏洞利用 (Exploit/How)**：
  1. 建 surface matrix：chat/API/coding/work。
  2. 每 surface 保存 golden tasks。
  3. coding/work 額外測 long-horizon task、tool retry、file integrity、permission behavior。
  4. 新 build 在每 surface獨立 canary。
  5. teen/regulatory segment 再套 safety matrix。
  6. release manifest 與 rollback pointer進 Git。
- **工具集 (Toolset)**：feature flags、eval CI、trace replay、GitHub Actions、model gateway。
- **影子技巧**：公告中的「某 surface 未改」要寫進 dependency lock，不能靠工程師記憶。
- **連結**：← [[S3]], [[G3]]

### E1：Effort Becomes the SKU Law
- **法則內容**：當同一 model family 可覆蓋 fast 與 deep reasoning，使用者真正選擇的是 inference effort，而不是型號名稱。
- **推論/啟示**：未來 pricing、routing、SLO、eval 都可能圍繞 effort tier 設計。
- **支撐證據**：← [[D1]], [[D4]], [[C1]]

### E2：Free Intelligence, Paid Execution Law
- **法則內容**：當強模型文字互動可以大規模免費提供，付費價值會移向高成本 execution、tools、persistence、throughput與 governance。
- **推論/啟示**：Agent product 的 ARPU moat 會比 pure chat model 更依賴 workflow integration。
- **支撐證據**：← [[D2]], [[C2]], [[S2]]

### E3：One Wrong Fact Poisons the Artifact Law
- **法則內容**：professional knowledge work 的 reliability 不只看平均正確率；長答案中一個錯誤 factual claim 就可能讓整份交付物失效。
- **推論/啟示**：response-with-any-error 與 claim-level severity 比 generic benchmark 更適合高價知識工作。
- **支撐證據**：← [[D3]], [[C3]], [[G1]]

### E4：Model Family ≠ Release Unit
- **法則內容**：同一 model family 在不同 surface、tools、policy 下是不同 production system，必須分開 release。
- **推論/啟示**：Agent reliability 的版本單位應是 `model + harness + tools + policy + surface`。
- **支撐證據**：← [[D6]], [[D7]], [[G3]]
