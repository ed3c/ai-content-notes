# Stacked PR Index｜目前分支圖與分子化末端實作

> Canonical branch/PR dependency index for issue #17 and the follow-up decomposition of the old monolithic runtime draft. GitHub branch/PR state is authority; this document must be updated when bases or heads change.

## A. Active documentation stack

```text
main
└── PR #18  agent/docs-card-catalog
    └── PR #19  agent/docs-agent-routing
        └── PR #20  agent/docs-state-machine
            └── PR #21  agent/docs-git-town-governance
```

### Stack task packets

| Stack | Branch | PR base | Scope / path lease | Required eval | Status |
|---:|---|---|---|---|---|
| 1 | `agent/docs-card-catalog` | `main` | `evals/semantic-yield/README.md`, `docs/SEMANTIC_YIELD_INTEGRATION_STATUS.md`, `INDEX.md` | link/read-back review | Draft PR #18 |
| 2 | `agent/docs-agent-routing` | Stack 1 | `AGENTS.md`, `CLAUDE.md`, `INTEGRATION_REQUIREMENTS.md` | exact read order and status consistency | Draft PR #19 |
| 3 | `agent/docs-state-machine` | Stack 2 | `README.md`, `tests/test_repository_navigation.py` | full pytest + navigation contract | Draft PR #20 |
| 4 | `agent/docs-git-town-governance` | Stack 3 | `docs/git/**`, convergence updates to README/Agent docs/test | full pytest + stack/profile checks | Draft PR #21 |

Merge order is strictly bottom-up by dependency:

```text
#18 -> retarget #19 to main -> merge #19
    -> retarget #20 to main -> merge #20
    -> retarget #21 to main -> merge #21
```

A trusted operator owns retargeting and merge. Workers do not invoke `git town ship` or automatic merge.

## B. Evidence lanes for this stack

| Lane | Current result |
|---|---|
| task decomposition | `PASS` — issue #17 contains goals, non-goals, parents, path leases, evals and rollback subjects |
| remote branch hierarchy | `PASS` — explicit GitHub parent branches exist |
| draft PR publication | `PASS` — PR #18/#19/#20/#21 exist with the recorded bases |
| live Git Town admission | `ABSENT` |
| live `git town sync` | `NOT_EXERCISED` |
| linked worktree/lease canary | `NOT_EXERCISED` |
| exact-HEAD local verification receipt | `NOT_EXERCISED` as a Git Town Worker lane; GitHub CI remains separate |
| publication gate | `NOT_IMPLEMENTED` |
| merge / promotion | `HUMAN ADMIT` |

## C. Historical implementation trace

| PR | State | Role |
|---:|---|---|
| #9 | merged | immutable v7.1 prompt lock, A/B harness and system audit |
| #11/#12 | merged | transcript acquisition and retained first v7.1 batch under `evals/live/` |
| #15 | merged | current 10-card Semantic Yield output |
| #16 | merged | deterministic artifact validator and partial QG evidence |
| #13 | open draft | monolithic grounded runtime draft; not current `main` authority |

PR #13 contains useful runtime work but mixes contracts, graph construction, projections, planning and evaluation in one 37-file/44-commit review surface. It should not be merged wholesale without decomposition and replay against current `main`.

## D. Molecular runtime leaf stack｜PR #13 的分子化末端實作

The following leaves are **planned**, not yet published PRs. Each leaf requires a fresh task packet and exact path lease. Independent leaves should become siblings; serial edges exist only where artifacts are consumed by the child.

```text
main
└── runtime/01-source-pack-and-run-receipt
    └── runtime/02-relation-graph-and-thesis-ranking
        ├── runtime/03a-knowledge-view-projections
        ├── runtime/03b-source-driven-batch-planner
        └── runtime/03c-semantic-yield-evaluator
            └── runtime/04-convergence-and-cvrngaqzq3y-replay

main
└── runtime/visual-01-rights-gated-frame-contracts
    └── runtime/visual-02-frame-extractor-and-annotation
        └── runtime/04-convergence-and-cvrngaqzq3y-replay

main
└── runtime/provider-01-model-run-adapter
    └── runtime/provider-02-raw-response-receipt
        └── runtime/04-convergence-and-cvrngaqzq3y-replay
```

