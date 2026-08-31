# Machine landing: trusted verify, exact-head land

This repository lands its own pull requests. The ceremony is three files and
one policy record, all owned here; nothing resolves outside this checkout, so
moving the repository anywhere keeps it operable.

| File | Role |
| --- | --- |
| `.github/workflows/verify.yml` | `pull_request_target` verification, trusted/candidate split |
| `.github/workflows/land.yml` | `workflow_run` on a successful `verify`, merges and closes |
| `scripts/land_pr.py` | exact-head merge, `Refs` Issue closure, read-backs |
| `policy/github.json` | repository, default branch, merge method |

## The trust split

`verify` runs two jobs.

1. `candidate-self-tests` checks out the candidate head with no credentials,
   installs the candidate's `requirements-contracts.txt` and runs the
   candidate's own `pytest -q`. A branch that breaks its own suite stops here.
2. `verify` checks out the default branch as `.trusted` and the exact candidate
   head as `.candidate`, then runs, in order,
   `python3 .trusted/tools/publication_guard.py --root .candidate` — the
   deterministic subset of the v7.1 quality gates, trusted bytes over candidate
   cards — and `pytest -q` inside `.candidate` after replacing
   `.candidate/tests` with `.trusted/tests`. Every test resolves its root from
   its own file, so this is trusted test bytes over candidate content. A
   candidate cannot weaken the suite, or the guard, that judges it.

`verify` then writes `verify-receipt.json` naming the exact `head_sha`, the PR
number and the trusted commit, and uploads it. The receipt, not the
`workflow_run` head, is what `land` trusts: a `pull_request_target` run reports
the base sha, never the candidate's.

`land` downloads that receipt, checks out the default branch and runs
`scripts/land_pr.py`, which refuses unless the PR is still open, its head is
still the verified sha, its base is the default branch, and its body carries
exactly one line

```text
Refs ed3c/ai-content-notes#<issue>
```

naming this repository. It merges at that exact sha, reads the merge back,
stamps `<!-- landing-… -->` markers into the Issue, closes it and reads the
closure back. Any refusal is a non-zero exit carrying the provider's own reason.

## Genesis (operator, once)

The ceremony cannot verify the pull request that installs it: a
`pull_request_target` workflow only runs from the default branch.

1. Merge the ceremony PR as a documented operator merge.
2. Enable branch protection on `main` immediately, with `verify` required:

   ```sh
   gh api -X PUT repos/ed3c/ai-content-notes/branches/main/protection \
     --input - <<'JSON'
   {
     "required_status_checks": {"strict": false, "contexts": ["verify"]},
     "enforce_admins": false,
     "required_pull_request_reviews": null,
     "restrictions": null
   }
   JSON
   ```

3. Read the protection back and keep the output as the receipt:

   ```sh
   gh api repos/ed3c/ai-content-notes/branches/main/protection \
     --jq '.required_status_checks.contexts'
   ```

Every pull request after genesis is machine-merged: `mergedBy` reads
`app/github-actions`, and the Issue named by the `Refs` line closes itself.
