"""Publication guard: one planted negative per enforced rule, red then green.

A guard nobody has watched go red is a claim, not a gate. Every test here first
asserts the pristine fixture batch is green, then plants a single defect and
asserts that exact rule reports it. The fixture is built from the real protocol
and the real registry schema, so a protocol change reaches these tests.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import publication_guard as guard  # noqa: E402
import reconcile_card_registry as registry  # noqa: E402

SOURCE_ID = "fixture-source"
SOURCE_DIGEST = "sha256:" + "a" * 64
UPDATED_AT = "2026-08-15T00:00:00Z"

# Deliberately unlike any card text below, so the green fixture shares no long
# run with it and the I-06 negative has something real to paste.
SOURCE_BODY = (
    "the interviewer asks how the team decides when a harness has stopped "
    "paying for itself and the guest answers that they watch the ratio of "
    "tokens spent on scaffolding against tokens spent on the task itself and "
    "then they talk about how that ratio moved across four model generations "
    "before returning to the question of who reads the traces at all"
)


def card(
    stable_id: str,
    *,
    links: str,
    payload: str = "",
    provenance: list[str] | None = None,
    body_extra: str = "",
) -> str:
    series = stable_id.split("-", 1)[0]
    meta = {
        "stable_id": stable_id,
        "canonical_key": (
            f"{series} | {stable_id.lower()} | asserts | fixture-object | fixture-scope | v1"
        ),
        "series": series,
        "lifecycle": "ACTIVE",
        "revision": 1,
        "scope": "fixture batch",
        "confidence_basis": "fixture",
        "source_provenance": provenance
        if provenance is not None
        else ["youtube:FIXTURE:fixture-backend#timestamp:00:00:01.000..00:00:09.000"],
        "unresolved_links": [],
    }
    return (
        f"### {stable_id}｜fixture card\n\n"
        "- **核心命題**：fixture proposition\n"
        "- **為什麼重要**：fixture reason\n"
        f"{payload}"
        f"{body_extra}"
        "- **證據與狀態**：OBSERVATION · SUPPORTED · HIGH\n"
        f"- **Typed Links**：{links}\n\n"
        "<!-- CARD_META\n"
        f"{json.dumps(meta, ensure_ascii=False, indent=2)}\n"
        "-->\n"
    )


CARDS = {
    "N-fixture-anchor": card("N-fixture-anchor", links="ROOT ← [[K-fixture-gap]]"),
    "P-fixture-recipe": card(
        "P-fixture-recipe",
        links="ROOT ← [[N-fixture-anchor]]",
        payload="- **Execution Status**：UNTESTED\n",
    ),
    "V-fixture-replay": card(
        "V-fixture-replay",
        links="VALIDATED_BY → [[P-fixture-recipe]]",
        payload=(
            "- **Observed Result**：PASS\n"
            "- **Verdict**：PASS\n"
            "- **Artifacts**：`fixture.json`\n"
        ),
    ),
    "K-fixture-gap": card(
        "K-fixture-gap",
        links="DEPENDS_ON → [[UNRESOLVED::C | fixture | needs | a-source | fixture-scope | v1]]",
        provenance=["LOCATOR_MISSING"],
    ),
}


def build(tmp_path: Path) -> Path:
    """A minimal but real tree: this repository's protocol and schema, one batch."""
    root = tmp_path / "tree"
    (root / "governance").mkdir(parents=True)
    (root / "schemas").mkdir(parents=True)
    shutil.copy(
        REPOSITORY_ROOT / "governance" / "CARD_PROTOCOL_V7_1.md",
        root / "governance" / "CARD_PROTOCOL_V7_1.md",
    )
    shutil.copy(
        REPOSITORY_ROOT / "schemas" / "card-registry.schema.json",
        root / "schemas" / "card-registry.schema.json",
    )

    sources = root / "sources" / "FIXTURE"
    sources.mkdir(parents=True)
    (sources / "captions.txt").write_text(SOURCE_BODY, encoding="utf-8")

    batch = root / "evals" / "semantic-yield" / "fixture"
    cards = batch / "cards"
    cards.mkdir(parents=True)
    for stable_id, text in CARDS.items():
        (cards / f"{stable_id}.md").write_text(text, encoding="utf-8")
    (batch / "card-manifest.json").write_text(
        json.dumps({"schema_version": "semantic-yield-card-manifest@1"}), encoding="utf-8"
    )

    reconciled, gaps = registry.reconcile(
        sorted(cards.glob("*.md")), SOURCE_ID, SOURCE_DIGEST, UPDATED_AT
    )
    assert not gaps, gaps
    (batch / "card-registry.json").write_text(registry.render(reconciled), encoding="utf-8")
    return root


