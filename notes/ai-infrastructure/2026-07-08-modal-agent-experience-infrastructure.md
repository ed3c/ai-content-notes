---
id: latent-space:modal-agent-experience
title: Why AI Infrastructure must evolve for Agent Experience — Akshat Bubna, Modal CTO
source: Latent Space
source_url: https://www.latent.space/p/modal2026
published_at: '2026-07-08'
monetization_score: 98
category: ai-infrastructure
language: zh-TW
note_format: zettelkasten-v6.6-cyberpunk
storage: private-github-markdown
repository: ed3c/ai-content-notes
path: notes/ai-infrastructure/2026-07-08-modal-agent-experience-infrastructure.md
citation_mapping: pending
library_mapping: pending
---

### N1：Cloud for Developers → Cloud for Agents
- **核心衝突**：傳統 cloud 假設操作者是會讀 docs、理解 YAML、看 dashboard、補齊缺失 context 的 human developer；agent 沒有這種隱性心智模型，因此 infra primitive 必須更可程式化、更快、更明確、更可觀測。
- **關鍵人物/實體**：Modal CTO Akshat Bubna、Modal、AI agents vs Kubernetes-era cloud stack。
- **衝擊力錨點 (Impact Anchors)**：
  - Latent Space episode 發布於 2026-07-08，完整節目約 57:55。
  - Modal 在此時剛完成 $355M Series C；兩年前 Latent Space 首次採訪時，Modal 還是約 $17M Series A 階段。
  - Modal 在 ChatGPT 推出前約 1 年就加入 GPU support。
  - Episode 將 Agent Experience (AX) 描述成下一階段 infra product surface。
- **劇情轉折**：Modal 最早只是嘗試做比 Kubernetes 更適合 bursty workloads 的 runtime；AI 使 workload shape、tooling consumer 與 iteration loop 同時改變，runtime 逐步長成 agent cloud。
- **生態背景**：Agent cloud 競爭包含 Databricks、Daytona、Railway、E2B、managed-agent products 與 hyperscaler primitives；真正戰場不是單一 VM/GPU，而是 agent 能否自己部署、執行、觀測、修正。
- **連結**：→ [[D1.1]], [[D1.2]], [[D2.1]], [[G1]]；≈ [[N2：Programmatic Infra Becomes Agent-Native Infra]]

### N2：Programmatic Infra Becomes Agent-Native Infra
- **核心衝突**：早期 developer-centric serverless 追求少寫 YAML；agent-centric infrastructure 進一步要求所有重要操作都能透過 deterministic CLI/API/tool surface 完成。
- **關鍵人物/實體**：Human developer workflow vs autonomous agent loop。
- **衝擊力錨點 (Impact Anchors)**：
  - Modal 在 2023-05 左右已建立 sandboxes；第一個 public example 把 smol developer 放進 loop，讓 agent 可以 iterate on itself。
  - 早期 models 約跑 10 iterations 後就容易 diverge；當時 tool calling 與 self-correction 都不成熟。
- **劇情轉折**：當 model capability 後來補上 reasoning/tool use，原本「太早」的 sandbox primitive 變成 agent infrastructure 的核心需求。
- **生態背景**：Infra product timing 不只取決於 backend readiness，也取決於 model 是否能消費 primitive。
- **連結**：→ [[D2.1]], [[C2]], [[S1]]

### N3：Inference Optimization 從 Kernel 微調轉成 System Multipliers
- **核心衝突**：只優化 kernel 常得到小幅提升；speculative decoding、elastic scheduling、snapshotting、tail-latency control 等 system-level design 能帶來 multiplicative gains。
- **關鍵人物/實體**：Modal DeFlash / Auto Endpoints vs raw vLLM / SGLang / GPU rental。
- **衝擊力錨點 (Impact Anchors)**：
  - DeFlash 被描述為 block-based speculator，Modal 將相關工作 open source。
  - 節目討論 speculative decoding 的 accept length，可產生約 2–4× speedup 等級的提升，而不是只有 few-percent kernel gain。
  - Auto Endpoints 將 DeFlash 等優化包進可由 UI/CLI 建立的 endpoint，同時保留 code transparency 與可 eject 到完整 Modal stack 的路徑。
- **劇情轉折**：Infra vendor 的價值從「有 GPU」變成「把 inference、autoscaling、reliability、observability、optimization 作成可操作 system」。
- **生態背景**：Open-source inference engines 快速進步，平台競爭必須往 elasticity、production SLO、customization 與 expert support 上移。
- **連結**：→ [[D3.1]], [[D3.2]], [[S2]], [[P2]]

### N4：Hard Guardrails 返回 Agent Runtime Kernel
- **核心衝突**：LLM-mediated permissions 很有彈性，但 sandbox-level security 不能完全依賴另一個 probabilistic model 判斷。
- **關鍵人物/實體**：Hard sandbox policy vs LLM-mediated permission system。
- **衝擊力錨點 (Impact Anchors)**：
  - 在約 43 分鐘處，Akshat 對 sandbox-level LLM-mediated permissions 明確表示 skeptical，理由是需要 hard boundaries 避免資料 exfiltration。
  - 他主張 hard guardrails 可以與 softer/LLM-mediated guardrails 配合，而不是二選一。
