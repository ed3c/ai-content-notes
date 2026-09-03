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

It reads the snapshot and nothing else: no network, no GitHub API, no Drive.
A row is only ever as good as its snapshot entry, which is why every row
carries the body digest and byte count it was read from, and why the snapshot
records `read_back_at` and the rule it was curated under. Nothing here detects
a land that happened after the snapshot was taken, or a body edited since.

Owner: ed3c/ai-content-notes#125.

    python3 tools/landing_marker_audit.py
    python3 tools/landing_marker_audit.py --json
    python3 tools/landing_marker_audit.py --strict   # exit 1 if any row is not CONFORMING
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT = ROOT / "docs" / "closure-audit" / "landing-marker-snapshot.json"

sys.path.insert(0, str(ROOT / "scripts"))

from land_pr import MARKER_PREFIX, land_markers  # noqa: E402

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

MARKER_LINE = re.compile(rf"^<!--\s*{MARKER_PREFIX}-([A-Za-z0-9._-]+):\s*(.*?)\s*-->[ \t]*$")


def parse_marker(text: str) -> tuple[str, str] | None:
    """Return the `(key, value)` a marker line carries, or None if it is not one."""
    found = MARKER_LINE.match(text)
    return (found.group(1), found.group(2)) if found else None


def live_block(marker_lines: list[dict], body_lines: int) -> list[dict]:
    """The trailing contiguous run of marker lines, i.e. the block a land owns.

    A body whose last line is not a marker has no live block even if it quotes
    markers higher up: `stamp` appends to the end, so anything not touching the
    end was not written by a land.
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
    args = parser.parse_args(argv)

    report = audit(load_snapshot(args.snapshot))
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else render(report))
    if args.strict and report["summary"]["not_conforming"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
