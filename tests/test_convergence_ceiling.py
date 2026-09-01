"""ed3c/ai-content-notes#75 - knowledge convergence must not read as verification.

The invariant under test:

    a batch reaching DONE in this repository's knowledge plane must not be
    readable as runtime verification

DONE is the strongest state this repository emits. Until now the only thing
between it and a downstream reader treating it as verified was a sentence:
`AGENTS.md` Required behavior #14, and the ceiling paragraph in
`evals/loop-batches/README.md` that records `gate_authority: "none"`,
`digest_authority: "runner"` and that the QG-01..QG-24 labels inside the round
responses are model claims. Nothing read either -

    grep -rn "Atlas admission\\|Evidence Grade\\|production routability\\|Skill lifecycle" tests/
    # no matches at main = d7631f5797687108ee2be8980e8e48a3e3da916c

- which is this issue's own non-goal, "no behavioral verification inferred
from prose or card coverage", applied to its own enforcement.

Each reader below takes its subject as data so a planted defect can be pushed
through it, and each refusal is demonstrated rather than asserted.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP_BATCHES = ROOT / "evals" / "loop-batches"
BATCH_README = LOOP_BATCHES / "README.md"
AGENT_FILES = (ROOT / "AGENTS.md", ROOT / "CLAUDE.md")

# The honest values. A receipt at DONE that carries anything else is claiming
# an authority the runner does not have.
HONEST_AUTHORITY = {"gate_authority": "none", "digest_authority": "runner"}

# Round keys that would promote a model-authored gate label into an unqualified
# one. The receipt keeps them under `model_authored_gate_labels` and keeps the
# runner's own verdict in `status`, next to the model's `declared_status`.
PROMOTED_CLAIM_KEYS = (
    "assertion_report",
    "next_state",
    "gate_labels",
    "quality_gates",
    "gate_report",
)

CEILING_SENTENCES = (
    "What DONE means here, and what it does not",
    'gate_authority: "none"',
    'digest_authority: "runner"',
    "QG-01..QG-24 labels inside the round responses are model claims",
)

LAW_14 = (
    "14. Never raise Atlas admission, runtime Evidence Grade, Skill lifecycle, "
    "production routability or implicit invocation from this repository."
)


def flatten(text: str) -> str:
    """Collapse wrapping so a sentence is matched, not a line break."""
    return re.sub(r"\s+", " ", text)


def receipt_violations(receipt: dict) -> list[str]:
    """Name every way a DONE receipt overstates what produced it."""
    if receipt.get("status") != "DONE":
        return []
    violations = []
    for field, honest in HONEST_AUTHORITY.items():
        actual = receipt.get(field)
        if actual != honest:
            violations.append(f"{field}={actual!r} not {honest!r}")
    for index, round_ in enumerate(receipt.get("rounds", []), start=1):
        if "model_authored_gate_labels" not in round_:
            violations.append(f"round {index} has no model_authored_gate_labels")
        for key in PROMOTED_CLAIM_KEYS:
            if key in round_:
                violations.append(f"round {index} promotes model claims to {key!r}")
        if "declared_status" not in round_:
            violations.append(f"round {index} has no separate declared_status")
    return violations


def ceiling_violations(readme: str) -> list[str]:
    flat = flatten(readme)
    return [
        f"ceiling paragraph is missing {sentence!r}"
        for sentence in CEILING_SENTENCES
        if sentence not in flat
    ]


def law_violations(agent_file: str) -> list[str]:
    return [] if LAW_14 in flatten(agent_file) else ["Required behavior #14 is missing"]


def receipts() -> list[tuple[Path, dict]]:
    found = [
        (path, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(LOOP_BATCHES.glob("*/run-receipt.json"))
    ]
    # An empty knowledge plane must not read as a clean one.
    assert found, f"no run receipts under {LOOP_BATCHES}"
    return found


def done_receipt() -> dict:
    for _path, receipt in receipts():
        if receipt.get("status") == "DONE":
            return receipt
    raise AssertionError("no batch at DONE; this atom has nothing to hold")


def test_every_done_batch_keeps_its_authority_honest() -> None:
    seen_done = False
    for path, receipt in receipts():
        assert receipt_violations(receipt) == [], path
        seen_done = seen_done or receipt.get("status") == "DONE"
    assert seen_done, "no batch at DONE; this atom has nothing to hold"


def test_batch_readme_states_what_done_does_not_cover() -> None:
    assert ceiling_violations(BATCH_README.read_text(encoding="utf-8")) == []


def test_both_agent_files_carry_required_behavior_14() -> None:
    for path in AGENT_FILES:
        assert law_violations(path.read_text(encoding="utf-8")) == [], path


def test_planted_external_gate_authority_goes_red() -> None:
    planted = copy.deepcopy(done_receipt())
    planted["gate_authority"] = "github-actions"
    violations = receipt_violations(planted)
    assert violations == ["gate_authority='github-actions' not 'none'"]


def test_planted_external_digest_authority_goes_red() -> None:
    planted = copy.deepcopy(done_receipt())
    planted["digest_authority"] = "external-validator"
    violations = receipt_violations(planted)
    assert violations == ["digest_authority='external-validator' not 'runner'"]


def test_planted_promotion_of_model_gate_labels_goes_red() -> None:
    planted = copy.deepcopy(done_receipt())
    planted["rounds"][-1]["assertion_report"] = planted["rounds"][-1].pop(
        "model_authored_gate_labels"
    )
    violations = receipt_violations(planted)
    assert "round 3 has no model_authored_gate_labels" in violations
    assert "round 3 promotes model claims to 'assertion_report'" in violations


def test_a_continue_batch_is_not_where_this_ceiling_is_enforced() -> None:
    # Negative control for the reader itself: the same overstatement below DONE
    # is out of scope here, so a green result above is about DONE and not about
    # the reader ignoring its input.
    planted = copy.deepcopy(done_receipt())
    planted["status"] = "CONTINUE"
    planted["gate_authority"] = "github-actions"
    assert receipt_violations(planted) == []


def test_planted_deletion_of_the_ceiling_paragraph_goes_red() -> None:
    readme = BATCH_README.read_text(encoding="utf-8")
    head, _, _tail = readme.partition("## What DONE means here, and what it does not")
    assert head != readme, "the ceiling heading moved; this plant no longer bites"
    violations = ceiling_violations(head)
    assert violations == [
        f"ceiling paragraph is missing {sentence!r}" for sentence in CEILING_SENTENCES
    ]


def test_planted_deletion_of_law_14_goes_red() -> None:
    for path in AGENT_FILES:
        text = path.read_text(encoding="utf-8")
        assert LAW_14 in flatten(text), path
        stripped = flatten(text).replace(LAW_14, "")
        assert law_violations(stripped) == ["Required behavior #14 is missing"], path