- **劇情轉折**：越 autonomous 的 agent 越需要 OS-like deterministic boundary；「更聰明的 agent」不會自動消除最小權限與 network isolation 的需求。
- **生態背景**：Claude Code 類 permission mediation、managed agent runtimes、specialized sandboxes 都在重新定義 AI OS security model。
- **連結**：→ [[D6.1]], [[G2]], [[E4]]

### Q1：Kubernetes 的問題是 UX，還是 workload shape？
- **核心疑問 (The Doubt)**：如果只是用更好的 CLI 包裝 Kubernetes，是否足以支撐 agent cloud？
- **現狀反差 (Reality Gap)**：Modal 的原始判斷同時包含兩類問題：developer experience 差，以及 Kubernetes 更偏 slow-scaling web-server workload，不適合高度 bursty、custom-image、accelerator-heavy workloads。
- **思維實驗 (Simulation)**：同一 workload 分別在固定 cluster、autoscaled K8s、serverless container 上做 0→1000 GPU burst；比較 scheduling lag、idle cost、image setup、state restore、failure recovery。
- **連結**：← [[D1.1]], [[D4.1]], → [[S1]]

### Q2：Agent Experience 與 Developer Experience 到底差多少？
- **核心疑問 (The Doubt)**：AX 是新市場語言，還是需要不同 primitive？
- **現狀反差 (Reality Gap)**：Akshat 認為兩者高度相似，但 agent 特別需要 CLI-accessible logs/metrics、deterministic primitives、short feedback loop；Modal Bench 用來找 agent 常失敗或「想像出」的 missing feature。
- **思維實驗 (Simulation)**：把 UI-only workflow 全部關掉，只給 agent docs + CLI；觀察它在哪些地方 hallucinate nonexistent commands 或無法 debug。
- **連結**：← [[D8.1]], → [[S4]], [[P4]]

### Q3：100,000 Sandboxes 是 Feature，還是新的 Cost/Safety Bug？
- **核心疑問 (The Doubt)**：RL rollouts 與 research agents 能快速平行啟動大量 sandbox，是否會把 iteration speed 轉成 runaway cost / unsafe action surface？
- **現狀反差 (Reality Gap)**：大規模 sandbox 能提高 throughput，但每個 sandbox 都需要 identity、network、storage、quota、cleanup 與 observability。
- **思維實驗 (Simulation)**：一次 100,000 sandbox rollout，若只有 0.1% cleanup failure，就會留下 100 個殘留 execution environments。
- **連結**：← [[D2.2]], [[D6.1]], → [[G2]], [[G3]]

### Q4：Open-Source Inference Engine 越強，Cloud Platform 的價值是否下降？
- **核心疑問 (The Doubt)**：若 vLLM/SGLang + commodity GPU 能服務同一模型，為何使用 specialized platform？
- **現狀反差 (Reality Gap)**：Akshat 將差異指向 elasticity、scale-to-zero、tail latency、delivery semantics、custom optimization 與 expert team，而不是把 inference engine 本身鎖成 proprietary moat。
- **思維實驗 (Simulation)**：固定 model/quantization，在 raw GPU + SGLang 與 managed elastic endpoint 上跑 bursty production trace，納入 cold-start、idle、p99、failure-retry、ops labor，不只比 tokens/sec。
- **連結**：← [[D3.2]], → [[S2]], [[T2]]

### C1：Agent Cloud
- **定義**：讓 agents 可以自行建立 runtime、取得 compute、執行 code、觀察結果、修改環境、重試、保存 state 並受到 policy 限制的 cloud control plane。
- **演化**：IaaS → PaaS → serverless → AI cloud → agent cloud。
- **本質**：把 infra 操作從 human-oriented console/YAML 轉成 agent-consumable deterministic primitives。
- **結構特徵**：sandbox、elastic compute、GPU、persistent storage、networking、CLI/API、observability、policy、snapshots、multi-node execution。
- **連結**：→ [[D1.1]], [[D2.1]], [[D4.1]], [[G1]], [[E1]]

### C2：Sandbox as an Agent Compute Primitive
- **定義**：為 agent 提供隔離、可建立/銷毀、可配置 image/network/storage 的 execution environment。
- **演化**：CI/build sandbox → code interpreter → agent runtime sandbox → RL rollout substrate。
- **本質**：讓 agent 有可驗證的「computer」而不是只會產生文字。
- **結構特徵**：ephemeral filesystem、snapshot/restore、network policy、resource quota、process lifecycle、artifact export、cleanup proof。
- **連結**：→ [[D2.1]], [[D2.2]], [[D6.1]], [[P1]], [[G2]]

