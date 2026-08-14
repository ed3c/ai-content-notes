# Stacked-PR Worker Protocol｜分支、租約、驗證與出版邊界

> Consumer-specific protocol for the shared `git-town-stacked-pr-worker` method. It is inactive for live Git Town synchronization until `GIT_TOWN_ADMISSION.md` is admitted.

## 1. Core invariants

- One Worker owns one linked worktree, one head branch and one branch lease.
- The primary/shared checkout is read-only for Workers.
- Independent tasks use sibling branches with disjoint path leases.
- Serial dependencies use an explicit parent branch and PR base.
- Shared aggregate files belong to one convergence branch.
- Semantic conflicts stop; Workers do not automatically continue, skip, undo, ship or invent semantic resolutions.
- Background activity is bounded and no-push.
- Publication, remote ancestry, GitHub checks and Human Admit remain separate evidence lanes.

## 2. Task packet

A branch must not start without this complete packet:

```yaml
issue_id: <issue>
goal: <observable result>
non_goals:
  - <excluded result>
base_branch: <perennial root>
parent_branch: <immediate stack parent>
head_branch: <owned branch>
stack_class: serial | sibling | convergence
allowed_paths:
  - <exact path or subtree>
excluded_paths:
  - <exact path or subtree>
dependencies:
  - <branch/PR/artifact>
parallel_safe_siblings:
  - <branch or none>
required_evals:
  - <typed command>
negative_or_mutation_controls:
  - <control>
evidence_boundary: <what the result proves and cannot prove>
cleanup_contract: <worktree/lease behavior>
rollback_subject: <immutable commit/ref>
human_owned_operations:
  - semantic_conflict_resolution
  - merge
  - ship
```

Missing fields produce `BLOCKED_TASK_PACKET`.

## 3. Path lease rules

1. A Worker may write only declared `allowed_paths`.
2. Parent/child branches may touch one shared aggregate path only when the child is the named convergence owner.
3. Sibling branches may not overlap writable paths.
4. `README.md`, `AGENTS.md`, `CLAUDE.md`, root indexes and generated aggregate manifests require an explicit convergence lease.
5. Source bodies, secrets, raw private transcripts and host-owned paths are never implicitly leased.
6. Lease loss stops the Worker and preserves the worktree.

## 4. Intended local sequence after Git Town admission

```text
validate task packet and profile
  -> acquire repository/branch/path leases
  -> create isolated linked worktree
  -> verify parent ancestry
  -> run dry-run no-push sync
  -> run bounded no-push sync
  -> verify post-sync ancestry
  -> run exact-HEAD evals and negative controls
  -> produce local verification receipt
  -> evaluate publication policy
  -> at most one admitted publication operation
  -> fetch and verify remote ancestry
  -> record trusted-check state separately
```

Intended sync command:

```bash
git town sync --stack --non-interactive --no-auto-resolve --no-push
```

Current state: `NOT_EXERCISED`.

## 5. Stable outcomes

```text
SYNCED
NO_CHANGE
BLOCKED_TASK_PACKET
BLOCKED_DIRTY
BLOCKED_CONFLICT
BLOCKED_PROMPT
BLOCKED_TIMEOUT
BLOCKED_BRANCH_LEASE
BLOCKED_ANCESTRY
BLOCKED_POLICY
FAILED_TOOL
FAILED_EVAL
ROLLBACK_REFUSED_DRIFT
```

Every non-success outcome preserves enough state for reviewed recovery and never silently rewrites history.

## 6. Repository evals

Minimum exact-HEAD verification:

```bash
python -m pip install -r requirements-contracts.txt
ruff check tools tests
python -m py_compile tools/*.py tests/*.py
pytest -q

python tools/validate_semantic_yield_artifacts.py \
  --target evals/semantic-yield/CvRngaQZQ3Y \
  --output evals/semantic-yield/CvRngaQZQ3Y/semantic-validator-report.json \
  --created-at 2026-08-14T01:15:00Z \
  --check
```

Documentation stacks additionally run `tests/test_repository_navigation.py`.

## 7. Required negative controls

- remove a required task-packet field → `BLOCKED_TASK_PACKET`;
- use the primary checkout → blocked;
- dirty worktree before sync → `BLOCKED_DIRTY`;
- wrong parent ancestry → `BLOCKED_ANCESTRY`;
- duplicate branch or overlapping path lease → `BLOCKED_BRANCH_LEASE`;
- unresolved Git Town version/checksum → `BLOCKED_POLICY`;
- credential-bearing remote → blocked;
- editor/credential prompt in unattended mode → `BLOCKED_PROMPT`;
- planted rebase conflict → `BLOCKED_CONFLICT`;
- timeout → `BLOCKED_TIMEOUT`;
- failed test/validator → `FAILED_EVAL`;
- stale exact-HEAD receipt or old remote SHA → publication blocked;
- background `--push`, raw `git push`, PR-ready transition, workflow rerun or merge → forbidden.

Live Git Town controls are `NOT_EXERCISED` until admission.

## 8. Publication lanes

Portable intents after publication-gate implementation:

```text
initial-pr
ready-for-review
batched-repair
```

The current documentation stack was created by a trusted operator through the GitHub connector. It is recorded as remote publication evidence only; it is not evidence that a repository Worker publication gate exists.

## 9. Rollback

- Rollback is bound to an immutable branch/commit subject.
- A Worker may propose rollback but may not execute destructive or drifted rollback.
- If remote or parent ancestry changed, return `ROLLBACK_REFUSED_DRIFT`.
- Merge, branch deletion, promotion and production rollback remain Human Admit.

## 10. Current task packet

Issue #17 defines the active four-PR documentation stack. Exact branches, path leases, PR bases and merge order are in [`STACKED_PRS.md`](STACKED_PRS.md).
