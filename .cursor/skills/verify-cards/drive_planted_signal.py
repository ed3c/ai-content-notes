#!/usr/bin/env python3
"""Drive the planted high-signal control from the command line.

`tests/test_planted_signal_falsifier.py` proves both directions in-process. A
verification run needs the same two directions through the real CLI, because
the thing being verified is the command an operator types, not the function a
test imports. Everything here is a thin CLI over the scripted LOOP agent that
already exists in `tests/loop_fixture.py`; no card, quote or control is
authored twice.

    # write the planted subject and its control file
    .cursor/skills/verify-cards/drive_planted_signal.py seed --out RUN

    # responder that never anchors the plant  -> the harness must refuse DONE
    .cursor/skills/verify-cards/drive_planted_signal.py respond REQUEST.json

    # responder that anchors it               -> the same run reaches DONE
    .cursor/skills/verify-cards/drive_planted_signal.py respond --anchor REQUEST.json

`seed` fails loudly if the plant is already present in
`evals/runner/synthetic-loop/source.md`: a control that the subject states on
its own is not a plant, and both directions would silently collapse into one.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY_ROOT / "tests"))

import loop_fixture as fixture  # noqa: E402

PLANT_KEY = "planted-unobserved-interruption"


def seed(out: Path) -> int:
    original = fixture.SYNTHETIC_SOURCE.read_text(encoding="utf-8")
    if fixture.PLANTED_QUOTE in original:
        raise SystemExit(
            "the plant is already in evals/runner/synthetic-loop/source.md; it controls "
            "nothing there and the two drive directions are no longer different"
        )
    out.mkdir(parents=True, exist_ok=True)
    source = out / "planted-source.md"
    controls = out / "high-signal.json"
    source.write_text(original + fixture.PLANTED_SECTION, encoding="utf-8")
    controls.write_text(
        json.dumps([{"key": PLANT_KEY, "quote": fixture.PLANTED_QUOTE}], ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"source": str(source), "high_signal": str(controls), "key": PLANT_KEY}))
    return 0


def respond(request_path: Path, anchor: bool) -> int:
    request = json.loads(request_path.read_text(encoding="utf-8"))
    rounds = (
        [fixture.ROUND_ONE, [*fixture.ROUND_TWO, fixture.planted_card()]] if anchor else None
    )
    sys.stdout.write(fixture.respond(request, rounds=rounds))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    seeder = sub.add_parser("seed", help="write the planted subject and its control file")
    seeder.add_argument("--out", required=True, type=Path)

    responder = sub.add_parser("respond", help="the harness responder, invoked as CMD <request.json>")
    responder.add_argument("request", type=Path)
    responder.add_argument(
        "--anchor",
        action="store_true",
        help="emit the one card that anchors the plant with TEXT_MATCH::",
    )

    args = parser.parse_args(argv)
    if args.command == "seed":
        return seed(args.out.resolve())
    return respond(args.request, args.anchor)


if __name__ == "__main__":
    raise SystemExit(main())
