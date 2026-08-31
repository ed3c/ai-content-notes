# Repository Profile — Git Town Stacked-PR Worker

> Repository-owned profile derived from the shared Skill template. `ABSENT`, `NOT_IMPLEMENTED` and `NOT_EXERCISED` are deliberate blocker states, not placeholders that may be guessed.

## Profile status

```text
profile schema: git-town-stacked-pr-worker/repo-profile/v1
profile state: BLOCKED_POLICY
blocking field: exact Git Town executable admission
```

## Identity

```yaml
schema: git-town-stacked-pr-worker/repo-profile/v1
repository:
  full_name: ed3c/ai-content-notes
  immutable_identity: github-repository-id:1327995338
  default_branch: main
  perennial_branches:
    - main
  allowed_remote_name: origin
  allowed_remote_url_pattern: '^https://github\.com/ed3c/ai-content-notes(?:\.git)?$'
```

## Authority documents

```yaml
authority:
  agents: AGENTS.md
  architecture: README.md
  git_governance: docs/git/README.md
  harness: docs/SEMANTIC_YIELD_VALIDATOR.md
  path_ownership: docs/git/STACKED_PRS.md
  git_town_admission: docs/git/GIT_TOWN_ADMISSION.md
  issue_template: ABSENT
  pull_request_template: ABSENT
```

The missing issue/PR templates do not invalidate the current human-created stack, but they block a generic unattended Worker adoption claim.

## Git Town admission

```yaml
git_town:
  version: ABSENT
  source_repository: ABSENT
  immutable_release: ABSENT
  platform: ABSENT
  architecture: ABSENT
  executable_sha256: ABSENT
  provenance_ref: ABSENT
  direct_license: ABSENT
  direct_license_sha256: ABSENT
  sbom_or_transitive_review: ABSENT
  notices_review: ABSENT
  legal_approval: ABSENT
```

Result:

```text
live sync: BLOCKED_POLICY
live canary: NOT_EXERCISED
```

Do not add mutable `latest`, infer a version from another host, or treat a permissive top-level license as complete legal/transitive evidence.

## Synchronization policy

These are the intended repository policies after admission; they are not a live execution receipt.

```yaml
sync:
  feature_strategy: rebase
  perennial_strategy: ff-only
  default_scope: stack
  non_interactive: true
  auto_resolve: false
  default_push: false
  allow_all_stacks: false
  timeout_seconds: 300
  dry_run_required: true
  post_sync_ancestry_check: true
  rerun_evals_after_sync: true
```

Deviations: none. The policy is inactive while admission is blocked.

## Worktree and lease policy

```yaml
workers:
  primary_checkout_mutation: denied
  linked_worktree_required: true
  worktree_root: HOST_SELECTOR::ai-content-notes-worktrees
  branch_lease_root: HOST_SELECTOR::ai-content-notes-branch-leases
  repository_lease: required
  lease_ttl_seconds: 1800
  sibling_path_overlap: denied
  preserve_blocked_worktree: true
```

Each task packet records exact allowed/excluded paths. Shared aggregate files such as root `README.md`, `AGENTS.md` and generated indexes belong to a designated convergence branch.

## Receipt policy

```yaml
receipts:
  root: receipts/git-town/
  schema: git-town-stacked-pr-worker/receipt/v1
  implementation: NOT_IMPLEMENTED
  append_only: true
  max_stream_bytes: 1048576
  secret_values: denied
  absolute_secret_paths: denied
  task_packet_digest_required: true
  before_after_graph_required: true
  cleanup_lane_required: true
```

## Background policy

```yaml
background:
  enabled: false
  max_iterations: 1
  interval_seconds: 60
  no_push: true
  stop_on_blocked_state: true
  stop_on_task_packet_change: true
  stop_on_lease_loss: true
  stop_on_conflict: true
  stop_on_failed_eval: true
```

No background loop may publish, mark a PR ready, rerun a workflow, merge, ship or mutate permissions.

## Publication policy