### C3：Elastic Inference
- **定義**：依 request/load shape 在 GPU resources 上快速 scale up/down，維持 throughput、latency 與 cost efficiency。
- **演化**：fixed replicas → autoscaling endpoints → scale-to-zero + burst-to-thousands。
- **本質**：AI workloads 的需求曲線高度 bursty；容量 management 是 model serving quality 的一部分。
- **結構特徵**：cold-start control、GPU snapshotting、request queue、tail latency、capacity pool、region-aware placement、batch tiers。
- **連結**：→ [[D3.1]], [[D4.1]], [[D5.1]], [[T2]], [[E2]]

### C4：Supercloud Capacity Pool
- **定義**：把多家 cloud provider / region / GPU supply 聚合成一個 fungible capacity control plane。
- **演化**：single-cloud reservation → multi-cloud failover → 17-provider capacity pool。
- **本質**：對 bursty AI workload，GPU supply chain 與 scheduling policy 本身就是 product capability。
- **結構特徵**：capacity forecasting、reservation mix、GPU substitutability、region policy、cost curve、placement algorithm。
- **連結**：→ [[D4.1]], [[D5.1]], [[S3]]

### C5：Agent-Native Observability
- **定義**：不只讓 human 看 dashboard，而是讓 agent 能透過 CLI/API 讀 logs、metrics、state、error context 並進行 corrective action。
- **演化**：human dashboard → API telemetry → tool-callable diagnostics。
- **本質**：agent 無法使用的 observability 等於不存在。
- **結構特徵**：structured logs、stable resource IDs、CLI query、trace correlation、error taxonomy、machine-readable suggestions。
- **連結**：→ [[D8.1]], [[P4]], [[E5]]

### D1.1：Modal 起點：Runtime Beyond Kubernetes
- **操作手法**：用 serverless functions/container runtime 支援 ETL、job queues、bursty processing，將 infra provisioning 藏在 code/decorator primitive 後方。
- **獨特特徵**：不是先建立「AI cloud」品牌，而是先解 workload orchestration + burstiness + developer experience。
- **影子證據**：Akshat 指出 Kubernetes 不適合 burstiness、custom images，且傳統設計偏 slow-scaling web server use cases。
- **連結**：↔ [[D1.2]], [[D4.1]] ⟨S1⟩

### D1.2：GPU Before ChatGPT
- **操作手法**：在早期 runtime primitive 上加入 accelerator support，最初想像包含 classical inference、computer vision、XGBoost 等 workload。
- **獨特特徵**：GPU capability 在需求爆發前先存在，後來被 foundation-model wave 放大。
- **影子證據**：Modal 約在 ChatGPT 出現前 1 年加入 GPUs。
- **連結**：↔ [[D1.1]] ⟨E3⟩

### D2.1：2023 Sandbox + smol developer Loop
- **操作手法**：Modal 早在 2023-05 左右建立 sandboxes，並把 smol developer 放進 loop，讓 agent 反覆生成、執行、觀察、修正。
- **獨特特徵**：primitive 早於成熟 agent market 約數年。
- **影子證據**：訪談回憶早期 model 約 10 iterations 後容易 divergence；當時 tool calling / self-correction 尚不成熟。
- **連結**：↔ [[D2.2]] ⟨S1⟩

### D2.2：RL Rollouts Need Massive Sandbox Parallelism
- **操作手法**：把每個 rollout / experiment 放在獨立 sandbox，並以大量平行 execution 提高 training/research throughput。
- **獨特特徵**：節目將 100,000 sandboxes 列為 RL rollout 的真實需求等級，而非 demo-scale concurrency。
- **影子證據**：episode discussion list 明列「why RL rollouts can require 100,000 sandboxes」。
- **連結**：↔ [[D2.1]], [[D6.1]] ⟨G3⟩

### D3.1：DeFlash Block-Based Speculative Decoding
- **操作手法**：用 draft/speculator 預測 token blocks，再由大模型 batch verify；提高 accept length 以換取 multiplicative speedup。
- **獨特特徵**：Modal open-source 相關工作，並與 SGLang 團隊合作/upstream improvements。
- **影子證據**：節目討論約 2–4× speedup 等級；相較之下單純 kernel optimization 常只是 few-percentage-point 改善。
- **連結**：↔ [[D3.2]] ⟨S2⟩

### D3.2：Auto Endpoints = Optimized Default + Ejectable Code
- **操作手法**：從 UI/CLI 建 endpoint，內建 DeFlash 等 optimization；同時提供完整 code，進階使用者可 eject 到完整 Modal code experience。
- **獨特特徵**：避免「easy mode = black box」；入門與深度 customization 走同一 stack。
- **影子證據**：Akshat 強調 endpoint 可 scaling-to-zero、bursty serving，並把 code transparency 作為產品特徵。
- **連結**：↔ [[D3.1]] ⟨P2⟩

