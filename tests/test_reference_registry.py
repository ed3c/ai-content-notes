"""ed3c/ai-content-notes#96 - the registry's five binding refusals.

`tools/verify_reference_registry.py` is only worth running if it refuses. Each
control below plants one defect and asserts the exact refusal, then asserts the
unplanted tree is clean, so a law that has stopped firing shows up as a failing
control rather than a quiet pass.

Two of the four refusals ed3c/ai-content-notes#64 specified are absent on
purpose: `missing issue` and `missing PR` were provider-existence checks, and
this reader has no network. They are named here rather than approximated by a
shape check pretending to be one.

The six *document* laws - opaque ids, no persisted `visibility`, the state
ceiling, credential-bearing URLs, duplicate identity - are not restated here.
`tests/test_reference_registry_inventory.py` owns them and arms against the
committed registry automatically now that it exists.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from test_reference_registry_inventory import REF_ID as TRUSTED_REF_ID  # noqa: E402
from verify_reference_registry import (  # noqa: E402
    DANGLING_REF,
    DIGEST_STALE,
    LOCATOR_KEY,
    LOCATOR_PUBLISHED,
    PROVIDER_LOCATOR_KEY,
    REF_CITATION,
    REGISTRY_JSON,
    SUBJECT_ABSENT,
    checked_relative,
    load_registry,
    verify,
)

REGISTRY_DIR = "docs/reference-registry"


def codes(report: dict) -> list[str]:
    return [finding["code"] for finding in report["findings"]]


def planted_tree(tmp_path: Path) -> Path:
    """A copy of just the directories the verifier reads."""
    root = tmp_path / "tree"
    (root / REGISTRY_DIR).mkdir(parents=True)
    for name in ("README.md", "reference-index.private.json"):
        shutil.copy2(ROOT / REGISTRY_DIR / name, root / REGISTRY_DIR / name)
    registry = load_registry(root / REGISTRY_JSON)
    for record in registry["references"]:
        subject = root / record["subject_path"]
        subject.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / record["subject_path"], subject)
    return root


def rewrite(root: Path, registry: dict) -> None:
    (root / REGISTRY_JSON).write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def test_the_committed_registry_verifies_clean() -> None:
    report = verify(ROOT)
    assert report["status"] == "PASS", report["findings"]
    # Tautology guards: a report over zero rows or zero files proves nothing.
    assert report["rows"] >= 1
    assert len(report["files_scanned"]) >= 2


def test_every_row_subject_is_a_path_this_repository_carries() -> None:
    """#96's first acceptance line, asserted rather than described."""
    registry = load_registry(ROOT / REGISTRY_JSON)
    for record in registry["references"]:
        assert (ROOT / checked_relative(record["subject_path"])).is_file(), record["id"]


def test_the_extracted_tree_is_green_before_any_plant(tmp_path: Path) -> None:
    """The control for the controls: each plant below starts from green."""
    assert verify(planted_tree(tmp_path))["status"] == "PASS"


def test_a_dangling_ref_is_refused(tmp_path: Path) -> None:
    root = planted_tree(tmp_path)
    readme = root / REGISTRY_DIR / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\nREF-9999\n", encoding="utf-8")
    report = verify(root)
    assert DANGLING_REF in codes(report)
    assert any(finding.get("ref") == "REF-9999" for finding in report["findings"])


def test_an_absent_subject_is_refused(tmp_path: Path) -> None:
    root = planted_tree(tmp_path)
    registry = load_registry(root / REGISTRY_JSON)
    registry["references"][0]["subject_path"] = "evals/no-such-packet/source-registry.json"
    rewrite(root, registry)
    assert SUBJECT_ABSENT in codes(verify(root))


def test_a_provider_file_id_key_is_refused(tmp_path: Path) -> None:
    """REG-05: `external_id` means provider file ID, and no row here has one.

    Without this the rename is a convention, and a convention is what the
    closed chain had. `main`'s `law_duplicate_titles_need_distinct_identity`
    reads `external_id` as a Drive identity; a repository path arriving under
    that name would be judged by a law written for a different kind of row.
    """
    root = planted_tree(tmp_path)
    registry = load_registry(root / REGISTRY_JSON)
    registry["references"][0][PROVIDER_LOCATOR_KEY] = "EXAMPLE-PLANTED-FILE-ID"
    rewrite(root, registry)
    assert LOCATOR_KEY in codes(verify(root))


