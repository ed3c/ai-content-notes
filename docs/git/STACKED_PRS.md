# Stacked PR Index｜已合併分支圖與分子化末端實作

> Canonical PR dependency and runtime-leaf index for `ed3c/ai-content-notes`. GitHub PR state is authority. Planned leaves remain plans until an issue, branch, path lease, eval receipt and PR exist.

## A. Completed documentation/governance stack

Issue [#17](https://github.com/ed3c/ai-content-notes/issues/17) decomposed the discoverability and governance work into four serial PRs:

```text
main
└── Merged PR #18  agent/docs-card-catalog
    └── Merged PR #19  agent/docs-agent-routing
        └── Merged PR #20  agent/docs-state-machine
            └── Merged PR #21  agent/docs-git-town-governance
```

| Stack | Branch | Original base | Scope / path lease | Validation | Merge commit |
|---:|---|---|---|---|---|
| 1 | `agent/docs-card-catalog` | `main` | `evals/semantic-yield/README.md`, `docs/SEMANTIC_YIELD_INTEGRATION_STATUS.md`, `INDEX.md` | Canonical contracts | `bbf92a4106b720f5b50707029779984d6672951f` |
| 2 | `agent/docs-agent-routing` | Stack 1 | `AGENTS.md`, `CLAUDE.md`, `INTEGRATION_REQUIREMENTS.md` | Canonical contracts | `073fbdd2c1d09b71f22a30b7458aa0be06b932d6` |
| 3 | `agent/docs-state-machine` | Stack 2 | `README.md`, `tests/test_repository_navigation.py` | Canonical contracts + Ruff | `c10f8b4572546262c34f93712c54798fdc451830` |
| 4 | `agent/docs-git-town-governance` | Stack 3 | `docs/git/**` plus convergence-owned root docs/tests | Canonical contracts + Ruff | `a2bd35a615c6754c5be70494bef55b65216bda7c` |

Actual merge/retarget sequence:

```text
merge PR #18 with ancestry-preserving merge commit
→ retarget PR #19 to main and merge
→ retarget PR #20 to main and merge
→ retarget PR #21 to main and merge
```

This is a proven GitHub branch/PR and Human-Admit lane. It is not proof that a Git Town executable ran.

## B. Evidence lanes for the completed stack

| Lane | Result | Evidence boundary |
|---|---|---|
| task decomposition | `PASS` | issue #17 recorded goal, non-goals, parent, path lease, evals and rollback subjects |
| remote branch hierarchy | `PASS` | PR #18 → #19 → #20 → #21 bases were read back |
| connector-backed PR publication | `PASS` | all four PRs existed and were reviewable |
| trusted checks | `PASS` | Canonical Contracts passed for each stack head; Ruff passed where present |
| retarget sequence | `PASS` | children were retargeted to `main` only after the parent merged |
| merge / promotion | `PASS / HUMAN ADMIT` | trusted operator explicitly admitted each merge |
| exact Git Town admission | `ABSENT / BLOCKED_POLICY` | no exact version/checksum/provenance/legal receipt |
| live `git town sync` | `NOT_EXERCISED` | branch graph was managed through GitHub APIs |
| linked worktree/lease canary | `NOT_EXERCISED` | no admitted Worker runtime |
| conflict canary | `NOT_EXERCISED` | no live Git Town canary |
| exact-HEAD Worker receipt | `NOT_EXERCISED` | GitHub CI is a separate evidence lane |
| Worker publication gate | `NOT_IMPLEMENTED` | no repo-owned admitted gate/wrapper |

The shared `git-town-stacked-pr-worker` method owns the portable rules. This repository owns the profile, issue packets, path leases, CI, receipts and branch graph. Missing live evidence stays `ABSENT`, `NOT_EXERCISED` or `NOT_IMPLEMENTED`.

## C. Current card-output authority

Only this content item has run the modified Semantic Yield flow:

```text
evals/semantic-yield/CvRngaQZQ3Y/cards/
```

Canonical navigation:

- [`../../evals/semantic-yield/README.md`](../../evals/semantic-yield/README.md)
- [`../SEMANTIC_YIELD_INTEGRATION_STATUS.md`](../SEMANTIC_YIELD_INTEGRATION_STATUS.md)
- [`../../README.md`](../../README.md)

The retained first-pass directory:

```text
evals/live/CvRngaQZQ3Y/
```

is a transcript-only v7.1 baseline and is not modified-flow coverage.

## D. Historical implementation trace

| PR | State | Role |
|---:|---|---|
| PR #9 | merged | immutable v7.1 prompt lock, A/B harness and system audit |
| PR #11 / PR #12 | merged | transcript acquisition and retained first v7.1 batch under `evals/live/` |
| PR #15 | merged | current 10-card Semantic Yield output |
| PR #16 | merged | deterministic artifact validator and partial QG evidence |
| PR #18 / PR #19 / PR #20 / PR #21 | merged | catalog, Agent routing, State Machine/data flow and Git/stack governance |
| PR #13 | open draft | monolithic grounded runtime draft; not current `main` authority |

PR #13 contains useful code but mixes source-pack contracts, relation graphs, projections, planning and evaluation in one large review surface. Reuse requires molecular extraction and replay against current `main`; do not merge it wholesale.

## E. Molecular runtime leaf stack｜PR #13 的分子化末端實作

These leaves are `PLANNED`, not implemented PRs. Every leaf needs a new task packet, branch, exact path lease, required evals, negative controls and rollback subject.

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

### Planned leaves and path leases

| Leaf | Primary responsibility | Proposed path lease | Dependency | Required completion evidence |
|---|---|---|---|---|
| `runtime/01-source-pack-and-run-receipt` | multimodal source-pack and provider/model run-receipt contracts/builders | dedicated source-pack/receipt schemas, builders and focused tests | `main` | Draft 2020-12 schema tests, deterministic digests, stale-subject rejection |
| `runtime/02-relation-graph-and-thesis-ranking` | evidence-bound relation IR and central-thesis selector | relation schema/tool/tests only | leaf 01 | supported edges require anchors; deterministic relation IDs and ranking |
| `runtime/03a-knowledge-view-projections` | causal flow, equation, timeline, state-plane and comparison views | projection schemas/renderers/tests | leaf 02 | relation provenance and UNKNOWN-safe cells |
| `runtime/03b-source-driven-batch-planner` | replace fixed series quota with decision-value coverage | batch planner/schema/tests | leaf 02 | comparison/action/visual coverage mutation tests |
| `runtime/03c-semantic-yield-evaluator` | HG-01..HG-06 deterministic evaluator | evaluator/schema/fixtures/tests | leaf 02 | false-positive, omission and unsupported-precision controls |
| `runtime/visual-01-rights-gated-frame-contracts` | rights, timestamp, digest and visual locator contracts | visual schemas/docs/tests | `main` | unauthorized or URL-based media fails closed |
| `runtime/visual-02-frame-extractor-and-annotation` | explicit local frame extraction and reviewed bbox/OCR/topology annotations | visual tools/tests | visual 01 | real local-media canary; no downloader; digest mismatch control |
| `runtime/provider-01-model-run-adapter` | provider-neutral exact-model invocation boundary | provider adapter interface/tests | `main` | fake-provider replay, timeout/error contract and secret-output guard |
| `runtime/provider-02-raw-response-receipt` | raw-response, sampling and compiled-output receipt | receipt builder/tests | provider 01 | exact digest binding and stale/mismatched subject rejection |
| `runtime/04-convergence-and-cvrngaqzq3y-replay` | integrate admitted siblings and run transcript/multimodal comparison | shared fixtures, aggregate indexes, CI and final replay | approved leaf heads | full suite, no fixed-series golden, stable IDs, Git read-back and 2×2 result |

### Dependency and sibling policy

```text
runtime/01 -> runtime/02 is serial because relation input consumes source-pack identity.

runtime/03a / runtime/03b / runtime/03c are siblings:
- separate branches;
- disjoint path leases;
- no artificial serial chain.

visual and provider stacks are independent roots from main.

runtime/04 is the sole convergence owner for:
- shared fixtures;
- aggregate indexes;
- canonical CI wiring;
- the final CvRngaQZQ3Y replay;
- the 2×2 transcript-only versus multimodal comparison.
```

## F. Next executable order

Current recommended order:

```text
1. create an epic/task packet for runtime/01;
2. extract only the source-pack and run-receipt slice from PR #13;
3. replay focused tests against current main;
4. publish a draft leaf PR;
5. keep runtime/02 blocked until leaf 01 contracts stabilize;
6. do not activate Git Town sync until admission is unblocked.
```

The first runtime leaf must not copy historical generated fixtures or aggregate indexes owned by convergence.

## G. Traceability matrix

| Requirement | Current artifact |
|---|---|
| find modified-flow cards | `evals/semantic-yield/README.md` |
| exact integration status | `docs/SEMANTIC_YIELD_INTEGRATION_STATUS.md` |
| Agent read order | `AGENTS.md`, `CLAUDE.md`, `INTEGRATION_REQUIREMENTS.md` |
| directory State Machine and data flow | root `README.md` |
| current card identities | `evals/semantic-yield/CvRngaQZQ3Y/card-manifest.json` |
| deterministic validation | `semantic-validator-report.json`, validator tool/tests |
| repository profile | `docs/git/REPO_PROFILE.md` |
| admission blocker | `docs/git/GIT_TOWN_ADMISSION.md` |
| Worker task/lease contract | `docs/git/WORKER_PROTOCOL.md` |
| completed and planned branch graph | this file |
| completed docs-stack owner | issue #17 |
| runtime implementation owner | new runtime epic/task packets, not issue #17 by implication |

## H. Update rules

Update this file whenever:

- a planned leaf receives an issue, branch or PR number;
- a PR base/head changes;
- a stack item is merged, closed or superseded;
- a path lease changes;
- Git Town admission or live evidence changes;
- a convergence artifact becomes authoritative.

Never report:

- a planned leaf as implemented;
- a GitHub branch graph as live Git Town sync;
- a green check as merge/promotion authority;
- a host projection as source visual evidence;
- a partial validator as full QG-01..QG-24 completion.
