"""ed3c/ai-content-notes#125 - the `landing-*` marker surface gets a reader.

The invariant under test:

    a landed Issue carries a marker block naming the land that closed it

`scripts/land_pr.py` produces that block and `docs/git/MACHINE_LANDING.md`
states what it means; before this atom nothing consumed it. `git grep -c
'landing-'` on `ac10987c85c3f2cc01ca302c76e1c2eb6e8ea88a` returned three files -
the producer, this repository's unit test for the producer's two pure
functions, and the document - none of which ever sees a provider body. #98 sat
`CLOSED` with a block missing the key naming its own landing pull request, and
no check in the repository could say so.

Nothing here is hardcoded to the snapshot's current contents. `verify.yml`
replaces a candidate's `tests/` with the default branch's, so a test asserting
"the snapshot says exactly this" would make the next re-curation unlandable -
the class ed3c/ai-content-notes#104 measured and #109 rewrote. Every assertion
below is relational: the reader is checked against whatever the snapshot
happens to hold, and the planted-defect controls build their own rows.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "scripts"))

from land_pr import land_markers  # noqa: E402
from landing_marker_audit import (  # noqa: E402
    CONFORMING,
    DEFAULT_SNAPSHOT,
    NON_CONFORMING,
    PER_PULL_REQUEST_ROWS_AFTER,
    UNSTAMPED,
    audit,
    audit_issue,
    live_block,
    load_snapshot,
    main,
    parse_marker,
)

REPOSITORY = "ed3c/ai-content-notes"
# A land after the per-pull-request rows entered the contract (PR #124 landing
# #110) and one before it (PR #116 landing #113). Both are provider facts.
LAND = {
    "pull_request": 124,
    "head": "6049d9aa9150ba81661fc758a444a7937ffbc97c",
    "merge": "ac10987c85c3f2cc01ca302c76e1c2eb6e8ea88a",
    "merged_at": "2026-09-03T04:47:53Z",
}
LAND_BEFORE_THE_ROWS = {
    "pull_request": 116,
    "head": "9cebf79f9136eb4ba851f27a26ebba10b2ba307f",
    "merge": "3ba1564a572d9e61c294ece9f7e4084d25e75e87",
    "merged_at": "2026-09-03T03:59:45Z",
}


def snapshot() -> dict:
    return load_snapshot(DEFAULT_SNAPSHOT)


def stamped_row(prose: int = 3, land: dict | None = None, **overrides) -> dict:
    """A snapshot row for one Issue whose block is exactly what the land wrote."""
    land = LAND if land is None else land
    markers = land_markers(REPOSITORY, land["pull_request"], land["head"], land["merge"])
    lines = [f"<!-- landing-{key}: {value} -->" for key, value in markers.items()]
    row = {
        "issue": 113,
        "state": "closed",
        "body_sha256": "0" * 64,
        "body_utf8_bytes": 1,
        "body_lines": prose + len(lines),
        "marker_lines": [
            {"line": prose + offset, "text": text} for offset, text in enumerate(lines, start=1)
        ],
        "lands": [land],
        "note": None,
    }
    row.update(overrides)
    return row


def test_snapshot_is_well_formed_and_says_where_it_came_from() -> None:
    data = snapshot()
    assert data["repository"] == REPOSITORY
    assert data["read_back_at"]
    assert data["curated_under"]
    issues = [row["issue"] for row in data["issues"]]
    assert len(issues) == len(set(issues))

    landing_pulls = [
        land["pull_request"] for row in data["issues"] for land in row["lands"]
    ]
    # One pull request lands one Issue: a pull request appearing under two
    # Issues would mean the `Refs` contract was violated upstream of here.
    assert len(landing_pulls) == len(set(landing_pulls))

    for row in data["issues"]:
        assert row["lands"], row["issue"]
        assert len(row["body_sha256"]) == 64
        assert row["body_utf8_bytes"] >= 0
        lines = [entry["line"] for entry in row["marker_lines"]]
        assert lines == sorted(lines), row["issue"]
        assert all(1 <= line <= row["body_lines"] for line in lines), row["issue"]
        for land in row["lands"]:
            assert len(land["head"]) == 40 and len(land["merge"]) == 40, row["issue"]


def test_every_unstamped_row_says_why_rather_than_shrugging() -> None:
    for row in audit(snapshot())["rows"]:
        if row["status"] == UNSTAMPED:
            assert row["note"], row["issue"]


def test_every_row_recomputes_from_the_lines_the_snapshot_recorded() -> None:
    # An independent recomputation, deliberately simpler than the reader: the
    # trailing run of marker lines, parsed, compared to what the newest land
    # should have written.
    data = snapshot()
    for row in data["issues"]:
        block = live_block(row["marker_lines"], row["body_lines"])
        markers = dict(
            parsed for entry in block if (parsed := parse_marker(entry["text"])) is not None
        )
        newest = sorted(row["lands"], key=lambda land: land["merged_at"])[-1]
        expected = {
            key: value
            for key, value in land_markers(
                REPOSITORY, newest["pull_request"], newest["head"], newest["merge"]
            ).items()
            if not key.startswith("pr-")
        }
        reported = audit_issue(row, REPOSITORY)
        if not row["marker_lines"]:
            assert reported["status"] == UNSTAMPED
        elif all(markers.get(key) == value for key, value in expected.items()):
            assert reported["status"] in {CONFORMING, NON_CONFORMING}
        else:
            assert reported["status"] == NON_CONFORMING, row["issue"]
            assert reported["findings"], row["issue"]


def test_a_block_that_matches_the_producer_is_the_green_baseline() -> None:
    reported = audit_issue(stamped_row(), REPOSITORY)
    assert reported["status"] == CONFORMING
    assert reported["findings"] == []
    assert reported["quoted_outside_block"] == []


def without_key(row: dict, key: str) -> dict:
    """The same row with one marker line removed and the block still trailing."""
    kept = [entry for entry in row["marker_lines"] if f"landing-{key}:" not in entry["text"]]
    assert len(kept) == len(row["marker_lines"]) - 1, key
    row = dict(row, body_lines=row["body_lines"] - 1)
    row["marker_lines"] = [
        {"line": row["body_lines"] - len(kept) + offset, "text": entry["text"]}
        for offset, entry in enumerate(kept, start=1)
    ]
    return row


def test_the_reader_demands_exactly_the_keys_the_producer_writes() -> None:
    # The contract is not restated in the reader. Dropping any one key the
    # producer emits has to be a finding, so a key added to `land_markers`
    # is checked here without editing this file.
    produced = land_markers(REPOSITORY, LAND["pull_request"], LAND["head"], LAND["merge"])
    assert LAND["merged_at"] > PER_PULL_REQUEST_ROWS_AFTER  # every key is required of it
    for key in produced:
        reported = audit_issue(without_key(stamped_row(), key), REPOSITORY)
        assert reported["status"] == NON_CONFORMING, key
        assert any(finding.startswith(f"{key}:") for finding in reported["findings"]), key


def test_a_land_older_than_a_key_is_not_asked_for_it() -> None:
    # The other arm, and the reason the boundary is recorded at all: #113
    # landed before the per-pull-request rows existed, and demanding rows its
    # producer never wrote would report a defect that is not there.
    row = stamped_row(land=LAND_BEFORE_THE_ROWS)
    assert LAND_BEFORE_THE_ROWS["merged_at"] < PER_PULL_REQUEST_ROWS_AFTER
    for key in ("pr-116-head", "pr-116-merge"):
        row = without_key(row, key)
    assert audit_issue(row, REPOSITORY)["status"] == CONFORMING


def test_the_missing_landed_pr_key_is_what_98_actually_reads_as() -> None:
    # The planted form of the live defect this atom was filed for: a block
    # carrying state/head/merge and no `landed-pr`.
    reported = audit_issue(without_key(stamped_row(), "landed-pr"), REPOSITORY)
    assert reported["status"] == NON_CONFORMING
    assert reported["findings"] == [
        f"landed-pr: expected '{REPOSITORY}#{LAND['pull_request']}', block says None"
    ]


def test_a_block_naming_a_different_merge_is_refused() -> None:
    row = stamped_row()
    row["marker_lines"] = [
        {
            "line": entry["line"],
            "text": entry["text"].replace(LAND["merge"], "d" * 40),
        }
        for entry in row["marker_lines"]
    ]
    reported = audit_issue(row, REPOSITORY)
    assert reported["status"] == NON_CONFORMING
    assert any(finding.startswith("merge:") for finding in reported["findings"])


def test_a_per_pull_request_row_naming_no_recorded_land_is_refused() -> None:
    row = stamped_row()
    row["marker_lines"].append(
        {"line": row["body_lines"] + 1, "text": f"<!-- landing-pr-999-merge: {'e' * 40} -->"}
    )
    row["body_lines"] += 1
    reported = audit_issue(row, REPOSITORY)
    assert reported["status"] == NON_CONFORMING
    assert any("pr-999-merge" in finding for finding in reported["findings"])


def test_marker_shaped_prose_above_the_block_is_quoted_not_state() -> None:
    # ed3c/ai-content-notes#120: an Issue about markers quotes markers. A
    # reader that scanned the whole body would read the quote as live state -
    # which is exactly how #98's block lost its `landed-pr` in the first place.
    row = stamped_row()
    quote = {"line": 1, "text": f"<!-- landing-landed-pr: {REPOSITORY}#94 -->"}
    row["marker_lines"] = [quote, *row["marker_lines"]]
    reported = audit_issue(row, REPOSITORY)
    assert reported["status"] == CONFORMING
    assert reported["quoted_outside_block"] == [1]


def test_a_block_that_does_not_reach_the_end_of_the_body_is_not_live() -> None:
    row = stamped_row()
    row["body_lines"] += 1  # one line of prose appended after the block
    reported = audit_issue(row, REPOSITORY)
    assert reported["status"] == NON_CONFORMING
    assert reported["block_lines"] == []
    assert reported["quoted_outside_block"] == [
        entry["line"] for entry in row["marker_lines"]
    ]


def test_an_issue_with_no_marker_line_is_unstamped_not_refused_silently() -> None:
    row = stamped_row()
    row["marker_lines"] = []
    reported = audit_issue(row, REPOSITORY)
    assert reported["status"] == UNSTAMPED
    assert reported["status"] != CONFORMING


def test_the_newest_land_is_the_one_the_pointer_must_name() -> None:
    # Two lands, oldest first in the file: the pointer names the newest, and a
    # pointer still naming the older land is a finding.
    older = dict(LAND_BEFORE_THE_ROWS, pull_request=95, head="8" * 40, merge="f" * 40,
                 merged_at="2026-09-01T08:20:14Z")
    row = stamped_row(land=LAND)
    row["lands"] = [LAND, older]
    assert audit_issue(row, REPOSITORY)["status"] == CONFORMING

    stale = stamped_row(land=older)
    stale["lands"] = [LAND, older]
    reported = audit_issue(stale, REPOSITORY)
    assert reported["status"] == NON_CONFORMING
    assert reported["newest_land"] == LAND["pull_request"]


def test_strict_exit_code_follows_the_report(tmp_path: Path) -> None:
    report = audit(snapshot())
    assert main([]) == 0
    assert main(["--strict"]) == (1 if report["summary"]["not_conforming"] else 0)

    conforming = copy.deepcopy(snapshot())
    conforming["issues"] = [stamped_row()]
    path = tmp_path / "conforming-snapshot.json"
    path.write_text(json.dumps(conforming), encoding="utf-8")
    assert main(["--strict", "--snapshot", str(path)]) == 0
    assert main(["--strict", "--json", "--snapshot", str(path)]) == 0

    broken = copy.deepcopy(conforming)
    broken["issues"] = [stamped_row(), stamped_row(issue=999, marker_lines=[])]
    path = tmp_path / "broken-snapshot.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    assert main(["--strict", "--snapshot", str(path)]) == 1


def test_an_unexpected_snapshot_schema_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "wrong-schema.json"
    path.write_text(json.dumps({"schema": "something-else@1"}), encoding="utf-8")
    try:
        load_snapshot(path)
    except ValueError:
        return
    raise AssertionError("a foreign snapshot schema was accepted")