def test_the_citation_scanner_agrees_with_the_trusted_ref_identity() -> None:
    """One REF identity, two spellings, held against each other.

    `tests/test_reference_registry_inventory.py` owns the identity predicate
    and runs in the trusted suite; the verifier needs a scanner form because
    it hunts ids inside prose with `findall`. The comparison has to be made
    against `findall` for that reason: `fullmatch` anchors on its own, so a
    control written with it is green whether the pattern is bounded or not -
    which is how the unbounded spelling survived to be found by review rather
    than by this suite.

    Unbounded, `REF-[0-9]{4}` finds `REF-0001` inside `XREF-0001` and inside
    `REF-00019`, neither of which the trusted predicate calls an id.
    """
    for text in ("REF-0001", "REF-9999", "XREF-0001", "REF-00019", "REF-001", "REF-0001X"):
        expected = [text] if TRUSTED_REF_ID.match(text) else []
        assert REF_CITATION.findall(text) == expected, text


def test_a_stale_digest_is_refused(tmp_path: Path) -> None:
    """#64's `stale head`, retargeted: the subject drifted, the row did not."""
    root = planted_tree(tmp_path)
    registry = load_registry(root / REGISTRY_JSON)
    subject = root / registry["references"][0]["subject_path"]
    subject.write_bytes(subject.read_bytes() + b"\n")
    assert DIGEST_STALE in codes(verify(root))


def test_a_stale_digest_is_refused_from_the_other_direction(tmp_path: Path) -> None:
    """And when the row is edited instead of the bytes - same refusal."""
    root = planted_tree(tmp_path)
    registry = load_registry(root / REGISTRY_JSON)
    registry["references"][0]["digest"] = "sha256:" + "0" * 64
    rewrite(root, registry)
    assert DIGEST_STALE in codes(verify(root))


def test_a_planted_drive_locator_is_refused(tmp_path: Path) -> None:
    """`Required behavior #13`, as a check that goes red on a planted locator."""
    root = planted_tree(tmp_path)
    readme = root / REGISTRY_DIR / "README.md"
    locator = "https://" + "drive.google.com/file/d/EXAMPLE-PLANTED-FILE-ID/view"
    readme.write_text(readme.read_text(encoding="utf-8") + "\n" + locator + "\n", encoding="utf-8")
    report = verify(root)
    assert LOCATOR_PUBLISHED in codes(report)

    # And the inverse: removing the plant restores green, so the law is
    # refusing the locator rather than the file's existence.
    readme.write_text(
        readme.read_text(encoding="utf-8").replace("\n" + locator + "\n", "\n"),
        encoding="utf-8",
    )
    assert verify(root)["status"] == "PASS"


def test_a_scheme_less_google_identifier_is_refused(tmp_path: Path) -> None:
    """The blocklist-of-hosts failure: a locator without a scheme still leaks."""
    root = planted_tree(tmp_path)
    readme = root / REGISTRY_DIR / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\nsee /document/d/EXAMPLE-PLANTED-FILE-ID\n",
        encoding="utf-8",
    )
    assert LOCATOR_PUBLISHED in codes(verify(root))


def test_a_registry_subject_cannot_escape_the_tree() -> None:
    for escape in ("../secrets.json", "/etc/passwd", ""):
        try:
            checked_relative(escape)
        except ValueError:
            continue
        raise AssertionError(f"escaping subject accepted: {escape!r}")


def test_exit_code_follows_the_report(tmp_path: Path) -> None:
    from verify_reference_registry import main

    assert main(["--root", str(ROOT)]) == 0
    root = planted_tree(tmp_path)
    registry = load_registry(root / REGISTRY_JSON)
    registry["references"][0]["digest"] = "sha256:" + "0" * 64
    rewrite(root, registry)
    assert main(["--root", str(root), "--json"]) == 1