### D4.1：17-Cloud Capacity Pool
- **操作手法**：把跨 17 cloud providers 的 capacity 統一管理，依 GPU type、region、reservation、demand 進行 placement。
- **獨特特徵**：平台把供應鏈風險與 capacity planning 直接內化成 runtime capability。
- **影子證據**：episode discussion list 明列 Modal 的 17-cloud capacity pool / supercloud strategy。
- **連結**：↔ [[D5.1]] ⟨S3⟩

### D4.2：Private IPv6 Overlay (I6PN) + eBPF Policy
- **操作手法**：同 workspace containers 透過 private IPv6 address 互相尋址；connection policy 可在 kernel/eBPF 層 allow/reject。
- **獨特特徵**：原本為 distributed training primitive 建立，後來被使用者挖掘成 general private networking primitive。
- **影子證據**：訪談提到 I6PN；早期方案曾涉及 sidecar，後續可利用 eBPF 做 kernel-level enforcement。
- **連結**：↔ [[D4.3]] ⟨G2⟩

### D4.3：RDMA and 3 Tb/s-Class Internal Networking
- **操作手法**：multi-node training 使用 RDMA bypass TCP stack，以更快搬運 weights/KV/state；private TCP overlay 可先完成 key exchange，再建立 RDMA path。
- **獨特特徵**：distributed training / RL 的 bottleneck 被重新描述為 memory movement + scheduling，而不是只有 FLOPS。
- **影子證據**：Akshat 提到約 3 terabit/s internal networking 等級，並把 RDMA 視為 multi-node training 的 standard requirement。
- **連結**：↔ [[D4.2]] ⟨E2⟩

### D5.1：Compute Strategy as a First-Class Team
- **操作手法**：專門團隊管理 capacity forecast、1-year vs 3-year reservations、GPU type/region fungibility、supply-chain outlook 與供給押注。
- **獨特特徵**：不是單純 FP&A；它直接影響 product SLO、unit economics 與可售 capacity。
- **影子證據**：Modal 將該角色直接稱為「compute strategy」。
- **連結**：↔ [[D4.1]] ⟨S3⟩

### D6.1：Hard Guardrails at Sandbox Level
- **操作手法**：network/storage/credential/resource boundary 由 deterministic sandbox policy enforce；LLM-mediated soft policy 可作上層輔助。
- **獨特特徵**：Akshat 對把 sandbox-level permission 完全交給 LLM 表示 skeptical。
- **影子證據**：訪談直接把 data exfiltration 作為需要 hard boundary 的理由。
- **連結**：↔ [[D2.2]], [[D4.2]] ⟨G2⟩

### D7.1：Managed Agents vs Specialized Sandboxes
- **操作手法**：managed agent 適合快速開始；production-grade agent 若需要 persistent files、snapshot/restore、network control、GPU、specialized compute，就往 dedicated sandbox provider 下沉。
- **獨特特徵**：Modal 對 harness 層保持相對中立：harness 可以在 managed agent 外面呼叫 sandbox，也可以直接跑在 sandbox 內。
- **影子證據**：Ramp 被訪談當作例子；外部-facing accounting agent 需要更細緻的 runtime control。
- **連結**：↔ [[D6.1]] ⟨S5⟩

### D8.1：Modal Bench as Agent Product Feedback
- **操作手法**：建立 benchmark 觀察 agents 使用 Modal 時在哪些任務失敗，特別是 observability / logs / debugging；對 recurring failure 新增 skill 或 product surface。
- **獨特特徵**：agent hallucinated features 被視為 product research signal：如果大量 agent 都「想要」某個 CLI operation，可能應該真的提供。
- **影子證據**：訪談提到 Modal Bench、Modal skill，並描述把原本 UI-only logs/metrics 移到 CLI 讓 agents 可存取。
- **連結**：↔ [[D8.2]] ⟨S4⟩

### D8.2：Python / TypeScript as Current Agent SDK Split
- **操作手法**：ML/inference/training 仍大量使用 Python；agent workloads 因不一定直接碰 ML，TypeScript SDK 使用比例上升；runtime 本身以 Rust 實作且 language-neutral。
- **獨特特徵**：agent-native infra 不等於 Python-only infra。
- **影子證據**：Modal 也有 Go SDK；Akshat 判斷短期主要仍是 Python + TypeScript。
- **連結**：↔ [[D8.1]] ⟨P4⟩

### D9.1：Runtime Sandboxes vs Build-Time Sandboxes
- **操作手法**：CI/build sandbox 重點是 dependency/build preparation；agent runtime sandbox 更重視 image configuration、persistent storage、networking、interactive lifecycle。
- **獨特特徵**：Gitpod/Ona 類 build environment 與 agent runtime 的核心 primitive 相近，但 timing / market / configuration surface 不同。
- **影子證據**：訪談將 CI 中 artifact/dependency preparation 的浪費與 memory snapshot/restore potential 連在一起。
- **連結**：↔ [[D2.1]], [[D10.1]] ⟨S6⟩

