# Git and Stacked-PR Governance｜Git Town 消費端入口

> Repository-owned binding for the shared [`git-town-stacked-pr-worker`](https://github.com/ed3c/skills-shared/tree/main/skills/git-town-stacked-pr-worker) method. This directory does not copy or shadow the shared Skill.

## Read order

Before creating, synchronizing, publishing, retargeting or reviewing a stacked branch, read:

1. root [`AGENTS.md`](../../AGENTS.md) or [`CLAUDE.md`](../../CLAUDE.md);
2. the shared `git-town-stacked-pr-worker` Skill;
3. [`REPO_PROFILE.md`](REPO_PROFILE.md);
4. [`GIT_TOWN_ADMISSION.md`](GIT_TOWN_ADMISSION.md);
5. [`WORKER_PROTOCOL.md`](WORKER_PROTOCOL.md);
6. [`STACKED_PRS.md`](STACKED_PRS.md);
7. issue #17 or the assigned task packet;
8. the nearest README for every writable path;
9. exact branch/PR/check state from GitHub.

A missing required input is `ABSENT`. Do not infer it from branch names, package manifests or prose.

## Ownership split

```text
shared git-town-stacked-pr-worker Skill
  = portable branch/worktree/sync/publication method

this repository
  = profile, path leases, task packets, branch graph,
    eval commands, CI, receipts and documentation

host/runtime
  = admitted Git Town executable, checksum, provenance,
    worktree roots and credentials

human / trusted operator
  = semantic conflict resolution, legal acceptance,
    merge order, ship/promotion and rollback
```

## Current status

```text
repository profile: MATERIALIZED
stacked PR graph: MATERIALIZED
connector-backed draft PR publication: EXERCISED
live git town executable admission: ABSENT
live git town sync: NOT_EXERCISED
background sync: DISABLED
worker publication gate: NOT_IMPLEMENTED
merge/ship: MACHINE LAND at the verified head, after `verify` succeeds
```

The current documentation stack uses explicit GitHub parent branches and PR bases. It is compatible with the intended Git Town hierarchy, but it is not evidence that `git town sync` ran.

## Directory contents

```text
docs/git/
├── README.md               # this entrypoint
├── REPO_PROFILE.md          # repository-owned policy/profile
├── GIT_TOWN_ADMISSION.md    # exact executable/version evidence state
├── WORKER_PROTOCOL.md       # task packet, leases, outcomes and boundaries
├── STACKED_PRS.md           # current stack and future molecular leaf plan
└── MACHINE_LANDING.md       # trusted verify + exact-head land ceremony
```

No `.git-town.toml`, sync wrapper or background loop should be added until exact Git Town admission and negative-control evals exist.

## Completion boundary

Git Town adoption is not complete from these documents alone. Completion requires an exact executable receipt, isolated worktree/lease canary, no-push sync canary, planted conflict, exact-HEAD verification receipt, guarded publication, post-push ancestry verification and Human Admit. Unrun lanes remain `NOT_EXERCISED`.
