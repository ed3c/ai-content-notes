#!/usr/bin/env python3
"""Compile source-bound atomic claims into a deterministic product-signal packet.

This compiler is deliberately conservative. It can establish source-evidence
lineage only. It cannot turn a source statement into observed product internals,
license truth, runtime proof, user validation, paid demand, merge, or release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

CLAIM_CLASSES = {
    "FACT", "SOURCE_STATEMENT", "INFERENCE", "HYPOTHESIS",
    "ASSUMPTION", "CONTRADICTION", "UNKNOWN",
}
HIGH_RISK = {
    "INTERNAL_ARCHITECTURE", "LICENSE", "PERFORMANCE", "COST",
    "PRODUCT_VALUE", "MARKET_DEMAND",
}
STRONG_EVIDENCE = {
    "EXTERNAL_PRIMARY", "RUNTIME_ARTIFACT", "LEGAL_REVIEW",
    "USER_EVIDENCE", "COMMERCIAL_EVIDENCE",
}
FORBIDDEN_PUBLIC_KEYS = {
    "credential", "credentials", "secret", "secrets", "raw_session",
    "private_note_body", "raw_source_body", "customer_data",
}

class Refused(RuntimeError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def digest(value: Any, drop: str | None = None) -> str:
    clone = json.loads(json.dumps(value, ensure_ascii=False))
    if drop and isinstance(clone, dict):
        clone.pop(drop, None)
    raw = json.dumps(clone, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Refused(f"unreadable JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Refused(f"{path}: root must be an object")
    return value


def load_claims(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise Refused(f"unreadable claims {path}: {exc}") from exc
    for index, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise Refused(f"claims line {index}: {exc}") from exc
        if not isinstance(row, dict):
            raise Refused(f"claims line {index}: object required")
        rows.append(row)
    if not rows:
        raise Refused("claims ledger is empty")
    return rows


def walk_forbidden(value: Any, path: str = "$") -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_PUBLIC_KEYS:
                out.append(f"PRIVACY_FIELD:{path}.{key}")
            out.extend(walk_forbidden(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            out.extend(walk_forbidden(child, f"{path}[{i}]"))
    return out


def validate_source_registry(registry: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    if registry.get("schema_version") != "source-registry@1":
        failures.append("SOURCE_REGISTRY_SCHEMA")
    if registry.get("evidence_mode") != "LIVE":
        failures.append("SOURCE_REGISTRY_NOT_LIVE")
    entries = registry.get("entries") or []
    if len(entries) != 1 or not isinstance(entries[0], dict):
        failures.append("SOURCE_ENTRY_CARDINALITY")
        return {}, failures
    entry = entries[0]
    if entry.get("state") != "ADMITTED":
        failures.append("SOURCE_NOT_ADMITTED")
    if entry.get("authority_ceiling") != "SOURCE_INPUT_ONLY":
        failures.append("SOURCE_AUTHORITY_WIDENED")
    if entry.get("readback", {}).get("status") != "PASS":
        failures.append("SOURCE_READBACK_NOT_PASS")
    if entry.get("rights", {}).get("decision") != "PASS":
        failures.append("SOURCE_RIGHTS_NOT_PASS")
    if entry.get("completeness", {}).get("status") != "COMPLETE":
        failures.append("SOURCE_INCOMPLETE")
    return entry, failures


def validate_inputs(claims: list[dict[str, Any]], evidence: dict[str, Any], contradictions: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    failures = walk_forbidden(claims) + walk_forbidden(evidence) + walk_forbidden(contradictions)
    source, source_failures = validate_source_registry(registry)
    failures.extend(source_failures)
    if not source:
        return failures

    source_id = source.get("source_id")
    source_digest = source.get("content", {}).get("digest")
    dep_key = source.get("source_dependency_key")
    evidence_rows = evidence.get("entries") or []
    evidence_by_id = {row.get("evidence_id"): row for row in evidence_rows if isinstance(row, dict)}
    if len(evidence_by_id) != len(evidence_rows):
        failures.append("DUPLICATE_EVIDENCE_ID")

    claim_by_id: dict[str, dict[str, Any]] = {}
    for row in claims:
        claim_id = row.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            failures.append("CLAIM_ID_MISSING")
            continue
        if claim_id in claim_by_id:
            failures.append(f"DUPLICATE_CLAIM_ID:{claim_id}")
        claim_by_id[claim_id] = row
        if row.get("claim_class") not in CLAIM_CLASSES:
            failures.append(f"CLAIM_CLASS:{claim_id}")
        if row.get("source_id") != source_id:
            failures.append(f"SOURCE_ID_DRIFT:{claim_id}")
        refs = row.get("evidence_refs") or []
        if not refs:
            failures.append(f"UNANCHORED_CLAIM:{claim_id}")
        ref_kinds: set[str] = set()
        for ref in refs:
            ev = evidence_by_id.get(ref)
            if not ev:
                failures.append(f"UNKNOWN_EVIDENCE:{claim_id}:{ref}")
                continue
            ref_kinds.add(str(ev.get("kind")))
            if ev.get("source_id") == source_id:
                if ev.get("source_digest") != source_digest:
                    failures.append(f"SOURCE_DIGEST_DRIFT:{ref}")
                if ev.get("dependency_key") != dep_key:
                    failures.append(f"DEPENDENCY_KEY_DRIFT:{ref}")
        locator = row.get("locator") or {}
        if locator.get("kind") not in {"PAGE", "VISUAL_REGION", "TEXT_MATCH", "SECTION"}:
            failures.append(f"LOCATOR_MISSING:{claim_id}")
        page = locator.get("page")
        if page is not None and (not isinstance(page, int) or page < 1 or page > 34):
            failures.append(f"LOCATOR_PAGE_RANGE:{claim_id}")
        risk = set(row.get("risk_tags") or [])
        if row.get("claim_class") == "FACT" and risk.intersection(HIGH_RISK) and not ref_kinds.intersection(STRONG_EVIDENCE):
            failures.append(f"HIGH_RISK_FACT_WITHOUT_STRONG_EVIDENCE:{claim_id}")
        if row.get("claim_class") == "SOURCE_STATEMENT" and row.get("verification") in {"TESTED", "CORROBORATED"}:
            failures.append(f"SOURCE_STATEMENT_OVERPROMOTED:{claim_id}")
        if row.get("claim_class") in {"HYPOTHESIS", "ASSUMPTION", "UNKNOWN"} and row.get("verification") in {"TESTED", "CORROBORATED"}:
            failures.append(f"SPECULATIVE_CLAIM_OVERPROMOTED:{claim_id}")

    contradiction_rows = contradictions.get("entries") or []
    unresolved = 0
    for row in contradiction_rows:
        ids = row.get("claim_ids") or []
        if len(ids) < 2 or any(item not in claim_by_id for item in ids):
            failures.append(f"CONTRADICTION_BAD_CLAIMS:{row.get('contradiction_id')}")
        if row.get("status") == "UNRESOLVED":
            unresolved += 1
            if not row.get("required_evidence"):
                failures.append(f"CONTRADICTION_NO_REQUIRED_EVIDENCE:{row.get('contradiction_id')}")
    if unresolved == 0:
        failures.append("CONTRADICTION_DENOMINATOR_EMPTY")
    return sorted(set(failures))


def compile_signal(claims: list[dict[str, Any]], evidence: dict[str, Any], contradictions: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    source = registry["entries"][0]
    groups: dict[str, dict[str, Any]] = {}
    for row in sorted(claims, key=lambda r: r["claim_id"]):
        for sig in row.get("signal_refs") or []:
            item = groups.setdefault(sig["signal_id"], {
                "signal_id": sig["signal_id"],
                "signal_class": sig["signal_class"],
                "title": sig["title"],
                "claim_ids": [],
                "open_gaps": [],
                "authority_ceiling": "SOURCE_EVIDENCE_ONLY",
            })
            item["claim_ids"].append(row["claim_id"])
            item["open_gaps"].extend(row.get("required_evidence") or [])
    signals = []
    for key in sorted(groups):
        item = groups[key]
        item["claim_ids"] = sorted(set(item["claim_ids"]))
        item["open_gaps"] = sorted(set(item["open_gaps"]))
        signals.append(item)

    result: dict[str, Any] = {
        "schema_version": "product-signal@1",
        "signal_set_id": "modern-web-architecture-2026-08-18",
        "source_binding": {
            "source_id": source["source_id"],
            "source_digest": source["content"]["digest"],
            "registry_digest": registry["registry_digest"],
            "dependency_key": source["source_dependency_key"],
        },
        "claims_digest": "sha256:" + hashlib.sha256("".join(canonical(r) for r in sorted(claims, key=lambda r: r["claim_id"])).encode()).hexdigest(),
        "evidence_digest": digest(evidence),
        "contradictions_digest": digest(contradictions),
        "signals": signals,
        "unresolved_contradictions": sorted(row["contradiction_id"] for row in contradictions["entries"] if row.get("status") == "UNRESOLVED"),
        "unknown_claims": sorted(row["claim_id"] for row in claims if row.get("claim_class") == "UNKNOWN"),
        "evidence_state": {
            "source": "PASS",
            "runtime": "ABSENT",
            "user": "ABSENT",
            "paid": "ABSENT",
            "legal": "ABSENT",
        },
        "decision": "VALIDATE",
        "authority_ceiling": "SOURCE_EVIDENCE_ONLY",
        "non_claims": [
            "No named product internal architecture is established as observed fact.",
            "No package license, performance, cost, runtime, user, paid, merge, or release state is established.",
        ],
        "product_signal_digest": "sha256:" + "0" * 64,
    }
    result["product_signal_digest"] = digest(result, drop="product_signal_digest")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claims", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--contradictions", type=Path, required=True)
    parser.add_argument("--source-registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        claims = load_claims(args.claims)
        evidence = load_json(args.evidence)
        contradictions = load_json(args.contradictions)
        registry = load_json(args.source_registry)
        failures = validate_inputs(claims, evidence, contradictions, registry)
        if failures:
            print(json.dumps({"status": "FAIL", "failures": failures}, indent=2), file=sys.stderr)
            return 2
        result = compile_signal(claims, evidence, contradictions, registry)
        text = canonical(result)
        if args.check:
            if not args.output.is_file() or args.output.read_text(encoding="utf-8") != text:
                print("PRODUCT_SIGNAL_DRIFT", file=sys.stderr)
                return 2
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
        print(json.dumps({"status": "PASS", "digest": result["product_signal_digest"], "signals": len(result["signals"])}, indent=2))
        return 0
    except Refused as exc:
        print(str(exc), file=sys.stderr)
        return 64

if __name__ == "__main__":
    raise SystemExit(main())
