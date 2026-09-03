"""Landing ceremony: the Refs contract, the Issue marker stamp, and the exit code.

The pure functions are exercised directly. The provider calls are exercised
through an injected `call`, because what has to be pinned about them is not the
provider's behaviour - its refusals are its own - but this script's: which
write is allowed to fail quietly, which is not, and what exit code each state
of the two marker surfaces earns.
"""

from __future__ import annotations

import json
import re
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


# --------------------------------------------------------------------------
# ed3c/ai-content-notes#117: the Issue body is a shared mutable field, and a
# whole-body write composed from a pre-land read deletes the marker block.
# The #113 instance, replayed from the SHAs recorded in that issue.
# --------------------------------------------------------------------------

LAND_113 = (116, "9cebf79f9136eb4ba851f27a26ebba10b2ba307f", "3ba1564a572d9e61c294ece9f7e4084d25e75e87")
PRE_LAND_BODY = "issue text\n\n## Evidence boundary\n\nOne instance, one issue.\n"

# The receipt `.github/workflows/verify.yml` actually writes. Every field it
# emits is here, including the ones no current caller reads.
#
# This suite is the trusted one: `verify.yml` deletes a candidate's `tests/`
# and copies the default branch's over it before the job that judges the tree.
# So a fixture that omits a field the producer always writes is not merely
# incomplete - it reads green forever, and it refuses the first candidate that
# stops ignoring that field, in a job whose bytes that candidate cannot edit.
# Measured on #118's consumer, which was refused
# `RECEIPT_VERIFIED_BASE_ABSENT:base_sha:None` by a fixture carrying three of
# nine fields (ed3c/ai-content-notes#130).
VERIFY_RECEIPT = {
    "schema_version": 1,
    "repository": REPOSITORY,
    "pull_request": LAND_113[0],
    "head_sha": LAND_113[1],
    "head_repository": REPOSITORY,
    "base_ref": "main",
    "base_sha": "b" * 40,
    "verify_run_id": 33667807749,
    "trusted_sha": "c" * 40,
}


def test_the_receipt_fixture_carries_every_field_verify_writes() -> None:
    """Bind the fixture's shape to its producer's, in the direction that ratchets.

    The bind costs something and the cost is the point: a pull request that adds
    a receipt field to `verify.yml` turns this red, and cannot fix it in the same
    pull request, because the trusted job discards the file that would. The
    two-step - a tests-only pull request teaching this fixture the field, then
    the atom that reads it - is the price of the swap, and paying it loudly here
    is what #130 buys over the silence that preceded it.
    """
    workflow = (REPOSITORY_ROOT / ".github" / "workflows" / "verify.yml").read_text(
        encoding="utf-8"
    )
    block = workflow.split("receipt = {", 1)[1].split("\n          }", 1)[0]
    written = set(re.findall(r'"([a-z_]+)":', block))

    assert written, "no receipt field names found in verify.yml"
    assert written == set(VERIFY_RECEIPT), (
        "the trusted receipt fixture and verify.yml disagree; land a tests-only "
        f"pull request teaching this fixture first: {written ^ set(VERIFY_RECEIPT)}"
    )


def stale_whole_body_write(pre_land: str) -> str:
    """What #113's 04:00:29Z edit was: a correction composed from the 03:58Z body.

    It never saw the markers, so it cannot preserve them - it is not malicious
    and no rule of politeness prevents it. That is the whole mechanism.
    """
    return pre_land.replace("One instance", "One instance, measured end to end")


def test_a_stale_whole_body_write_deletes_the_body_markers() -> None:
    # The defect itself, asserted rather than assumed: this is what happened to
    # #113, and nothing in `stamp` can prevent a later writer from doing it.
    stamped = land(PRE_LAND_BODY, LAND_113)
    assert len(land_pr.split_marker_block(stamped)[1]) == 6

    after = stale_whole_body_write(PRE_LAND_BODY)
    assert land_pr.split_marker_block(after)[1] == []


def test_the_marker_receipt_survives_the_write_that_deletes_the_body_block() -> None:
    # The cure: the same land's marker set also lives in a comment, which a
    # body PATCH cannot reach. Both directions of the reader, on one fixture.
    posted: list[dict] = []

    def fake(method: str, path: str, payload: dict | None = None):
        if method == "GET":
            return []
        posted.append(payload)
        return {}

    markers = land_pr.land_markers(REPOSITORY, *LAND_113)
    assert land_pr.post_marker_receipt(REPOSITORY, 113, 116, markers, call=fake) == "posted"
    receipt = posted[0]["body"]

    stamped = land(PRE_LAND_BODY, LAND_113)
    assert land_pr.marker_surface(stamped, [receipt]) == land_pr.LANDED

    # the direction #113 actually took: body block gone, receipt untouched
    after = stale_whole_body_write(PRE_LAND_BODY)
    assert land_pr.marker_surface(after, [receipt]) == land_pr.MARKERS_LOST

    # and the marker set is recoverable from the receipt, not merely detected
    assert land_pr.split_marker_block(receipt)[1] == land_pr.stamp("", markers).rstrip("\n").split(
        "\n"
    )


