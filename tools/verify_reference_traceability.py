#!/usr/bin/env python3
"""Deterministically validate the private reference and traceability graph.

This verifier checks repository-local graph shape only. It never upgrades a URL,
issue, PR, or CI result into source truth, rights, runtime, or market evidence.
Cross-repository public-registry parity is an optional input and remains an
independent evidence lane.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlparse

VALID_TRACE_STATES = {
    "BOUND",
    "PARTIAL",
    "UNBOUND",
    "NO_IMPLEMENTATION_REQUIREMENT",
}
SECRET_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "credential",
    "password",
    "secret",
    "signature",
    "token",
}
REF_ID = re.compile(r"^REF-[0-9]{4,}$")
CTX_ID = re.compile(r"^CTX-[0-9]{4,}$")
WORK_SUBJECT = re.compile(r"^[A-Z][A-Z0-9-]*#[0-9]+$")


class TraceabilityValidationError(RuntimeError):
    """Raised when an input file is malformed."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TraceabilityValidationError(f"cannot load JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TraceabilityValidationError(f"expected JSON object: {path}")
    return value


def _status(failures: Iterable[str], evidence: Iterable[str], *, skipped: bool = False) -> dict[str, Any]:
    failure_list = sorted(set(failures))
    if failure_list:
        state = "FAIL"
    elif skipped:
        state = "NOT_EXERCISED"
    else:
        state = "PASS"
    return {
        "status": state,
        "evidence": sorted(set(evidence)),
        "failures": failure_list,
    }


def _records_from(path: Path, key: str) -> list[dict[str, Any]]:
    value = load_json(path).get(key, [])
    if not isinstance(value, list):
        raise TraceabilityValidationError(f"{path}:{key} must be a list")
    records: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise TraceabilityValidationError(f"{path}:{key}[{index}] must be an object")
        records.append(item)
    return records


def authoritative_records(root: Path) -> list[tuple[str, dict[str, Any]]]:
    registry = root / "docs" / "reference-registry"
    sources: list[tuple[Path, str]] = [
        (registry / "reference-index.private.json", "references"),
        (registry / "reference-index.private.methods.json", "references"),
        (registry / "context-reference-backfill.json", "records"),
    ]
    records: list[tuple[str, dict[str, Any]]] = []
    for path, key in sources:
        if not path.exists():
            continue
        for item in _records_from(path, key):
            records.append((str(path.relative_to(root)), item))

    codex_path = registry / "codexdoc-index.json"
    if codex_path.exists():
        codex = load_json(codex_path)
        folder = codex.get("folder")
        if not isinstance(folder, dict):
            raise TraceabilityValidationError(f"{codex_path}:folder must be an object")
        records.append((str(codex_path.relative_to(root)), folder))
        for item in _records_from(codex_path, "items"):
            records.append((str(codex_path.relative_to(root)), item))
    return records


