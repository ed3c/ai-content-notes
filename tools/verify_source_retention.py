#!/usr/bin/env python3
"""Every retained subject artifact must be bound by a source-manifest receipt.

The CvRngaQZQ3Y transcript was acquired, compiled into ten cards, and then
lost. Its digest survives inside those cards, so the batch can be described but
never replayed: `runtime/04-convergence-and-cvrngaqzq3y-replay` has no subject
to bind a source pack to.

Retaining the subject in the repository fixes that only if retention is
verified. A file sitting under `sources/` that no manifest lists is not
evidence, it is a loose file that the next reader will guess about. So:

- every regular file under `sources/<content-id>/` other than the manifest
  itself must appear in that content's `source-manifest.json` with a matching
  SHA-256;
- every artifact the manifest lists must exist;
- a `sources/<content-id>/` directory with no manifest fails closed.

An absent or empty `sources/` tree passes. Retention is a forward rule, and
this adapter does not retroactively claim the lost subject exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

MANIFEST_NAME = "source-manifest.json"
SOURCES_DIR = "sources"


class RetentionError(RuntimeError):
    """Raised when the retained tree cannot be read at all."""


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_artifacts(manifest: dict) -> dict[str, str]:
    """Map artifact path to declared digest, across the manifest's source list."""
    artifacts: dict[str, str] = {}
    for source in manifest.get("sources", []):
        path = source.get("retained_path")
        digest = source.get("sha256") or source.get("digest")
        if path and digest:
            artifacts[str(path)] = str(digest)
    return artifacts


def verify(root: Path) -> list[str]:
    """Return every retention violation. Empty means the tree is admissible."""
    failures: list[str] = []
    sources = root / SOURCES_DIR
    if not sources.is_dir():
        return failures

    for content_dir in sorted(item for item in sources.iterdir() if item.is_dir()):
        manifest_path = content_dir / MANIFEST_NAME
        retained = sorted(
            item
            for item in content_dir.rglob("*")
            if item.is_file() and item.name != MANIFEST_NAME
        )
        if not manifest_path.is_file():
            failures.append(f"{content_dir.name}: no {MANIFEST_NAME}")
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{content_dir.name}: {MANIFEST_NAME} is not valid JSON: {exc}")
            continue

        declared = _manifest_artifacts(manifest)
        for item in retained:
            relative = item.relative_to(content_dir).as_posix()
            if relative not in declared:
                failures.append(f"{content_dir.name}: {relative} is retained but not declared")
            elif declared[relative] != _sha256(item):
                failures.append(f"{content_dir.name}: {relative} does not match its declared digest")
        present = {item.relative_to(content_dir).as_posix() for item in retained}
        for relative in sorted(set(declared) - present):
            failures.append(f"{content_dir.name}: {relative} is declared but not retained")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        raise RetentionError(f"missing repository root: {root}")
    failures = verify(root)
    print(
        json.dumps(
            {
                "retained_content_ids": sorted(
                    item.name
                    for item in (root / SOURCES_DIR).iterdir()
                    if item.is_dir()
                )
                if (root / SOURCES_DIR).is_dir()
                else [],
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
    except RetentionError as error:
        print(f"source retention unusable: {error}", file=sys.stderr)
        raise SystemExit(2) from error