def test_an_issue_that_was_never_landed_is_not_read_as_markers_lost() -> None:
    """ABSENT is never NEGATIVE: silence on both surfaces is its own answer.

    Without this direction the reader would be a detector that fires on every
    unlanded issue, which is the same as not having one.
    """
    assert land_pr.marker_surface(PRE_LAND_BODY, []) == land_pr.NO_LAND
    assert land_pr.marker_surface(PRE_LAND_BODY, ["an ordinary comment"]) == land_pr.NO_LAND
    assert land_pr.marker_surface(None, []) == land_pr.NO_LAND


def test_a_land_older_than_the_receipt_reads_as_receipt_absent() -> None:
    """Every issue landed before this change is this state, not LANDED."""
    stamped = land(PRE_LAND_BODY, LAND_113)
    assert land_pr.marker_surface(stamped, []) == land_pr.RECEIPT_ABSENT
    assert (
        land_pr.marker_surface(
            stamped, ["physical-receipt-anchor: pr=116 merge-commit=" + LAND_113[2]]
        )
        == land_pr.RECEIPT_ABSENT
    )


def test_the_marker_receipt_is_posted_once_per_pull_request() -> None:
    def fake(method: str, path: str, payload: dict | None = None):
        if method == "GET":
            return [{"body": f"{land_pr.MARKER_RECEIPT_TOKEN}116\n\nearlier receipt"}]
        raise AssertionError(f"unexpected write after an existing receipt: {method} {path}")

    markers = land_pr.land_markers(REPOSITORY, *LAND_113)
    assert land_pr.post_marker_receipt(REPOSITORY, 113, 116, markers, call=fake) == "exists"


def test_the_marker_receipt_never_gates_a_land() -> None:
    def fake(method: str, path: str, payload: dict | None = None):
        raise SystemExit("GITHUB_API_REFUSED:POST:/comments:403:secondary rate limit")

    markers = land_pr.land_markers(REPOSITORY, *LAND_113)
    assert land_pr.post_marker_receipt(REPOSITORY, 113, 116, markers, call=fake) == "failed"


def test_audit_issue_refuses_only_the_state_that_names_a_loss() -> None:
    """A reader that cannot go red is not a reader (ed3c/skill-concerns#91)."""
    receipt = f"{land_pr.MARKER_RECEIPT_TOKEN}116\n\n" + land_pr.stamp(
        "", land_pr.land_markers(REPOSITORY, *LAND_113)
    )

    def provider(body: str, comments: list[dict]):
        def fake(method: str, path: str, payload: dict | None = None):
            return comments if path.endswith("/comments?per_page=100") else {"body": body}

        return fake

    stamped = land(PRE_LAND_BODY, LAND_113)
    assert land_pr.audit_issue(REPOSITORY, 113, call=provider(stamped, [{"body": receipt}])) == 0
    wiped = stale_whole_body_write(PRE_LAND_BODY)
    assert land_pr.audit_issue(REPOSITORY, 113, call=provider(wiped, [{"body": receipt}])) == 1
    assert land_pr.audit_issue(REPOSITORY, 113, call=provider(wiped, [])) == 0


def test_audit_issue_reads_the_marker_set_back_off_the_receipt(capsys) -> None:
    """The durable copy is read, not merely written.

    In MARKERS_LOST the body block is `[]` by definition, so a reader that
    printed only the body block would name the loss and print nothing of what
    was lost - and the receipt comment would be a store no process ever reads a
    value out of. MARKERS_LOST is the state the comment exists for, so it is
    the state the recovery has to be visible in.
    """
    markers = land_pr.land_markers(REPOSITORY, *LAND_113)
    receipt = f"{land_pr.MARKER_RECEIPT_TOKEN}116\n\n" + land_pr.stamp("", markers)
    wiped = stale_whole_body_write(PRE_LAND_BODY)
    assert land_pr.split_marker_block(wiped)[1] == []

    def fake(method: str, path: str, payload: dict | None = None):
        if path.endswith("/comments?per_page=100"):
            return [{"body": "ordinary comment"}, {"body": receipt}]
        return {"body": wiped}

    assert land_pr.audit_issue(REPOSITORY, 113, call=fake) == 1
    reported = json.loads(capsys.readouterr().out)
    assert reported["marker_surface"] == land_pr.MARKERS_LOST
    assert reported["markers"] == land_pr.stamp("", markers).rstrip("\n").split("\n")
    assert f"<!-- landing-merge: {LAND_113[2]} -->" in reported["markers"]

    # The other direction: with no receipt there is nothing to recover, and the
    # reader must not report a marker set it did not read off any surface.
    def unreceipted(method: str, path: str, payload: dict | None = None):
        return [] if path.endswith("/comments?per_page=100") else {"body": wiped}

    assert land_pr.audit_issue(REPOSITORY, 113, call=unreceipted) == 0
    assert json.loads(capsys.readouterr().out)["markers"] == []


