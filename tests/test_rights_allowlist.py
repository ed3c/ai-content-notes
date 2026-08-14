"""The rights allowlist must fail closed on every path that is not an attestation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import rights_allowlist  # noqa: E402

SCHEMA = REPOSITORY_ROOT / "schemas" / "rights-allowlist.schema.json"
AS_OF = "2026-08-14"
BACKEND = "creator-caption"


def entry(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "video_id": "CvRngaQZQ3Y",
        "canonical_url": "https://www.youtube.com/watch?v=CvRngaQZQ3Y",
        "channel": "Example Channel",
        "title": "Example talk",
        "published_at": "2026-08-01",
        "rights_basis": "creator-permission",
        "rights_reference": "rights-log/2026-08-10-example-channel.md",
        "attestor": "repository owner",
        "attested_on": "2026-08-10",
        "expires_on": None,
        "authorization_status": "verified",
        "permitted_backends": ["creator-caption", "platform-auto-caption"],
        "gold_transcript": None,
        "glossary_path": None,
    }
    base.update(overrides)
    return base


def allowlist(*entries: dict[str, object]) -> dict[str, object]:
    return {"schema_version": "rights-allowlist@1", "entries": list(entries)}


def write(tmp_path: Path, value: object) -> Path:
    path = tmp_path / "rights-allowlist.json"
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def test_attested_row_is_permitted() -> None:
    decision = rights_allowlist.resolve(allowlist(entry()), "CvRngaQZQ3Y", BACKEND, AS_OF)
    assert decision["decision"] == "permitted"
    assert decision["blocked_reason"] is None
    assert decision["rights_basis"] == "creator-permission"
    assert decision["attestor"] == "repository owner"


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"authorization_status": "blocked"}, "blocked"),
        ({"expires_on": "2026-08-13"}, "expired"),
        ({"attested_on": "2026-09-01"}, "future"),
        ({"permitted_backends": ["asr-faster-whisper-large-v3"]}, "not permitted"),
        ({"rights_reference": "https://drive.example/x?access_token=abc"}, "credential"),
        ({"rights_reference": "Bearer ya29.example"}, "credential"),
        ({"rights_reference": "0123456789abcdef0123456789abcdef"}, "credential"),
    ],
)
def test_every_non_attestation_path_is_blocked(
    overrides: dict[str, object], fragment: str
) -> None:
    decision = rights_allowlist.resolve(
        allowlist(entry(**overrides)), "CvRngaQZQ3Y", BACKEND, AS_OF
    )
    assert decision["decision"] == "blocked"
    assert fragment in decision["blocked_reason"]


def test_unknown_row_is_blocked_not_permitted_by_default() -> None:
    decision = rights_allowlist.resolve(allowlist(), "dQw4w9WgXcQ", BACKEND, AS_OF)
    assert decision["decision"] == "blocked"
    assert decision["blocked_reason"] == "no rights record for this video id"


def test_malformed_video_id_is_blocked() -> None:
    for candidate in ("", "short", "https://youtu.be/CvRngaQZQ3Y"):
        decision = rights_allowlist.resolve(allowlist(entry()), candidate, BACKEND, AS_OF)
        assert decision["decision"] == "blocked"
        assert "canonical YouTube id" in decision["blocked_reason"]


def test_public_visibility_is_not_an_expressible_rights_basis(tmp_path: Path) -> None:
    path = write(tmp_path, allowlist(entry(rights_basis="public-visibility")))
    with pytest.raises(rights_allowlist.RightsError, match="failed validation"):
        rights_allowlist.load_allowlist(path, SCHEMA)


def test_blocked_row_does_not_stop_the_ranked_queue() -> None:
    permitted = entry()
    revoked = entry(video_id="aaaaaaaaaaa", authorization_status="blocked")
    decisions = rights_allowlist.plan_batch(
        allowlist(permitted, revoked),
        ["aaaaaaaaaaa", "bbbbbbbbbbb", "CvRngaQZQ3Y"],
        BACKEND,
        AS_OF,
    )
    assert [item["decision"] for item in decisions] == ["blocked", "blocked", "permitted"]
    assert decisions[1]["blocked_reason"] == "no rights record for this video id"


def test_duplicate_records_fail_closed(tmp_path: Path) -> None:
    path = write(tmp_path, allowlist(entry(), entry(attestor="someone else")))
    with pytest.raises(rights_allowlist.RightsError, match="duplicate rights record"):
        rights_allowlist.load_allowlist(path, SCHEMA)


def test_unreadable_allowlist_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(rights_allowlist.RightsError, match="unreadable"):
        rights_allowlist.load_allowlist(tmp_path / "absent.json", SCHEMA)


def test_valid_allowlist_round_trips_through_the_schema(tmp_path: Path) -> None:
    gold = {
        "path": "evidence/gold/CvRngaQZQ3Y.md",
        "source": "human review",
        "version": "1",
        "sha256": "sha256:" + "a" * 64,
        "reviewed_by": "repository owner",
    }
    path = write(tmp_path, allowlist(entry(gold_transcript=gold)))
    loaded = rights_allowlist.load_allowlist(path, SCHEMA)
    assert loaded["entries"][0]["gold_transcript"]["sha256"] == gold["sha256"]


def test_user_directed_evaluation_can_never_be_verified(tmp_path: Path) -> None:
    """AT-001 records a direction, not a right. The schema pins it closed."""
    forged = entry(rights_basis="user-directed-evaluation", authorization_status="verified")
    path = write(tmp_path, allowlist(forged))
    with pytest.raises(rights_allowlist.RightsError, match="failed validation"):
        rights_allowlist.load_allowlist(path, SCHEMA)


def test_a_user_directed_evaluation_entry_blocks_acquisition(tmp_path: Path) -> None:
    admissible = entry(
        rights_basis="user-directed-evaluation",
        authorization_status="evaluation-only",
        rights_reference="governance/RIGHTS_ATTESTATIONS.md#AT-001",
    )
    loaded = rights_allowlist.load_allowlist(write(tmp_path, allowlist(admissible)), SCHEMA)
    decision = rights_allowlist.resolve(loaded, "CvRngaQZQ3Y", BACKEND, AS_OF)
    assert decision["decision"] == "evaluation-only"
    assert decision["may_compile_evaluation_cards"] is True
    assert decision["may_complete_note"] is False
    assert decision["may_publish_raw_media"] is False


def test_the_committed_allowlist_still_grants_nothing() -> None:
    loaded = rights_allowlist.load_allowlist(
        REPOSITORY_ROOT / "governance" / "RIGHTS_ALLOWLIST.json", SCHEMA
    )
    permitted = [
        item
        for item in loaded["entries"]
        if item["authorization_status"] == "verified"
    ]
    assert permitted == [], "a verified entry needs a stated basis and a human attestation"

def test_a_verified_row_may_complete_a_note() -> None:
    decision = rights_allowlist.resolve(allowlist(entry()), "CvRngaQZQ3Y", BACKEND, AS_OF)
    assert decision["decision"] == "permitted"
    assert decision["may_compile_evaluation_cards"] is True
    assert decision["may_complete_note"] is True
    assert decision["may_publish_raw_media"] is True


def test_only_blocked_stops_compilation() -> None:
    """The three states match schemas/multimodal-source-pack.schema.json."""
    states = {
        status: rights_allowlist.resolve(
            allowlist(entry(authorization_status=status)), "CvRngaQZQ3Y", BACKEND, AS_OF
        )
        for status in ("verified", "evaluation-only", "blocked")
    }
    assert states["verified"]["decision"] == "permitted"
    assert states["evaluation-only"]["decision"] == "evaluation-only"
    assert states["blocked"]["decision"] == "blocked"
    assert [states[s]["may_compile_evaluation_cards"] for s in ("verified", "evaluation-only", "blocked")] == [True, True, False]
    assert [states[s]["may_complete_note"] for s in ("verified", "evaluation-only", "blocked")] == [True, False, False]


def test_a_row_with_no_record_still_grants_nothing() -> None:
    decision = rights_allowlist.resolve(allowlist(), "dQw4w9WgXcQ", BACKEND, AS_OF)
    assert decision["decision"] == "blocked"
    assert decision["may_compile_evaluation_cards"] is False
