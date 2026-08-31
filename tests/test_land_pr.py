"""Landing ceremony: the Refs contract and the Issue marker stamp.

Only the two pure functions are exercised. Everything else in `land_pr.py` is a
GitHub API call whose refusal is the provider's own, and is asserted by the
read-backs inside the script rather than by a mock of the provider here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import land_pr  # noqa: E402

REPOSITORY = "ed3c/ai-content-notes"


def test_policy_names_this_repository_and_a_merge_method() -> None:
    policy = json.loads(
        (REPOSITORY_ROOT / "policy" / "github.json").read_text(encoding="utf-8")
    )
    assert policy["repository"] == REPOSITORY
    assert policy["default_branch"] == "main"
    assert policy["merge_method"] in {"merge", "squash", "rebase"}


def test_exactly_one_refs_line_yields_the_issue_number() -> None:
    body = f"Refs {REPOSITORY}#79"
    assert land_pr.parse_refs(body, REPOSITORY) == 79


def test_refs_line_is_recognised_among_other_lines() -> None:
    body = f"prose above\n\nRefs {REPOSITORY}#12\n\nprose below\n"
    assert land_pr.parse_refs(body, REPOSITORY) == 12


@pytest.mark.parametrize(
    "body",
    [
        None,
        "",
        "no refs line at all",
        f"Closes {REPOSITORY}#3",
        f"Refs {REPOSITORY}#3 and something else",
        f"Refs {REPOSITORY}#3\nRefs {REPOSITORY}#4",
    ],
)
def test_a_body_without_exactly_one_refs_line_refuses(body: str | None) -> None:
    with pytest.raises(SystemExit) as refusal:
        land_pr.parse_refs(body, REPOSITORY)
    assert str(refusal.value).startswith("REFS_LINE_COUNT:")


def test_a_foreign_repository_refs_line_refuses() -> None:
    with pytest.raises(SystemExit) as refusal:
        land_pr.parse_refs("Refs other/elsewhere#7", REPOSITORY)
    assert str(refusal.value) == "REFS_FOREIGN_REPOSITORY:other/elsewhere"


def test_stamp_appends_markers_to_a_body_that_has_none() -> None:
    stamped = land_pr.stamp("issue text", {"state": "landed", "head": "a" * 40})
    assert stamped.startswith("issue text\n")
    assert "<!-- landing-state: landed -->" in stamped
    assert f"<!-- landing-head: {'a' * 40} -->" in stamped


def test_stamp_replaces_an_existing_marker_in_place_without_duplicating() -> None:
    first = land_pr.stamp("issue text", {"state": "landed"})
    second = land_pr.stamp(first, {"state": "relanded"})
    assert second.count("<!-- landing-state:") == 1
    assert "<!-- landing-state: relanded -->" in second
    assert second.startswith("issue text\n")


def test_stamp_of_an_absent_body_still_produces_the_markers() -> None:
    stamped = land_pr.stamp(None, {"state": "landed"})
    assert stamped.strip() == "<!-- landing-state: landed -->"