### D10.1：AI Expands Infra Demand into Biotech, Robotics, Video
- **操作手法**：同一 elastic compute primitive 支援 computational biology、drug discovery、robotics、audio/video model inference 與 agentic media production。
- **獨特特徵**：Modal 明確不想只服務 LLM inference market。
- **影子證據**：訪談提及 Chai Discovery 類 computational-bio workloads、robotics active deployments、Suno custom architecture inference，以及 video agent + FFmpeg/Adobe 類 workflow。
- **連結**：↔ [[D3.2]] ⟨S5⟩

### S1：Build Primitive Before Market Category
- **策略邏輯**：優先解決 stable workload invariant：burstiness、isolation、programmatic provisioning、fast feedback；不要只追當下熱門 Agent wrapper。
- **生態位對照 (Ecological Context)**：
  - 主角表現：Modal 在 agent boom 前已有 serverless runtime、GPU、sandbox primitives。
  - **環境/競對參照**：只在需求爆發後才包裝 generic VM 的平台，通常缺少底層 scheduling / image / network control。
- **反面教材 (Pre-mortem)**：primitive 太早且沒有 model/user 能消費，可能沉寂數年；需要保留 technical option value 同時控制 burn。
- **理論基礎**：← [[D1.1]], [[D1.2]], [[D2.1]]
- **實踐路徑**：→ [[P1]]
- **支撐框架**：← [[R1]]

### S2：Open Source the Engine, Monetize the System
- **策略邏輯**：把 DeFlash / SGLang improvements upstream，平台 moat 放在 elasticity、production serving、capacity、expertise、control plane，而不是把 optimization 藏起來。
- **生態位對照 (Ecological Context)**：
  - 主角表現：open-source inference contributions + managed elastic system。
  - **環境/競對參照**：raw GPU vendor 價格透明、switching cost 低；pure proprietary inference engine 又會面臨 open-source catch-up。
- **反面教材 (Pre-mortem)**：開源技術卻沒有可量化的 operations advantage，最後只替 commodity layer 提升品質。
- **理論基礎**：← [[D3.1]], [[D3.2]]
- **實踐路徑**：→ [[P2]]
- **支撐框架**：← [[T2]]

### S3：Compute Strategy Is Product Strategy
- **策略邏輯**：capacity forecast、reservation duration、GPU substitution、region placement 直接決定能不能承諾 latency、burst、price 與 availability。
- **生態位對照 (Ecological Context)**：
  - 主角表現：17-cloud pool + compute strategy team。
  - **環境/競對參照**：single-cloud startup 容易被某 GPU/region shortage 綁死。
- **反面教材 (Pre-mortem)**：只追最低 on-demand GPU price，忽略 burst availability、egress、reliability、support、tail latency。
- **理論基礎**：← [[D4.1]], [[D5.1]]
- **實踐路徑**：→ [[P3]]
- **支撐框架**：← [[T2]], [[G3]]

### S4：Treat Agent Failures as Interface Telemetry
- **策略邏輯**：agents 反覆失敗、hallucinate command 或找不到 logs，不只是一個 model bug；它暴露 product surface 對 machine operator 不友善。
- **生態位對照 (Ecological Context)**：
  - 主角表現：Modal Bench → identify failures → add skill/CLI/product surface。
  - **環境/競對參照**：只為 human 寫 docs/dashboard 的 infra 會讓 agent 必須猜 hidden state。
- **反面教材 (Pre-mortem)**：把所有 agent failure 都用 prompt patch 解，形成 prompt debt，卻不改真正的 interface bug。
- **理論基礎**：← [[D8.1]]
- **實踐路徑**：→ [[P4]]
- **支撐框架**：← [[G4]]

### S5：Own Specialized Runtime, Stay Harness-Neutral
- **策略邏輯**：不要與所有 managed-agent harness 正面競爭；提供其 production 化必須依賴的 sandbox/network/storage/GPU layer。
- **生態位對照 (Ecological Context)**：
  - 主角表現：managed agent 可呼叫 Modal sandbox；custom harness 也可直接跑在 Modal。
  - **環境/競對參照**：foundation labs 往 managed agent 上移，specialized infra 往 runtime control 下沉。
- **反面教材 (Pre-mortem)**：過早把 infra 綁單一 harness，model/harness 市場變化時失去 neutrality。
- **理論基礎**：← [[D7.1]], [[D10.1]]
- **實踐路徑**：→ [[P5]]
- **支撐框架**：← [[G2]]

### S6：CI Is Another Bursty Agent Workload
- **策略邏輯**：coding agents 增加後，CI execution volume 上升；snapshot/restore、dependency caching、on-demand compute 可直接降低 loop latency。
- **生態位對照 (Ecological Context)**：
  - 主角表現：將 runtime primitive 延伸到 build/test loops。
  - **環境/競對參照**：傳統 CI 大量時間浪費在環境 preparation，而 agent 會把這些等待倍增。
- **反面教材 (Pre-mortem)**：只增加 parallel runners，沒有減少 repeated setup cost。
- **理論基礎**：← [[D9.1]]
- **實踐路徑**：→ [[P6]]
- **支撐框架**：← [[T3]]

