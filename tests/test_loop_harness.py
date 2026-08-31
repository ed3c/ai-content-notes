"""The LOOP harness closes the loop, and refuses the rounds it cannot trust.

Acceptance for issue #80: one synthetic-source run reaches DONE, every round is
schema-valid, and the registry is idempotent on re-run. The rest is failure
injection, because a harness that only proves it works on a good round proves
nothing about the round it was built to catch.
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
import parse_compiler_channels as channels  # noqa: E402
import reconcile_card_registry as registry  # noqa: E402
import run_loop_harness as harness  # noqa: E402

SOURCE_ID = "synthetic:runner-loop"
CONTENT_ID = "synthetic-loop"
UPDATED_AT = "2026-09-01T00:00:00Z"


def scripted(mutate: Callable[[dict[str, Any]], None] | None = None) -> Callable[[int, Path], str]:
    def responder(round_number: int, request_path: Path) -> str:
        del round_number
        request = json.loads(request_path.read_text(encoding="utf-8"))
        if mutate is not None:
            mutate(request)
        return fixture.respond(request)

    return responder


def drive(run_dir: Path, responder: Callable[[int, Path], str]) -> dict[str, Any]:
    return harness.run(
        run_dir,
        fixture.SYNTHETIC_SOURCE,
        SOURCE_ID,
        CONTENT_ID,
        UPDATED_AT,
        responder,
        REPOSITORY_ROOT,
    )


def test_a_synthetic_source_run_reaches_done(tmp_path: Path) -> None:
    receipt = drive(tmp_path / "run", scripted())

    assert receipt["status"] == "DONE"
    assert receipt["blocked_by"] == []
    assert receipt["round_count"] == 2
    assert receipt["card_count"] == 3
    assert receipt["stopped_on"] == "completion-contract"
    assert [item["declared_status"] for item in receipt["rounds"]] == ["CONTINUE", "DONE"]

    cards = sorted(path.stem for path in (tmp_path / "run" / "cards").glob("*.md"))
    assert cards == [
        "D-stall-check-costs-one-comparison",
        "N-round-budget-hides-truncation",
        "P-recheck-the-finished-batch",
    ]


def test_every_round_of_that_run_is_independently_schema_valid(tmp_path: Path) -> None:
    """The harness validated each round; re-validate the captured bytes anyway."""
    drive(tmp_path / "run", scripted())
    raws = sorted((tmp_path / "run" / "rounds").glob("round-*.raw.md"))
    assert len(raws) == 2
    for path in raws:
        parsed = channels.parse(path.read_text(encoding="utf-8"), REPOSITORY_ROOT)
        assert parsed["gate_authority"] == "none"
        assert set(parsed["channels"]) == {"CARD_PATCH", "ASSERTION_REPORT", "NEXT_STATE"}


def test_the_registry_that_run_produced_is_idempotent(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    receipt = drive(run_dir, scripted())
    persisted = json.loads((run_dir / "card-registry.json").read_text(encoding="utf-8"))

    replay, gaps = registry.reconcile(
        sorted((run_dir / "cards").glob("*.md")),
        SOURCE_ID,
        receipt["source_digest"],
        UPDATED_AT,
        prior=persisted,
    )
    assert gaps == []
    assert registry.render(replay) == registry.render(persisted)
    assert replay["registry_revision"] == persisted["registry_revision"]


def test_the_registry_digest_is_the_runners_and_never_the_models(tmp_path: Path) -> None:
    receipt = drive(tmp_path / "run", scripted())
    assert receipt["digest_authority"] == "runner"
    assert receipt["gate_authority"] == "none"
    for record in receipt["rounds"]:
        # The fixture claims a digest it cannot possibly have computed. The
        # harness records the claim and chains on its own reconciliation.
        assert record["model_authored_registry_after_digest"] != record["registry_after_digest"]
        assert record["registry_after_digest"].startswith("sha256:")


def test_model_authored_quality_gates_stay_quarantined(tmp_path: Path) -> None:
    receipt = drive(tmp_path / "run", scripted())
    final = receipt["rounds"][-1]["model_authored_gate_labels"]
    assert all(gate["status"] == "PASS" for gate in final["next_state"].values())
    assert "quality_gates" not in receipt
    assert receipt["gate_authority"] == "none"


def test_a_round_compiled_against_a_stale_registry_is_refused(tmp_path: Path) -> None:
    def stale(request: dict[str, Any]) -> None:
        request["registry_before_digest"] = "sha256:" + "9" * 64

    with pytest.raises(harness.HarnessError, match="stale prior registry"):
        drive(tmp_path / "run", scripted(stale))


def test_a_round_compiled_against_a_different_source_is_refused(tmp_path: Path) -> None:
    def swapped(request: dict[str, Any]) -> None:
        request["source"]["source_digest"] = "sha256:" + "8" * 64

    with pytest.raises(harness.HarnessError, match="different source"):
        drive(tmp_path / "run", scripted(swapped))


def test_a_round_naming_a_different_subject_is_refused(tmp_path: Path) -> None:
    def renamed(request: dict[str, Any]) -> None:
        request["source"]["content_id"] = "some-other-batch"

    with pytest.raises(harness.HarnessError, match="different subject"):
        drive(tmp_path / "run", scripted(renamed))


def test_round_one_must_echo_the_empty_registry_digest(tmp_path: Path) -> None:
    """The empty-registry constant is a real link in the chain, not a formality."""
    seen: list[str] = []

    def capture(round_number: int, request_path: Path) -> str:
        del round_number
        request = json.loads(request_path.read_text(encoding="utf-8"))
        seen.append(request["registry_before_digest"])
        return fixture.respond(request)

    drive(tmp_path / "run", capture)
    assert seen[0] == harness.EMPTY_REGISTRY_DIGEST
    assert seen[1] != harness.EMPTY_REGISTRY_DIGEST


def test_a_loop_that_stops_advancing_fails_instead_of_spinning(tmp_path: Path) -> None:
    """No round budget: the run ends because it stopped moving, not because it counted."""

    def stuck(round_number: int, request_path: Path) -> str:
        del round_number
        return fixture.noop_continue(json.loads(request_path.read_text(encoding="utf-8")))

    receipt = drive(tmp_path / "run", stuck)
    assert receipt["status"] == "FAILED"
    assert receipt["round_count"] == 2
    assert "advanced neither the registry nor the source cursor" in receipt["blocked_by"][0]


def test_an_add_over_an_existing_card_is_refused(tmp_path: Path) -> None:
    """Two rounds cannot both claim to create the same card."""

    def repeat(round_number: int, request_path: Path) -> str:
        del round_number
        request = json.loads(request_path.read_text(encoding="utf-8"))
        return fixture.respond(request, rounds=[fixture.ROUND_ONE, fixture.ROUND_ONE])

    with pytest.raises(harness.HarnessError, match="ADD would overwrite"):
        drive(tmp_path / "run", repeat)


def test_a_card_the_registry_contract_rejects_stops_the_round(tmp_path: Path) -> None:
    broken = dict(fixture.ROUND_ONE[0])
    broken["visible_payload"] = "### N-round-budget-hides-truncation｜no status line"

    def responder(round_number: int, request_path: Path) -> str:
        del round_number
        request = json.loads(request_path.read_text(encoding="utf-8"))
        return fixture.respond(request, rounds=[[broken]])

    with pytest.raises(harness.HarnessError, match="does not reconcile"):
        drive(tmp_path / "run", responder)


def test_done_admission_reports_a_registry_that_is_not_idempotent(tmp_path: Path) -> None:
    """The completion check has to be able to go red, so drive it red directly."""
    run_dir = tmp_path / "run"
    receipt = drive(run_dir, scripted())
    cards_dir = run_dir / "cards"
    card_paths = sorted(cards_dir.glob("*.md"))
    persisted = json.loads((run_dir / "card-registry.json").read_text(encoding="utf-8"))

    assert (
        harness._admit_done(
            card_paths, persisted, SOURCE_ID, receipt["source_digest"], UPDATED_AT, [], cards_dir
        )
        == []
    )

    # A registry that does not account for a card on disk is exactly what a
    # premature DONE looks like: the second reconciliation adds the card back,
    # advances the revision, and stops being byte-identical.
    dropped = "P-recheck-the-finished-batch"
    drifted = dict(
        persisted,
        cards={k: v for k, v in persisted["cards"].items() if k != dropped},
        canonical_index={k: v for k, v in persisted["canonical_index"].items() if v != dropped},
    )
    reasons = harness._admit_done(
        card_paths,
        drifted,
        SOURCE_ID,
        receipt["source_digest"],
        UPDATED_AT,
        ["K-never-rendered"],
        cards_dir,
    )
    assert any("render_order names cards absent from disk" in item for item in reasons)
    assert any("registry_revision" in item for item in reasons)
    assert any("did not reproduce the same registry" in item for item in reasons)


def test_the_cli_drives_a_run_through_a_responder_subprocess(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    exit_code = harness.main(
        [
            "--run-dir",
            str(run_dir),
            "--source",
            str(fixture.SYNTHETIC_SOURCE),
            "--source-id",
            SOURCE_ID,
            "--content-id",
            CONTENT_ID,
            "--updated-at",
            UPDATED_AT,
            "--repo-root",
            str(REPOSITORY_ROOT),
            "--responder",
            f"{sys.executable} {REPOSITORY_ROOT / 'tests' / 'loop_fixture.py'}",
        ]
    )
    assert exit_code == 0
    receipt = json.loads((run_dir / "run-receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "DONE"
    assert receipt["card_count"] == 3


def test_a_responder_that_fails_is_not_a_compile_verdict(tmp_path: Path) -> None:
    with pytest.raises(harness.HarnessError, match="responder exited"):
        drive(
            tmp_path / "run",
            harness._responder_from_command(f"{sys.executable} -c 'raise SystemExit(3)'", REPOSITORY_ROOT),
        )


def test_an_exhausted_replay_is_an_explicit_absence(tmp_path: Path) -> None:
    empty = tmp_path / "replay"
    empty.mkdir()
    with pytest.raises(harness.HarnessError, match="replay has no round 1"):
        drive(tmp_path / "run", harness._responder_from_replay(empty))


def test_a_replayed_run_reproduces_the_same_registry(tmp_path: Path) -> None:
    """A finished run's rounds/ directory is replayable as-is, with no renaming."""
    first = tmp_path / "live"
    receipt = drive(first, scripted())

    second = tmp_path / "replayed"
    replayed = drive(second, harness._responder_from_replay(first / "rounds"))
    assert replayed["status"] == "DONE"
    assert replayed["registry_digest"] == receipt["registry_digest"]