```yaml
publication:
  enabled: false
  task_packet_authorization_required: true
  explicit_cli_flag: --publish
  environment_guard_name: AI_CONTENT_NOTES_ALLOW_PUBLISH
  environment_guard_expected_value: '1'
  allowed_remote: origin
  protected_branch_rewrite: denied
  post_push_fetch_and_verify: true

  CI_PUBLICATION_GATE: ABSENT
  CI_PUBLICATION_SNAPSHOT_SCHEMA: github-actions-publish-snapshot/v1
  CI_LOCAL_VERIFICATION_SCHEMA: github-delivery-local-verification/v1
  CI_ALLOWED_INTENTS:
    - initial-pr
    - ready-for-review
    - batched-repair
  CI_DRAFT_PR_RUNNER_POLICY: no-runner
  CI_BILLING_CIRCUIT_POLICY: fail-closed
  CI_OBSOLETE_HEAD_POLICY: cancel-in-progress
  CI_TRUSTED_CHECK_NAME: verify
```

`verify` is the trusted check installed by [`MACHINE_LANDING.md`](MACHINE_LANDING.md). `Canonical contracts` still runs on `pull_request`, but it is not the landing authority.

The current PR stack was published by a trusted operator through the GitHub connector. It is not Worker publication evidence and does not resolve `CI_PUBLICATION_GATE: ABSENT`.

## Prompt suppression

```yaml
unattended_environment:
  GIT_TERMINAL_PROMPT: '0'
  GIT_EDITOR: ':'
  GIT_SEQUENCE_EDITOR: ':'
  GCM_INTERACTIVE: Never
```

## Required task packet fields

```yaml
task_packet:
  required:
    - issue_id
    - goal
    - non_goals
    - base_branch
    - parent_branch
    - head_branch
    - stack_class
    - allowed_paths
    - excluded_paths
    - dependencies
    - parallel_safe_siblings
    - required_evals
    - negative_or_mutation_controls
    - evidence_boundary
    - cleanup_contract
    - rollback_subject
    - human_owned_operations
```

## Required eval commands

```yaml
evals:
  commands:
    - python -m pip install -r requirements-contracts.txt
    - ruff check tools tests
    - python -m py_compile tools/*.py tests/*.py
    - pytest -q
    - python tools/validate_semantic_yield_artifacts.py --target evals/semantic-yield/CvRngaQZQ3Y --output evals/semantic-yield/CvRngaQZQ3Y/semantic-validator-report.json --created-at 2026-08-14T01:15:00Z --check
  live_git_town_canary: NOT_EXERCISED
  conflict_canary: NOT_EXERCISED
  publication_canary: NOT_EXERCISED
```

## Forbidden paths and data

```yaml
forbidden:
  paths:
    - '**/.env*'
    - '**/*token*'
    - '**/*credential*'
    - '**/*private-key*'
    - '**/raw-transcript*'
    - '**/browser-profile/**'
    - '**/device-session/**'
  data_classes:
    - credentials
    - tokens
    - private_keys
    - env_values
    - cookies
    - browser_profiles
    - device_sessions
    - host_keyrings
    - unbounded_model_output
```

## Human-owned operations

```yaml
human_owned:
  - semantic_conflict_resolution
  - git_town_continue_skip_undo_ship
  - merge_or_merge_queue_admission
  - branch_protection_or_permission_change
  - legal_or_license_acceptance
  - secret_or_credential_setup
  - release_promotion
  - production_deployment
  - destructive_or_drifted_rollback
```

## Admission checklist

- [x] repository identity and credential-free remote pattern are exact;
- [x] default sync policy is non-interactive, no-auto-resolve, bounded and no-push;
- [x] worktree/branch/path lease policy is declared;
- [x] background publication is disabled;
- [x] Human Admit boundary is explicit;
- [ ] exact Git Town version and executable evidence exist;
- [ ] direct/transitive/license/notices/legal review exists;
- [ ] task and PR templates enforce leases/evals;
- [ ] receipt writer exists;
- [ ] dry-run/no-push sync canary exists;
- [ ] planted conflict canary exists;
- [ ] exact-HEAD publication gate exists;
- [ ] remote ancestry and billing-circuit canaries exist.
