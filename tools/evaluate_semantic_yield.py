#!/usr/bin/env python3
"""Evaluate persisted HG-01 through HG-06 artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import semantic_yield_result


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--graph", required=True, type=Path)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--coverage-manifest", required=True, type=Path)
    parser.add_argument("--visual-ledger", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = semantic_yield_result.evaluate(
        load_json(args.fixture),
        load_json(args.graph),
        load_json(args.bundle),
        load_json(args.coverage_manifest),
        load_json(args.visual_ledger),
        args.candidate.read_text(encoding="utf-8"),
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.exists() or load_json(args.output) != result:
            raise ValueError("persisted semantic-yield result is missing or stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
