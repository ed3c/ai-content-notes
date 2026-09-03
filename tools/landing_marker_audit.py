#!/usr/bin/env python3
"""Report whether each landed Issue's `landing-*` marker block conforms.

`scripts/land_pr.py` stamps a marker block into the Issue a landing pull
request's `Refs` line names, and `docs/git/MACHINE_LANDING.md` states what that
block means. Until this reader, nothing consumed it. On the default branch the
string `landing-` occurred in exactly three files - the producer, the producer's
own unit test (which only ever stamps synthetic bodies), and the document
describing it - so no committed check ever compared a *provider* body against
the contract. Two corruptions were caught by a person reading an issue by hand
(#117, #120), and a third was not caught at all: #98 has sat `CLOSED` since
2026-09-03 with a marker block missing the key that names the pull request that
landed it, which is the contract #98 itself defines.

This reader states the difference. Its input is a curated snapshot of what the
provider returned - every land, and every marker-shaped line with its line
number - and its output is one row per landed Issue:

    CONFORMING      the live block names the newest land, and every
                    per-pull-request row present agrees with a recorded land
    NON_CONFORMING  the live block is absent, incomplete, or names something
                    other than what landed
    UNSTAMPED       the Issue carries no marker line at all - a land that left
                    no trace; a distinct state, never a pass

The contract is not restated here. `land_pr.land_markers` is the only producer
of a land's marker keys, so this reader asks it what the newest land should
have written and compares. A key added or renamed there moves this check with
it; a check that hardcoded the key set would silently keep passing. The one
thing the producer cannot say is *when* it began writing a key, so the single
instant at which the per-pull-request rows entered the contract is recorded
below; a land older than that is not asked for rows its producer never wrote.

The live block is the *trailing* contiguous run of marker-shaped lines. Marker
shaped text elsewhere in a body is quoted prose - an issue about markers quotes
markers - and is reported as `quoted_outside_block` rather than read as state.
That is the same span `stamp()` should edit and, per #120, does not; this
reader reports the discrepancy, it does not fix the writer.

Reading is zero-network: the audit touches the snapshot and nothing else, so it
runs in a test and in a checkout with no token. A row is only ever as good as
its snapshot entry, which is why every row carries the body digest, byte count
and line count it was read from, and why the snapshot records `read_back_at`
and the rule it was curated under.

`--curate` is the other half, and the reason those digests are worth recording:
it re-reads the provider and prints a fresh snapshot, so `body_sha256` is a
number something can resolve again rather than a decoration. The ceiling stays
exactly what it was - nothing here sees a land, or a body edit, after
`read_back_at` - but it is now payable in one command instead of being a
permanent property of the file. It is not idle: three lands merged between this
snapshot's first curation and its own.

Owner: ed3c/ai-content-notes#125.

    python3 tools/landing_marker_audit.py
    python3 tools/landing_marker_audit.py --json
    python3 tools/landing_marker_audit.py --strict   # exit 1 if any row is not CONFORMING
    python3 tools/landing_marker_audit.py --curate > docs/closure-audit/landing-marker-snapshot.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT = ROOT / "docs" / "closure-audit" / "landing-marker-snapshot.json"

sys.path.insert(0, str(ROOT / "scripts"))

from land_pr import MARKER_LINE, REFS_LINE, land_markers  # noqa: E402

CONFORMING = "CONFORMING"
NON_CONFORMING = "NON_CONFORMING"
UNSTAMPED = "UNSTAMPED"

# The instant the per-pull-request rows became part of the contract: the merge
# of PR #119 (`dfb3fcb79842ae834517704634391945d465c005`), which landed
# ed3c/ai-content-notes#98 and added the `pr-<n>-*` keys to `land_markers`.
# Strictly after, because `land.yml` checks out the default branch *before* the
# merge, so #98's own land was stamped by the producer it replaced. A land
# older than this is not asked for rows its producer never wrote; a land newer
# than it is. A merge SHA is immutable provider truth and the timestamp beside
# it recomputes from `pulls/119.merged_at`.
PER_PULL_REQUEST_ROWS_AFTER = "2026-09-03T04:23:07Z"

def parse_marker(text: str) -> tuple[str, str] | None:
    """Return the `(key, value)` a marker line carries, or None if it is not one.

    The grammar is `land_pr.MARKER_LINE`, the one expression `stamp` matches
    keys with, rather than a second copy here. A copy diverged on its first
    day: it admitted `.` in a key, so `<!-- landing-pr.1-head: … -->` read as
    live state to this reader and as an unrecognised key to `stamp`, which
    would then have appended a duplicate rather than replacing it.
    """
    found = MARKER_LINE.match(text)
    return (found.group(1), found.group(2)) if found else None


def live_block(marker_lines: list[dict], body_lines: int) -> list[dict]:
    """The trailing contiguous run of marker lines, i.e. the block a land owns.

    A body whose last line is not a marker has no live block even if it quotes
    markers higher up: `stamp` appends to the end, so anything not touching the
    end was not written by a land.

    Ceiling, measured rather than assumed. This is a second implementation of
    `land_pr.split_marker_block`'s rule, because the snapshot records line
    *numbers* and not the body's blank lines, and `split_marker_block` decides
    the end of the body by skipping trailing blank ones. So a body ending in a
    blank line reads as having no live block here while `stamp` still finds
    one. On the committed snapshot the two agree on 23 rows of 23, checked by
    reconstructing each body from its line records; the divergence is latent,
    not live, and curing it means the snapshot recording where the body's
    content ends rather than how many lines it has.
    """
    block: list[dict] = []
    expected = body_lines
    for entry in reversed(marker_lines):
        if entry["line"] != expected:
            break
        block.insert(0, entry)
        expected -= 1
    return block


def audit_issue(row: dict, repository: str) -> dict:
    """Classify one snapshot row against what its newest land should have stamped."""
    block = live_block(row["marker_lines"], row["body_lines"])
    quoted = [
        entry["line"] for entry in row["marker_lines"] if entry not in block
    ]
    markers = {}
    unparsed = []
    for entry in block:
        parsed = parse_marker(entry["text"])
        if parsed is None:  # pragma: no cover - live_block only admits marker lines
            unparsed.append(entry["line"])
        else:
            markers[parsed[0]] = parsed[1]

    lands = sorted(row["lands"], key=lambda land: land["merged_at"])
    newest = lands[-1]
    expected = land_markers(repository, newest["pull_request"], newest["head"], newest["merge"])
    pointer = {key: value for key, value in expected.items() if not key.startswith("pr-")}

    # Every recorded land supplies the per-pull-request rows it is allowed to
    # have written; a `pr-*` row naming anything else is a marker for a land
    # this repository has no record of. Rows are *required* only from a land
    # that merged after the producer began writing them.
    recorded: dict[str, str] = {}
    required: dict[str, str] = {}
    for land in lands:
        rows = {
            key: value
            for key, value in land_markers(
                repository, land["pull_request"], land["head"], land["merge"]
            ).items()
            if key.startswith("pr-")
        }
        recorded.update(rows)
        if land["merged_at"] > PER_PULL_REQUEST_ROWS_AFTER:
            required.update(rows)

    findings = [
        f"{key}: expected {value!r}, block says {markers.get(key)!r}"
        for key, value in {**pointer, **required}.items()
        if markers.get(key) != value
    ]
    findings.extend(
        f"{key}: names no recorded land of this Issue ({value!r})"
        for key, value in sorted(markers.items())
        if key.startswith("pr-") and recorded.get(key) != value
    )
    findings.extend(f"line {line}: marker-shaped line the parser could not read" for line in unparsed)

    if not row["marker_lines"]:
        status = UNSTAMPED
    elif findings:
        status = NON_CONFORMING
    else:
        status = CONFORMING
    return {
        "issue": row["issue"],
        "status": status,
        "lands": [land["pull_request"] for land in lands],
        "newest_land": newest["pull_request"],
        "block_lines": [entry["line"] for entry in block],
        "quoted_outside_block": quoted,
        "findings": findings,
        "note": row.get("note"),
        "body_sha256": row["body_sha256"],
    }


def audit(snapshot: dict) -> dict:
    rows = [audit_issue(row, snapshot["repository"]) for row in snapshot["issues"]]
    rows.sort(key=lambda row: row["issue"])
    return {
        "schema": "landing-marker-report@1",
        "repository": snapshot["repository"],
        "read_back_at": snapshot["read_back_at"],
        "rows": rows,
        "summary": {
            "landed_issues": len(rows),
            "conforming": sum(1 for row in rows if row["status"] == CONFORMING),
            "non_conforming": sum(1 for row in rows if row["status"] == NON_CONFORMING),
            "unstamped": sum(1 for row in rows if row["status"] == UNSTAMPED),
            "not_conforming": [
                row["issue"] for row in rows if row["status"] != CONFORMING
            ],
        },
    }


def load_snapshot(path: Path) -> dict:
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    if snapshot.get("schema") != "landing-marker-snapshot@1":
        raise ValueError(f"unexpected snapshot schema: {snapshot.get('schema')!r}")
    return snapshot


CURATION_RULE = (
    "Every merged pull request of this repository whose body carries exactly one "
    "'Refs <repository>#<n>' line naming this repository is a land of issue <n>, by "
    "land_pr.REFS_LINE - the same expression land_pr.parse_refs binds a land with. "
    "For each such issue the provider's issue body was read once, at read_back_at, and "
    "every line matching land_pr.MARKER_LINE was recorded with its 1-based line number, "
    "together with the body's sha256 over raw UTF-8 bytes and its line count. Nothing "
    "is normalised, summarised or inferred; the reader does the extraction. Regenerate "
    "with: python3 tools/landing_marker_audit.py --curate > "
    "docs/closure-audit/landing-marker-snapshot.json"
)

# `gh` is the only network this file has, and it is reached only from `--curate`.
# Reading the snapshot stays zero-network, which is why the audit can run in a
# test and in a checkout with no token.
GH = "gh"


def gh_json(*args: str):
    done = subprocess.run([GH, "api", *args], capture_output=True)
    if done.returncode != 0:
        raise SystemExit(f"GH_API_REFUSED:{' '.join(args)}:{done.stderr.decode()[:400]}")
    return json.loads(done.stdout)


def provider_now() -> str:
    """The provider's own clock, not this host's.

    `read_back_at` is the instant everything below it stops being true, so it is
    read off the same wire the bodies came from: a skewed host clock would make
    the staleness ceiling claim more than it can.
    """
    done = subprocess.run([GH, "api", "-i", "meta"], capture_output=True)
    if done.returncode != 0:
        raise SystemExit(f"GH_API_REFUSED:meta:{done.stderr.decode()[:200]}")
    for line in done.stdout.decode("utf-8", "replace").splitlines():
        if line.lower().startswith("date:"):
            stamp = parsedate_to_datetime(line.split(":", 1)[1].strip())
            return stamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    raise SystemExit("GH_API_NO_DATE_HEADER:meta")


def curate(
    repository: str,
    notes: dict[int, str | None] | None = None,
    call: Any = None,
    now: Any = None,
) -> dict:
    """Rebuild the snapshot from provider bytes. Reads only; writes nothing.

    This is the producer the snapshot's rows previously did not have. Without
    it every `body_sha256` in the file was a number nothing could re-resolve,
    and a snapshot goes stale the moment the next pull request merges - three
    lands happened between this file's first curation and its own land. The
    ceiling is not removed by having a producer; it is made payable.

    `call` and `now` are injected the way `scripts/land_pr.py` injects its own
    provider, so the binding rule below - which merged pull requests count as
    lands - is exercised by a test instead of only by a live run.
    """
    call = gh_json if call is None else call
    read_back_at = (provider_now if now is None else now)()
    pulls = call(
        "--paginate",
        f"repos/{repository}/pulls?state=closed&per_page=100",
        "--jq",
        "[.[] | {number, merged_at, merge_commit_sha, head: .head.sha, body}]",
    )
    lands: dict[int, list[dict]] = {}
    for pull in sorted((item for item in pulls if item["merged_at"]), key=lambda p: p["merged_at"]):
        hits = [
            match
            for match in (
                REFS_LINE.match(line.strip()) for line in (pull["body"] or "").splitlines()
            )
            if match and match.group(1) == repository
        ]
        if len(hits) != 1:  # not a land of this repository by land_pr's own rule
            continue
        lands.setdefault(int(hits[0].group(2)), []).append(
            {
                "pull_request": pull["number"],
                "head": pull["head"],
                "merge": pull["merge_commit_sha"],
                "merged_at": pull["merged_at"],
            }
        )

    previous = (
        {row["issue"]: row.get("note") for row in load_snapshot(DEFAULT_SNAPSHOT)["issues"]}
        if notes is None
        else notes
    )
    issues = []
    for number in sorted(lands):
        data = call(f"repos/{repository}/issues/{number}")
        body = data.get("body") or ""
        lines = body.splitlines()
        issues.append(
            {
                "issue": number,
                "state": data["state"],
                "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "body_utf8_bytes": len(body.encode("utf-8")),
                "body_lines": len(lines),
                "marker_lines": [
                    {"line": index, "text": text}
                    for index, text in enumerate(lines, start=1)
                    if MARKER_LINE.match(text)
                ],
                "lands": lands[number],
                # Notes are the one hand-written field, so a re-curation keeps
                # them rather than silently dropping a row's explanation.
                "note": previous.get(number),
            }
        )
    return {
        "schema": "landing-marker-snapshot@1",
        "repository": repository,
        "read_back_at": read_back_at,
        "curated_under": CURATION_RULE,
        "issues": issues,
    }


def render(report: dict) -> str:
    lines = [
        f"landing markers  {report['repository']}  read_back_at={report['read_back_at']}"
    ]
    for row in report["rows"]:
        lines.append(
            f"  #{row['issue']:<4} {row['status']:<14} "
            f"lands={','.join(str(number) for number in row['lands'])}"
        )
        if row["status"] == UNSTAMPED:
            # Every pointer key is missing by definition; the note is the finding.
            lines.append(f"        {row['note'] or 'no marker line in the body'}")
        for finding in row["findings"] if row["status"] == NON_CONFORMING else []:
            lines.append(f"        {finding}")
        if row["quoted_outside_block"]:
            lines.append(
                "        quoted marker-shaped lines outside the live block: "
                + ",".join(str(line) for line in row["quoted_outside_block"])
            )
    summary = report["summary"]
    lines.append(
        f"  landed_issues={summary['landed_issues']} conforming={summary['conforming']} "
        f"non_conforming={summary['non_conforming']} unstamped={summary['unstamped']}"
    )
    outstanding = summary["not_conforming"]
    lines.append(
        "  NOT_CONFORMING: "
        + (", ".join(f"#{number}" for number in outstanding) if outstanding else "none")
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 when any landed Issue's marker block does not conform",
    )
    parser.add_argument(
        "--curate",
        action="store_true",
        help="re-read the provider and print a fresh snapshot to stdout; needs `gh`",
    )
    args = parser.parse_args(argv)

    if args.curate:
        print(
            json.dumps(
                curate(load_snapshot(args.snapshot)["repository"]), indent=2, sort_keys=True
            )
        )
        return 0

    report = audit(load_snapshot(args.snapshot))
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else render(report))
    if args.strict and report["summary"]["not_conforming"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