### P1：Agent Sandbox Loop Harness
- **場景 (Scenario)**：讓 coding/research agent 在隔離環境反覆 execute → inspect → patch。
- **價值 (Value)**：把 text-only reasoning 變成 evidence-producing loop。
- **漏洞利用 (Exploit/How)**：
  1. 每個 task 建 immutable base image digest。
  2. 每次 run 建 ephemeral sandbox ID、resource quota、network policy。
  3. Agent 只透過 typed CLI/API 操作 files/processes/logs/artifacts。
  4. 每輪保存 command、exit code、stdout/stderr digest、artifact diff。
  5. 失敗可 snapshot/restore；成功輸出 signed receipt。
  6. Run 結束強制 destroy sandbox，驗證 cleanup proof。
- **工具集 (Toolset)**：container/microVM sandbox、snapshot store、policy engine、CLI schema、trace/event log。
- **影子技巧**：benchmark 不只評 task success，也評 agent 是否能自行使用 observability 找到 failure cause。
- **連結**：← [[S1]], [[S4]]

### P2：Inference Delta Benchmark
- **場景 (Scenario)**：比較 raw vLLM/SGLang GPU deployment 與 managed elastic endpoint 的真實差異。
- **價值 (Value)**：避免只看 tokens/sec 做錯平台決策。
- **漏洞利用 (Exploit/How)**：
  1. 固定 model weights、precision、prompt distribution。
  2. 重放 production burst trace，而非 constant QPS synthetic load。
  3. 同時計算 TTFT、tokens/sec、p50/p95/p99、cold start、idle cost、failure/retry、operator hours。
  4. 加入 speculative decoding on/off，記錄 accept length 與 effective cost/token。
  5. 加入 scale-to-zero 與 sudden burst test。
  6. 用 cost-per-successful-request 排名，不只 GPU-hour。
- **工具集 (Toolset)**：load generator、OpenTelemetry、GPU metrics、trace replay、cost model。
- **影子技巧**：把 tail latency 與 request-delivery semantics 列為 hard gate；平均 latency 很容易掩蓋 production glitch。
- **連結**：← [[S2]]

### P3：Multi-Cloud Capacity Optimizer
- **場景 (Scenario)**：管理跨 provider / region / GPU type 的 AI compute supply。
- **價值 (Value)**：降低 shortage、reservation mismatch 與 burst failure。
- **漏洞利用 (Exploit/How)**：
  1. 建 capacity ledger：provider、region、GPU、reserved/on-demand、expiry、effective price。
  2. 建 demand forecast：base、burst、training window、RL rollout、batch slack。
  3. 對 GPU type 建 substitution matrix 與 performance/cost ratio。
  4. 對 1-year / 3-year reservation 做 scenario stress test。
  5. Routing 以 SLO + availability + total cost，而非 sticker price 排序。
  6. 每週把 forecast error 回饋 reservation policy。
- **工具集 (Toolset)**：capacity DB、forecasting、scheduler、FinOps dashboard、SLO policy engine。
- **影子技巧**：把 airline fuel hedging 當 cross-domain analogy：compute reservation 是供應鏈金融，不只是 DevOps。
- **連結**：← [[S3]]

### P4：Agent Experience Benchmark Compiler
- **場景 (Scenario)**：用 agents 實際操作 infra，找出 machine-interface gaps。
- **價值 (Value)**：把 hallucinated commands、debug dead ends 轉成 product roadmap。
- **漏洞利用 (Exploit/How)**：
  1. 定義 task pool：deploy service、inspect logs、fix crash、attach storage、network services、rollback。
  2. 保留 no-skill baseline 與 skill-assisted arm。
  3. 記錄每次 nonexistent command、doc search、UI dependency、manual intervention。
  4. 對 repeated failure 分類：missing primitive、poor naming、poor docs、missing observability、model gap。
  5. 只有 missing primitive / interface friction 才進 product backlog；model gap 進 skill/eval backlog。
  6. 新 CLI surface 上線後跑 paired regression。
- **工具集 (Toolset)**：Modal Bench-like harness、trajectory capture、task fixtures、CLI telemetry、paired eval。
- **影子技巧**：Agent hallucination 有時是「counterfactual UX research」：它會生成自己期待存在的 interface。
- **連結**：← [[S4]]

### P5：Harness-Neutral Sandbox Contract
- **場景 (Scenario)**：同一 sandbox layer 同時服務 managed agents、Claude/Codex/custom harness。
- **價值 (Value)**：降低上層 framework churn 對 runtime 的 lock-in。
- **漏洞利用 (Exploit/How)**：
  1. 定義 `create/exec/read/write/snapshot/restore/network/destroy` 最小 API。
  2. Identity 與 policy 不依賴單一 harness token schema。
  3. Artifacts/receipts 使用 vendor-neutral format。
  4. Harness-specific adapter 不得直接控制 host network/root privilege。
  5. 每個 adapter 共享同一 conformance + security suite。
