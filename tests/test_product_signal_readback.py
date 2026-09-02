"""Fail-closed tests for the Stage 3 product-signal Git blob read-back."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import product_signal  # noqa: E402
import product_signal_readback as readback  # noqa: E402
import source_registry  # noqa: E402

PACKET = ROOT / "evals" / "product-signal" / "modern-web-architecture"
REGISTRY = (
    ROOT / "evals" / "source-intake" / "modern-web-architecture" / "source-registry.json"
)
INPUTS = ("claims.jsonl", "evidence-ledger.json", "contradictions.json")


def build_packet(tmp_path: Path) -> Path:
    """Copy the committed inputs and emit the product-signal the compiler derives."""
    packet = tmp_path / "packet"
    packet.mkdir()
    for name in INPUTS:
        shutil.copy(PACKET / name, packet / name)
    claims = product_signal.load_claims(packet / "claims.jsonl")
    evidence = product_signal.load_json(packet / "evidence-ledger.json")
    contradictions = product_signal.load_json(packet / "contradictions.json")
    registry = product_signal.load_json(REGISTRY)
    compiled = product_signal.compile_signal(claims, evidence, contradictions, registry)
    (packet / "product-signal.json").write_text(
        product_signal.canonical(compiled), encoding="utf-8"
    )
    return packet


def test_git_blob_sha1_matches_the_git_binary(tmp_path: Path) -> None:
    """Second arrival: the git binary must name the same object we compute.

    Pure-Python hashing and `git hash-object` are independent implementations;
    agreeing on a payload with an embedded NUL and a trailing newline is what
    makes the read-back primitive trustworthy rather than merely self-consistent.
    """
    if shutil.which("git") is None:  # pragma: no cover - git is present in CI
        pytest.skip("git binary unavailable")
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"stage-3\x00packet\n")
    expected = subprocess.run(
        ["git", "hash-object", "--", str(sample)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert source_registry.git_blob_sha1(sample.read_bytes()) == expected


def test_clean_packet_reads_back(tmp_path: Path) -> None:
    packet = build_packet(tmp_path)
    receipt = readback.build_receipt(packet, REGISTRY)
    assert receipt["deterministic_replay"] == "PASS"
    assert receipt["git_blob_readback"] == "PASS"
    assert receipt["decision"] == "VALIDATE"
    assert receipt["authority_ceiling"] == "SOURCE_EVIDENCE_ONLY"
    assert [item["path"] for item in receipt["files"]] == list(readback.PACKET_FILES)
    for item in receipt["files"]:
        assert len(item["git_blob_sha1"]) == 40


def test_receipt_git_blob_sha_matches_the_git_binary(tmp_path: Path) -> None:
    if shutil.which("git") is None:  # pragma: no cover - git is present in CI
        pytest.skip("git binary unavailable")
    packet = build_packet(tmp_path)
    receipt = readback.build_receipt(packet, REGISTRY)
    for item in receipt["files"]:
        expected = subprocess.run(
            ["git", "hash-object", "--", str(packet / item["path"])],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        assert item["git_blob_sha1"] == expected


def test_reformatted_packet_is_refused(tmp_path: Path) -> None:
    """The control that the semantic digest alone cannot provide.

    Re-serializing the packet leaves every digest in it unchanged while the
    bytes and the Git object name both move. Only a byte comparison sees it.
    """
    packet = build_packet(tmp_path)
    signal_path = packet / "product-signal.json"
    payload = json.loads(signal_path.read_text(encoding="utf-8"))
    signal_path.write_text(json.dumps(payload, indent=4, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(readback.ReadbackError) as excinfo:
        readback.build_receipt(packet, REGISTRY)
    assert "PRODUCT_SIGNAL_BYTE_DRIFT" in str(excinfo.value)


def test_single_byte_change_is_refused(tmp_path: Path) -> None:
    packet = build_packet(tmp_path)
    signal_path = packet / "product-signal.json"
    signal_path.write_text(
        signal_path.read_text(encoding="utf-8") + " ", encoding="utf-8"
    )
    with pytest.raises(readback.ReadbackError):
        readback.build_receipt(packet, REGISTRY)


def test_missing_packet_file_is_refused(tmp_path: Path) -> None:
    packet = build_packet(tmp_path)
    (packet / "product-signal.json").unlink()
    with pytest.raises(readback.ReadbackError):
        readback.build_receipt(packet, REGISTRY)


def test_tampered_claim_promotion_is_refused(tmp_path: Path) -> None:
    """A source statement promoted to TESTED must not reach a receipt."""
    packet = build_packet(tmp_path)
    claims_path = packet / "claims.jsonl"
    rows = [
        json.loads(line)
        for line in claims_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    promoted = False
    for row in rows:
        if row.get("claim_class") == "SOURCE_STATEMENT":
            row["verification"] = "TESTED"
            promoted = True
            break
    assert promoted, "fixture must contain a SOURCE_STATEMENT to promote"
    claims_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    with pytest.raises(readback.ReadbackError) as excinfo:
        readback.build_receipt(packet, REGISTRY)
    assert "OVERPROMOTED" in str(excinfo.value)


def test_receipt_carries_no_raw_source_body(tmp_path: Path) -> None:
    packet = build_packet(tmp_path)
    receipt = readback.build_receipt(packet, REGISTRY)
    assert product_signal.walk_forbidden(receipt) == []
