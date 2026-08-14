"""Every rights gate in the pipeline must speak one vocabulary.

The repository carried three incompatible dialects, and two of them shared no
value at all: a video acquired under `creator-permission` could never satisfy
the frame sampler, and an allowlist entry written as `user-provided` could
never be handed to any adapter. Nothing failed — the record simply could not
flow, and the block looked like a rights problem rather than a spelling one.

These tests bind every constant and every schema enum to
`tools/rights_vocabulary.py`, so a fourth dialect is a red test.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import rights_vocabulary as vocab  # noqa: E402

ADAPTERS = {
    "youtube_transcript.py": "ALLOWED_RIGHTS_BASES",
    "youtube_direct_caption_adapter.py": "VERIFIED_RIGHTS_BASES",
    "youtube_transcript_ai_adapter.py": "VERIFIED_RIGHTS_BASES",
    "ai_video_transcriber_contract.py": "VERIFIED_RIGHTS_BASES",
}


def literal_set(module_name: str, constant: str) -> set[str]:
    """Read a module-level set literal without importing the module."""
    tree = ast.parse((REPOSITORY_ROOT / "tools" / module_name).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == constant for t in node.targets
        ):
            return set(ast.literal_eval(node.value))
    raise AssertionError(f"{module_name}: {constant} not found")


@pytest.mark.parametrize(("module_name", "constant"), sorted(ADAPTERS.items()))
def test_every_acquisition_adapter_uses_the_canonical_set(module_name: str, constant: str) -> None:
    assert literal_set(module_name, constant) == set(vocab.VERIFIED_RIGHTS_BASES)


def test_the_allowlist_schema_enum_matches() -> None:
    schema = json.loads(
        (REPOSITORY_ROOT / "schemas/rights-allowlist.schema.json").read_text(encoding="utf-8")
    )
    enum = schema["$defs"]["entry"]["properties"]["rights_basis"]["enum"]
    assert set(enum) == set(vocab.ALL_RIGHTS_BASES)
    assert len(enum) == len(set(enum))


def test_the_visual_receipt_schema_enum_matches() -> None:
    schema = json.loads(
        (REPOSITORY_ROOT / "schemas/visual-evidence-receipt.schema.json").read_text(encoding="utf-8")
    )
    enum = set(schema["properties"]["rights"]["properties"]["basis"]["enum"])
    # `unattested` exists only for a receipt written before any attestation.
    assert enum == set(vocab.ALL_RIGHTS_BASES) | {"unattested"}


def test_the_frame_sampler_gates_on_the_canonical_verified_set() -> None:
    import frame_sampling_plan

    assert set(frame_sampling_plan.ALLOWED) == set(vocab.VERIFIED_RIGHTS_BASES)


def test_the_visual_receipt_tool_gates_on_the_canonical_verified_set() -> None:
    import visual_evidence_receipt

    assert set(visual_evidence_receipt.ATTESTED_BASES) == set(vocab.VERIFIED_RIGHTS_BASES)


def test_public_visibility_is_not_expressible_anywhere() -> None:
    """Being public, or paying to view, is never a rights basis."""
    for candidate in ("public-visibility", "publicly-available", "youtube-premium", "premium"):
        assert candidate not in vocab.ALL_RIGHTS_BASES


def test_the_evaluation_only_basis_can_never_acquire_media() -> None:
    assert vocab.EVALUATION_ONLY_BASIS not in vocab.VERIFIED_RIGHTS_BASES
    for status in ("verified", "evaluation-only", "blocked"):
        assert not vocab.may_acquire_media(vocab.EVALUATION_ONLY_BASIS, status)


def test_media_acquisition_needs_both_a_verified_basis_and_a_verified_status() -> None:
    assert vocab.may_acquire_media("creator-permission", "verified") is True
    assert vocab.may_acquire_media("creator-permission", "evaluation-only") is False
    assert vocab.may_acquire_media("user-provided-media", "verified") is True
    assert vocab.may_acquire_media("not-a-basis", "verified") is False


def test_a_record_can_flow_from_allowlist_to_adapter_to_frame_sampler() -> None:
    """The interop this vocabulary exists to restore."""
    import frame_sampling_plan

    basis = "creator-permission"
    allowlist_schema = json.loads(
        (REPOSITORY_ROOT / "schemas/rights-allowlist.schema.json").read_text(encoding="utf-8")
    )
    assert basis in allowlist_schema["$defs"]["entry"]["properties"]["rights_basis"]["enum"]
    assert basis in literal_set("youtube_direct_caption_adapter.py", "VERIFIED_RIGHTS_BASES")
    planned = frame_sampling_plan.build("sha256:" + "0" * 64, 120.0, 4, basis)
    assert planned["status"] == "PLANNED"