- **工具集 (Toolset)**：OpenAPI/JSON Schema、capability tokens、policy-as-code、sandbox SDKs。
- **影子技巧**：把 runtime receipt 當跨 harness 的共同 truth object。
- **連結**：← [[S5]]

### P6：Snapshot-First Agent CI
- **場景 (Scenario)**：大量 coding agents 反覆跑 test/build。
- **價值 (Value)**：壓縮 dependency preparation 與 environment setup latency。
- **漏洞利用 (Exploit/How)**：
  1. 對 lockfile + toolchain + base image 建 environment digest。
  2. Cache 完成 dependency install 的 memory/filesystem snapshot。
  3. 每個 PR/task 從 snapshot fork ephemeral runner。
  4. Test artifacts 與 logs 回寫 trace；runner 立即銷毀。
  5. Snapshot 只在 digest 命中時 reuse；dependency change 強制 invalidation。
- **工具集 (Toolset)**：snapshot/restore runtime、CAS cache、CI scheduler、artifact store。
- **影子技巧**：量測 `time-to-first-test`，它比 total CI duration 更直接影響 agent iteration velocity。
- **連結**：← [[S6]]

### T1：Developer Cloud vs Agent Cloud
- **用途**：識別 AX 需要新增的 interface invariants。
- **結構內容**：
  | 維度 | Developer Cloud | Agent Cloud |
  |---|---|---|
  | 操作入口 | UI + docs + YAML | typed CLI/API/tools |
  | Context | 人腦補齊 | machine-readable state |
  | Debug | dashboard inspection | queryable logs + error schema |
  | Provision | minutes / manual | seconds / programmatic |
  | Scale | steady services | bursty executions / RL rollouts |
  | Security | human IAM flows | ephemeral identity + hard sandbox policy |
  | State | long-lived server | snapshot/restore + ephemeral workspace |
  | Success | service up | task outcome + receipt |
- **連結**：→ [[S1]], [[S4]], [[P1]], [[P4]]

### T2：Inference Platform Value Matrix
- **用途**：比較 raw engine 與 managed system 的真正差異。
- **結構內容**：
  | 維度 | Raw GPU + Engine | Elastic Agent Cloud |
  |---|---|---|
  | Engine | vLLM/SGLang | 同樣可使用 open-source engine |
  | Optimization | 自行調 | DeFlash/Auto Endpoint 等 prebuilt optimization |
  | Scale-to-zero | 自建 | native |
  | Bursty scale | scheduler 自建 | platform capacity pool |
  | Tail latency | 自管 | platform SLO/ops |
  | Multi-cloud | 自建 | 17-cloud pool strategy |
  | Custom code | 完全自由 | code transparency + eject path |
  | Expertise | internal ops | specialist inference/FDE team |
- **連結**：→ [[S2]], [[S3]], [[P2]], [[P3]]

### T3：Agent Workload Shape Matrix
- **用途**：按 workload 選 primitive。
- **結構內容**：
  | Workload | 核心形狀 | 關鍵 Primitive |
  |---|---|---|
  | Coding Agent | interactive burst + filesystem | sandbox、snapshot、CLI observability |
  | RL Rollout | massive parallel | 100K-class sandbox orchestration、quota、cleanup |
  | Inference | bursty latency-sensitive | elastic GPU、spec decode、tail latency |
  | Multi-node training | memory/network heavy | RDMA、private networking、scheduler |
  | CI | repeated setup + burst | snapshot cache、ephemeral runners |
  | Robotics/Bio | custom models/workflows | custom images、GPU、persistent artifacts |
  | Video Agent | GPU + external tooling | sandbox、media tools、stateful pipeline |
- **連結**：→ [[S1]], [[S6]], [[G3]]

### R1：Agent Cloud MVP → Production Roadmap
- **總體目標**：把「agent 可以執行 code」升級成可大規模、安全、可觀測、可經濟運行的 execution plane。
- **階段劃分**：
  - **Phase 1 Primitive**：typed sandbox API、immutable image、exec/read/write/artifact/destroy。
  - **Phase 2 Feedback**：CLI-first logs/metrics/errors、trace IDs、agent benchmark。
  - **Phase 3 Elasticity**：snapshot/restore、scale-to-zero、burst scheduling、GPU allocation。
  - **Phase 4 Security**：network allowlist、ephemeral identity、hard guardrails、cleanup proof。
  - **Phase 5 Supercloud**：multi-provider capacity ledger、reservation optimizer、region/GPU substitution。
  - **Phase 6 Research Runtime**：100K-class rollout orchestration、RDMA multi-node、auto-research sweeps。
- **系統風險 (Glitches)**：orphan sandboxes、capacity mismatch、hidden UI-only state、network over-permission、GPU idle cost、non-reproducible snapshots、agent command hallucination。
- **連結**：→ [[G1]], [[G2]], [[G3]], [[G4]]

