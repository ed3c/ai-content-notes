"""ed3c/ai-content-notes#107 - a promotion declaration must carry its own gate record.

The invariant under test:

    a machine-readable promotion declaration in this repository must record the
    Promotion Gate it went through, or be refused

`docs/DOMAIN_CONTEXT_SUPPLY_PLANE.md` defines the Promotion Gate as a six-step
sequence and `AGENTS.md` Required behavior #17 requires it before downstream
architecture work is created from cards. Both are Guide-layer prose, and the
same document names the rule that makes that insufficient - "a repeatedly
violated mechanically expressible invariant must migrate downward from Guide to
Guard or Shape". `README.md` has carried the admission in its own words:

    nothing in `tests/` refuses a promotion that skipped it

This reader is the Guard for the part that is mechanically expressible. It is
deliberately not a gate on merging: whether a promotion is *justified* stays a
human judgement, and nothing here decides it. It refuses only the case where a
declaration asserts a promotion and records no gate.

## What this reader reads, and what its silence means

Its live reading is `ABSENT`, not `PASS`. No artifact on `main` declares a
promotion - 37 schemas name no promotion field, and the single `promot` hit
anywhere in the repository's JSON is a free-text value in
`evals/source-intake/modern-web-architecture/shadow-review.json` ("market and
commercial promotion"), which is prose inside a value and not a declaration.

An `ABSENT` census and a clean one are the same bytes unless the scanner is
shown to work, so `test_the_scanner_finds_a_planted_declaration` plants one and
proves the walk would have found it. Without that, the green above would be
evidence about this file rather than about the repository.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
README = REPOSITORY_ROOT / "README.md"

# Any key naming a promotion, in any spelling. Matching keys rather than values
# is what keeps prose out: a sentence about promotion inside a string is not a
# declaration, and the repository already contains one such sentence.
PROMOTION_KEY = re.compile(r"promot", re.IGNORECASE)
GATE_KEY = "promotion_gate"

# The two Promotion Gate steps that are mechanically answerable. Step 3 is the
# Existing-System Check and step 4 is the lowest deterministic owner; the other
# four steps are judgements this reader does not adjudicate.
EXISTING_SYSTEM_CHECK = ("MAPPED", "MISSING")
OWNERS = ("Shape", "Guard", "Guide")


def gate_violations(declaration: dict) -> list[str]:
    """Name every way this promotion declaration skipped the Promotion Gate."""
    gate = declaration.get(GATE_KEY)
    if not isinstance(gate, dict):
        return [f"promotion declared with no {GATE_KEY} record"]
    violations = []
    check = gate.get("existing_system_check")
    if check not in EXISTING_SYSTEM_CHECK:
        violations.append(
            f"existing_system_check={check!r} is not one of {EXISTING_SYSTEM_CHECK}"
        )
    owner = gate.get("owner")
    if owner not in OWNERS:
        violations.append(f"owner={owner!r} is not one of {OWNERS}")
    return violations


def declarations(value: object) -> list[dict]:
    """Every object anywhere in this document that names a promotion."""
    found: list[dict] = []
    if isinstance(value, dict):
        if any(PROMOTION_KEY.search(key) for key in value):
            found.append(value)
        for item in value.values():
            found.extend(declarations(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(declarations(item))
    return found


def documents(root: Path) -> list[tuple[Path, object]]:
    """Every JSON and JSONL document in the tree, parsed."""
    found: list[tuple[Path, object]] = []
    for path in sorted(root.rglob("*.json*")):
        if ".git" in path.parts or path.suffix not in {".json", ".jsonl"}:
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".jsonl":
            found.extend(
                (path, json.loads(line)) for line in text.splitlines() if line.strip()
            )
        else:
            found.append((path, json.loads(text)))
    # An empty walk must not read the same as a clean one.
    assert found, f"no JSON documents found under {root}"
    return found


def census(root: Path) -> list[str]:
    """Every promotion declaration in the tree that skipped its gate."""
    return sorted(
        f"{path.relative_to(root).as_posix()}: {violation}"
        for path, document in documents(root)
        for declaration in declarations(document)
        for violation in gate_violations(declaration)
    )


def promoted_count(root: Path) -> int:
    return sum(len(declarations(document)) for _path, document in documents(root))


# A declaration that answered the two mechanically answerable gate steps.
GATED = {
    "promoted_concept": "one obvious writer for durable state",
    GATE_KEY: {"existing_system_check": "MISSING", "owner": "Shape"},
}


def test_the_live_census_is_absent_and_not_a_pass() -> None:
    # No promotion event has ever been emitted here, so there is nothing to
    # refuse. This is a measurement of absence, not a verdict on any artifact.
    # The census is asserted first so a refusal names the skipped gate rather
    # than only the fact that the reading is no longer ABSENT.
    assert census(REPOSITORY_ROOT) == []
    assert promoted_count(REPOSITORY_ROOT) == 0


def test_the_scanner_finds_a_planted_declaration(tmp_path: Path) -> None:
    # Without this, ABSENT above would be unfalsifiable: a walk that sees
    # nothing and a walk that cannot see are the same green.
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "pack.json").write_text(
        json.dumps({"cards": [GATED]}), encoding="utf-8"
    )
    assert promoted_count(tmp_path) == 1
    assert census(tmp_path) == []


def test_a_declaration_without_a_gate_record_is_refused() -> None:
    assert gate_violations({"promoted_to": "Shape"}) == [
        f"promotion declared with no {GATE_KEY} record"
    ]


def test_a_gate_record_that_is_not_an_object_is_refused() -> None:
    for planted in (None, "PASSED", [], True):
        assert gate_violations({GATE_KEY: planted}) == [
            f"promotion declared with no {GATE_KEY} record"
        ], planted


def test_an_unanswered_existing_system_check_is_refused() -> None:
    for planted in (None, "", "SKIPPED", "PASS", "mapped"):
        planted_gate = {**GATED, GATE_KEY: {**GATED[GATE_KEY], "existing_system_check": planted}}
        assert gate_violations(planted_gate) == [
            f"existing_system_check={planted!r} is not one of {EXISTING_SYSTEM_CHECK}"
        ], planted


def test_an_owner_outside_shape_guard_guide_is_refused() -> None:
    # FeatureMap and Spatial Loop are escalations *after* an owner is chosen,
    # never the owner itself, so naming one here is a skipped step 4.
    for planted in (None, "FeatureMap", "Spatial Loop", "shape", "AGENTS.md"):
        planted_gate = {**GATED, GATE_KEY: {**GATED[GATE_KEY], "owner": planted}}
        assert gate_violations(planted_gate) == [
            f"owner={planted!r} is not one of {OWNERS}"
        ], planted


def test_a_complete_gate_record_passes() -> None:
    # Negative control for the reader itself: it must be able to say yes, or
    # every red above would be about a reader that refuses everything.
    assert gate_violations(GATED) == []
    for owner in OWNERS:
        for check in EXISTING_SYSTEM_CHECK:
            assert gate_violations(
                {"promotion": "x", GATE_KEY: {"existing_system_check": check, "owner": owner}}
            ) == []


def test_prose_about_promotion_inside_a_value_is_not_a_declaration() -> None:
    # The repository already contains one such sentence. A reader that counted
    # it would report a promotion nobody made.
    assert declarations({"themes": ["market and commercial promotion"]}) == []
    assert declarations({"note": "run the Promotion Gate first"}) == []


def test_the_readme_states_the_carrier_and_the_remaining_ceiling() -> None:
    # The admission this issue was filed against is a landed line; the sensor is
    # worth nothing if the line still says nothing refuses a skipped promotion.
    readme = README.read_text(encoding="utf-8")
    assert "nothing in `tests/` refuses a promotion that skipped it" not in readme
    assert "tests/test_promotion_gate_sensor.py" in readme
    assert "no promotion event has ever been emitted" in readme
