# Semantic Yield Card Catalog｜新流程卡片總索引

> This file is the canonical navigation surface for card batches produced by the prompt-external Semantic Yield flow. Existence and state remain authoritative only when the linked manifest, files, Git blobs and validator artifacts can be read back.
>
> 本檔是修改後 Semantic Yield 流程的卡片批次總索引。真正的存在與狀態仍以可回讀的 manifest、檔案、Git blob 與 validator artifact 為準。

## Current coverage｜目前覆蓋範圍

As of 2026-08-14, **one content item** has run the modified Semantic Yield flow on `main`.

| Content ID | Source dependency | Card directory | Cards | Validator | State |
|---|---|---|---:|---|---|
| `CvRngaQZQ3Y` | `youtube-video:CvRngaQZQ3Y` | [`CvRngaQZQ3Y/cards/`](CvRngaQZQ3Y/cards/) | 10 | `PASS_WITH_DEFERRED_VISUAL_AND_PARTIAL_QG` | `CONTINUE` |

No other content directory under `evals/semantic-yield/` currently exists. A new directory must not be inferred from an issue, branch, expected path or prompt output.

## Cards that ran the modified flow｜已跑過新流程的卡片

The following ten cards were selected by the source-driven batch planner and validated by the deterministic host validator:

1. [`N-autonomy-trace-mining`](CvRngaQZQ3Y/cards/N-autonomy-trace-mining.md) — autonomy → lower static predictability → runtime evidence → Trace Mining.
2. [`C-model-harness-task-fit`](CvRngaQZQ3Y/cards/C-model-harness-task-fit.md) — `fit(Model, Harness, Task / Distribution)`.
3. [`S-harness-finetune-harness`](CvRngaQZQ3Y/cards/S-harness-finetune-harness.md) — Harness → measured ceiling → model update → re-Harness.
4. [`T-trace-judge-comparison`](CvRngaQZQ3Y/cards/T-trace-judge-comparison.md) — UNKNOWN-safe Frontier/Open-model comparison.
5. [`P-trace-driven-improvement-cycle`](CvRngaQZQ3Y/cards/P-trace-driven-improvement-cycle.md) — replayable and rollback-capable improvement procedure.
6. [`D-trace-scale-bottleneck`](CvRngaQZQ3Y/cards/D-trace-scale-bottleneck.md) — trace volume, input cost and context-window bottleneck.
7. [`D-four-stage-trace-loop`](CvRngaQZQ3Y/cards/D-four-stage-trace-loop.md) — Ship → Collect → Mine → Experiment.
8. [`C-continual-learning-state-planes`](CvRngaQZQ3Y/cards/C-continual-learning-state-planes.md) — Data, Harness and Memory planes.
9. [`V-semantic-yield-replay`](CvRngaQZQ3Y/cards/V-semantic-yield-replay.md) — host replay verification; verdict remains `PARTIAL`.
10. [`K-visual-identifier-evidence-gap`](CvRngaQZQ3Y/cards/K-visual-identifier-evidence-gap.md) — missing authorized slide/frame and canonical identifier evidence.

Canonical order and Git blob bindings are stored in [`CvRngaQZQ3Y/card-manifest.json`](CvRngaQZQ3Y/card-manifest.json).

## Do not confuse these outputs｜不要混淆兩套輸出

```text
evals/live/CvRngaQZQ3Y/
  = first transcript-only v7.1 evaluation batch
  = 12 cards materialized before the Semantic Yield regeneration
  = retained baseline/provenance artifact

evals/semantic-yield/CvRngaQZQ3Y/
  = modified host-side Semantic Yield flow
  = central-thesis ranking + projections + source-driven batch
  = 10 current cards + deterministic validator
```

The `evals/live/` batch did **not** run the complete modified Semantic Yield flow and must not be counted in the table above.

## Batch artifact contract｜每個新流程批次的檔案契約

```text
evals/semantic-yield/<content-id>/
├── README.md                         # human entry and card order
├── cards/                            # one stable-ID Markdown file per card
├── card-manifest.json                # prompt/source/card/blob bindings
├── knowledge-views.md                # host-side graph projections
├── semantic-validator-report.json    # deterministic validator evidence
├── semantic-yield.result.json        # HG/QG summary and blockers
└── run-state.md                      # CONTINUE | DONE | BLOCKED | FAILED
```

Optional multimodal artifacts may be added only when their rights, source dependency and digest contracts are explicit. Host-generated Mermaid/ASCII/table views are projections, not original-slide evidence.

## State meaning｜狀態語義

```text
CONTINUE
  persisted card batch exists, but one or more required evidence or QG lanes remain open

DONE
  allowed only when the v7.1 Completion Contract is satisfied and every required artifact is readable

BLOCKED
  a necessary source, right, registry, tool, permission or authority is unavailable

FAILED
  the input/state cannot be repaired within the declared self-repair boundary
```

The current `CvRngaQZQ3Y` batch remains `CONTINUE` because authorized visual evidence, human-reviewed identifiers, remaining QG evidence and a provider/model raw-run receipt are incomplete.

## Validator replay｜重播驗證

```bash
python tools/validate_semantic_yield_artifacts.py \
  --target evals/semantic-yield/CvRngaQZQ3Y \
  --output evals/semantic-yield/CvRngaQZQ3Y/semantic-validator-report.json \
  --created-at 2026-08-14T01:15:00Z \
  --check
```

The validator currently provides deterministic evidence for QG-07, QG-08, QG-10, QG-11, QG-12, QG-16, QG-18, QG-20, QG-21 and QG-23. Unlisted gates remain `NOT_RUN`; partial validation never authorizes `DONE`.