### Planned leaves

| Leaf | Primary responsibility | Proposed path lease | Dependency | Completion evidence |
|---|---|---|---|---|
| `runtime/01-source-pack-and-run-receipt` | multimodal source-pack and provider-neutral receipt schemas/builders | `schemas/*source-pack*`, `schemas/model-run-receipt*`, bounded builder/tests | `main` | schema tests + deterministic digest replay |
| `runtime/02-relation-graph-and-thesis-ranking` | evidence-bound relation IR and central-thesis selector | relation graph schema/tool/tests | leaf 01 | supported edges require anchors; ranking idempotency |
| `runtime/03a-knowledge-view-projections` | causal flow, equation, timeline, state-plane and comparison projections | projection schemas/renderers/tests | leaf 02 | UNKNOWN-safe cells + exact relation provenance |
| `runtime/03b-source-driven-batch-planner` | replace fixed series quota with decision-value coverage | batch planner/schema/tests | leaf 02 | T/visual/action coverage mutation tests |
| `runtime/03c-semantic-yield-evaluator` | HG-01..HG-06 deterministic evaluator | evaluator/schema/fixtures/tests | leaf 02 | false-positive and omission controls |
| `runtime/visual-01-rights-gated-frame-contracts` | rights, timestamp, digest and visual locator contracts | visual schemas/docs/tests | `main` | unauthorized media fails closed |
| `runtime/visual-02-frame-extractor-and-annotation` | explicit frame extraction and reviewed bbox/OCR/topology annotations | visual tools/tests | visual 01 | real local-media canary; no URL downloader |
| `runtime/provider-01-model-run-adapter` | provider-neutral exact-model invocation boundary | provider adapter interfaces/tests | `main` | fake provider replay + secret-output guard |
| `runtime/provider-02-raw-response-receipt` | raw-response, sampling and compiled-output receipt | receipt builder/tests | provider 01 | exact digest and stale-subject rejection |
| `runtime/04-convergence-and-cvrngaqzq3y-replay` | assemble approved siblings, migrate fixtures and run 2×2 transcript/multimodal comparison | shared fixtures, README/index, CI convergence | approved leaf heads | full suite, no fixed-series golden, stable card IDs, read-back |

### Independent sibling policy

```text
03a / 03b / 03c
  = sibling branches after relation graph contract stabilizes
  = disjoint path leases

visual stack and provider stack
  = independent roots from main
  = converge only in runtime/04
```

Do not create an artificial serial chain for unrelated writable paths.

## E. Traceability matrix

| Requirement | Current artifact |
|---|---|
| find current modified-flow cards | `evals/semantic-yield/README.md` |
| exact integration status | `docs/SEMANTIC_YIELD_INTEGRATION_STATUS.md` |
| Agent read order | `AGENTS.md`, `CLAUDE.md`, `INTEGRATION_REQUIREMENTS.md` |
| directory/state-machine/data flow | root `README.md` |
| current card identities | `evals/semantic-yield/CvRngaQZQ3Y/card-manifest.json` |
| deterministic validation | `semantic-validator-report.json`, validator tool/tests |
| Git Town repo profile | `docs/git/REPO_PROFILE.md` |
| exact admission blocker | `docs/git/GIT_TOWN_ADMISSION.md` |
| Worker task/lease contract | `docs/git/WORKER_PROTOCOL.md` |
| active/future stack graph | this file |
| work owner | issue #17 |

## F. Update rules

Update this file whenever:

- a PR number is assigned;
- a PR base/head changes;
- a stack item is merged, closed or superseded;
- a planned leaf becomes an issue/branch/PR;
- a path lease changes;
- Git Town admission or a live evidence lane changes state.

Do not report a planned leaf as implemented, a draft as merged, a GitHub branch graph as live Git Town sync, or a green check as Human Admit.
