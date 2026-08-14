"""Registry reconciliation: identity reuse, collisions, SUPERSEDES, NOOP replay."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import reconcile_card_registry as registry  # noqa: E402

SCHEMA = REPOSITORY_ROOT / "schemas" / "card-registry.schema.json"
SOURCE_ID = "youtube-video:cvrngaqzq3y"
SOURCE_DIGEST = "sha256:" + "b" * 64
UPDATED = "2026-08-14T02:00:00Z"
LIVE_CARDS = REPOSITORY_ROOT / "evals" / "semantic-yield" / "CvRngaQZQ3Y" / "cards"


def card(
    directory: Path,
    stable_id: str,
    canonical_key: str,
    *,
    series: str = "N",
    body: str = "core claim",
    links: str = "",
    evidence: str = "EV-cvrngaqzq3y-observability-learning",
    lifecycle: str = "ACTIVE",
    revision: int = 1,
) -> Path:
    meta = {
        "stable_id": stable_id,
        "canonical_key": canonical_key,
        "series": series,
        "lifecycle": lifecycle,
        "revision": revision,
        "scope": "unit fixture",
        "confidence_basis": "one dependency, no independent corroboration",
        "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
        "source_provenance": [f"sha256:{'b' * 64}"],
        "unresolved_links": [],
    }
    text = (
        f"### {stable_id}｜fixture\n\n"
        f"- **核心命題**：{body}\n"
        f"- **證據與狀態**：INFERENCE · SUPPORTED · MEDIUM\n"
        f"  - [[{evidence}]]\n"
        f"- **Typed Links**：{links}\n\n"
        "<!-- CARD_META\n" + json.dumps(meta, ensure_ascii=False) + "\n-->\n"
    )
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{stable_id}.md"
    path.write_text(text, encoding="utf-8")
    return path


def reconcile(directory: Path, prior: dict | None = None, updated_at: str = UPDATED):
    return registry.reconcile(
        sorted(directory.glob("*.md")), SOURCE_ID, SOURCE_DIGEST, updated_at, prior
    )


def test_a_complete_batch_reconciles_and_validates(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    card(cards, "N-first-case", "N | a | shifts | b | c | source-digest:bbbbbbbb")
    card(cards, "C-second-case", "C | d | explains | e | f | source-digest:bbbbbbbb", series="C")

    result, gaps = reconcile(cards)
    assert gaps == []
    registry.validate(result, SCHEMA)
    assert sorted(result["cards"]) == ["C-second-case", "N-first-case"]
    assert result["canonical_index"]["N | a | shifts | b | c | source-digest:bbbbbbbb"] == (
        "N-first-case"
    )
    assert result["registry_revision"] == 1


def test_stable_id_is_reused_by_exact_canonical_key(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    key = "N | a | shifts | b | c | source-digest:bbbbbbbb"
    card(cards, "N-first-case", key)
    prior, _ = reconcile(cards)

    # Same key, same id, changed body: the identity is reused, not re-minted.
    card(cards, "N-first-case", key, body="revised core claim")
    result, gaps = reconcile(cards, prior)
    assert gaps == []
    assert result["canonical_index"][key] == "N-first-case"
    assert len(result["cards"]) == 1
    assert result["registry_revision"] == 2


def test_a_second_id_for_a_known_canonical_key_fails_closed(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    key = "N | a | shifts | b | c | source-digest:bbbbbbbb"
    card(cards, "N-first-case", key)
    prior, _ = reconcile(cards)

    renamed = tmp_path / "renamed"
    card(renamed, "N-first-case-v2", key)
    with pytest.raises(registry.RegistryError, match="canonical key already bound"):
        reconcile(renamed, prior)


def test_one_id_carrying_two_canonical_keys_fails_closed(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    card(cards, "N-first-case", "N | a | shifts | b | c | source-digest:bbbbbbbb")
    prior, _ = reconcile(cards)

    drifted = tmp_path / "drifted"
    card(drifted, "N-first-case", "N | z | shifts | y | x | source-digest:bbbbbbbb")
    with pytest.raises(registry.RegistryError, match="stable id collision"):
        reconcile(drifted, prior)


def test_supersedes_marks_the_target_and_records_the_edge(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    card(cards, "N-old-case", "N | a | shifts | b | c | source-digest:bbbbbbbb")
    prior, _ = reconcile(cards)
    assert prior["cards"]["N-old-case"]["lifecycle_status"] == "ACTIVE"

    replacement = tmp_path / "replacement"
    card(
        replacement,
        "N-merged-case",
        "N | a | shifts | b-merged | c | source-digest:bbbbbbbb",
        links="SUPERSEDES → [[N-old-case]]",
    )
    result, gaps = reconcile(replacement, prior)
    assert gaps == []
    registry.validate(result, SCHEMA)
    by_id = result["cards"]
    assert by_id["N-old-case"]["lifecycle_status"] == "SUPERSEDED"
    assert by_id["N-merged-case"]["supersedes"] == ["N-old-case"]


def test_superseding_an_unknown_card_fails_closed(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    card(
        cards,
        "N-merged-case",
        "N | a | shifts | b | c | source-digest:bbbbbbbb",
        links="SUPERSEDES → [[N-never-existed]]",
    )
    with pytest.raises(registry.RegistryError, match="supersedes an unknown card"):
        reconcile(cards)


def test_identical_input_replay_is_a_noop(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    card(cards, "N-first-case", "N | a | shifts | b | c | source-digest:bbbbbbbb")
    first, _ = reconcile(cards)
    # A later wall clock must not manufacture a new revision.
    second, gaps = reconcile(cards, first, updated_at="2026-09-01T00:00:00Z")
    assert gaps == []
    assert second["registry_revision"] == first["registry_revision"]
    assert registry.render(second) == registry.render(first)


def test_content_change_advances_exactly_one_revision(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    key = "N | a | shifts | b | c | source-digest:bbbbbbbb"
    card(cards, "N-first-case", key)
    first, _ = reconcile(cards)
    card(cards, "N-first-case", key, body="changed")
    second, _ = reconcile(cards, first)
    assert second["registry_revision"] == first["registry_revision"] + 1
    assert (second["cards"]["N-first-case"]["content_digest"]
            != first["cards"]["N-first-case"]["content_digest"])


def test_the_sidecar_is_excluded_from_the_content_digest(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    key = "N | a | shifts | b | c | source-digest:bbbbbbbb"
    card(cards, "N-first-case", key)
    first, _ = reconcile(cards)
    # Only the sidecar revision counter moves; the payload is untouched.
    card(cards, "N-first-case", key, revision=2)
    second, _ = reconcile(cards, first)
    assert (second["cards"]["N-first-case"]["content_digest"]
            == first["cards"]["N-first-case"]["content_digest"])


def test_a_filename_that_disagrees_with_stable_id_is_a_gap(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    path = card(cards, "N-first-case", "N | a | shifts | b | c | source-digest:bbbbbbbb")
    path.rename(cards / "N-renamed-on-disk.md")
    result, gaps = reconcile(cards)
    assert result is None
    assert any("does not match the filename" in gap for gap in gaps)


def test_missing_registry_fields_are_reported_not_invented(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    path = card(cards, "N-first-case", "N | a | shifts | b | c | source-digest:bbbbbbbb")
    text = path.read_text(encoding="utf-8")
    meta = json.loads(text.split("<!-- CARD_META\n")[1].split("\n-->")[0])
    del meta["scope"]
    del meta["confidence_basis"]
    path.write_text(
        text.split("<!-- CARD_META\n")[0]
        + "<!-- CARD_META\n"
        + json.dumps(meta, ensure_ascii=False)
        + "\n-->\n",
        encoding="utf-8",
    )
    result, gaps = reconcile(cards)
    assert result is None
    assert gaps == ["N-first-case.md: CARD_META missing scope, confidence_basis"]


def test_an_unknown_verification_label_is_a_gap(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    path = card(cards, "N-first-case", "N | a | shifts | b | c | source-digest:bbbbbbbb")
    path.write_text(
        path.read_text(encoding="utf-8").replace("SUPPORTED", "PROBABLY_FINE"), encoding="utf-8"
    )
    result, gaps = reconcile(cards)
    assert result is None
    assert any("unknown verification PROBABLY_FINE" in gap for gap in gaps)


def test_the_committed_batch_reports_its_real_registry_gap() -> None:
    """The ten shipped cards do not yet satisfy the registry contract."""
    result, gaps = reconcile(LIVE_CARDS)
    assert result is None, "a registry must not be written while a gap stands"
    assert len(gaps) == 8
    assert all("CARD_META missing" in gap for gap in gaps)
    # Two cards are already complete; they are not reported.
    reported = {gap.split(".md")[0] for gap in gaps}
    assert "N-autonomy-trace-mining" not in reported
    assert "C-model-harness-task-fit" not in reported
