#!/usr/bin/env python3
"""Land a verified pull request at its exact verified head and close its Issue.

Trust split: the receipt (produced by the trusted verify job) names *which*
commit was verified; `policy/github.json` on the default branch names the
repository, base branch and merge method. Nothing is taken from the candidate.

This repository owns its own copy of the ceremony. It resolves no path, script
or policy outside this checkout, so the machine keeps working with every other
repository absent.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API = "https://api.github.com"
REFS_LINE = re.compile(r"^Refs\s+([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)#(\d+)$")
MARKER_PREFIX = "landing"
MARKER_LINE = re.compile(rf"^<!--\s*{MARKER_PREFIX}-([A-Za-z0-9_-]+):.*?-->[ \t]*$")
MARKER_RECEIPT_TOKEN = "landing-marker-receipt: pr="

# What an Issue's two marker surfaces - the mutable body and the durable
# receipt comment - say together about whether it was landed. Every name has a
# producer: `main` emits one at land time, `audit_issue` emits one on demand.
LANDED = "LANDED"  # both surfaces carry the land
MARKERS_LOST = "MARKERS_LOST"  # receipt present, body block gone: #117's measured failure
RECEIPT_ABSENT = "RECEIPT_ABSENT"  # body block only: a land before this receipt existed
NO_LAND = "NO_LAND"  # neither surface records a land

COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")

# `GET /repos/{repo}/compare/{base}...{head}` states the head's position
# relative to the base. Only these two mean the base is reachable from the head:
# `identical` (the same commit) and `ahead` (the head contains it). `behind` and
# `diverged` both mean the commit a green was earned against is not in the
# history about to receive the merge.
BASE_IN_HISTORY = frozenset({"identical", "ahead"})
VERIFIED_BASE_FIELDS = ("base_sha", "trusted_sha")


def parse_refs(body: str | None, repository: str) -> int:
    """Return the Issue number from the single 'Refs <owner>/<repo>#<n>' line."""
    hits = [
        match
        for match in (REFS_LINE.match(line.strip()) for line in (body or "").splitlines())
        if match
    ]
    if len(hits) != 1:
        raise SystemExit(f"REFS_LINE_COUNT:{len(hits)}")
    named, number = hits[0].group(1), int(hits[0].group(2))
    if named != repository:
        raise SystemExit(f"REFS_FOREIGN_REPOSITORY:{named}")
    return number


def land_markers(repository: str, number: int, head: str, merge_sha: str) -> dict[str, str]:
    """Markers for one land: a newest-land pointer plus a per-pull-request row set.

    `stamp` replaces a marker key in place, so a key that does not carry the
    landing pull request holds exactly one land per Issue and a second land
    overwrites the first. This function is the only producer of a land's marker
    keys precisely so no call site has to remember that: the `pr-<number>-*`
    keys differ per pull request and therefore append, while `state`,
    `landed-pr`, `head` and `merge` are deliberately unnamespaced and keep
    pointing at the newest land, which no longer costs anything because the
    per-pull-request rows hold the history they used to be the only record of.
    """
    return {
        "state": "landed",
        "landed-pr": f"{repository}#{number}",
        "head": head,
        "merge": merge_sha,
        f"pr-{number}-head": head,
        f"pr-{number}-merge": merge_sha,
    }


def split_marker_block(text: str) -> tuple[list[str], list[str]]:
    """Split `text` into (everything before the live marker block, the block).

    The live block is the run of marker lines the text *ends* with, ignoring
    trailing blank lines. Marker-shaped text anywhere else - a quoted example,
    a fenced illustration, an issue whose subject happens to be these markers -
    is prose, and belongs to the prefix.
    """
    lines = text.split("\n")
    end = len(lines)
    while end and not lines[end - 1].strip():
        end -= 1
    start = end
    while start and MARKER_LINE.match(lines[start - 1]):
        start -= 1
    return lines[:start], lines[start:end]


def stamp(body: str | None, markers: dict[str, str]) -> str:
    """Set each `<!-- landing-<key>: ... -->` marker inside the live marker block.

    Replaces a key in place if the block already carries it, appends to the
    block otherwise. The edit is scoped to the block returned by
    `split_marker_block` because the previous whole-body `re.subn` matched the
    first marker-shaped line anywhere in the text: landing
    ed3c/ai-content-notes#98 rewrote a quoted historical example two sections
    above the real block, and - because that match consumed the one
    substitution the `landed-pr` key allows itself - the live block silently
    never received a `landing-landed-pr` line at all
    (ed3c/ai-content-notes#120).

    Ceiling: the block is identified by position, so an issue body that *ends*
    with an unfenced quoted marker line still hands that line to this function
    as live. Position is the only signal a shared prose field carries.
    """
    prefix, block = split_marker_block(body or "")
    for key, value in markers.items():
        line = f"<!-- {MARKER_PREFIX}-{key}: {value} -->"
        for index, existing in enumerate(block):
            match = MARKER_LINE.match(existing)
            if match and match.group(1) == key:
                block[index] = line
                break
        else:
            block.append(line)
    return "\n".join(prefix + block).rstrip("\n") + "\n"


def marker_surface(body: str | None, comments: list[str | None]) -> str:
    """Read what one Issue's two marker surfaces say about a land.

    A body carrying no marker block is not evidence of no land. It is evidence
    of no land *only when the durable surface is silent too* - and that is the
    distinction #113 could not make after a stale whole-body edit deleted its
    four markers: closed, no block, and nothing anywhere saying whether a land
    had ever happened (ed3c/ai-content-notes#117).
    """
    receipted = any(MARKER_RECEIPT_TOKEN in (comment or "") for comment in comments)
    in_body = bool(split_marker_block(body or "")[1])
    if receipted:
        return LANDED if in_body else MARKERS_LOST
    return RECEIPT_ABSENT if in_body else NO_LAND


def api(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{API}{path}",
        method=method,
        data=None if payload is None else json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:  # surface the provider's own reason
        raise SystemExit(
            f"GITHUB_API_REFUSED:{method}:{path}:{exc.code}:{exc.read().decode('utf-8', 'replace')}"
        ) from exc


def verified_base_in_history(
    receipt: dict[str, Any], repository: str, default_branch: str, call: Any = None
) -> dict[str, str]:
    """Refuse a receipt whose verified base is not in the branch about to receive it.

    `verify` records two commits beside the head it tested: `base_sha`, the
    pull request's base at verification time, and `trusted_sha`, the default
    branch commit whose `tests/` and `publication_guard.py` did the judging.
    Until this function existed both were write-only as far as a literal search
    reaches: `git grep -c` over this repository at `ac10987` found one hit each,
    their own producer line in `verify.yml`. That instrument was checked in both
    directions - a planted sibling consumer takes each count from one file to
    two, a planted consumer that assembles the key name at runtime takes neither
    - so what the silence supports is "nothing here names these fields
    literally", not "nothing reads them" (#118).

    What is checked: each recorded commit is still reachable from the default
    branch this land is merging into. A rewritten, reset or force-pushed default
    branch makes the green unattributable, and that is refused here rather than
    discovered afterwards.

    What is *not* checked, deliberately: that the default branch has not moved
    forward. It moves forward on every land, and refusing that would mean no two
    pull requests could ever be verified concurrently. The stronger property -
    the green was earned against exactly the commit receiving it - is
    `required_status_checks.strict: true` on the branch protection, an operator
    setting with its own re-verification cost, not something this script can
    assert on its own. Reachability is what the receipt's own bytes can prove.
    """
    call = api if call is None else call
    statuses: dict[str, str] = {}
    for field in VERIFIED_BASE_FIELDS:
        sha = receipt.get(field)
        if not isinstance(sha, str) or not COMMIT_SHA.match(sha):
            raise SystemExit(f"RECEIPT_VERIFIED_BASE_ABSENT:{field}:{sha!r}")
        status = str(
            call("GET", f"/repos/{repository}/compare/{sha}...{default_branch}").get("status")
        )
        if status not in BASE_IN_HISTORY:
            raise SystemExit(f"VERIFIED_BASE_NOT_IN_HISTORY:{field}:{sha}:{status}")
        statuses[field] = status
    return statuses


def post_receipt_anchor(
    repository: str, number: int, merge_sha: str, call: Any = None
) -> str:
    """Post the physical-receipt anchor on the merged PR, once.

    N-class: runs only after merge + issue-closure readback and can never gate
    a land - every failure path returns 'failed' instead of raising. The Drive
    index is appended by the periodic batch reconcile, not here.
    Returns 'exists' | 'posted' | 'failed'.
    """
    call = api if call is None else call
    try:
        comments = call("GET", f"/repos/{repository}/issues/{number}/comments?per_page=100")
        if any(
            "physical-receipt-anchor" in str(item.get("body") or "")
            for item in comments
            if isinstance(item, dict)
        ):
            return "exists"
        merged_at = str(call("GET", f"/repos/{repository}/pulls/{number}").get("merged_at") or "")
        call(
            "POST",
            f"/repos/{repository}/issues/{number}/comments",
            {
                "body": (
                    f"physical-receipt-anchor: pr={number} merge-commit={merge_sha} "
                    f"merged-at={merged_at}\n\n"
                    "Anchor is the merge commit SHA (immutable provider truth). The Drive "
                    "index is appended by the periodic batch reconcile; receipts are "
                    "N-class, never a landing-gate dependency."
                )
            },
        )
        return "posted"
    except (SystemExit, Exception):
        return "failed"


def post_marker_receipt(
    repository: str, issue: int, number: int, markers: dict[str, str], call: Any = None
) -> str:
    """Post this land's marker set as a comment on the Issue, once per PR.

    The Issue *body*'s copy of the set is deletable: `main` writes it with a
    read-modify-write and no concurrency control, so any writer whose edit was
    composed from a pre-land read deletes the whole block on PATCH. Measured on
    #113 - one land, a correct `stamp`, four markers, and 42 seconds later zero
    (ed3c/ai-content-notes#117).

    The anchor comment on the merged pull request survived that identical edit,
    because a comment is a separate object no body PATCH can reach. This is the
    same durability applied to the surface a reader of the *Issue* consults:
    the receipt-anchor answers "was this PR merged", this answers "what did the
    land write on this Issue", and a body edit reaches neither.

    N-class like `post_receipt_anchor`: never raises, and cannot gate a land -
    it runs after the merge and the closure read-back. It is not silent
    though: `main` reads both surfaces afterwards and exits non-zero unless
    they agree, so 'failed' costs a red job rather than a log line nobody
    reads. Returns 'exists' | 'posted' | 'failed'.
    """
    call = api if call is None else call
    header = f"{MARKER_RECEIPT_TOKEN}{number}"
    try:
        comments = call("GET", f"/repos/{repository}/issues/{issue}/comments?per_page=100")
        if any(
            header in str(item.get("body") or "") for item in comments if isinstance(item, dict)
        ):
            return "exists"
        call(
            "POST",
            f"/repos/{repository}/issues/{issue}/comments",
            {
                # The marker block goes last so `split_marker_block` reads it
                # here exactly as it reads it in the Issue body.
                "body": (
                    f"{header}\n\nDurable copy of the marker block this land wrote into the "
                    "Issue body. The body is a shared mutable field and another writer's "
                    "whole-body edit can delete that copy without seeing it; this comment "
                    "is a separate object, so `--audit-issue` can still tell a land that "
                    "left no trace from an Issue that was never landed.\n\n"
                    + stamp("", markers)
                )
            },
        )
        return "posted"
    except (SystemExit, Exception):
        return "failed"


def audit_issue(repository: str, issue: int, call: Any = None) -> int:
    """Report one Issue's marker surface. Exit 1 when a landed Issue lost it.

    This is the reader ed3c/ai-content-notes#117 asks for: without it, an Issue
    whose markers were deleted by another writer's stale PATCH reads exactly
    like an Issue that was never landed, and nobody finds out.
    """
    call = api if call is None else call
    body = call("GET", f"/repos/{repository}/issues/{issue}").get("body")
    comments = [
        item.get("body")
        for item in call("GET", f"/repos/{repository}/issues/{issue}/comments?per_page=100")
        if isinstance(item, dict)
    ]
    surface = marker_surface(body, comments)

    # Read the marker lines off whichever surface still carries them. The body
    # copy is `[]` by definition in MARKERS_LOST - the one state this reader
    # refuses - so printing only the body block would print nothing at the one
    # moment the durable copy exists for, and the receipt comment would be a
    # store nothing ever reads a value back out of.
    receipt = next((item for item in comments if MARKER_RECEIPT_TOKEN in (item or "")), "")
    markers = split_marker_block(body or "")[1] or split_marker_block(receipt)[1]

    print(
        json.dumps(
            {"issue": issue, "marker_surface": surface, "markers": markers},
            indent=2,
            sort_keys=True,
        )
    )
    return 1 if surface == MARKERS_LOST else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--policy", type=Path, default=Path("policy/github.json"))
    parser.add_argument(
        "--audit-issue",
        type=int,
        help="read one Issue's marker surface and exit; performs no write",
    )
    args = parser.parse_args(argv)

    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    if args.audit_issue is not None:
        return audit_issue(policy["repository"], args.audit_issue)
    if args.receipt is None:
        parser.error("one of --receipt or --audit-issue is required")

    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))

    repository = policy["repository"]
    if receipt.get("repository") != repository:
        raise SystemExit(f"RECEIPT_FOREIGN_REPOSITORY:{receipt.get('repository')}")
    number = int(receipt["pull_request"])
    head = receipt["head_sha"]

    pull = api("GET", f"/repos/{repository}/pulls/{number}")
    if pull["state"] != "open":
        raise SystemExit(f"PULL_NOT_OPEN:{number}:{pull['state']}")
    if pull["head"]["sha"] != head:
        raise SystemExit(f"HEAD_MOVED:{number}:{pull['head']['sha']}:{head}")
    if pull["base"]["ref"] != policy["default_branch"]:
        raise SystemExit(f"BASE_NOT_DEFAULT_BRANCH:{number}:{pull['base']['ref']}")
    verified_base = verified_base_in_history(receipt, repository, policy["default_branch"])
    issue = parse_refs(pull.get("body"), repository)

    merged = api(
        "PUT",
        f"/repos/{repository}/pulls/{number}/merge",
        {"sha": head, "merge_method": policy["merge_method"]},
    )
    if not merged.get("merged"):
        raise SystemExit(f"MERGE_REFUSED:{number}:{merged.get('message')}")
    merge_sha = merged["sha"]

    readback = api("GET", f"/repos/{repository}/pulls/{number}")
    if not readback.get("merged"):
        raise SystemExit(f"MERGE_READBACK_ABSENT:{number}")

    markers = land_markers(repository, number, head, merge_sha)
    body = api("GET", f"/repos/{repository}/issues/{issue}").get("body")
    api(
        "PATCH",
        f"/repos/{repository}/issues/{issue}",
        {
            "body": stamp(body, markers),
            "state": "closed",
            "state_reason": "completed",
        },
    )
    closed = api("GET", f"/repos/{repository}/issues/{issue}")
    if closed["state"] != "closed":
        raise SystemExit(f"ISSUE_CLOSE_READBACK_ABSENT:{issue}:{closed['state']}")

    anchor = post_receipt_anchor(repository, number, merge_sha)
    receipt_comment = post_marker_receipt(repository, issue, number, markers)

    # Read the pair back rather than assert the write succeeded. This cannot
    # gate the land - the merge already happened - but it decides the exit
    # code, which is the only durable surface left at this point.
    surface = marker_surface(
        closed.get("body"),
        [
            item.get("body")
            for item in api("GET", f"/repos/{repository}/issues/{issue}/comments?per_page=100")
            if isinstance(item, dict)
        ],
    )

    print(
        json.dumps(
            {
                "landed_pull_request": number,
                "head_sha": head,
                "merge_sha": merge_sha,
                "closed_issue": issue,
                "receipt_anchor": anchor,
                "marker_receipt": receipt_comment,
                "marker_surface": surface,
                "verified_base": verified_base,
            },
            indent=2,
            sort_keys=True,
        )
    )

    # This land wrote both surfaces, so anything but LANDED means a write did
    # not take, and the job goes red. `post_marker_receipt` is N-class and
    # never raises: before this line its failure printed the word 'failed' into
    # an ephemeral Actions log and exited 0 - the same exit as a clean land -
    # after which the Issue read RECEIPT_ABSENT, and NO_LAND once any later
    # whole-body edit took the body copy too. That is #117's own incident
    # reading as an Issue that was never landed, which is the state this atom
    # exists to make impossible.
    #
    # `audit_issue` deliberately keeps the narrower predicate: on an arbitrary
    # Issue only MARKERS_LOST names a loss, because RECEIPT_ABSENT is every
    # land older than this commit and NO_LAND is every unlanded Issue. Here,
    # immediately after this land, neither is admissible.
    #
    # The merge is done and read back before this returns; the printed record
    # names the merge sha. A non-zero exit here is 'the receipt did not land',
    # never 'the pull request did not merge'.
    return 0 if surface == LANDED else 1


if __name__ == "__main__":
    raise SystemExit(main())
