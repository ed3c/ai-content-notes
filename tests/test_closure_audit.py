"""ed3c/ai-content-notes#61 - CLOSED(issue) must not outrun the default branch.

The invariant under test:

    CLOSED(issue) => the artifact its acceptance names is readable on the
                     default branch

Seven issues in this repository - #56, #59, #62, #63, #64, #69, #70 - were
closed by receipt comments naming heads on a chain of drafts, so they read
CLOSED while none of their bytes are reachable from `main`. The machine
ceremony closes that hole forward only; nothing re-reads an already-closed
issue against the tree. `tools/closure_audit.py` is that reader, and these are
its controls.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from closure_audit import (  # noqa: E402
    ABSENT,
    CLOSURE_WITHOUT_ARTIFACT,
    DEFAULT_LEDGER,
    NO_PATH_NAMED,
    PRESENT,
    audit,
    checked_relative,
    load_ledger,
    main,
)

# The closures this atom exists to report. This tuple is a *provider* fact -
# how these seven issues were closed - and it does not change when one of them
# acquires its artifact.
#
# It used to be asserted equal to the tree-derived
# `summary.closure_without_artifact`, with a comment telling the materializing
# PR to "update this tuple and the affected ledger row together". That
# instruction is unexecutable here: `verify.yml` replaces the candidate's
# `tests/` with the default branch's before judging it, so a PR that
# materializes an artifact *and* edits this tuple is still judged by the old
# tuple and goes red. Measured on a candidate tree carrying only
# `docs/reference-registry/README.md` and `reference-index.private.json`:
#
#     E  assert (59, 62, 63, 64, 69, 70) == (56, 59, 62, 63, 64, 69, ...)
#
# Same class as ed3c/ai-content-notes#104, which measured the trusted-suite
# swap failing a correct atom against exactly this kind of stale hardcoded
# set, and was fixed in PR #105.
#
# What replaces it is stricter, not looser. Equality let a future PR silently
# rewrite the literal; the reconciliation below cannot be satisfied that way:
# a closure may leave the bare set only by acquiring its artifact *and*
# recording what superseded it in the ledger row, and no closure outside this
# tuple may ever enter the bare set.
RECEIPT_CLOSED_WITHOUT_ARTIFACT = (56, 59, 62, 63, 64, 69, 70)

# The token a ledger note must carry once its closure leaves the bare set.
SUPERSEDED_BY = "superseded-by:"


def report() -> dict:
    return audit(load_ledger(DEFAULT_LEDGER), ROOT)


def reconcile(rendered: dict, ledger: dict) -> list[str]:
    """Findings when an audit report disagrees with the receipt-closed set.

    Two directions, and they are not symmetric:

    - a closure *entering* the bare set is always a finding - the seven are
      the recorded extent of this defect, and an eighth is new damage;
    - a closure *leaving* it is legitimate, but only against a ledger note
      that says what materialized the path. Without that the row reads as if
      the original draft chain landed, which is the exact substitution of a
      receipt for a merge this audit exists to refuse.
    """
    bare = set(rendered["summary"]["closure_without_artifact"])
    recorded = set(RECEIPT_CLOSED_WITHOUT_ARTIFACT)
    notes = {closure["issue"]: str(closure.get("note") or "") for closure in ledger["closures"]}
    findings = [
        f"#{issue}: bare closure outside the recorded receipt-closed set"
        for issue in sorted(bare - recorded)
    ]
    findings.extend(
        f"#{issue}: left the bare set with no {SUPERSEDED_BY!r} note"
        for issue in sorted(recorded - bare)
        if SUPERSEDED_BY not in notes.get(issue, "")
    )
    return findings


def test_ledger_covers_each_closed_issue_once_with_in_tree_paths() -> None:
    ledger = load_ledger(DEFAULT_LEDGER)
    issues = [closure["issue"] for closure in ledger["closures"]]
    assert len(issues) == len(set(issues))
    assert ledger["repository"] == "ed3c/ai-content-notes"
    for closure in ledger["closures"]:
        assert isinstance(closure["title"], str) and closure["title"]
        assert isinstance(closure["artifacts"], list)
        for path in closure["artifacts"]:
            checked_relative(path)
        if not closure["artifacts"]:
            # NO_PATH_NAMED is a state, not a shrug: it has to say why.
            assert closure.get("note"), closure["issue"]


def test_every_row_status_agrees_with_the_working_tree() -> None:
    for row in report()["rows"]:
        missing = [
            entry["path"]
            for entry in row["artifacts"]
            if not (ROOT / entry["path"]).exists()
        ]
        assert missing == row["missing"]
        if not row["artifacts"]:
            assert row["status"] == NO_PATH_NAMED
        elif missing:
            assert row["status"] == ABSENT
        else:
            assert row["status"] == PRESENT


def test_all_three_states_are_emitted_by_the_current_tree() -> None:
    states = {row["status"] for row in report()["rows"]}
    assert states == {PRESENT, ABSENT, NO_PATH_NAMED}


def test_the_seven_receipt_closures_stay_accounted_for() -> None:
    ledger = load_ledger(DEFAULT_LEDGER)
    rendered = report()
    assert reconcile(rendered, ledger) == []

    # Tautology guard: the reconciliation above is vacuous if the seven fell
    # out of the ledger entirely, so the rows have to still be there.
    issues = {closure["issue"] for closure in ledger["closures"]}
    assert set(RECEIPT_CLOSED_WITHOUT_ARTIFACT) <= issues

    for row in rendered["rows"]:
        if row["issue"] in rendered["summary"]["closure_without_artifact"]:
            assert row["issue"] in RECEIPT_CLOSED_WITHOUT_ARTIFACT
            assert row["status"] == ABSENT
            assert row["verdict"] == CLOSURE_WITHOUT_ARTIFACT
            assert row["missing"]


def test_an_eighth_bare_closure_is_refused() -> None:
    """Entering the bare set is new damage, whatever the ledger note says."""
    rendered = copy.deepcopy(report())
    rendered["summary"]["closure_without_artifact"].append(999)
    findings = reconcile(rendered, load_ledger(DEFAULT_LEDGER))
    assert any("#999" in finding for finding in findings), findings


def test_acquiring_the_artifact_without_a_superseding_note_is_refused() -> None:
    """The red-before-green half of the rule the old equality could not state."""
    rendered = copy.deepcopy(report())
    rendered["summary"]["closure_without_artifact"] = [
        issue
        for issue in rendered["summary"]["closure_without_artifact"]
        if issue != 56
    ]
    ledger = copy.deepcopy(load_ledger(DEFAULT_LEDGER))
    row = next(closure for closure in ledger["closures"] if closure["issue"] == 56)
    row["note"] = "planted: artifact present, nothing recorded about what put it there"
    findings = reconcile(rendered, ledger)
    assert any("#56" in finding and SUPERSEDED_BY in finding for finding in findings), findings


def test_acquiring_the_artifact_with_a_superseding_note_is_allowed() -> None:
    """And the green half: the rule must not make materialization unreachable."""
    rendered = copy.deepcopy(report())
    rendered["summary"]["closure_without_artifact"] = [
        issue
        for issue in rendered["summary"]["closure_without_artifact"]
        if issue != 56
    ]
    ledger = copy.deepcopy(load_ledger(DEFAULT_LEDGER))
    row = next(closure for closure in ledger["closures"] if closure["issue"] == 56)
    row["note"] = f"planted: {SUPERSEDED_BY} 0000000000000000000000000000000000000000"
    assert reconcile(rendered, ledger) == []


def test_no_path_named_is_not_counted_as_a_pass() -> None:
    rendered = report()
    unchecked = [row for row in rendered["rows"] if row["status"] == NO_PATH_NAMED]
    assert unchecked
    for row in unchecked:
        assert row["verdict"] is None
        assert row["missing"] == []
    summary = rendered["summary"]
    assert summary["closed"] == summary["present"] + summary["absent"] + summary[
        "no_path_named"
    ]


def test_planted_absent_path_turns_a_green_closure_red() -> None:
    ledger = copy.deepcopy(load_ledger(DEFAULT_LEDGER))
    victim = next(
        closure
        for closure in ledger["closures"]
        if closure["issue"] not in RECEIPT_CLOSED_WITHOUT_ARTIFACT
        and closure["artifacts"]
    )
    green = next(
        entry
        for entry in audit(ledger, ROOT)["rows"]
        if entry["issue"] == victim["issue"]
    )
    assert green["status"] == PRESENT  # green before the plant

    victim["artifacts"] = ["docs/closure-audit/no-such-artifact.json"]
    row = next(
        entry
        for entry in audit(ledger, ROOT)["rows"]
        if entry["issue"] == victim["issue"]
    )
    assert row["status"] == ABSENT
    assert row["verdict"] == CLOSURE_WITHOUT_ARTIFACT
    assert row["missing"] == ["docs/closure-audit/no-such-artifact.json"]


def test_planted_present_path_turns_a_red_closure_green() -> None:
    # The negative control for the control: the verdict follows the tree, not
    # the issue number.
    ledger = copy.deepcopy(load_ledger(DEFAULT_LEDGER))
    victim = next(
        closure for closure in ledger["closures"] if closure["issue"] == 62
    )
    victim["artifacts"] = ["tools/closure_audit.py"]
    row = next(
        entry for entry in audit(ledger, ROOT)["rows"] if entry["issue"] == 62
    )
    assert row["status"] == PRESENT
    assert row["verdict"] is None
    assert 62 not in audit(ledger, ROOT)["summary"]["closure_without_artifact"]


def test_a_ledger_path_cannot_escape_the_audited_tree() -> None:
    for escape in ("../secrets.json", "/etc/passwd", ""):
        try:
            checked_relative(escape)
        except ValueError:
            continue
        raise AssertionError(f"escaping path accepted: {escape!r}")


def test_strict_exit_code_follows_the_report(tmp_path: Path) -> None:
    assert main(["--strict"]) == 1
    assert main([]) == 0

    clean = copy.deepcopy(load_ledger(DEFAULT_LEDGER))
    for closure in clean["closures"]:
        closure["artifacts"] = []
        closure.setdefault("note", "planted: nothing to check")
    ledger_path = tmp_path / "clean-ledger.json"
    ledger_path.write_text(json.dumps(clean), encoding="utf-8")
    assert main(["--strict", "--ledger", str(ledger_path)]) == 0
