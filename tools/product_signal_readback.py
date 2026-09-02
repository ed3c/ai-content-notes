#!/usr/bin/env python3
"""Read a persisted product-signal packet back from its exact Git blob identity.

`tools/product_signal.py --check` proves that the persisted `product-signal.json`
matches what the compiler emits for its inputs, but only for that one file, and
it records no Git object identity for what was persisted -- a byte comparison is
not the same as naming the object those bytes are. Its three sibling packet
files (`claims.jsonl`, `contradictions.json`, `evidence-ledger.json`) get no
byte check from either tool. Both gaps are what #50 asks for and #54 must hand
to Stage 4, so they live here.

Two independent controls have to hold:

1. deterministic replay - recompiling the inputs must reproduce the committed
   `product-signal.json` byte for byte, not merely re-derive the same digest;
2. Git blob read-back - each persisted packet file is named by its Git object
   name, recomputed from the bytes on disk.

Those are independent: a hand-reformatted artifact keeps its semantic digest
while both its bytes and its Git object name change, so control 1 catches what
a digest comparison alone would wave through.

The receipt carries digests and identities only. No raw source body, private
note body, credential, session or customer field is copied into it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import product_signal
from source_registry import git_blob_sha1

# The packet inputs and outputs this receipt binds, in stable order.
PACKET_FILES = (
    "claims.jsonl",
    "contradictions.json",
    "evidence-ledger.json",
    "product-signal.json",
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class ReadbackError(RuntimeError):
    """Raised when a persisted packet cannot be read back."""


def repo_relative(path: Path) -> str:
    """Render a path so the receipt never depends on where the checkout lives.

    An absolute path would change the receipt bytes per machine, which is
    exactly the nondeterminism this lane refuses. Packets outside the
    repository (staging or test scratch) degrade to their own name rather than
    leaking a scratch directory into a persisted artifact.
    """
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.name


def file_identity(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ReadbackError(f"missing packet file: {path}")
    payload = path.read_bytes()
    return {
        "path": path.name,
        "size_bytes": len(payload),
        "sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
        "git_blob_sha1": git_blob_sha1(payload),
    }


def build_receipt(packet_dir: Path, registry_path: Path) -> dict[str, Any]:
    claims_path = packet_dir / "claims.jsonl"
    evidence_path = packet_dir / "evidence-ledger.json"
    contradictions_path = packet_dir / "contradictions.json"
    signal_path = packet_dir / "product-signal.json"

    try:
        claims = product_signal.load_claims(claims_path)
        evidence = product_signal.load_json(evidence_path)
        contradictions = product_signal.load_json(contradictions_path)
        registry = product_signal.load_json(registry_path)
    except product_signal.Refused as exc:
        raise ReadbackError(str(exc)) from exc

    failures = product_signal.validate_inputs(claims, evidence, contradictions, registry)
    if failures:
        raise ReadbackError("; ".join(failures))

    compiled = product_signal.compile_signal(claims, evidence, contradictions, registry)
    expected_text = product_signal.canonical(compiled)

    if not signal_path.is_file():
        raise ReadbackError(f"missing packet file: {signal_path}")
    persisted_text = signal_path.read_text(encoding="utf-8")
    if persisted_text != expected_text:
        raise ReadbackError(
            "PRODUCT_SIGNAL_BYTE_DRIFT: the persisted packet is not the bytes the "
            "compiler emits for these inputs"
        )

    # Refuse to certify a packet whose ceiling has been widened out from under us.
    if compiled["decision"] != "VALIDATE":
        raise ReadbackError("DECISION_CEILING_WIDENED")
    if compiled["authority_ceiling"] != "SOURCE_EVIDENCE_ONLY":
        raise ReadbackError("AUTHORITY_CEILING_WIDENED")

    source = registry["entries"][0]
    files = [file_identity(packet_dir / name) for name in PACKET_FILES]
    privacy = product_signal.walk_forbidden(files)
    if privacy:
        raise ReadbackError("; ".join(privacy))

    return {
        "schema_version": "product-signal-readback-receipt@1",
        "signal_set_id": compiled["signal_set_id"],
        "packet_dir": repo_relative(packet_dir),
        "source_binding": compiled["source_binding"],
        "source_registry_readback": {
            "path": repo_relative(registry_path),
            "registry_digest": registry["registry_digest"],
            "source_digest": source["content"]["digest"],
            "source_readback_status": source["readback"]["status"],
            "source_authority_ceiling": source["authority_ceiling"],
        },
        "deterministic_replay": "PASS",
        "git_blob_readback": "PASS",
        "files": files,
        "product_signal_digest": compiled["product_signal_digest"],
        "claims_digest": compiled["claims_digest"],
        "evidence_digest": compiled["evidence_digest"],
        "contradictions_digest": compiled["contradictions_digest"],
        "unresolved_contradictions": compiled["unresolved_contradictions"],
        "unknown_claims": compiled["unknown_claims"],
        "evidence_state": compiled["evidence_state"],
        "decision": compiled["decision"],
        "authority_ceiling": compiled["authority_ceiling"],
        "non_claims": [
            "The receipt proves exact persisted bytes and Git object identity, not source factual accuracy.",
            "Named product internals, licenses, performance and cost remain source statements or hypotheses.",
            "Read-back does not establish runtime, user, paid, legal, BUILD, merge or release state.",
        ],
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-dir", type=Path, required=True)
    parser.add_argument(
        "--source-registry",
        type=Path,
        default=root
        / "evals"
        / "source-intake"
        / "modern-web-architecture"
        / "source-registry.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        receipt = build_receipt(args.packet_dir, args.source_registry)
    except ReadbackError as error:
        print(f"product-signal read-back refused: {error}", file=sys.stderr)
        return 2

    text = product_signal.canonical(receipt)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != text:
            print("READBACK_RECEIPT_DRIFT", file=sys.stderr)
            return 2
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "PASS",
                "product_signal_digest": receipt["product_signal_digest"],
                "files": len(receipt["files"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