### G1：Agent-Native Interface Protocol
- **核心協議 (Protocol)**：任何 production-critical infra state 都必須能被 agent 透過 stable machine interface 查詢與操作。
- **具體條款/機制**：
  - UI-only state 禁止作唯一 control surface。
  - CLI/API output 必須 structured + stable IDs。
  - Error 必須有 typed code、resource ID、suggested safe next action。
  - 每個 mutating command 支援 idempotency key。
- **決策流程**：Intent → Inspect State → Plan → Execute → Verify → Trace → Continue/Rollback。
- **違規後果**：agent 需要猜測 hidden state 的流程標記為 AX bug。
- **連結**：← [[R1]], → [[S4]]

### G2：Sandbox Hard-Boundary Protocol
- **核心協議 (Protocol)**：Sandbox security 由 deterministic policy enforce；LLM policy 只能加嚴，不能擴權。
- **具體條款/機制**：
  - deny-by-default network。
  - scoped ephemeral credentials。
  - CPU/GPU/memory/time quotas。
  - persistent storage 顯式 mount。
  - snapshot/restore 綁 digest。
  - destroy + cleanup attestation 必須成功。
- **決策流程**：Create → Bind Policy → Execute → Monitor → Verify → Destroy → Attest。
- **違規後果**：cleanup、policy 或 identity mismatch 立即 quarantine；不得重用 workspace。
- **連結**：← [[R1]], → [[S5]], [[P1]], [[P5]]

### G3：Massive Rollout Safety & Economics Protocol
- **核心協議 (Protocol)**：Parallelism 必須與 quota、budget、cleanup、denominator evidence 同步擴張。
- **具體條款/機制**：
  - 全局 / project / run concurrency caps。
  - cost budget 與 kill threshold。
  - sandbox TTL。
  - failure denominator 全保留。
  - cleanup success rate 作 hard SLO。
  - 100K-class rollout 先做 geometric ramp：10→100→1K→10K→100K。
- **決策流程**：Plan → Budget → Ramp → Observe → Expand/Halt → Cleanup → Reconcile Cost/Evidence。
- **違規後果**：orphan rate、cost overshoot、policy failure 超 threshold 立即停止擴容。
- **連結**：← [[R1]], → [[S3]], [[P3]]

### G4：Agent Interface Admission Policy
- **核心協議 (Protocol)**：產品 surface 的 AX 改動必須由 benchmark trajectory 驗證，而非只靠 human intuition。
- **具體條款/機制**：
  - 每個 new CLI command 綁 agent task/eval。
  - no-skill baseline 保留。
  - hallucinated command frequency 追蹤。
  - UI-only dependency 必須有 migration backlog。
  - Skill patch 與 product patch 分開衡量。
- **決策流程**：Failure Cluster → Root Classification → Skill/Product Candidate → Paired Eval → Admit。
- **違規後果**：只改善 demo prompt、未改善 repeated task success 的 change 不算 AX improvement。
- **連結**：← [[R1]], → [[S4]], [[P4]]

### E1：Agents Turn Infrastructure into an API Consumer Problem
- **法則內容**：當 infra 的操作者從 human 變 agent，最重要的 UX 是 deterministic machine interface，而不是更漂亮的 dashboard。
- **推論/啟示**：CLI/API/error schema/receipts 將成為 cloud product 的核心 UX layer。
- **支撐證據**：← [[C1]], [[C5]], [[D8.1]], [[G1]]

### E2：AI Infrastructure Is a Memory-Movement and Scheduling Problem
- **法則內容**：在大規模 inference/training/RL 中，性能瓶頸不只在 GPU FLOPS，而在 KV/weights/state movement、network、placement、burst scheduling。
- **推論/啟示**：RDMA、snapshotting、capacity routing、speculative decoding 都是模型體驗的一部分。
- **支撐證據**：← [[C3]], [[D3.1]], [[D4.3]], [[D5.1]]

### E3：Primitive Timing Can Precede Market Timing
- **法則內容**：真正有長期 option value 的 infra primitive 可能在市場知道它名字以前就存在。
- **推論/啟示**：技術 roadmap 應圍繞 workload invariant，而不是只跟當期 product category。
- **支撐證據**：← [[D1.2]], [[D2.1]], [[S1]]

### E4：Probabilistic Intelligence Still Needs Deterministic Boundaries
- **法則內容**：Agent 越 autonomous，越不能把 sandbox/network/credential safety 完全交給同一 probabilistic reasoning loop。
- **推論/啟示**：AI OS 的 kernel 應包含 hard policy，LLM 只能在 kernel 授權範圍內做 adaptive decision。
- **支撐證據**：← [[N4]], [[D6.1]], [[G2]]

### E5：Observability That Agents Cannot Query Is Dead State
- **法則內容**：若 logs/metrics/error context 只能 human 從 UI 讀取，agent runtime 就缺少 self-correction 所需 feedback channel。
- **推論/啟示**：Agent-native observability 必須是 tool-callable、structured、stable、actionable。
- **支撐證據**：← [[C5]], [[D8.1]], [[P4]], [[G1]]
