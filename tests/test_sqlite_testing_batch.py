"""The first production batch, held to the things that make it evidence.

Ten cards were compiled from one real public article through the LOOP harness.
What separates that from ten plausible paragraphs is entirely mechanical, so
this module checks the mechanical part and nothing else:

- the retained text plane is reproducible from the retained fetched bytes;
- every anchor in the evidence manifest is the exact substring at its declared
  character offsets;
- every claim in every card is backed by an anchor that resolves;
- the batch replays from its own captured rounds to the same registry;
- the registry is idempotent, and the rights basis is one the policy admits.

Issue #82.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import html_article_adapter as article  # noqa: E402
import reconcile_card_registry as registry  # noqa: E402
import rights_vocabulary as rights  # noqa: E402
import run_loop_harness as harness  # noqa: E402

BATCH = REPOSITORY_ROOT / "evals" / "loop-batches" / "sqlite-testing"
RETAINED = REPOSITORY_ROOT / "sources" / "sqlite-testing"
CARDS = BATCH / "cards"
TEXT_MATCH = "TEXT_MATCH::"
EVIDENCE_REF = re.compile(r"\[\[(EV-[A-Za-z0-9._:-]+)\]\]")

SOURCE_ID = "article:sqlite.org-testing"
UPDATED_AT = "2026-08-31T17:29:21Z"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def cards() -> list[Path]:
    return sorted(CARDS.glob("*.md"))


def card_meta(path: Path) -> dict:
    match = registry.CARD_META.search(path.read_text(encoding="utf-8"))
    assert match is not None, f"{path.name}: no CARD_META"
    return json.loads(match.group(1))


def test_the_retained_text_plane_is_reproducible_from_the_fetched_bytes() -> None:
    """The anchors index this file, so it has to be derivable, not just present."""
    raw = (RETAINED / "article.raw.html").read_bytes()
    text = (RETAINED / "article.txt").read_text(encoding="utf-8")
    assert article.extract_text(raw.decode("utf-8")) == text

    manifest = load(RETAINED / "source-manifest.json")
    declared = {entry["retained_path"]: entry["sha256"] for entry in manifest["sources"]}
    assert declared["article.raw.html"] == digest(raw)
    assert declared["article.txt"] == digest(text.encode("utf-8"))
    assert manifest["canonical_url"] == "https://www.sqlite.org/testing.html"
    assert manifest["retrieved_at"] == UPDATED_AT


def test_the_rights_basis_is_one_the_policy_admits() -> None:
    entry = load(RETAINED / "source-manifest.json")["rights"]
    assert entry["rights_basis"] in rights.VERIFIED_RIGHTS_BASES
    assert entry["authorization_status"] in rights.AUTHORIZATION_STATUSES
    assert rights.may_acquire_media(entry["rights_basis"], entry["authorization_status"])
    assert entry["basis_reference"].startswith("https://")


def test_every_anchor_is_the_exact_substring_at_its_declared_offsets() -> None:
    manifest = load(BATCH / "evidence-manifest.json")
    text = (RETAINED / "article.txt").read_text(encoding="utf-8")
    assert manifest["text_plane"]["sha256"] == digest(text.encode("utf-8"))
    assert manifest["text_plane"]["characters"] == len(text)
    assert manifest["fetched_content"]["sha256"] == digest(
        (RETAINED / "article.raw.html").read_bytes()
    )

    anchors = manifest["anchors"]
    assert anchors, "an evidence manifest with no anchors anchors nothing"
    for anchor in anchors:
        start, end = anchor["char_start"], anchor["char_end"]
        assert text[start:end] == anchor["quote"], anchor["evidence_id"]
        # A quote that occurs twice does not identify a place in the source.
        assert text.count(anchor["quote"]) == 1, anchor["evidence_id"]
    ids = [anchor["evidence_id"] for anchor in anchors]
    assert len(set(ids)) == len(ids)


def test_every_card_claim_is_anchor_backed() -> None:
    manifest = load(BATCH / "evidence-manifest.json")
    by_id = {anchor["evidence_id"]: anchor for anchor in manifest["anchors"]}
    quotes = {anchor["quote"] for anchor in manifest["anchors"]}

    for path in cards():
        body = path.read_text(encoding="utf-8")
        meta = card_meta(path)
        matched = [
            entry[len(TEXT_MATCH) :]
            for entry in meta["source_provenance"]
            if entry.startswith(TEXT_MATCH)
        ]
        assert matched, f"{path.name}: no TEXT_MATCH anchor in source_provenance"
        for quote in matched:
            assert quote in quotes, f"{path.name}: anchor is not in the evidence manifest: {quote}"

        referenced = set(EVIDENCE_REF.findall(body))
        assert referenced, f"{path.name}: card body cites no evidence"
        for evidence_id in referenced:
            assert evidence_id in by_id, f"{path.name}: unknown evidence id {evidence_id}"
            # The visible quote is the anchored text, not a paraphrase of it.
            assert by_id[evidence_id]["quote"] in body, f"{path.name}: {evidence_id} misquoted"

        assert "artifact:sources/sqlite-testing/article.txt" in meta["source_provenance"]


def test_the_batch_is_ten_cards_and_the_manifest_agrees() -> None:
    manifest = load(BATCH / "card-manifest.json")
    receipt = load(BATCH / "run-receipt.json")
    on_disk = sorted(path.stem for path in cards())

    assert len(on_disk) == 10
    assert sorted(manifest["card_order"]) == on_disk
    assert manifest["card_count"] == 10
    assert manifest["status"] == "DONE" == receipt["status"]
    assert manifest["registry_digest"] == receipt["registry_digest"]
    # Ten cards from one article should not be ten of the same thing.
    assert len(set(manifest["series_order"])) >= 8


def test_the_run_reached_done_on_the_completion_contract() -> None:
    receipt = load(BATCH / "run-receipt.json")
    assert receipt["stopped_on"] == "completion-contract"
    assert receipt["blocked_by"] == []
    assert receipt["round_count"] == 3
    assert [item["declared_status"] for item in receipt["rounds"]] == [
        "CONTINUE",
        "CONTINUE",
        "DONE",
    ]
    # The gates that reached DONE were the harness's, not the model's labels.
    assert receipt["gate_authority"] == "none"
    assert receipt["digest_authority"] == "runner"


def test_every_declared_high_signal_item_is_mapped() -> None:
    controls = load(BATCH / "high-signal.json")
    receipt = load(BATCH / "run-receipt.json")
    text = (RETAINED / "article.txt").read_text(encoding="utf-8")

    assert receipt["high_signal_control"] == "PRESENT"
    assert receipt["high_signal_declared"] == len(controls)
    assert receipt["high_signal_unmapped"] == []
    for control in controls:
        assert control["quote"] in text, control["key"]
    assert harness.unmapped_high_signal(controls, CARDS) == []


def test_the_persisted_registry_is_idempotent() -> None:
    persisted = load(BATCH / "card-registry.json")
    replay, gaps = registry.reconcile(
        cards(),
        SOURCE_ID,
        persisted["source_digest"],
        UPDATED_AT,
        prior=persisted,
    )
    assert gaps == []
    assert registry.render(replay) == registry.render(persisted)
    assert replay["registry_revision"] == persisted["registry_revision"]
    assert sorted(persisted["cards"]) == sorted(path.stem for path in cards())


def test_replaying_the_captured_rounds_rebuilds_the_batch(tmp_path: Path) -> None:
    """The committed rounds are the run, not a description of it."""
    receipt = harness.run(
        tmp_path / "replayed",
        RETAINED / "article.txt",
        SOURCE_ID,
        "sqlite-testing",
        UPDATED_AT,
        harness._responder_from_replay(BATCH / "rounds"),
        REPOSITORY_ROOT,
        BATCH / "high-signal.json",
    )
    committed = load(BATCH / "run-receipt.json")
    assert receipt["status"] == "DONE"
    assert receipt["registry_digest"] == committed["registry_digest"]
    assert receipt["card_count"] == committed["card_count"]
    for path in cards():
        rebuilt = tmp_path / "replayed" / "cards" / path.name
        assert rebuilt.read_text(encoding="utf-8") == path.read_text(encoding="utf-8")