class Provider:
    """Enough provider for one land: an open pull request at head, one Issue.

    Comment POSTs can be refused, which is the only axis these tests vary: it
    is the axis `post_marker_receipt` absorbs, and therefore the one where a
    failure could otherwise leave no trace.

    `compare` answers too. Without it the fallthrough returned the Issue object
    for a commit-comparison path, so a caller asking whether a recorded commit
    is in the default branch's history read `status: None` and refused a land
    that should have proceeded (ed3c/ai-content-notes#130). A dispatcher whose
    default answer is a different object's JSON does not model 'no opinion'.
    """

    def __init__(self, *, comments_accepted: bool = True, compare: str = "ahead") -> None:
        self.issue = {"state": "open", "body": PRE_LAND_BODY}
        self.comments: list[dict] = []
        self.comments_accepted = comments_accepted
        self.compare = compare

    def __call__(self, method: str, path: str, payload: dict | None = None):
        if "/compare/" in path:
            return {"status": self.compare}
        if path.endswith("/comments?per_page=100"):
            return list(self.comments)
        if path.endswith("/comments"):
            if not self.comments_accepted:
                raise SystemExit("GITHUB_API_REFUSED:POST:/comments:403:secondary rate limit")
            self.comments.append({"body": payload["body"]})
            return {}
        if "/pulls/" in path:
            if method == "PUT":
                return {"merged": True, "sha": LAND_113[2]}
            return {
                "state": "open",
                "merged": True,
                "head": {"sha": LAND_113[1]},
                "base": {"ref": "main"},
                "body": f"Refs {REPOSITORY}#113",
                "merged_at": "2026-09-03T00:00:00Z",
            }
        if method == "PATCH":
            self.issue = {"state": payload["state"], "body": payload["body"]}
        return self.issue


def test_a_land_whose_durable_receipt_did_not_post_exits_non_zero(
    tmp_path, monkeypatch, capsys
) -> None:
    """A write that cannot raise still has to cost something. Both directions.

    `post_marker_receipt` is N-class: it absorbs every provider refusal and
    returns 'failed'. Before this control that word went into an ephemeral
    Actions log and `main` returned 0 - identical, at the exit code, to a clean
    land - after which the Issue read RECEIPT_ABSENT, and NO_LAND once any
    later whole-body edit took the body copy too. That is #117's own incident
    exiting green, on the branch that exists to make it visible.

    `audit_issue` keeps the narrower predicate on purpose: on an arbitrary
    Issue only MARKERS_LOST names a loss. Here, one API call after this land
    wrote both surfaces, nothing but LANDED is admissible.
    """
    receipt = tmp_path / "verify-receipt.json"
    receipt.write_text(json.dumps(VERIFY_RECEIPT), encoding="utf-8")
    argv = ["--receipt", str(receipt), "--policy", str(REPOSITORY_ROOT / "policy" / "github.json")]

    monkeypatch.setattr(land_pr, "api", Provider())
    assert land_pr.main(argv) == 0
    green = json.loads(capsys.readouterr().out)
    assert green["marker_surface"] == land_pr.LANDED
    assert green["marker_receipt"] == "posted"

    monkeypatch.setattr(land_pr, "api", Provider(comments_accepted=False))
    assert land_pr.main(argv) == 1
    red = json.loads(capsys.readouterr().out)
    assert red["marker_receipt"] == "failed"
    assert red["marker_surface"] == land_pr.RECEIPT_ABSENT

    # ...and the red exit must not read as a failed merge: the merge is done,
    # read back, and named in the same record. Retrying a land after this would
    # hit PULL_NOT_OPEN, so the record has to say which half failed.
    assert red["merge_sha"] == LAND_113[2]
    assert red["closed_issue"] == 113
    assert red["landed_pull_request"] == LAND_113[0]
