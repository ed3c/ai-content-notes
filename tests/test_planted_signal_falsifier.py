"""A planted control that makes `high_signal_unmapped = 0` refutable.

Section 9 lets a run declare DONE when `high_signal_unmapped = 0`, and until
now that number came from the same run that wanted to be finished. Nothing in
the repository could tell an exhaustive batch from a batch that stopped early
and said it was exhaustive, because both report the same zero.

So plant one known high-signal item into a copy of the source and assert both
directions, which is the only shape that can fail:

    unmapped  -> DONE is unreachable; the run ends BLOCKED naming the control
    mapped    -> the identical run reaches DONE

Only one thing differs between the two, and it is the card that anchors the
plant. Issue #81.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import loop_fixture as fixture  # noqa: E402
import run_loop_harness as harness  # noqa: E402

SOURCE_ID = "synthetic:runner-loop"
CONTENT_ID = "synthetic-loop"
UPDATED_AT = "2026-09-01T00:00:00Z"
PLANT_KEY = "planted-unobserved-interruption"

# Quotes the scripted cards already anchor, used as the positive control: the
# check must stay quiet when coverage really is complete.
ANCHORED_QUOTES = [
    {"key": "round-budget", "quote": "a round budget stops the wrong thing"},
    {"key": "stall-check", "quote": "a stall is not the same as a budget"},
    {"key": "completion", "quote": "the completion contract has to be checked"},
]


def planted_source(tmp_path: Path) -> Path:
    """A copy of the synthetic source with one high-signal item added."""
    original = fixture.SYNTHETIC_SOURCE.read_text(encoding="utf-8")
    assert fixture.PLANTED_QUOTE not in original, "the plant must not already be in the source"
    path = tmp_path / "planted-source.md"
    path.write_text(original + fixture.PLANTED_SECTION, encoding="utf-8")
    return path


def controls(tmp_path: Path, items: list[dict[str, str]]) -> Path:
    path = tmp_path / "high-signal.json"
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def responder(rounds: list[list[dict[str, Any]]]) -> Callable[[int, Path], str]:
    def call(round_number: int, request_path: Path) -> str:
        del round_number
        request = json.loads(request_path.read_text(encoding="utf-8"))
        return fixture.respond(request, rounds=rounds)

    return call


def drive(
    run_dir: Path,
    source: Path,
    rounds: list[list[dict[str, Any]]],
    high_signal: Path | None,
) -> dict[str, Any]:
    return harness.run(
        run_dir,
        source,
        SOURCE_ID,
        CONTENT_ID,
        UPDATED_AT,
        responder(rounds),
        REPOSITORY_ROOT,
        high_signal,
    )


PLANT = [{"key": PLANT_KEY, "quote": fixture.PLANTED_QUOTE}]
BLIND_RUN = [fixture.ROUND_ONE, fixture.ROUND_TWO]


def mapping_run() -> list[list[dict[str, Any]]]:
    return [fixture.ROUND_ONE, [*fixture.ROUND_TWO, fixture.planted_card()]]


def test_an_unmapped_planted_signal_makes_done_unreachable(tmp_path: Path) -> None:
    receipt = drive(
        tmp_path / "run",
        planted_source(tmp_path),
        BLIND_RUN,
        controls(tmp_path, PLANT),
    )
    assert receipt["status"] != "DONE"
    assert receipt["status"] == "BLOCKED"
    assert receipt["high_signal_unmapped"] == [PLANT_KEY]
    assert f"high_signal_unmapped: {PLANT_KEY}" in receipt["blocked_by"]
    # The round itself still said DONE. The refusal is the harness's, not the model's.
    assert receipt["rounds"][-1]["declared_status"] == "DONE"


def test_mapping_the_planted_signal_restores_done(tmp_path: Path) -> None:
    receipt = drive(
        tmp_path / "run",
        planted_source(tmp_path),
        mapping_run(),
        controls(tmp_path, PLANT),
    )
    assert receipt["status"] == "DONE"
    assert receipt["high_signal_unmapped"] == []
    assert receipt["blocked_by"] == []
    assert receipt["card_count"] == 4
    assert "K-unobserved-interruption" in json.loads(
        (tmp_path / "run" / "card-registry.json").read_text(encoding="utf-8")
    )["cards"]


def test_the_two_directions_differ_only_by_the_mapping_card(tmp_path: Path) -> None:
    """Same source, same controls, same rounds but one card. Nothing else moved."""
    blind = drive(tmp_path / "blind", planted_source(tmp_path), BLIND_RUN, controls(tmp_path, PLANT))
    mapped = drive(
        tmp_path / "mapped", planted_source(tmp_path), mapping_run(), controls(tmp_path, PLANT)
    )
    assert blind["source_digest"] == mapped["source_digest"]
    assert blind["round_count"] == mapped["round_count"] == 2
    assert (blind["status"], mapped["status"]) == ("BLOCKED", "DONE")
    assert mapped["card_count"] - blind["card_count"] == 1


def test_a_control_absent_from_the_source_is_refused(tmp_path: Path) -> None:
    """A plant that is not in the subject would fail forever and prove nothing."""
    absent = [{"key": "not-a-control", "quote": "this sentence is nowhere in the source"}]
    with pytest.raises(harness.HarnessError, match="not present in the source"):
        drive(
            tmp_path / "run",
            planted_source(tmp_path),
            mapping_run(),
            controls(tmp_path, absent),
        )


def test_complete_coverage_of_real_controls_still_reaches_done(tmp_path: Path) -> None:
    """The negative control: the check has to stay quiet when nothing is missing."""
    receipt = drive(
        tmp_path / "run",
        fixture.SYNTHETIC_SOURCE,
        BLIND_RUN,
        controls(tmp_path, ANCHORED_QUOTES),
    )
    assert receipt["status"] == "DONE"
    assert receipt["high_signal_control"] == "PRESENT"
    assert receipt["high_signal_declared"] == 3
    assert receipt["high_signal_unmapped"] == []


def test_a_run_without_controls_says_so_rather_than_reporting_zero(tmp_path: Path) -> None:
    receipt = drive(tmp_path / "run", fixture.SYNTHETIC_SOURCE, BLIND_RUN, None)
    assert receipt["status"] == "DONE"
    assert receipt["high_signal_control"] == "ABSENT"
    assert receipt["high_signal_declared"] == 0


def test_malformed_controls_fail_closed(tmp_path: Path) -> None:
    for payload, message in (
        ("[]", "non-empty list"),
        ('[{"key": "k"}]', "needs a key and a quote"),
        ('["not an object"]', "not an object"),
        ("{not json", "cannot read high-signal controls"),
    ):
        path = tmp_path / "high-signal.json"
        path.write_text(payload, encoding="utf-8")
        with pytest.raises(harness.HarnessError, match=message):
            harness.load_high_signal(path, fixture.SYNTHETIC_SOURCE.read_text(encoding="utf-8"))


def test_the_cli_exposes_the_falsifier(tmp_path: Path) -> None:
    """The whole chain, including the flag, executed once through main()."""
    exit_code = harness.main(
        [
            "--run-dir",
            str(tmp_path / "run"),
            "--source",
            str(planted_source(tmp_path)),
            "--source-id",
            SOURCE_ID,
            "--content-id",
            CONTENT_ID,
            "--updated-at",
            UPDATED_AT,
            "--repo-root",
            str(REPOSITORY_ROOT),
            "--high-signal",
            str(controls(tmp_path, PLANT)),
            "--responder",
            f"{sys.executable} {REPOSITORY_ROOT / 'tests' / 'loop_fixture.py'}",
        ]
    )
    assert exit_code == 1
    receipt = json.loads((tmp_path / "run" / "run-receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "BLOCKED"
    assert receipt["high_signal_unmapped"] == [PLANT_KEY]