def findings(root: Path) -> dict[str, list[str]]:
    return guard.run(root)["findings"]


def green(root: Path) -> Path:
    assert findings(root) == {}
    return root


def card_path(root: Path, stable_id: str) -> Path:
    return root / "evals" / "semantic-yield" / "fixture" / "cards" / f"{stable_id}.md"


def rewrite(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"planted defect anchor is not unique: {old!r}"
    path.write_text(text.replace(old, new), encoding="utf-8")


def test_the_fixture_batch_is_green_and_the_guard_exits_zero(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    report = guard.run(root)
    assert report["batches"] == ["semantic-yield/fixture"]
    assert report["finding_count"] == 0
    assert report["retained_source_text"] == "PRESENT"
    assert guard.main(["--root", str(root)]) == 0


def test_the_enforced_rules_all_carry_their_protocol_title(tmp_path: Path) -> None:
    report = guard.run(build(tmp_path))
    assert report["enforced"]["QG-07"] == "Stable Identity"
    assert report["enforced"]["I-06"] == "Shadow Evidence Fidelity"
    # Everything not mechanised is named as still prompt-enforced, not omitted.
    assert "QG-01" in report["prompt_enforced_only"]
    assert "QG-07" not in report["prompt_enforced_only"]


def test_a_rule_the_protocol_no_longer_states_is_fatal(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    protocol = root / "governance" / "CARD_PROTOCOL_V7_1.md"
    text = protocol.read_text(encoding="utf-8")
    protocol.write_text(
        text.replace("QG-07 Stable Identity\t", "QG-77 Stable Identity\t"), encoding="utf-8"
    )
    with pytest.raises(guard.GuardError) as refusal:
        guard.run(root)
    assert str(refusal.value) == "RULE_ABSENT_FROM_PROTOCOL:QG-07"


def test_a_missing_sidecar_is_red_under_qg_16(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    path = card_path(root, "N-fixture-anchor")
    text = path.read_text(encoding="utf-8")
    path.write_text(text.split("<!-- CARD_META")[0], encoding="utf-8")
    assert any("CARD_META" in item for item in findings(root)["QG-16"])
    assert guard.main(["--root", str(root)]) == 1


def test_two_cards_sharing_a_canonical_key_are_red_under_qg_07(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    stolen = json.loads(
        registry.CARD_META.search(
            card_path(root, "N-fixture-anchor").read_text(encoding="utf-8")
        ).group(1)
    )["canonical_key"]
    rewrite(
        card_path(root, "P-fixture-recipe"),
        '"canonical_key": "P | p-fixture-recipe | asserts | fixture-object | fixture-scope | v1"',
        f'"canonical_key": "{stolen}"',
    )
    assert any("canonical key" in item for item in findings(root)["QG-07"])


def test_a_registry_binding_the_key_to_another_card_is_red_under_qg_07(
    tmp_path: Path,
) -> None:
    root = green(build(tmp_path))
    path = root / "evals" / "semantic-yield" / "fixture" / "card-registry.json"
    persisted = json.loads(path.read_text(encoding="utf-8"))
    key = next(
        name for name, value in persisted["canonical_index"].items() if value == "N-fixture-anchor"
    )
    persisted["canonical_index"][key] = "N-some-other-card"
    path.write_text(registry.render(persisted), encoding="utf-8")
    assert any("registry binds" in item for item in findings(root)["QG-07"])


def test_a_second_reconciliation_that_moves_is_red_under_qg_24(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = green(build(tmp_path))
    honest = registry.reconcile

    def drifting(paths, source_id, source_digest, updated_at, prior=None, evidence=None):
        result, gaps = honest(paths, source_id, source_digest, updated_at, prior, evidence)
        if prior is not None and result is not None:
            result = dict(result, registry_revision=result["registry_revision"] + 1)
        return result, gaps

    monkeypatch.setattr(guard.registry, "reconcile", drifting)
    assert any("registry_revision" in item for item in findings(root)["QG-24"])


def test_a_link_target_that_resolves_to_nothing_is_red_under_qg_08(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    rewrite(
        card_path(root, "N-fixture-anchor"),
        "ROOT ← [[K-fixture-gap]]",
        "ROOT ← [[K-never-written]]",
    )
    assert any("resolves to no card" in item for item in findings(root)["QG-08"])


def test_a_generic_untyped_link_is_red_under_qg_08(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    rewrite(
        card_path(root, "N-fixture-anchor"),
        "ROOT ← [[K-fixture-gap]]",
        "ROOT ← [[K-fixture-gap]] · ← [[相關證據]]",
    )
    assert any("untyped or generic link" in item for item in findings(root)["QG-08"])


def test_an_unresolved_link_without_a_k_card_is_red_under_qg_08(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    # The K card is the thing that stands for an unresolved target; remove it and
    # the UNRESOLVED:: marker on the remaining card has nothing behind it.
    rewrite(
        card_path(root, "N-fixture-anchor"),
        "ROOT ← [[K-fixture-gap]]",
        "ROOT ← [[UNRESOLVED::C | fixture | needs | a-source | fixture-scope | v1]]",
    )
    card_path(root, "K-fixture-gap").unlink()
    assert any("no K card standing for it" in item for item in findings(root)["QG-08"])


def test_a_provenance_entry_without_a_locator_is_red_under_qg_03(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    rewrite(
        card_path(root, "N-fixture-anchor"),
        "youtube:FIXTURE:fixture-backend#timestamp:00:00:01.000..00:00:09.000",
        "youtube:FIXTURE:fixture-backend",
    )
    assert any("without a locator" in item for item in findings(root)["QG-03"])


def test_an_artifact_locator_that_does_not_resolve_is_red_under_qg_03(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    rewrite(
        card_path(root, "N-fixture-anchor"),
        "youtube:FIXTURE:fixture-backend#timestamp:00:00:01.000..00:00:09.000",
        "artifact:evals/semantic-yield/fixture/never-written.json",
    )
    assert any("does not resolve" in item for item in findings(root)["QG-03"])


def test_a_status_outside_the_protocol_vocabulary_is_red_under_qg_10(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    rewrite(
        card_path(root, "P-fixture-recipe"),
        "- **Execution Status**：UNTESTED",
        "- **Execution Status**：PROBABLY_FINE",
    )
    assert any("not in the protocol vocabulary" in item for item in findings(root)["QG-10"])


def test_a_claimed_run_without_artifacts_is_red_under_qg_10(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    rewrite(card_path(root, "V-fixture-replay"), "- **Artifacts**：`fixture.json`\n", "")
    assert any("without naming artifacts" in item for item in findings(root)["QG-10"])


def test_a_missing_verdict_is_red_under_qg_10(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    rewrite(card_path(root, "V-fixture-replay"), "- **Verdict**：PASS\n", "")
    assert any("expected one Verdict" in item for item in findings(root)["QG-10"])


def test_a_pasted_source_body_is_red_under_i_06(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    path = card_path(root, "N-fixture-anchor")
    rewrite(
        path,
        "- **為什麼重要**：fixture reason\n",
        f"- **為什麼重要**：{SOURCE_BODY[:260]}\n",
    )
    assert any("copied verbatim" in item for item in findings(root)["I-06"])


def test_a_short_quote_from_the_source_stays_green_under_i_06(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    rewrite(
        card_path(root, "N-fixture-anchor"),
        "- **為什麼重要**：fixture reason\n",
        f"- **為什麼重要**：「{SOURCE_BODY[:80]}」\n",
    )
    assert findings(root) == {}


def test_a_recorded_gap_is_a_state_and_its_drift_is_red_under_qg_16(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    batch = root / "evals" / "semantic-yield" / "fixture"
    (batch / "card-registry.json").unlink()
    rewrite(card_path(root, "N-fixture-anchor"), '  "scope": "fixture batch",\n', "")

    recorded = ["N-fixture-anchor.md: CARD_META missing scope"]
    report = batch / "card-registry-gap-report.json"
    report.write_text(json.dumps({"gaps": recorded}), encoding="utf-8")
    assert findings(root) == {}, "a faithfully recorded gap is a state, not a failure"

    report.write_text(json.dumps({"gaps": []}), encoding="utf-8")
    assert any("not in the recorded report" in item for item in findings(root)["QG-16"])


def test_a_batch_with_neither_registry_nor_gap_report_is_fatal(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    (root / "evals" / "semantic-yield" / "fixture" / "card-registry.json").unlink()
    with pytest.raises(guard.GuardError) as refusal:
        guard.run(root)
    assert str(refusal.value).startswith("BATCH_STATE_ABSENT:")


def test_a_tree_with_no_batches_at_all_is_fatal(tmp_path: Path) -> None:
    root = green(build(tmp_path))
    shutil.rmtree(root / "evals")
    with pytest.raises(guard.GuardError) as refusal:
        guard.run(root)
    assert str(refusal.value).startswith("NO_CARD_BATCHES:")


def test_this_repository_is_green_under_its_own_guard() -> None:
    report = guard.run(REPOSITORY_ROOT)
    assert report["findings"] == {}, report["findings"]
    assert report["batches"], "the guard must be pointed at something"
