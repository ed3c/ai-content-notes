# Stacked PR Index｜已合併分支圖與分子化末端實作

> Canonical PR dependency and runtime-leaf index for `ed3c/ai-content-notes`. GitHub state is authority. A planned leaf becomes implemented only after an issue/task packet, branch, exact path lease, tests, PR, trusted checks and Human Admit exist.

## A. Completed documentation/governance stack

```text
Merged PR #18  agent/docs-card-catalog
  -> Merged PR #19  agent/docs-agent-routing
  -> Merged PR #20  agent/docs-state-machine
  -> Merged PR #21  agent/docs-git-town-governance
  -> Merged PR #22  agent/docs-stack-finalize
```

| PR | Scope | Merge commit |
|---:|---|---|
| #18 | card catalog + integration-status SSOT | `bbf92a4106b720f5b50707029779984d6672951f` |
| #19 | Agent read order and state guard | `073fbdd2c1d09b71f22a30b7458aa0be06b932d6` |
| #20 | root directory/state/data-flow map + navigation test | `c10f8b4572546262c34f93712c54798fdc451830` |
| #21 | repo profile, admission blocker and Worker protocol | `a2bd35a615c6754c5be70494bef55b65216bda7c` |
| #22 | exact merged-stack convergence | `f67ccad478f30d6b17a4ebbf73aaab41f2f05dda` |

## B. Runtime Stack PR state

