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

## What the receipt's base commits are checked against

The receipt records two commits beside the head it tested: `base_sha`, the pull
request's base at verification time, and `trusted_sha`, the default branch
commit whose `tests/` and `publication_guard.py` did the judging. `land_pr.py`
compares each one against the default branch it is about to merge into and
refuses `VERIFIED_BASE_NOT_IN_HISTORY` unless the provider reports `identical`
or `ahead` — that is, unless the commit the green was earned against is still
reachable. A rewritten, reset or force-pushed default branch is caught before
the merge rather than after it.

Forward movement is *not* refused. The default branch moves forward on every
land, and refusing that would mean no two pull requests could be verified
concurrently. The stronger property — the green was earned against exactly the
commit receiving it — is `required_status_checks.strict: true` on the branch
protection, an operator setting with its own re-verification cost. This
repository's protection reads `strict: false`, so `main` can and does move
between a `verify` run and its `land` run; what the ceremony guarantees is
reachability, not identity.

## What the Issue markers record

`stamp` replaces a marker key in place, so a key that does not carry the landing
pull request holds exactly one land per Issue. `land_markers` therefore writes
two surfaces, and it is the only producer of a land's keys so that no call site
has to remember the difference:

| Key | Surface |
| --- | --- |
| `landing-state`, `landing-landed-pr`, `landing-head`, `landing-merge` | the newest land; rewritten by every land |
| `landing-pr-<n>-head`, `landing-pr-<n>-merge` | that one land; appended, never rewritten by another pull request |

An Issue that takes a second land keeps both row sets, so the first land's head
and merge SHAs stay readable from the Issue body rather than only from the
earlier pull request. Re-running a land for the same pull request rewrites that
pull request's own rows, so a retry stays idempotent.

Whether an Issue's acceptance is actually satisfied by any of those lands stays
a human judgement. These markers record what landed, never that it was enough.

## Who reads the markers back

`tools/landing_marker_audit.py` does, against
`docs/closure-audit/landing-marker-snapshot.json` — a curated read-back of every
land and every marker-shaped line the provider returned, with its line number.
It asks `land_markers` what the newest land should have written rather than
restating the key set, and reports one row per landed Issue: `CONFORMING`,
`NON_CONFORMING`, or `UNSTAMPED` for a land that left no marker at all.
`--strict` exits 1 while any row is not `CONFORMING`.

The live block is the *trailing* contiguous run of marker lines. Marker-shaped
text anywhere else is quoted prose and is reported as `quoted_outside_block`
rather than read as state.

The snapshot is the ceiling. Reading is zero-network, so the audit cannot see a
land that happened after `read_back_at`, or a body edited since; it states
whether the bytes it was given conform, and every row carries the body digest
and byte count those bytes were read from.

`--curate` is what makes those digests worth recording: it re-reads the
provider and prints a fresh snapshot, so the ceiling is a bill this repository
can pay rather than a permanent property of the file. Regenerate after a land:

```text
python3 tools/landing_marker_audit.py --curate > docs/closure-audit/landing-marker-snapshot.json
```

A land is counted by `land_pr.REFS_LINE` — the same expression `parse_refs`
binds a land with, exactly one line naming this repository — and marker lines
by `land_pr.MARKER_LINE`, the one expression `stamp` edits keys with. Neither
grammar is restated in the reader. `read_back_at` comes off the provider's own
`Date` header, not the curating host's clock.

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
