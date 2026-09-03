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


# The #75 double-land, replayed from the SHAs recorded in ed3c/ai-content-notes#98.
FIRST_LAND = (95, "81389f92f14dcc305dc39effb4a41678db34655b", "f292deafbc0feca5dedacf27af8ce192f4a6314f")
SECOND_LAND = (97, "f60841314a857746356e4f86d7c93df8a90cca71", "cb011d188996c86e640bb1212c18e0a7030289ea")


def land(body: str | None, land_facts: tuple[int, str, str]) -> str:
    number, head, merge = land_facts
    return land_pr.stamp(body, land_pr.land_markers(REPOSITORY, number, head, merge))


def test_a_second_land_leaves_the_first_land_readable() -> None:
    # Planted defect control for #98: before the per-pull-request rows existed,
    # the second stamp replaced `landing-head` and `landing-merge` in place and
    # PR #95's two SHAs left the Issue body with nothing recording that they had
    # ever been there. Both lands must survive.
    first = land("issue text", FIRST_LAND)
    second = land(first, SECOND_LAND)

    for number, head, merge in (FIRST_LAND, SECOND_LAND):
        assert f"<!-- landing-pr-{number}-head: {head} -->" in second
        assert f"<!-- landing-pr-{number}-merge: {merge} -->" in second

    # and the unnamespaced pointer is the newest land, not an ambiguous mixture
    assert f"<!-- landing-landed-pr: {REPOSITORY}#97 -->" in second
    assert f"<!-- landing-head: {SECOND_LAND[1]} -->" in second
    assert f"<!-- landing-merge: {SECOND_LAND[2]} -->" in second
    assert second.count("<!-- landing-head:") == 1
    assert second.count("<!-- landing-merge:") == 1


def test_relanding_the_same_pull_request_is_idempotent() -> None:
    # The other direction: a retried land of one pull request must not grow a
    # second row set for it, or the ledger would count lands that never happened.
    once = land("issue text", SECOND_LAND)
    twice = land(once, SECOND_LAND)
    assert twice == once
    assert twice.count("<!-- landing-pr-97-head:") == 1


# The #98 corruption, replayed from the bytes recorded in ed3c/ai-content-notes#120.
# `<!-- landing-landed-pr: ... -->` sits at column 0 inside a fenced quotation two
# sections above the live block, because #98's own subject is these markers.
QUOTING_BODY = """\
## Instance 1

```text
#61 was closed by the machine on 2026-09-01 when PR #94 landed:

<!-- landing-landed-pr: ed3c/ai-content-notes#94 -->

PR #94's subject is `audit(closure): refuse a CLOSED issue whose acceptance
artifact is not here`.
```

## Evidence boundary

Two instances in two waves is what is claimed.
"""


def test_a_quoted_marker_line_is_not_the_live_block() -> None:
    # Planted defect control for #120: the pre-fix `re.subn(..., re.MULTILINE,
    # count=1)` rewrote this quotation to name the landing PR, and the live
    # block then never received a `landing-landed-pr` line at all, because that
    # key had already spent its one substitution on the quote.
    stamped = land(QUOTING_BODY, (119, "8" * 40, "d" * 40))

    assert "<!-- landing-landed-pr: ed3c/ai-content-notes#94 -->" in stamped
    assert stamped.startswith(QUOTING_BODY.rstrip("\n") + "\n<!-- landing-state: landed -->")
    _, block = land_pr.split_marker_block(stamped)
    assert f"<!-- landing-landed-pr: {REPOSITORY}#119 -->" in block
    assert sorted(land_pr.MARKER_LINE.match(line).group(1) for line in block) == [
        "head",
        "landed-pr",
        "merge",
        "pr-119-head",
        "pr-119-merge",
        "state",
    ]


def test_a_body_whose_quotation_is_the_whole_body_still_gains_a_live_block() -> None:
    # The quote must survive even when it is the only marker-shaped text there
    # is, and the block must be built beside it rather than on top of it.
    once = land(QUOTING_BODY, (119, "8" * 40, "d" * 40))
    twice = land(once, (121, "e" * 40, "f" * 40))
    assert once.count("<!-- landing-landed-pr: ed3c/ai-content-notes#94 -->") == 1
    assert twice.count("<!-- landing-landed-pr: ed3c/ai-content-notes#94 -->") == 1
    assert f"<!-- landing-landed-pr: {REPOSITORY}#121 -->" in twice
    assert f"<!-- landing-pr-119-head: {'8' * 40} -->" in twice


def test_split_marker_block_reads_a_quoting_body_as_carrying_no_block() -> None:
    """Both directions: an empty block is what "not landed" looks like here."""
    prefix, block = land_pr.split_marker_block(QUOTING_BODY)
    assert block == []
    assert "\n".join(prefix).rstrip("\n") == QUOTING_BODY.rstrip("\n")

    prefix, block = land_pr.split_marker_block(land(QUOTING_BODY, SECOND_LAND))
    assert len(block) == 6
    assert "\n".join(prefix).rstrip("\n") == QUOTING_BODY.rstrip("\n")


def test_land_markers_name_the_landing_pull_request_in_every_history_key() -> None:
    markers = land_pr.land_markers(REPOSITORY, 97, "f" * 40, "c" * 40)
    history = {key: value for key, value in markers.items() if key.startswith("pr-")}
    assert history == {"pr-97-head": "f" * 40, "pr-97-merge": "c" * 40}
    assert set(markers) - set(history) == {"state", "landed-pr", "head", "merge"}


def test_clean_pr_gets_exactly_one_anchor_comment() -> None:
    calls: list[tuple[str, str]] = []

    def fake(method: str, path: str, payload: dict | None = None):
        calls.append((method, path))
        if method == "GET" and "comments" in path:
            return [{"body": "ordinary review comment"}]
        if method == "GET":
            return {"merged_at": "2026-09-01T00:00:00Z"}
        assert "physical-receipt-anchor: pr=85 merge-commit=" + "c" * 40 in payload["body"]
        assert "merged-at=2026-09-01T00:00:00Z" in payload["body"]
        return {}

    assert land_pr.post_receipt_anchor(REPOSITORY, 85, "c" * 40, call=fake) == "posted"
    assert sum(1 for method, _ in calls if method == "POST") == 1


def test_existing_anchor_is_never_duplicated() -> None:
    def fake(method: str, path: str, payload: dict | None = None):
        if method == "GET" and "comments" in path:
            return [{"body": "physical-receipt-anchor: pr=85 merge-commit=old"}]
        raise AssertionError(f"unexpected call after existing anchor: {method} {path}")

    assert land_pr.post_receipt_anchor(REPOSITORY, 85, "c" * 40, call=fake) == "exists"


def test_provider_refusal_never_gates_the_land() -> None:
    # planted negative: a secondary-rate-limit SystemExit from the api helper
    # must be absorbed, never raised - the anchor can never gate a land.
    def fake(method: str, path: str, payload: dict | None = None):
        raise SystemExit("GITHUB_API_REFUSED:POST:/comments:403:secondary rate limit")

    assert land_pr.post_receipt_anchor(REPOSITORY, 85, "c" * 40, call=fake) == "failed"
