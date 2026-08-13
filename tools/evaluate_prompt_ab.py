#!/usr/bin/env python3
"""Deterministically score saved v7.0/v7.1 card-compiler outputs.

This replay evaluator never invokes a model. Live runners may create new saved
outputs later and reuse the same contract checks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

HEADING = re.compile(r"^###\s+(?P<id>[A-Z][A-Za-z0-9._:-]*)｜.+$", re.MULTILINE)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
TIMESTAMP = re.compile(r"\b\d{2}:\d{2}:\d{2}\b")
ADMIN = re.compile(
    r"^- \*\*(?:Stable ID|Canonical Key|Series|Lifecycle|Revision|Claim Kind|"
    r"Verification|Confidence|Confidence Basis|Scope|Source Provenance)\*\*[：:]",
    re.MULTILINE,
)
TYPED_LINK = re.compile(
    r"(?:ROOT\s*←|FLOW\s*→|CONFLICT\s*↔|ANALOGY\s*≈|INSTANCE_OF\s*→|"
    r"IMPLEMENTS\s*→|VALIDATED_BY\s*→|SUPERSEDES\s*→|DEPENDS_ON\s*→|MITIGATES\s*→)"
)
GENERIC_LINKS = ("[[D系列]]", "[[相關證據]]", "[[All Series]]")
HUMAN_ENTRY = {"N", "C", "T", "P"}


class EvaluationError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvaluationError(f"expected JSON object: {path}")
    return value


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def visible(text: str) -> str:
    return COMMENT.sub("", text)


def cards(text: str) -> list[tuple[str, str]]:
    matches = list(HEADING.finditer(text))
    if not matches:
        raise EvaluationError("candidate contains no parseable card headings")
    result: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result.append((match.group("id"), visible(text[match.start():end])))
    return result


def values(text: str, field: str) -> list[str]:
    pattern = re.compile(rf"^- \*\*{re.escape(field)}\*\*[：:]\s*(.+)$", re.MULTILINE)
    return [match.group(1).strip() for match in pattern.finditer(visible(text))]


def corroborated_status(text: str) -> bool:
    if "CORROBORATED" in values(text, "Verification"):
        return True
    compact = re.compile(
        r"^- \*\*證據與狀態\*\*[：:]\s*[^\n]*?·\s*CORROBORATED\s*·",
        re.MULTILINE,
    )
    return compact.search(visible(text)) is not None


def metadata_ratio(text: str) -> float:
    lines = [line.strip() for line in visible(text).splitlines() if line.strip()]
    body = [line for line in lines if not line.startswith("###")]
    return 1.0 if not body else sum(bool(ADMIN.match(line)) for line in body) / len(body)


def payload_first(first_card: str) -> bool:
    lines = [line.strip() for line in first_card.splitlines() if line.strip()]
    window = [line for line in lines if not line.startswith("###")][:6]
    core = next((i for i, line in enumerate(window) if "**核心命題**" in line), None)
    why = next((i for i, line in enumerate(window) if "**為什麼重要**" in line), None)
    admin = next((i for i, line in enumerate(window) if ADMIN.match(line)), None)
    return core is not None and why is not None and (admin is None or max(core, why) < admin)


def test_honesty(parsed: list[tuple[str, str]], tool_execution: str) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for card_id, body in parsed:
        if tool_execution == "DISALLOW":
            if "TESTED" in values(body, "Execution Status"):
                failures.append(f"{card_id}: TESTED execution while tools are disabled")
            if "TESTED" in values(body, "Verification"):
                failures.append(f"{card_id}: TESTED verification while tools are disabled")
        if "PASS" in values(body, "Verdict"):
            artifacts = values(body, "Artifacts")
            if not any(item not in {"NONE", "N/A", "N/A：未提供", ""} for item in artifacts):
                failures.append(f"{card_id}: PASS has no concrete artifact")
    return not failures, failures


def typed_links(parsed: list[tuple[str, str]]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for card_id, body in parsed:
        if any(link in body for link in GENERIC_LINKS):
            failures.append(f"{card_id}: generic series link")
        if not TYPED_LINK.search(body):
            failures.append(f"{card_id}: no typed relationship")
    return not failures, failures


def human_rubric(run: dict[str, Any]) -> dict[str, Any]:
    rubric = run.get("human_rubric")
    if not isinstance(rubric, dict):
        return {}
    dimensions = rubric.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise EvaluationError("human_rubric.dimensions must be a non-empty list")
    result: dict[str, Any] = {}
    for arm in ("a", "b"):
        source = rubric.get(arm)
        if not isinstance(source, dict):
            raise EvaluationError(f"human_rubric.{arm} must be an object")
        scores = [float(source[name]) for name in dimensions]
        if any(score < 1 or score > 5 for score in scores):
            raise EvaluationError("human rubric scores must be between 1 and 5")
        result[arm] = {
            "arithmetic_mean": round(sum(scores) / len(scores), 3),
            "five_factor_multiplicative_quality": round(
                math.prod(score / 5 for score in scores[:5]), 6
            ),
            "scores": source,
        }
    result["delta_b_minus_a"] = round(
        result["b"]["arithmetic_mean"] - result["a"]["arithmetic_mean"], 3
    )
    return result


def evaluate_candidate(name: str, text: str, fixture: dict[str, Any]) -> dict[str, Any]:
    parsed = cards(text)
    required = fixture.get("required_shadow_evidence", [])
    allowed = set(fixture.get("allowed_timestamps", []))
    dependencies = fixture.get("source_dependency_keys", [])
    ratio_limit = float(fixture.get("expectations", {}).get("visible_metadata_ratio_max", 0.25))

    missing = [item for item in required if item not in text]
    observed_times = sorted(set(TIMESTAMP.findall(text)))
    fabricated_times = sorted(set(observed_times) - allowed)
    honest, honesty_failures = test_honesty(
        parsed, str(fixture.get("runtime", {}).get("tool_execution", "DISALLOW"))
    )
    links_ok, link_failures = typed_links(parsed)
    asserted_corroboration = corroborated_status(text)
    independence_ok = not (len(set(dependencies)) < 2 and asserted_corroboration)

    order = [card_id for card_id, _ in parsed]
    counts = Counter(card_id.split("-", 1)[0] for card_id in order)
    first_series = order[0].split("-", 1)[0]
    entry = first_series in HUMAN_ENTRY
    balanced = entry and counts["P"] > 0 and counts["D"] > 0 and (
        counts["V"] > 0 or counts["K"] > 0
    )
    ratio = metadata_ratio(text)
    checks = {
        "shadow_evidence_recall": {
            "pass": not missing,
            "recall": round((len(required) - len(missing)) / max(len(required), 1), 3),
            "missing": missing,
        },
        "locator_integrity": {
            "pass": not fabricated_times,
            "observed_timestamps": observed_times,
            "fabricated_timestamps": fabricated_times,
        },
        "test_honesty": {"pass": honest, "failures": honesty_failures},
        "source_independence": {
            "pass": independence_ok,
            "dependency_key_count": len(set(dependencies)),
            "corroborated_present": asserted_corroboration,
        },
        "dependency_provenance": {
            "pass": all(item in text for item in dependencies),
            "missing_dependency_keys": [item for item in dependencies if item not in text],
        },
        "typed_links": {"pass": links_ok, "failures": link_failures},
        "human_entry_first": {"pass": entry, "first_series": first_series},
        "payload_first": {"pass": payload_first(parsed[0][1])},
        "reader_efficiency": {
            "pass": ratio <= ratio_limit,
            "visible_admin_metadata_ratio": round(ratio, 3),
            "maximum": ratio_limit,
        },
        "batch_balance": {
            "pass": balanced,
            "has_human_entry": entry,
            "has_action": counts["P"] > 0,
            "has_verification_or_gap": counts["V"] > 0 or counts["K"] > 0,
            "has_detail": counts["D"] > 0,
        },
    }
    score = 20 * checks["shadow_evidence_recall"]["recall"]
    for key in (
        "locator_integrity", "test_honesty", "source_independence",
        "dependency_provenance", "typed_links", "human_entry_first", "payload_first",
    ):
        score += 10 if checks[key]["pass"] else 0
    score += 5 if checks["reader_efficiency"]["pass"] else 0
    score += 5 if checks["batch_balance"]["pass"] else 0
    return {
        "arm": name,
        "sha256": sha256(text),
        "card_count": len(parsed),
        "series_counts": dict(sorted(counts.items())),
        "card_order": order,
        "card_meta_sidecar_count": text.count("<!-- CARD_META"),
        "run_state_present": "<!-- RUN_STATE" in text,
        "checks": checks,
        "deterministic_score_0_to_100": round(score, 3),
    }


def build_result(fixture_path: Path, a_path: Path, b_path: Path, run_path: Path) -> dict[str, Any]:
    fixture, run = read_json(fixture_path), read_json(run_path)
    a_text, b_text = a_path.read_text(encoding="utf-8"), b_path.read_text(encoding="utf-8")
    arm_a = evaluate_candidate("A:v7.0", a_text, fixture)
    arm_b = evaluate_candidate("B:v7.1", b_text, fixture)
    return {
        "schema_version": "prompt-ab-result@1",
        "experiment_id": run.get("experiment_id"),
        "fixture_id": fixture.get("fixture_id"),
        "artifact_digests": {
            "fixture_sha256": sha256(fixture_path.read_text(encoding="utf-8")),
            "run_sha256": sha256(run_path.read_text(encoding="utf-8")),
        },
        "a": arm_a,
        "b": arm_b,
        "delta_b_minus_a": round(
            arm_b["deterministic_score_0_to_100"] - arm_a["deterministic_score_0_to_100"], 3
        ),
        "human_rubric": human_rubric(run),
        "limitations": run.get("limitations", []),
        "verdict": (
            "B_OUTPERFORMS_ON_THIS_SMOKE_FIXTURE"
            if arm_b["deterministic_score_0_to_100"] > arm_a["deterministic_score_0_to_100"]
            else "NO_DETERMINISTIC_ADVANTAGE_ON_THIS_FIXTURE"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--output-a", required=True, type=Path)
    parser.add_argument("--output-b", required=True, type=Path)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build_result(args.fixture, args.output_a, args.output_b, args.run)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.exists() or read_json(args.output) != result:
            raise EvaluationError("persisted A/B result is missing or stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
