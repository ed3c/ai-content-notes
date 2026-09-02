"""Fail-closed tests for the live GitHub blob source adapter."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import github_source_adapter as adapter  # noqa: E402
import source_registry  # noqa: E402

DESCRIPTOR_SCHEMA = json.loads(
    (ROOT / "schemas" / "github-source-descriptor.schema.json").read_text(encoding="utf-8")
)
REGISTRY_SCHEMA = json.loads(
    (ROOT / "schemas" / "source-registry.schema.json").read_text(encoding="utf-8")
)
EXAMPLES = ROOT / "examples" / "source-registry"
DESCRIPTOR_PATH = EXAMPLES / "github-blob-descriptor.json"
SUBJECT = ROOT / "governance" / "CARD_PROTOCOL_V7_1.md"


def load_descriptor() -> dict:
    return json.loads(DESCRIPTOR_PATH.read_text(encoding="utf-8"))


def failures_for(descriptor: dict, payload: bytes, tmp_path: Path) -> list[str]:
    blob = tmp_path / "blob.bin"
    blob.write_bytes(payload)
    observation = adapter.inspect_blob(blob)
    return adapter.validate_descriptor(descriptor, DESCRIPTOR_SCHEMA, observation)


def test_git_blob_sha1_matches_the_repository_governance_pointer() -> None:
    """The pure-Python Git object name must agree with the pointer already committed.

    This is a second, independent arrival for the same blob identity: the pointer
    was written by a different tool at a different time. If either drifts, this
    test is the thing that goes red.
    """
    pointer = json.loads(
        (ROOT / "governance" / "CARD_PROTOCOL_CURRENT.json").read_text(encoding="utf-8")
    )
    computed = adapter.git_blob_sha1(SUBJECT.read_bytes())
    assert computed == pointer["git_blob_sha1"]


def test_exact_subject_is_admitted() -> None:
    registry, receipt, observation = adapter.generate(
        SUBJECT,
        DESCRIPTOR_PATH,
        ROOT / "schemas" / "github-source-descriptor.schema.json",
        ROOT / "schemas" / "source-registry.schema.json",
    )
    assert source_registry.validate_registry(registry, REGISTRY_SCHEMA) == []
    entry = registry["entries"][0]
    assert entry["state"] == "ADMITTED"
    assert entry["source_kind"] == "GITHUB_BLOB"
    assert entry["identity"]["immutable"] is True
    assert entry["readback"]["method"] == "GITHUB_BLOB_SHA"
    assert entry["authority_ceiling"] == "SOURCE_INPUT_ONLY"
    assert receipt["readback_method"] == "GIT_BLOB_SHA1_RECOMPUTE"
    assert observation["git_blob_sha1"] == entry["identity"]["blob_sha"]


def test_committed_example_packet_is_byte_stable() -> None:
    """The persisted example must reproduce from its own inputs, byte for byte."""
    registry, receipt, _ = adapter.generate(
        SUBJECT,
        DESCRIPTOR_PATH,
        ROOT / "schemas" / "github-source-descriptor.schema.json",
        ROOT / "schemas" / "source-registry.schema.json",
    )
    persisted_registry = (EXAMPLES / "github-blob-source-registry.json").read_text(
        encoding="utf-8"
    )
    persisted_receipt = (EXAMPLES / "github-blob-readback-receipt.json").read_text(
        encoding="utf-8"
    )
    assert source_registry.canonical_document(registry) == persisted_registry
    assert adapter.canonical_json(receipt) == persisted_receipt


def test_one_flipped_byte_breaks_the_read_back(tmp_path: Path) -> None:
    """The load-bearing control: retained bytes must be the named Git object."""
    payload = bytearray(SUBJECT.read_bytes())
    payload[0] ^= 0x01
    failures = failures_for(load_descriptor(), bytes(payload), tmp_path)
    assert "descriptor: GITHUB_BLOB_SHA_MISMATCH" in failures
    assert "descriptor: GITHUB_CONTENT_DIGEST_MISMATCH" in failures


def test_branch_url_is_refused_as_mutable_identity(tmp_path: Path) -> None:
    descriptor = load_descriptor()
    descriptor["resolved_url"] = (
        "https://github.com/ed3c/ai-content-notes/blob/main/governance/CARD_PROTOCOL_V7_1.md"
    )
    failures = failures_for(descriptor, SUBJECT.read_bytes(), tmp_path)
    assert "descriptor: GITHUB_RESOLVED_URL_NOT_COMMIT_PINNED" in failures


def test_public_visibility_is_not_a_rights_basis(tmp_path: Path) -> None:
    descriptor = load_descriptor()
    descriptor["rights"]["basis"] = "PUBLIC_VISIBILITY_ONLY"
    failures = failures_for(descriptor, SUBJECT.read_bytes(), tmp_path)
    assert "descriptor: PUBLIC_VISIBILITY_USED_AS_RIGHTS" in failures


def test_title_or_snippet_only_is_refused(tmp_path: Path) -> None:
    descriptor = load_descriptor()
    descriptor["content_profile"]["content_scope"] = "TITLE_OR_SNIPPET_ONLY"
    failures = failures_for(descriptor, SUBJECT.read_bytes(), tmp_path)
    assert "descriptor: GITHUB_PARTIAL_CONTENT_NOT_ADMITTED" in failures


def test_incomplete_source_is_refused(tmp_path: Path) -> None:
    descriptor = load_descriptor()
    descriptor["completeness"]["status"] = "PARTIAL"
    descriptor["completeness"]["missing_parts"] = ["appendix"]
    failures = failures_for(descriptor, SUBJECT.read_bytes(), tmp_path)
    assert "descriptor: SOURCE_COMPLETENESS_NOT_PASS" in failures
    assert "descriptor: COMPLETE_SOURCE_HAS_MISSING_PARTS" in failures


def test_widened_authority_ceiling_is_refused(tmp_path: Path) -> None:
    descriptor = load_descriptor()
    descriptor["authority_ceiling"] = "HUMAN_PROJECTION"
    failures = failures_for(descriptor, SUBJECT.read_bytes(), tmp_path)
    # The schema pins the ceiling, so the refusal arrives as a schema failure.
    assert any(item.startswith("schema:authority_ceiling") for item in failures)


def test_mutable_identity_cannot_reach_admitted() -> None:
    """A GITHUB_BLOB entry marked mutable must not survive the semantic gate."""
    registry, _, _ = adapter.generate(
        SUBJECT,
        DESCRIPTOR_PATH,
        ROOT / "schemas" / "github-source-descriptor.schema.json",
        ROOT / "schemas" / "source-registry.schema.json",
    )
    tampered = copy.deepcopy(registry)
    tampered["entries"][0]["identity"]["immutable"] = False
    tampered = source_registry.canonicalize(tampered)
    failures = source_registry.validate_registry(tampered, REGISTRY_SCHEMA)
    assert any("GITHUB_BLOB_MARKED_MUTABLE" in item for item in failures)


def test_empty_blob_is_refused(tmp_path: Path) -> None:
    blob = tmp_path / "empty.bin"
    blob.write_bytes(b"")
    with pytest.raises(adapter.GithubSourceError):
        adapter.inspect_blob(blob)
