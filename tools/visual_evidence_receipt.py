#!/usr/bin/env python3
"""Validate a rights-gated visual evidence receipt.

Issue #14 requires that frame and visual evidence carry a timestamp, a frame
digest and a bbox locator, and that a blocked visual modality becomes
`BLOCKED_WITH_K_CARD` rather than an exact visual claim. Until now the only
mechanism enforcing that was a validator grepping the string "bbox" out of a
card body, which a card can satisfy by writing the word.

This adapter enforces the rule structurally. The dangerous direction is
upward: a frame nobody extracted must never end up carrying an exact claim
about what it shows. Every check below exists to block that direction.

It reads a committed receipt and, when the frames are present, the frame files
themselves. It never downloads, extracts or decodes media.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path("schemas/visual-evidence-receipt.schema.json")
PRESENT = {"RENDERED", "CARD_MAPPED"}
ATTESTED_BASES = {
    "owned",
    "licensed",
    "public-domain",
    "user-provided",
    "creator-permission",
}


class VisualEvidenceError(RuntimeError):
    """Raised when a receipt claims more visual authority than it can carry."""


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _schema_errors(receipt: dict[str, Any], schema_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return [
        f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(receipt),
            key=lambda item: list(item.absolute_path),
        )
    ]


def validate(
    receipt: dict[str, Any],
    root: Path,
    schema_path: Path = SCHEMA_PATH,
) -> list[str]:
    """Return every violation. An empty list means the receipt is admissible."""
    failures = _schema_errors(receipt, schema_path)
    if failures:
        return failures

    rights = receipt["rights"]
    attested = (
        rights["authorization_status"] == "verified" and rights["basis"] in ATTESTED_BASES
    )
    duration = receipt["video"]["duration_seconds"]
    if duration is None and receipt["frames"]:
        failures.append("frames are declared without a known video duration")

    frames: dict[str, dict[str, Any]] = {}
    for frame in receipt["frames"]:
        frame_id = frame["frame_id"]
        if frame_id in frames:
            failures.append(f"duplicate frame_id: {frame_id}")
            continue
        frames[frame_id] = frame

        if duration is not None and frame["timestamp_seconds"] > duration:
            failures.append(
                f"{frame_id}: timestamp {frame['timestamp_seconds']} exceeds "
                f"duration {duration}"
            )
        present = frame["disposition"] in PRESENT
        if present and not attested:
            failures.append(
                f"{frame_id}: {frame['disposition']} requires an attested rights basis"
            )
        if present:
            if not frame["sha256"] or not frame["path"]:
                failures.append(f"{frame_id}: {frame['disposition']} requires a digest and path")
            else:
                candidate = root / frame["path"]
                if not candidate.is_file():
                    failures.append(f"{frame_id}: frame artifact is missing: {frame['path']}")
                elif _sha256_file(candidate) != frame["sha256"]:
                    failures.append(f"{frame_id}: frame digest does not match the artifact")
        else:
            if frame["sha256"] or frame["path"]:
                failures.append(
                    f"{frame_id}: {frame['disposition']} must not carry a frame artifact"
                )
            if not frame["reason"]:
                failures.append(f"{frame_id}: {frame['disposition']} requires a reason")

    seen: set[str] = set()
    for annotation in receipt["annotations"]:
        annotation_id = annotation["annotation_id"]
        if annotation_id in seen:
            failures.append(f"duplicate annotation_id: {annotation_id}")
            continue
        seen.add(annotation_id)

        frame = frames.get(annotation["frame_id"])
        if frame is None:
            failures.append(f"{annotation_id}: references an unknown frame")
            continue

        box = annotation["bbox"]
        if box["x"] + box["width"] > 1 or box["y"] + box["height"] > 1:
            failures.append(f"{annotation_id}: bbox leaves the frame")

        if annotation["claim_status"] == "EXACT_VISUAL_CLAIM":
            # The whole point of the receipt: an exact claim about what a frame
            # shows requires that frame to exist and to be attested.
            if frame["disposition"] not in PRESENT:
                failures.append(
                    f"{annotation_id}: exact visual claim on a "
                    f"{frame['disposition']} frame"
                )
            if not attested:
                failures.append(
                    f"{annotation_id}: exact visual claim without an attested rights basis"
                )
        elif frame["disposition"] == "BLOCKED_WITH_K_CARD" and (
            annotation["claim_status"] != "BLOCKED_WITH_K_CARD"
        ):
            failures.append(
                f"{annotation_id}: a blocked frame may only carry a BLOCKED_WITH_K_CARD annotation"
            )

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    args = parser.parse_args()

    if not args.receipt.is_file():
        raise VisualEvidenceError(f"missing visual evidence receipt: {args.receipt}")
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    failures = validate(receipt, args.root.resolve(), args.schema)
    print(
        json.dumps(
            {
                "receipt": str(args.receipt),
                "failure_count": len(failures),
                "failures": failures,
                "status": "ADMISSIBLE" if not failures else "REJECTED",
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VisualEvidenceError as error:
        print(f"visual evidence receipt unusable: {error}", file=sys.stderr)
        raise SystemExit(2) from error
