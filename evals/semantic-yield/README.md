# Semantic Yield Card Catalog｜新流程卡片總索引

> This file is the canonical navigation surface for card batches produced by the prompt-external Semantic Yield flow. Existence and state remain authoritative only when the linked manifest, files, Git blobs and validator artifacts can be read back.
>
> 本檔是修改後 Semantic Yield 流程的卡片批次總索引。真正的存在與狀態仍以可回讀的 manifest、檔案、Git blob 與 validator artifact 為準。

## Current coverage｜目前覆蓋範圍

As of 2026-08-14, **one content item** has run the modified Semantic Yield flow on `main`, across **two batches**.

| Batch | Source dependency | Card directory | Cards | Gate result | State |
|---|---|---|---:|---|---|
| `CvRngaQZQ3Y` | `youtube-video:CvRngaQZQ3Y` | [`CvRngaQZQ3Y/cards/`](CvRngaQZQ3Y/cards/) | 10 | `PASS_WITH_DEFERRED_VISUAL_AND_PARTIAL_QG` | `CONTINUE` |
| `CvRngaQZQ3Y-v2` | `youtube-video:CvRngaQZQ3Y` | [`CvRngaQZQ3Y-v2/cards/`](CvRngaQZQ3Y-v2/cards/) | 9 | `HG-01..HG-06 PASS` | `CONTINUE` |

Both batches describe the same video. They are **not** interchangeable: they were compiled from two different acquisitions of the auto-caption track, with different normalized digests, so their stable IDs and canonical keys do not correspond. The v2 batch is the first whose subject is retained in-repo under `sources/CvRngaQZQ3Y/`, and therefore the first that can be replayed.

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

## The v2 batch｜第二次批次

Run locally on 2026-08-14 from a freshly acquired English auto-caption track.

```text
rights gate       evaluation-only  (AT-001, user-directed-evaluation)
retained subject  sources/CvRngaQZQ3Y/  bound by source-manifest.json
pack              sp-CvRngaQZQ3Y-auto-caption-v2
relation graph    18 nodes, 15 relations, 15 evidence anchors
selected thesis   traces-are-the-improvement-substrate  (0.6496)
projections       causal-dataflow, comparison-matrix, timeline, state-planes, equation
gates             HG-01..HG-06 PASS
registry          9 cards reconciled, 0 gaps
```

1. [`N-autonomy-shifts-evidence-to-traces`](CvRngaQZQ3Y-v2/cards/N-autonomy-shifts-evidence-to-traces.md) — determinism traded for autonomy moves the evidence surface onto traces.
2. [`C-fit-is-a-three-way-function`](CvRngaQZQ3Y-v2/cards/C-fit-is-a-three-way-function.md) — performance is the joint fit of model, harness and task.
3. [`C-dense-feedback-is-the-improvable-signal`](CvRngaQZQ3Y-v2/cards/C-dense-feedback-is-the-improvable-signal.md) — a pass/fail bit is not an improvable signal.
4. [`S-harness-then-tune-then-harness`](CvRngaQZQ3Y-v2/cards/S-harness-then-tune-then-harness.md) — order intervention by feedback latency.
5. [`P-four-step-trace-improvement-recipe`](CvRngaQZQ3Y-v2/cards/P-four-step-trace-improvement-recipe.md) — ship, collect, mine, experiment. `UNTESTED`.
6. [`T-trace-judge-cost-comparison`](CvRngaQZQ3Y-v2/cards/T-trace-judge-cost-comparison.md) — frontier vs open judge; exact figures stay `UNKNOWN`.
7. [`D-trace-reading-cost-bottleneck`](CvRngaQZQ3Y-v2/cards/D-trace-reading-cost-bottleneck.md) — reading cost and the context ceiling.
8. [`V-projection-replay-v2`](CvRngaQZQ3Y-v2/cards/V-projection-replay-v2.md) — replay verification; verdict `PARTIAL`.
9. [`K-visual-and-identifier-gap`](CvRngaQZQ3Y-v2/cards/K-visual-and-identifier-gap.md) — slides, chart values and product spelling unverifiable.

This batch is `evaluation-only`. It may not complete a note, raise claim evidence, or publish raw media, and `tools/rights_allowlist.py` returns exactly that decision for the video.

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
