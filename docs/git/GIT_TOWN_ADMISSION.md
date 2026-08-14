# Git Town Admission｜可執行檔與法律證據狀態

## Current decision

```text
admission_status: ABSENT
worker_outcome: BLOCKED_POLICY
live_git_town_sync: NOT_EXERCISED
live_conflict_canary: NOT_EXERCISED
live_publication_canary: NOT_EXERCISED
```

The current execution host exposed `git` but did not expose an admitted `git town` executable or `gh` CLI. No exact version, release identity, checksum, provenance, SBOM/transitive review, notices review or legal approval receipt was available.

The documentation stack was therefore created with explicit GitHub parent branches and PR bases by a trusted operator. This proves the remote branch dependency graph; it does not prove Git Town synchronization.

## Required evidence before admission

Record all fields as one subject-bound admission receipt:

```yaml
source_repository: <exact URL>
version: <exact immutable version>
release_or_commit: <tag, release ID or commit SHA>
platform: <exact OS>
architecture: <exact architecture>
executable_sha256: <sha256>
provenance_ref: <package/release provenance>
direct_license: <SPDX ID>
direct_license_sha256: <sha256 of admitted license bytes>
sbom_or_transitive_review: <PASS/FAIL + artifact>
notices_review: <PASS/FAIL + artifact>
legal_approval: <PASS/FAIL + authority>
installed_path_or_host_selector: <non-secret selector>
```

Mutable `latest`, a version string without binary identity, or an executable from another host is not admissible evidence.

## Required live canaries

After admission, execute these lanes separately:

1. **Doctor** — exact executable/version/checksum matches the profile.
2. **Dry-run sync** — selected stack, non-interactive, no-auto-resolve and no-push.
3. **Bounded sync** — timeout enforced; post-sync ancestry checked.
4. **Conflict canary** — deterministic semantic conflict stops with `BLOCKED_CONFLICT`; no automatic continue/skip/undo.
5. **Lease canary** — duplicate branch lease and overlapping sibling path lease fail closed.
6. **Publication canary** — exact-HEAD gate admits one permitted operation only.
7. **Draft policy canary** — draft publication is recorded separately from runner-backed validation.
8. **Remote ancestry canary** — fetched remote head equals the admitted local subject.
9. **Cleanup lane** — worktree/lease cleanup has a receipt; blocked worktrees are preserved by policy.

## Intended sync command after admission

```bash
git town sync --stack --non-interactive --no-auto-resolve --no-push
```

It must run only through the repository-owned bounded wrapper after task-packet, lease and exact-version checks.

## Forbidden claims

- branch hierarchy means Git Town ran;
- `git town sync` exit 0 means implementation or tests passed;
- a push means GitHub trusted checks ran;
- a trusted check means merge/promotion is authorized;
- direct permissive license means transitive/legal review is complete;
- documentation means live adoption is complete.

## Unblock criteria

Change `admission_status` only after the exact admission receipt and all required negative controls are committed or stored in the governed receipt authority. Until then, no `.git-town.toml`, Worker sync wrapper or background loop should be treated as active.
