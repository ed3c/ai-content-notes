### T-trace-judge-cost-comparison｜Trace judge：frontier 與 open model 的對照與未知欄位

- **核心命題**：來源宣稱在其法律 benchmark 上，較便宜的 open model 可大致匹配 Opus 的 trace judging 能力，成本低約一到兩個數量級；精確分數與價格未給出，必須維持 UNKNOWN。
- **為什麼重要**：這是決定 trace judging 要不要花 frontier token 的關鍵對照，但可引用的只有量級，不是數字。

- **Decision Use**：決定 trace judging 由哪一類模型承擔。
- **Comparison Contract**：同一個法律 benchmark、同一個 judging 任務，harness 經過調整。
- **Dimensions**：

| Dimension | Frontier judge (Opus) | Open cheaper model |
|---|---|---|
| Trace judging capability | reference point | roughly matched（來源用語） |
| Relative cost | baseline | 低約 1–2 個數量級（來源用語） |
| Exact benchmark score | UNKNOWN | UNKNOWN |
| Exact price per million tokens | UNKNOWN | UNKNOWN |
| Model identity and version | Opus（僅點名系列） | UNKNOWN |

- **Interpretation**：可用於方向性決策，不可用於精確成本模型。
- **Decision Threshold**：在精確分數補齊前，僅在可接受量級誤差的場景採用 open model。
- **證據與狀態**：SOURCE_STATEMENT · SUPPORTED · LOW
- **反證／限制**：若在相同 benchmark 與相同 harness 投入下，open model 無法接近 frontier judging，本對照即失效。
- **Typed Links**：ROOT ← [[S-harness-then-tune-then-harness]] · DEPENDS_ON → [[K-visual-and-identifier-gap]]

<!-- CARD_META
{
  "stable_id": "T-trace-judge-cost-comparison",
  "canonical_key": "T | trace-judging | compares | frontier-against-open-model | cost-and-capability | source-digest:304e9a05",
  "series": "T",
  "lifecycle": "ACTIVE",
  "revision": 1,
  "scope": "CvRngaQZQ3Y English auto-generated caption track retrieved 2026-08-14; user-directed evaluation only",
  "confidence_basis": "來源以合作對象與 benchmark 具體陳述，但僅給量級；LOW 反映精確值缺席。",
  "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
  "source_provenance": [
    "youtube:CvRngaQZQ3Y:youtube-transcript-api#timestamp:00:07:36.880..00:09:00.920",
    "sha256:304e9a058721298f7498906d2539fdabdac515f2304645d52824e6719bc5f9bf"
  ],
  "unresolved_links": []
}
-->
