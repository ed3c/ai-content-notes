# Open-source Artifact Ranking｜開源資產排名

## Purpose｜目的

Rank exact-version code, model, data, and trajectory assets for different implementation contexts without converting popularity or repository visibility into a production recommendation.

依精確版本評估 code/model/data/trajectory 資產，避免把 star、熱度或「可下載」誤當成 production approval。

## Ranking views｜排名視角

Each candidate is scored independently for:

```text
Hackathon MVP
Commercial use
Research use
Production use
Stack compatibility
Evidence maturity
```

A single global score is not sufficient. The same asset can be excellent for a hackathon and unsafe for production.

## Hard gates before scoring｜計分前 Gate

```text
identity and exact version known
canonical repository/model/dataset URL known
applicable artifact-plane licenses resolved
security and maintenance status known
required runtime/toolchain compatibility known
source and benchmark evidence reproducible enough for the view
```

A failed or unknown hard gate blocks Commercial or Production recommendation.

## Scoring dimensions｜計分維度

Each dimension is 0–100, with evidence attached:

| Dimension | Meaning |
|---|---|
| MVP speed | time to first working demo, setup friction, examples |
| Commercial fit | license, support, integration surface, cost predictability |
| Research value | novelty, ablation access, reproducibility, extensibility |
| Production readiness | reliability, security, observability, upgrade/rollback, maintenance |
| Compatibility | target languages, runtimes, hosts, deployment, data/model formats |
| Evidence | primary sources, exact-version tests, independent reproduction, production observation |

## Suggested aggregate views｜建議視角權重

```text
Hackathon MVP:
  MVP speed 40
  Compatibility 20
  Evidence 15
  Commercial fit 10
  Research value 10
  Production readiness 5

Commercial:
  Commercial fit 30
  Production readiness 25
  Compatibility 20
  Evidence 20
  MVP speed 5

Research:
  Research value 35
  Evidence 30
  Compatibility 15
  MVP speed 10
  Production readiness 10

Production:
  Production readiness 35
  Evidence 25
  Compatibility 20
  Commercial fit 15
  MVP speed 5
```

Weights are view metadata and must be versioned when changed.

## Evidence states｜證據狀態

```text
discovered
source-anchored
cross-checked
locally-reproduced
sandbox-attested
production-observed
stale-or-invalidated
```

Do not rank an asset as Production-ready from marketing claims or a single synthetic benchmark.

## Compatibility contract｜相容性契約

Record exact versions for:

```text
language/runtime
framework/SDK
operating system/container
CPU/GPU/accelerator
model/data/trajectory format
Claude Code/Codex/MCP host when applicable
network/secret/permission policy
```

## Failure and downgrade｜失敗與降級

A candidate is automatically queued for review when:

```text
license changes
release deprecates an interface
security advisory affects the exact version
benchmark cannot be reproduced
maintainer status materially changes
required host/runtime compatibility fails
source evidence expires or is contradicted
```

Historical scores remain, but the active recommendation becomes blocked until re-evaluated.

## Current entries｜目前條目

No asset is promoted in this file by default. Machine-readable entries must validate against `schemas/rank-entry.schema.json` and link to exact evidence. Discovery candidates remain in note claim maps until license and evidence gates pass.
