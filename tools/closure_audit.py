#!/usr/bin/env python3
"""Report whether each closed issue's acceptance-named artifact is readable here.

`CLOSED(issue)` is not evidence that the artifact its acceptance names reached
the default branch. A receipt comment naming a draft head closes an issue as
convincingly as a merge does, and nothing downstream re-reads the tree, so a
whole subtree can read `CLOSED` while none of its bytes are reachable from
`main`. `RECEIPT_COMMENT != MERGE`; `DRAFT_HEAD != DEFAULT_BRANCH`.

This reader states the difference. Its input is the curated ledger of this
repository's closed issues and the repository-relative paths each acceptance
names; its output is one row per closure:

    PRESENT         every named path resolves inside the tree
    ABSENT          at least one named path does not - CLOSURE_WITHOUT_ARTIFACT
    NO_PATH_NAMED   the acceptance named no repository path, so nothing here
                    can check it; a distinct state, never a pass

It reads the working tree and nothing else: no network, no GitHub API, no Drive.
A row is only ever as good as its ledger entry, which is why the ledger records
the rule it was curated under rather than asserting authority it does not have.

Owner: ed3c/ai-content-notes#61.

    python3 tools/closure_audit.py
    python3 tools/closure_audit.py --json
    python3 tools/closure_audit.py --strict   # exit 1 if any closure is bare
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "docs" / "closure-audit" / "closed-issue-artifacts.json"

PRESENT = "PRESENT"
ABSENT = "ABSENT"
NO_PATH_NAMED = "NO_PATH_NAMED"
CLOSURE_WITHOUT_ARTIFACT = "CLOSURE_WITHOUT_ARTIFACT"


def checked_relative(raw: str) -> PurePosixPath:
    """Reject any ledger path that could resolve outside the audited tree.

    A row that escapes the root would report PRESENT against a file this
    repository does not own, which is the exact silent widening the audit
    exists to refuse.
    """
    path = PurePosixPath(raw)
    if not raw or raw.startswith("/") or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"ledger path escapes the repository: {raw!r}")
    return path


def load_ledger(path: Path) -> dict:
    ledger = json.loads(path.read_text(encoding="utf-8"))
    if ledger.get("schema") != "closure-audit-ledger@1":
        raise ValueError(f"unexpected ledger schema: {ledger.get('schema')!r}")
    return ledger


def audit(ledger: dict, root: Path) -> dict:
    """Resolve every ledger row against `root` and classify the closure."""
    rows = []
    for closure in ledger["closures"]:
        named = list(closure.get("artifacts", []))
        artifacts = [
            {
                "path": raw,
                "present": root.joinpath(*checked_relative(raw).parts).exists(),
            }
            for raw in named
        ]
        missing = [entry["path"] for entry in artifacts if not entry["present"]]
        if not named:
            status = NO_PATH_NAMED
        elif missing:
            status = ABSENT
        else:
            status = PRESENT
        rows.append(
            {
                "issue": closure["issue"],
                "title": closure["title"],
                "status": status,
                "artifacts": artifacts,
                "missing": missing,
                "verdict": CLOSURE_WITHOUT_ARTIFACT if status == ABSENT else None,
                "note": closure.get("note"),
            }
        )
    rows.sort(key=lambda row: row["issue"])
    return {
        "schema": "closure-audit-report@1",
        "repository": ledger["repository"],
        "root": str(root),
        "rows": rows,
        "summary": {
            "closed": len(rows),
            "present": sum(1 for row in rows if row["status"] == PRESENT),
            "absent": sum(1 for row in rows if row["status"] == ABSENT),
            "no_path_named": sum(1 for row in rows if row["status"] == NO_PATH_NAMED),
            "closure_without_artifact": [
                row["issue"] for row in rows if row["verdict"] == CLOSURE_WITHOUT_ARTIFACT
            ],
        },
    }


def render(report: dict) -> str:
    lines = [f"closure audit  {report['repository']}  root={report['root']}"]
    for row in report["rows"]:
        line = f"  #{row['issue']:<4} {row['status']:<14}"
        if row["verdict"]:
            line += f" {row['verdict']} missing={','.join(row['missing'])}"
        elif row["status"] == NO_PATH_NAMED:
            line += f" {row['note'] or 'acceptance names no repository path'}"
        else:
            line += f" {len(row['artifacts'])} artifact(s)"
        lines.append(line)
    summary = report["summary"]
    lines.append(
        f"  closed={summary['closed']} present={summary['present']} "
        f"absent={summary['absent']} no_path_named={summary['no_path_named']}"
    )
    bare = summary["closure_without_artifact"]
    lines.append(
        "  CLOSURE_WITHOUT_ARTIFACT: "
        + (", ".join(f"#{number}" for number in bare) if bare else "none")
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 when any closure has an absent acceptance artifact",
    )
    args = parser.parse_args(argv)

    report = audit(load_ledger(args.ledger), args.root.resolve())
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else render(report))
    if args.strict and report["summary"]["closure_without_artifact"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
