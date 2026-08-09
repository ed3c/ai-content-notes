---
id: <source>:<stable-content-id>
title: <source title>
source: <source name>
source_url: <canonical URL>
published_at: 'YYYY-MM-DD'
monetization_score: 0
category: <technical-category>
language: zh-TW
note_format: zettelkasten-v6.6-cyberpunk
storage: private-github-markdown
repository: ed3c/ai-content-notes
path: notes/<technical-category>/<yyyy-mm-dd>-<slug>.md
citation_mapping: pending
library_mapping: pending
---

<!--
Validation boundary:
- Use complete source text, article body, or transcript.
- Output cards only. Remove this comment in a real note.
- One Case, One Card. Do not summarize D/P/N cards.
- Preserve exact dates, figures, identifiers, and short source quotations.
-->

### N1：<Narrative title>
- **核心衝突**：<core contradiction>
- **關鍵人物/實體**：<actor A> vs <actor B/environment>
- **衝擊力錨點 (Impact Anchors)**：
  - <exact evidence 1>
  - <exact evidence 2>
- **劇情轉折**：<beginning → development → turn → consequence>
- **生態背景**：<industry baseline>
- **連結**：→ [[D1]], → [[G1]]

### Q1：<Question>
- **核心疑問 (The Doubt)**：<system doubt>
- **現狀反差 (Reality Gap)**：<ideal vs evidence>
- **思維實驗 (Simulation)**：<counterfactual>
- **連結**：← [[D1]], → [[S1]]

### C1：<Concept>
- **定義**：<definition>
- **演化**：<past vs present>
- **本質**：<underlying mechanism>
- **結構特徵**：<components>
- **連結**：→ [[D1]], → [[E1]]

### D1：<Single case or entity>
- **操作手法**：<specific operation>
- **獨特特徵**：<difference>
- **影子證據**：<exact figure/date/identifier/short quotation>
- **連結**：↔ [[D2]] ⟨S1⟩

### S1：<Strategy>
- **策略邏輯**：<mechanism>
- **生態位對照 (Ecological Context)**：
  - 主角表現：<behavior>
  - **環境/競對參照**：<baseline>
- **反面教材 (Pre-mortem)**：<failure Bug>
- **理論基礎**：← [[D1]]
- **實踐路徑**：→ [[P1]]
- **支撐框架**：← [[T1]], [[R1]], [[G1]]

### P1：<Executable practice>
- **場景 (Scenario)**：<What>
- **價值 (Value)**：<Why>
- **漏洞利用 (Exploit/How)**：
  1. <command/step/parameter>
  2. <command/step/parameter>
- **工具集 (Toolset)**：
  - <tool/resource>
- **輸入與前置條件**：<required state>
- **輸出與斷言**：<observable result>
- **Abort Boundary**：<stop condition>
- **影子技巧**：<advanced technique>
- **連結**：← [[S1]]

### T1：<Decision table>
- **用途**：<decision problem>
- **結構內容**：
  | Dimension | Entity A | Entity B |
  |---|---|---|
  | Evidence | ... | ... |
- **決策規則**：<how result changes action>
- **連結**：→ [[S1]], [[P1]]

### R1：<Roadmap>
- **總體目標**：<observable target>
- **階段劃分**：
  - **Phase 1 <name>**：<action and exit criteria>
  - **Phase 2 <name>**：<action and exit criteria>
- **系統風險 (Glitches)**：<failure and rollback>
- **連結**：→ [[G1]]

### G1：<Governance model>
- **核心協議 (Protocol)**：<governing principle>
- **具體條款/機制**：
  - <clause 1>：<content>
  - <clause 2>：<content>
- **決策流程**：<authority, gate, evidence>
- **違規後果**：<abort/quarantine/rollback>
- **連結**：← [[R1]], → [[S1]]

### E1：<Essential law>
- **法則內容**：<one-sentence law>
- **推論/啟示**：<implication>
- **支撐證據**：← [[D1]], [[G1]]
- **Assertion Candidate**：<machine-checkable invariant>
