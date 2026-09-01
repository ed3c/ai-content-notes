"""The generated `verify-cards` skill keeps the shape its readers depend on.

Two readers depend on it and neither is a person reading prose. The pinned
`/maintain-verification-skill` Step 0 looks for a project-local skill with
launch/drive sections and a feature map; its live pass then reads each feature
file's four H2 sections. And the skill's own planted-signal drive is only a
control while the plant it seeds is absent from the synthetic subject.

So this file reds when the skill stops being maintainable rather than when its
wording changes: a dropped section, a feature file that lost its four-H2 shape,
an index that no longer matches its directory, a helper that lost its
executable bit, a plant that drifted into the subject it is supposed to
control, or an evidence directory that a cleanup ate. Issue #91.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import loop_fixture as fixture  # noqa: E402

SKILL = REPOSITORY_ROOT / ".cursor" / "skills" / "verify-cards"
SKILL_MD = SKILL / "SKILL.md"
FEATURES = SKILL / "features"
HELPER = SKILL / "drive_planted_signal.py"
EVIDENCE = SKILL / "evidence"

# The six sections `/create-verification-skill` requires of a generated skill,
# plus the maintenance record this repository's issue #91 asked for.
REQUIRED_SECTIONS = ("Launch", "Doctor", "Drive", "Evidence", "Cleanup", "Helpers", "Maintenance")

# The feature-entry contract: exactly these four H2s, in this order.
FEATURE_H2S = ("Sub-features", "How to get to it (user POV)", "Driving it with the card pipeline CLI", "Gotchas")

H2 = re.compile(r"^## (.+)$", re.M)
INDEX_LINK = re.compile(r"\]\(\./([a-z0-9-]+\.md)\)")


def test_the_skill_registers_and_carries_all_six_generated_sections() -> None:
    text = SKILL_MD.read_text(encoding="utf-8")
    assert text.startswith("---\n"), "no YAML frontmatter: the skill would never register"
    frontmatter = text.split("---\n", 2)[1]
    assert "name: verify-cards" in frontmatter
    assert "description:" in frontmatter

    headings = H2.findall(text)
    for section in REQUIRED_SECTIONS:
        assert section in headings, f"SKILL.md lost its {section} section"

    for placeholder in ("TODO", "FIXME", "<app>", "<harness>", "<placeholder>"):
        assert placeholder not in text, f"SKILL.md still carries the {placeholder} placeholder"


def test_the_feature_index_and_the_feature_directory_agree() -> None:
    index = FEATURES / "README.md"
    linked = set(INDEX_LINK.findall(index.read_text(encoding="utf-8")))
    on_disk = {path.name for path in FEATURES.glob("*.md")} - {"README.md"}

    assert linked == on_disk, f"index and directory disagree: {linked ^ on_disk}"
    assert on_disk == {
        "compile-to-done.md",
        "planted-signal-refusal.md",
        "registry-idempotency.md",
        "guard-verdicts.md",
    }


def test_every_feature_file_keeps_the_four_h2_shape() -> None:
    for path in sorted(FEATURES.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        assert text.startswith("# "), f"{path.name}: no H1 title"
        assert H2.findall(text) == list(FEATURE_H2S), f"{path.name}: not the four-H2 shape"
        driving = text.split(f"## {FEATURE_H2S[2]}\n", 1)[1]
        assert driving.lstrip().startswith("Preconditions:"), (
            f"{path.name}: the driving section must open with Preconditions:"
        )


def test_the_helper_is_executable_and_its_invocation_is_documented() -> None:
    import os

    assert os.access(HELPER, os.X_OK), "a helper the reader cannot run is not a helper"
    body = SKILL_MD.read_text(encoding="utf-8")
    for invocation in (
        ".cursor/skills/verify-cards/drive_planted_signal.py seed --out",
        ".cursor/skills/verify-cards/drive_planted_signal.py respond",
        ".cursor/skills/verify-cards/drive_planted_signal.py respond --anchor",
    ):
        assert invocation in body, f"SKILL.md does not show `{invocation}`"


def test_the_seeded_plant_is_absent_from_the_subject_it_controls(tmp_path: Path) -> None:
    """The helper's plant comes from tests/loop_fixture.py, and must stay a plant."""
    subject = fixture.SYNTHETIC_SOURCE.read_text(encoding="utf-8")
    assert fixture.PLANTED_QUOTE not in subject

    result = subprocess.run(
        [sys.executable, str(HELPER), "seed", "--out", str(tmp_path / "planted")],
        capture_output=True,
        text=True,
        cwd=REPOSITORY_ROOT,
    )
    assert result.returncode == 0, result.stderr
    seeded = json.loads(result.stdout)

    source = Path(seeded["source"]).read_text(encoding="utf-8")
    assert fixture.PLANTED_QUOTE in source
    controls = json.loads(Path(seeded["high_signal"]).read_text(encoding="utf-8"))
    assert controls == [{"key": seeded["key"], "quote": fixture.PLANTED_QUOTE}]


def test_the_committed_proof_survived_its_own_cleanup() -> None:
    """Evidence lives outside every run directory, so cleanup cannot eat it."""
    runs = sorted(path for path in EVIDENCE.glob("*") if path.is_dir())
    assert runs, "the skill names an evidence location that holds no proof"
    for run in runs:
        assert (run / "README.md").is_file(), f"{run.name}: no account of what was driven"
        assert (run / "drive-log.txt").is_file(), (
            f"{run.name}: no command log. Not `transcript.txt`: "
            "tests/test_live_cvrngaqzq3y_v7_1.py bans that exact filename tree-wide."
        )
        receipts = sorted(run.glob("*run-receipt.json"))
        assert receipts, f"{run.name}: no run receipt, only prose"
        for receipt in receipts:
            assert json.loads(receipt.read_text(encoding="utf-8"))["stopped_on"] == (
                "completion-contract"
            )