Issue [#23](https://github.com/ed3c/ai-content-notes/issues/23) owns the runtime decomposition.

```text
main
└── Merged PR #24  runtime/01-source-pack-and-run-receipt
    └── runtime/02-relation-graph-and-thesis-ranking  [NEXT / PLANNED]
        ├── runtime/03a-knowledge-view-projections    [PLANNED]
        ├── runtime/03b-source-driven-batch-planner   [PLANNED]
        └── runtime/03c-semantic-yield-evaluator      [PLANNED]
            └── runtime/04-convergence-and-cvrngaqzq3y-replay [PLANNED]

main
└── runtime/visual-01-rights-gated-frame-contracts   [PLANNED]
    └── runtime/visual-02-frame-extractor-and-annotation
        └── runtime/04-convergence-and-cvrngaqzq3y-replay

main
└── runtime/provider-01-model-run-adapter             [PLANNED]
    └── runtime/provider-02-raw-response-receipt
        └── runtime/04-convergence-and-cvrngaqzq3y-replay
```

### Implemented Leaf 01

| Field | Value |
|---|---|
| issue | #23 |
| PR | #24 |
| branch | `runtime/01-source-pack-and-run-receipt` |
| base | `main` |
| merge commit | `d39d4791eed8c0cd3b1227ef8aeafd9685736e91` |
| changed paths | four schemas, two builders, focused tests, `docs/runtime/README.md` |
| local evidence | Python compilation, four schema checks, 10 focused tests |
| GitHub evidence | Ruff + Canonical Contracts on Python 3.11 and 3.13 |
| boundary | identity receipts only; no provider invocation, cards, relation graph or visual extraction |

Leaf 01 materializes:

```text
multimodal-source-pack-descriptor@1
  -> build-multimodal-source-pack@1
  -> multimodal-source-pack@1

model-run-receipt-descriptor@1
  -> build-model-run-receipt@1
  -> model-run-receipt@1
```

The receipts prove exact artifact identity and declared metadata. They do not prove source accuracy, claim truth, visual fidelity, model quality, QG completion or production admission.

## C. Remaining leaf task contracts

| Leaf | Responsibility | Proposed path lease | Dependency | Required evidence |
|---|---|---|---|---|
| `runtime/02-relation-graph-and-thesis-ranking` | evidence-bound relation IR and deterministic central-thesis selector | relation schema/tool/tests only | merged PR #24 | anchored supported edges, stable relation IDs, deterministic ranking, negative controls |
| `runtime/03a-knowledge-view-projections` | causal flow, equation, timeline, state-plane and comparison views | projection schemas/renderers/tests | leaf 02 | exact relation provenance and UNKNOWN-safe cells |
| `runtime/03b-source-driven-batch-planner` | decision-value coverage instead of fixed series quota | batch planner/schema/tests | leaf 02 | action/comparison/visual coverage mutation tests |
| `runtime/03c-semantic-yield-evaluator` | HG-01..HG-06 deterministic evaluator | evaluator/schema/fixtures/tests | leaf 02 | omission, unsupported precision and false-positive controls |
| `runtime/visual-01-rights-gated-frame-contracts` | rights, timestamps, digests and visual locators | visual schemas/docs/tests | `main` | unauthorized and URL-based media fail closed |
| `runtime/visual-02-frame-extractor-and-annotation` | local frame extraction and reviewed bbox/OCR/topology | visual tools/tests | visual 01 | local-media canary, no downloader, digest mismatch control |
| `runtime/provider-01-model-run-adapter` | provider-neutral exact-model invocation boundary | provider interface/tests | `main` | fake-provider replay, timeout/error contract, secret-output guard |
| `runtime/provider-02-raw-response-receipt` | integrate adapter output with the merged receipt contract | provider receipt adapter/tests | provider 01 + PR #24 | exact digest and stale/mismatched-subject rejection |
| `runtime/04-convergence-and-cvrngaqzq3y-replay` | integrate admitted siblings and run transcript/multimodal comparison | shared fixtures, indexes, CI and final replay | approved leaf heads | full suite, stable IDs, no fixed-series golden, read-back and 2×2 result |

### Dependency policy

```text
PR #24 -> runtime/02 is serial because relation inputs consume source-pack identity.

runtime/03a / 03b / 03c are siblings:
- independent branches;
- disjoint path leases;
- no artificial serial dependency.

visual and provider stacks are independent roots from main.

runtime/04 is the only owner of:
- shared fixtures;
- aggregate indexes;
- canonical CI convergence;
- final CvRngaQZQ3Y replay;
- transcript-only versus multimodal 2×2 comparison.
```

## D. Current evidence lanes

| Lane | State | Meaning |
|---|---|---|
| issue/task decomposition | `PASS` | #17 and #23 contain goals, non-goals, leases, tests and rollback subjects |
| GitHub branch/PR publication | `PASS` | connector-backed publication receipts exist |
| trusted checks | `PASS` through PR #24 | exact PR heads received green CI |
| merge sequence | `PASS / HUMAN ADMIT` | explicit merges, not Worker auto-ship |
| exact Git Town admission | `ABSENT / BLOCKED_POLICY` | version/checksum/provenance/legal receipt missing |
| live `git town sync` | `NOT_EXERCISED` | GitHub graph is not a sync receipt |
| linked worktree/lease canary | `NOT_EXERCISED` | no admitted Worker runtime |
| conflict canary | `NOT_EXERCISED` | no live Git Town canary |
| Worker publication gate | `NOT_IMPLEMENTED` | connector publication is a separate trusted-operator lane |

## E. Current card-output authority

Modified-flow cards:

```text
evals/semantic-yield/CvRngaQZQ3Y/cards/
```

Canonical indexes:

- [`../../evals/semantic-yield/README.md`](../../evals/semantic-yield/README.md)
- [`../SEMANTIC_YIELD_INTEGRATION_STATUS.md`](../SEMANTIC_YIELD_INTEGRATION_STATUS.md)
- [`../../README.md`](../../README.md)

The retained `evals/live/CvRngaQZQ3Y/` directory is a transcript-only v7.1 baseline, not modified-flow coverage.

## F. Historical implementation trace

| PR | State | Role |
|---:|---|---|
| #9 | merged | immutable v7.1 prompt, A/B harness and audit |
| #11/#12 | merged | acquisition and retained transcript-only output |
| #15 | merged | current 10-card Semantic Yield batch |
| #16 | merged | deterministic card validator |
| #18–#22 | merged | discoverability, Agent routing, State Machine and Git/stack governance |
| #24 | merged | source-pack and model-run receipt foundation |
| #13 | open draft | monolithic runtime draft; extract remaining leaves, do not merge wholesale |

## G. Next executable order

```text
1. create a Leaf 02 task packet under issue #23;
2. branch from current main after PR #24;
3. extract only relation-graph and thesis-ranking code from PR #13;
4. bind relation inputs to multimodal-source-pack@1 identity;
5. add deterministic IDs, ranking and mutation controls;
6. publish Leaf 02 as a separate PR;
7. keep 03a/03b/03c blocked until the relation contract stabilizes.
```

## H. Update rules

Update this file whenever a leaf receives an issue/branch/PR, changes base or path lease, passes or fails checks, merges, closes or is superseded.

Never report:

- a planned leaf as implemented;
- a GitHub branch graph as live Git Town sync;
- a receipt as claim truth or quality evidence;
- a host projection as source visual evidence;
- a partial validator as full QG completion;
- a green check as automatic merge/promotion authority.
