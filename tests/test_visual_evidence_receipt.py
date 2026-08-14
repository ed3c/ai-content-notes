"""A visual receipt may never claim more than the frames it actually holds."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import visual_evidence_receipt as visual  # noqa: E402

SCHEMA = REPOSITORY_ROOT / "schemas" / "visual-evidence-receipt.schema.json"


def attested_rights(**overrides: Any) -> dict[str, Any]:
    value = {
        "basis": "creator-permission",
        "authorization_status": "verified",
        "attestor": "repository owner",
        "reference": "rights-log/2026-08-10-example.md",
    }
    value.update(overrides)
    return value


def blocked_rights() -> dict[str, Any]:
    return {
        "basis": "unattested",
        "authorization_status": "blocked",
        "attestor": None,
        "reference": None,
    }


def frame(
    frame_id: str = "VIS-fit-equation",
    *,
    disposition: str = "BLOCKED_WITH_K_CARD",
    timestamp: float = 12.5,
    sha256: str | None = None,
    path: str | None = None,
    reason: str | None = "visual extraction requires an authorized local video source",
) -> dict[str, Any]:
    return {
        "frame_id": frame_id,
        "timestamp_seconds": timestamp,
        "disposition": disposition,
        "sha256": sha256,
        "path": path,
        "reason": reason,
    }


def annotation(
    *,
    frame_id: str = "VIS-fit-equation",
    claim_status: str = "BLOCKED_WITH_K_CARD",
    bbox: dict[str, float] | None = None,
    annotation_id: str = "ANN-1",
) -> dict[str, Any]:
    return {
        "annotation_id": annotation_id,
        "frame_id": frame_id,
        "bbox": bbox or {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.2},
        "label": "fit equation region",
        "claim_status": claim_status,
    }


def receipt(**overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": "visual-evidence-receipt@1",
        "content_id": "CvRngaQZQ3Y",
        "source_dependency_key": "youtube-video:CvRngaQZQ3Y",
        "rights": blocked_rights(),
        "video": {"sha256": None, "duration_seconds": 600.0},
        "frames": [frame()],
        "annotations": [annotation()],
        "created_at": "2026-08-14T02:00:00Z",
    }
    value.update(overrides)
    return value


def write_frame(tmp_path: Path, name: str = "frame-000.png") -> tuple[str, str]:
    path = tmp_path / "frames" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = b"\x89PNG synthetic frame"
    path.write_bytes(payload)
    digest = "sha256:" + hashlib.sha256(payload).hexdigest()
    return f"frames/{name}", digest


def validate(value: dict[str, Any], root: Path) -> list[str]:
    return visual.validate(value, root, SCHEMA)


def test_a_blocked_modality_receipt_is_admissible(tmp_path: Path) -> None:
    assert validate(receipt(), tmp_path) == []


def test_an_attested_rendered_frame_with_a_matching_digest_is_admissible(
    tmp_path: Path,
) -> None:
    path, digest = write_frame(tmp_path)
    value = receipt(
        rights=attested_rights(),
        video={"sha256": "sha256:" + "c" * 64, "duration_seconds": 600.0},
        frames=[frame(disposition="RENDERED", sha256=digest, path=path, reason=None)],
        annotations=[annotation(claim_status="EXACT_VISUAL_CLAIM")],
    )
    assert validate(value, tmp_path) == []


def test_an_exact_claim_on_a_blocked_frame_is_rejected(tmp_path: Path) -> None:
    value = receipt(annotations=[annotation(claim_status="EXACT_VISUAL_CLAIM")])
    failures = validate(value, tmp_path)
    assert any("exact visual claim on a BLOCKED_WITH_K_CARD frame" in item for item in failures)
    assert any("without an attested rights basis" in item for item in failures)


def test_a_blocked_frame_may_only_carry_a_blocked_annotation(tmp_path: Path) -> None:
    value = receipt(annotations=[annotation(claim_status="DESCRIPTIVE")])
    failures = validate(value, tmp_path)
    assert any("only carry a BLOCKED_WITH_K_CARD annotation" in item for item in failures)


def test_a_rendered_frame_without_attested_rights_is_rejected(tmp_path: Path) -> None:
    path, digest = write_frame(tmp_path)
    value = receipt(
        frames=[frame(disposition="RENDERED", sha256=digest, path=path, reason=None)],
        annotations=[],
    )
    failures = validate(value, tmp_path)
    assert any("requires an attested rights basis" in item for item in failures)


def test_a_rendered_frame_whose_artifact_is_absent_is_rejected(tmp_path: Path) -> None:
    value = receipt(
        rights=attested_rights(),
        frames=[
            frame(
                disposition="RENDERED",
                sha256="sha256:" + "d" * 64,
                path="frames/never-extracted.png",
                reason=None,
            )
        ],
        annotations=[],
    )
    failures = validate(value, tmp_path)
    assert any("frame artifact is missing" in item for item in failures)


def test_a_frame_digest_that_does_not_match_the_artifact_is_rejected(tmp_path: Path) -> None:
    path, _ = write_frame(tmp_path)
    value = receipt(
        rights=attested_rights(),
        frames=[
            frame(disposition="RENDERED", sha256="sha256:" + "e" * 64, path=path, reason=None)
        ],
        annotations=[],
    )
    failures = validate(value, tmp_path)
    assert any("digest does not match the artifact" in item for item in failures)


def test_a_blocked_frame_may_not_carry_an_artifact(tmp_path: Path) -> None:
    path, digest = write_frame(tmp_path)
    value = receipt(frames=[frame(sha256=digest, path=path)], annotations=[])
    failures = validate(value, tmp_path)
    assert any("must not carry a frame artifact" in item for item in failures)


def test_a_timestamp_past_the_end_of_the_video_is_rejected(tmp_path: Path) -> None:
    value = receipt(frames=[frame(timestamp=601.0)], annotations=[])
    failures = validate(value, tmp_path)
    assert any("exceeds duration" in item for item in failures)


def test_a_bbox_that_leaves_the_frame_is_rejected(tmp_path: Path) -> None:
    value = receipt(
        annotations=[annotation(bbox={"x": 0.8, "y": 0.1, "width": 0.5, "height": 0.2})]
    )
    failures = validate(value, tmp_path)
    assert any("bbox leaves the frame" in item for item in failures)


def test_a_bbox_outside_the_unit_interval_fails_the_schema(tmp_path: Path) -> None:
    value = receipt(
        annotations=[annotation(bbox={"x": -0.1, "y": 0.1, "width": 0.2, "height": 0.2})]
    )
    failures = validate(value, tmp_path)
    assert failures and any("bbox/x" in item for item in failures)


def test_an_annotation_on_an_unknown_frame_is_rejected(tmp_path: Path) -> None:
    value = receipt(annotations=[annotation(frame_id="VIS-never-declared")])
    failures = validate(value, tmp_path)
    assert any("references an unknown frame" in item for item in failures)


def test_duplicate_identifiers_are_rejected(tmp_path: Path) -> None:
    value = receipt(
        frames=[frame(), frame()],
        annotations=[annotation(), annotation()],
    )
    failures = validate(value, tmp_path)
    assert any("duplicate frame_id" in item for item in failures)
    assert any("duplicate annotation_id" in item for item in failures)


def test_public_visibility_is_not_an_expressible_rights_basis(tmp_path: Path) -> None:
    value = receipt(rights=attested_rights(basis="public-visibility"))
    failures = validate(value, tmp_path)
    assert failures and any("rights/basis" in item for item in failures)


def test_a_receipt_holding_no_media_records_an_empty_frame_set(tmp_path: Path) -> None:
    """The honest shape when nothing was ever extracted: no duration, no frames."""
    value = receipt(
        video={"sha256": None, "duration_seconds": None}, frames=[], annotations=[]
    )
    assert validate(value, tmp_path) == []


def test_frames_without_a_known_duration_are_rejected(tmp_path: Path) -> None:
    value = receipt(video={"sha256": None, "duration_seconds": None}, annotations=[])
    failures = validate(value, tmp_path)
    assert any("without a known video duration" in item for item in failures)


def test_a_missing_receipt_file_fails_closed(tmp_path: Path) -> None:
    original = sys.argv
    sys.argv = [
        "visual_evidence_receipt.py",
        "--receipt",
        str(tmp_path / "absent.json"),
        "--root",
        str(tmp_path),
    ]
    try:
        with pytest.raises(visual.VisualEvidenceError, match="missing visual evidence receipt"):
            visual.main()
    finally:
        sys.argv = original