def check_identity(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    evidence: list[str] = []
    by_ref: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    external_ids: dict[str, set[str]] = defaultdict(set)
    urls: dict[str, set[str]] = defaultdict(set)

    for source, record in authoritative_records(root):
        ref = record.get("ref_id") or record.get("id")
        if not isinstance(ref, str):
            failures.append(f"{source}: missing ref/id")
            continue
        if not (REF_ID.match(ref) or CTX_ID.match(ref)):
            failures.append(f"{source}: invalid reference id {ref!r}")
            continue
        by_ref[ref].append((source, record))
        external_id = record.get("external_id")
        if isinstance(external_id, str) and external_id:
            external_ids[external_id].add(ref)
        url = record.get("url")
        if isinstance(url, str) and url:
            urls[url].add(ref)

    for external_id, refs in sorted(external_ids.items()):
        if len(refs) > 1:
            failures.append(f"external_id {external_id} maps to multiple refs: {sorted(refs)}")
    for url, refs in sorted(urls.items()):
        if len(refs) > 1:
            failures.append(f"exact URL maps to multiple refs: {url} -> {sorted(refs)}")

    for ref, occurrences in sorted(by_ref.items()):
        if len(occurrences) < 2:
            continue
        external_values = {
            record.get("external_id")
            for _, record in occurrences
            if isinstance(record.get("external_id"), str) and record.get("external_id")
        }
        url_values = {
            record.get("url")
            for _, record in occurrences
            if isinstance(record.get("url"), str) and record.get("url")
        }
        if len(external_values) > 1 or len(url_values) > 1:
            failures.append(
                f"ref {ref} is reused with conflicting identity: external={sorted(external_values)}, urls={sorted(url_values)}"
            )

    evidence.append(f"authoritative_reference_occurrences={sum(len(v) for v in by_ref.values())}")
    evidence.append(f"unique_reference_ids={len(by_ref)}")
    return _status(failures, evidence)


def check_codexdoc(root: Path) -> dict[str, Any]:
    path = root / "docs" / "reference-registry" / "codexdoc-index.json"
    if not path.exists():
        return _status(["codexdoc-index.json missing"], [])
    codex = load_json(path)
    items = codex.get("items")
    summary = codex.get("summary")
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        return _status(["codexdoc items malformed"], [])
    if not isinstance(summary, dict):
        return _status(["codexdoc summary missing"], [])

    failures: list[str] = []
    evidence: list[str] = []
    counts = Counter(str(item.get("trace_status")) for item in items)
    expected = {
        "item_count": len(items),
        "bound": counts["BOUND"],
        "partial": counts["PARTIAL"],
        "unbound": counts["UNBOUND"],
        "no_implementation_requirement": counts["NO_IMPLEMENTATION_REQUIREMENT"],
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            failures.append(f"codexdoc summary {key}={summary.get(key)!r}, expected {value}")

    for item in items:
        ref = item.get("ref_id")
        state = item.get("trace_status")
        if state not in VALID_TRACE_STATES:
            failures.append(f"{ref}: invalid trace_status {state!r}")
            continue
        issues = item.get("issues")
        if issues is not None and (
            not isinstance(issues, list)
            or any(not isinstance(issue, str) or not WORK_SUBJECT.match(issue) for issue in issues)
        ):
            failures.append(f"{ref}: malformed issue identities")
        if state == "BOUND":
            has_issue = isinstance(issues, list) and bool(issues)
            has_work_evidence = bool(item.get("prs") or item.get("evidence_urls"))
            if item.get("role") == "SOURCE_PROPOSAL" and (not has_issue or not has_work_evidence):
                failures.append(f"{ref}: BOUND source proposal lacks issue plus PR/evidence edge")
            if item.get("role") == "CONTEXT_PROJECTION" and not has_issue:
                failures.append(f"{ref}: BOUND context projection lacks owning issue")
        elif state == "PARTIAL":
            if not (item.get("consumer_repositories") or item.get("evidence_urls") or issues):
                failures.append(f"{ref}: PARTIAL lacks any observed binding")
        elif state == "UNBOUND":
            if not isinstance(issues, list) or not any(issue in {"AI-CONTENT#61", "AI-CONTENT#62"} for issue in issues):
                failures.append(f"{ref}: UNBOUND source lacks audit owner")
        elif state == "NO_IMPLEMENTATION_REQUIREMENT":
            if not item.get("notes"):
                failures.append(f"{ref}: NO_IMPLEMENTATION_REQUIREMENT requires rationale")

    if summary.get("global_verdict") == "TRACE_CLOSED" and (counts["PARTIAL"] or counts["UNBOUND"]):
        failures.append("global TRACE_CLOSED is illegal while PARTIAL/UNBOUND entries remain")

    evidence.extend(f"{state}={counts[state]}" for state in sorted(VALID_TRACE_STATES))
    return _status(failures, evidence)


def check_repo_namespaces(root: Path) -> dict[str, Any]:
    index_path = root / "docs" / "reference-registry" / "repo-directory-index.json"
    if not index_path.exists():
        return _status(["repo-directory-index.json missing"], [])
    index = load_json(index_path)
    repositories = index.get("repositories")
    if not isinstance(repositories, list):
        return _status(["repo-directory-index repositories must be a list"], [])

    failures: list[str] = []
    evidence: list[str] = []
    names: set[str] = set()
    paths: set[str] = set()
    for row in repositories:
        if not isinstance(row, dict):
            failures.append("repo-directory-index contains non-object row")
            continue
        name = row.get("repo_name")
        rel = row.get("path")
        if not isinstance(name, str) or not isinstance(rel, str):
            failures.append("repo-directory-index row missing repo_name/path")
            continue
        if name in names:
            failures.append(f"duplicate repo_name in directory index: {name}")
        if rel in paths:
            failures.append(f"duplicate path in directory index: {rel}")
        names.add(name)
        paths.add(rel)
        path = root / rel
        if not path.exists():
            failures.append(f"namespace missing: {rel}")
            continue
        namespace = load_json(path)
        if namespace.get("repo_name") != name:
            failures.append(f"{rel}: repo_name mismatch")
        if namespace.get("repository_ref_id") != row.get("repository_ref_id"):
            failures.append(f"{rel}: repository_ref_id mismatch")
        url = namespace.get("repository_url")
        if not isinstance(url, str) or not url.startswith("https://github.com/"):
            failures.append(f"{rel}: invalid repository_url")

    evidence.append(f"repo_namespaces={len(names)}")
    return _status(failures, evidence)


def check_url_hygiene(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    evidence: list[str] = []
    checked = 0
    for source, record in authoritative_records(root):
        url = record.get("url")
        ref = record.get("ref_id") or record.get("id")
        if url is None:
            state = record.get("state")
            if isinstance(ref, str) and CTX_ID.match(ref) and state == "NO_CANONICAL_URL_MATERIALIZED":
                continue
            failures.append(f"{source}:{ref}: null URL without explicit conversation-artifact state")
            continue
        if not isinstance(url, str):
            failures.append(f"{source}:{ref}: URL must be string or explicit unresolved artifact")
            continue
        checked += 1
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            failures.append(f"{source}:{ref}: non-HTTPS or malformed URL {url}")
        for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
            if key.lower() in SECRET_QUERY_KEYS:
                failures.append(f"{source}:{ref}: secret-shaped query parameter {key}")

    evidence.append(f"urls_checked={checked}")
    return _status(failures, evidence)


def check_context_provenance(root: Path) -> dict[str, Any]:
    path = root / "docs" / "reference-registry" / "context-reference-backfill.json"
    if not path.exists():
        return _status(["context-reference-backfill.json missing"], [])
    records = _records_from(path, "records")
    failures: list[str] = []
    unresolved = 0
    for record in records:
        ref = record.get("ref_id")
        origin = record.get("source_origin")
        if not isinstance(origin, str) or not origin:
            failures.append(f"{ref}: missing source_origin")
        if record.get("url") is None:
            unresolved += 1
            if record.get("state") not in {
                "NO_CANONICAL_URL_MATERIALIZED",
                "ISSUE_IDENTITIES_NAMED_URLS_NOT_REBOUND",
            }:
                failures.append(f"{ref}: unresolved URL lacks explicit state")
            if record.get("trace_status") not in {"UNBOUND", "PARTIAL"}:
                failures.append(f"{ref}: unresolved conversation artifact cannot be closed")
    return _status(failures, [f"context_records={len(records)}", f"unresolved_context_records={unresolved}"])


def _public_ref_ids(paths: list[Path]) -> set[str]:
    refs: set[str] = set()
    for path in paths:
        value = load_json(path).get("references", [])
        if not isinstance(value, list):
            raise TraceabilityValidationError(f"{path}:references must be a list")
        for record in value:
            if isinstance(record, dict) and isinstance(record.get("id"), str):
                refs.add(record["id"])
    return refs


def check_public_parity(root: Path, public_paths: list[Path]) -> dict[str, Any]:
    if not public_paths:
        return _status([], ["public_registry_snapshot=absent"], skipped=True)
    failures: list[str] = []
    public_refs = _public_ref_ids(public_paths)
    repo_index = load_json(root / "docs" / "reference-registry" / "repo-directory-index.json")
    repositories = repo_index.get("repositories", [])
    if not isinstance(repositories, list):
        raise TraceabilityValidationError("repo-directory-index repositories malformed")
    expected_public = {
        row.get("repository_ref_id")
        for row in repositories
        if isinstance(row, dict) and row.get("visibility") == "PUBLIC" and isinstance(row.get("repository_ref_id"), str)
    }
    missing = sorted(expected_public - public_refs)
    if missing:
        failures.append(f"public registry missing public repository refs: {missing}")
    return _status(failures, [f"public_refs={len(public_refs)}", f"expected_public_repo_refs={len(expected_public)}"])


def build_report(root: Path, *, public_registry_paths: list[Path] | None = None) -> dict[str, Any]:
    public_registry_paths = public_registry_paths or []
    checks = {
        "TR-01-reference-identity": check_identity(root),
        "TR-02-codexdoc-denominator-and-edges": check_codexdoc(root),
        "TR-03-repo-namespace-coverage": check_repo_namespaces(root),
        "TR-04-url-hygiene": check_url_hygiene(root),
        "TR-05-conversation-provenance": check_context_provenance(root),
        "TR-06-public-private-parity": check_public_parity(root, public_registry_paths),
    }
    failed = any(check["status"] == "FAIL" for check in checks.values())
    not_exercised = any(check["status"] == "NOT_EXERCISED" for check in checks.values())
    if failed:
        overall = "FAIL"
    elif not_exercised:
        overall = "PASS_WITH_EXTERNAL_PARITY_NOT_EXERCISED"
    else:
        overall = "PASS"
    return {
        "schema": "reference-traceability-report@1",
        "verifier": "reference-traceability-verifier@1",
        "overall_status": overall,
        "checks": checks,
        "evidence_ceiling": (
            "Repository-local trace graph shape only. No source accuracy, rights, live GitHub/Google state, runtime, legal/store, or market closure."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--public-registry", action="append", type=Path, default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = build_report(args.root.resolve(), public_registry_paths=[path.resolve() for path in args.public_registry])
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 1 if report["overall_status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
