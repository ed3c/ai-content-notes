#!/usr/bin/env python3
"""Verify the consumption-scoped reference registry against the tree it indexes.

A registry whose rows nobody re-reads is prose with braces. This reader takes
every row's subject back to the bytes it claims and refuses four ways:

    REG-01  DANGLING_REF        a REF id cited under docs/reference-registry/
                                that no row resolves
    REG-02  SUBJECT_ABSENT      a row whose subject path is not in the tree
    REG-03  DIGEST_STALE        a row whose recorded digest is not the sha256
                                of the bytes at its subject path
    REG-04  LOCATOR_PUBLISHED   a locator inside docs/reference-registry/ -
                                any URI scheme, or a Google Drive/Docs
                                identifier without one

It reads the working tree and nothing else: no network, no GitHub API, no
Drive. That is a deliberate ceiling, and it costs two of the four refusals
ed3c/ai-content-notes#64 specified. `missing issue` and `missing PR` were
provider-existence checks; nothing here can perform them, so they are not
approximated by a shape check pretending to be one. REG-01 and REG-03 are the
retargeted forms of #64's `dangling REF` and `stale head` against a subject
that exists; REG-02 and REG-04 are new, and REG-04 is the one this repository's
`Required behavior #13` actually needs.

This reader does not restate the six laws in
`tests/test_reference_registry_inventory.py` (#57, settled against #96 in PR
#103, merge `3039adde19fc7d10f024325fd86ff68508408e2b`). That module owns the
document's internal laws - opaque ids, no persisted `visibility`, the state
ceiling, credential-bearing URLs, duplicate identity - and runs in the trusted
suite against every candidate tree. Two owners for one law is the failure this
registry's own history is made of.

Owner: ed3c/ai-content-notes#96.

    python3 tools/verify_reference_registry.py
    python3 tools/verify_reference_registry.py --json
    python3 tools/verify_reference_registry.py --root PATH
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = PurePosixPath("docs/reference-registry")
REGISTRY_JSON = REGISTRY_DIR / "reference-index.private.json"
REGISTRY_SCHEMA = "reference-index.private@1"

REF_ID = re.compile(r"REF-[0-9]{4}")
URI_SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*://")
GOOGLE_LOCATOR = re.compile(r"(?:drive|docs)\.google\.com|/(?:document|spreadsheets|file)/d/")

DANGLING_REF = "DANGLING_REF"
SUBJECT_ABSENT = "SUBJECT_ABSENT"
DIGEST_STALE = "DIGEST_STALE"
LOCATOR_PUBLISHED = "LOCATOR_PUBLISHED"


def checked_relative(raw: str) -> PurePosixPath:
    """Reject any subject path that could resolve outside the audited tree."""
    path = PurePosixPath(raw)
    if not raw or raw.startswith("/") or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"registry subject escapes the repository: {raw!r}")
    return path


def load_registry(path: Path) -> dict:
    registry = json.loads(path.read_text(encoding="utf-8"))
    if registry.get("schema") != REGISTRY_SCHEMA:
        raise ValueError(f"unexpected registry schema: {registry.get('schema')!r}")
    return registry


def registry_files(root: Path) -> list[Path]:
    """Every file under docs/reference-registry/, sorted for stable output."""
    directory = root / REGISTRY_DIR
    return sorted(path for path in directory.rglob("*") if path.is_file())


def check_subjects(registry: dict, root: Path) -> list[dict]:
    """REG-02 and REG-03: every row is taken back to the bytes it claims."""
    findings = []
    for record in registry["references"]:
        ref_id = str(record.get("id"))
        subject = str(record.get("external_id") or "")
        path = root.joinpath(*checked_relative(subject).parts)
        if not path.is_file():
            findings.append({"code": SUBJECT_ABSENT, "ref": ref_id, "subject": subject})
            continue
        actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != record.get("digest"):
            findings.append(
                {
                    "code": DIGEST_STALE,
                    "ref": ref_id,
                    "subject": subject,
                    "recorded": record.get("digest"),
                    "actual": actual,
                }
            )
    return findings


def check_cited_refs(registry: dict, root: Path) -> list[dict]:
    """REG-01: a REF id cited in this directory must resolve to one row."""
    resolvable = {str(record.get("id")) for record in registry["references"]}
    findings = []
    for path in registry_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:  # a binary here is itself out of contract
            findings.append({"code": DANGLING_REF, "file": str(path.relative_to(root)), "ref": None})
            continue
        for ref_id in sorted(set(REF_ID.findall(text)) - resolvable):
            findings.append(
                {"code": DANGLING_REF, "file": str(path.relative_to(root)), "ref": ref_id}
            )
    return findings


def check_no_locator(root: Path) -> list[dict]:
    """REG-04: this directory carries ids, roles, states and repository paths.

    Never a locator. Any URI scheme is refused, and so is a Google Drive or
    Docs identifier written without one - the closed chain's own bytes carried
    27 of those, which is why the scheme test alone is not enough.
    """
    findings = []
    for path in registry_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for pattern in (URI_SCHEME, GOOGLE_LOCATOR):
                match = pattern.search(line)
                if match:
                    findings.append(
                        {
                            "code": LOCATOR_PUBLISHED,
                            "file": str(path.relative_to(root)),
                            "line": number,
                            "match": match.group(0),
                        }
                    )
                    break
    return findings


def verify(root: Path) -> dict:
    registry = load_registry(root / REGISTRY_JSON)
    findings = (
        check_cited_refs(registry, root)
        + check_subjects(registry, root)
        + check_no_locator(root)
    )
    return {
        "schema": "reference-registry-report@1",
        "root": str(root),
        "rows": len(registry["references"]),
        "files_scanned": [str(path.relative_to(root)) for path in registry_files(root)],
        "findings": findings,
        "status": "FAIL" if findings else "PASS",
        "evidence_ceiling": (
            "Registry shape and subject binding on one tree. Not source accuracy, "
            "not rights, not provider state, not whether any subject was ever read "
            "by anything but this reader."
        ),
    }


def render(report: dict) -> str:
    lines = [f"reference registry  root={report['root']}  rows={report['rows']}"]
    for finding in report["findings"]:
        lines.append("  " + json.dumps(finding, sort_keys=True))
    lines.append(
        f"  files_scanned={len(report['files_scanned'])} "
        f"findings={len(report['findings'])} status={report['status']}"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = parser.parse_args(argv)

    report = verify(args.root.resolve())
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else render(report))
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
