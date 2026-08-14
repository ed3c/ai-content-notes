"""Create a rights-gated deterministic video-frame sampling plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED = {"authorized-local-file", "creator-provided", "user-provided"}


def build(video_digest: str, duration_seconds: float, maximum_frames: int, rights_status: str) -> dict[str, Any]:
    if rights_status not in ALLOWED:
        return {
            "schema_version": "frame-sampling-plan@1",
            "video_digest": video_digest,
            "rights_status": rights_status,
            "timestamps_seconds": [],
            "status": "BLOCKED",
            "reason": "visual extraction requires an authorized local video source",
        }
    if duration_seconds <= 0 or maximum_frames < 1:
        raise ValueError("duration_seconds and maximum_frames must be positive")
    if maximum_frames == 1:
        timestamps = [0.0]
    else:
        end = max(duration_seconds - 0.001, 0.0)
        step = end / (maximum_frames - 1)
        timestamps = [round(index * step, 3) for index in range(maximum_frames)]
    return {
        "schema_version": "frame-sampling-plan@1",
        "video_digest": video_digest,
        "rights_status": rights_status,
        "duration_seconds": duration_seconds,
        "maximum_frames": maximum_frames,
        "timestamps_seconds": timestamps,
        "status": "PLANNED",
        "reason": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    result = build(source["video_digest"], float(source["duration_seconds"]), int(source.get("maximum_frames", 12)), source["rights_status"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
