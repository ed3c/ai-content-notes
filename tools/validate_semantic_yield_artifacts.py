#!/usr/bin/env python3
"""Validate persisted semantic-yield cards with deterministic host checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Sequence

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_VERSION = "semantic-validator-report@1"
VALIDATOR_VERSION = "semantic-yield-validator@1"

CARD_HEADING = re.compile(
    r"^###\s+(?P<stable_id>[A-Z][A-Za-z0-9._:-]*)｜(?P<title>.+)$",
    re.MULTILINE,
)
CARD_META = re.compile(r"<!-- CARD_META\s*(?P<meta>\{.*?\})\s*-->", re.DOTALL)
RUN_STATE = re.compile(r"<!-- RUN_STATE\s*(?P<state>\{.*?\})\s*-->", re.DOTALL)
SEQUENCE_ONLY_ID = re.compile(r"^[A-Z]-?\d+(?:\.\d+)?$")
TYPED_LINK_TARGET = re.compile(r"\[\[([A-Z][A-Za-z0-9._:-]*)\]\]")
NUMBER_OVERREACH = (
    re.compile(r"\$\s*\d"),
    re.compile(r"\+\s*\d+(?:\.\d+)?\s*(?:pts?|points?)", re.IGNORECASE),
    re.compile(r"(?:>|至少|超過)\s*10,?000"),
)
REQUIRED_VIEW_MARKERS = (
    "## 1. Autonomy → Trace Mining",
    "fit(Model, Harness, Task / Distribution)",
    "## 3. Intervention Sequence",
    "Data Plane",
    "## 5. Trace Judge Comparison",
)
GENERIC_LINKS = ("[[D系列]]", "[[相關證據]]", "[[All Series]]")

SERIES_REQUIRED_MARKERS = {
    "N": (
        "**核心衝突**",
        "**角色矩陣**",
        "**Impact Anchors**",
        "**完整劇情鏈**",
        "**生態背景**",
        "**未解段落**",
    ),
    "C": (
        "**定義**",
        "**Non-Goals**",
        "**演化**",
        "**底層機制**",
        "**Invariants**",
        "**Boundary Conditions**",
        "**正例**",
        "**反例**",
    ),
    "S": (
        "**Objective**",
        "**Preconditions**",
        "**策略邏輯**",
        "**Ecological Context**",
        "**Trade-offs**",
        "**Pre-mortem Glitches**",
        "**Success Criteria**",
        "**Implementation Path**",
    ),
    "P": (
        "**Scenario**",
        "**Value**",
        "**Prerequisites**",
        "**Inputs**",
        "**Exploit / Procedure**",
        "**Expected Output**",
        "**Rollback**",
        "**Failure Handling**",
        "**Security / Privacy Constraints**",
        "**Toolset**",
        "**Execution Status**",
    ),
    "T": (
        "**Decision Use**",
        "**Comparison Contract**",
        "**Dimensions**",
        "**Interpretation**",
        "**Decision Threshold**",
    ),
    "D": (
        "**Entity**",
        "**Behavior / Case**",
        "**操作手法**",
        "**獨特特徵**",
        "**Shadow Evidence**",
        "**Outcome**",
        "**Comparison Target**",
    ),
    "V": (
        "**Target Assertion**",
        "**Verification Method**",
        "**Oracle**",
        "**Environment / Fixture**",
        "**Procedure**",
        "**Expected Result**",
        "**Observed Result**",
        "**Verdict**",
        "**Artifacts**",
        "**Limitations**",
    ),
    "K": (
        "**Unknown**",
        "**Why Unresolved**",
        "**Impact**",
        "**Evidence Needed**",
        "**Retrieval / Test Plan**",
        "**Unblock Criteria**",
        "**Priority**",
    ),
}

CLAIM_STATUS = re.compile(r"-\s*\*\*證據與狀態\*\*[：:]\s*(.+)")
FALSIFIER_LINE = re.compile(r"-\s*\*\*反證／限制\*\*[：:]\s*(.+)")
ARTIFACTS_LINE = re.compile(r"-\s*\*\*Artifacts\*\*[：:]\s*(.+)")
EVIDENCE_REF = re.compile(r"\[\[EV-[A-Za-z0-9._:-]+\]\]")

# P, V and K state their boundary through series-specific fields that the
# series payload contract already requires, so QG-09 does not ask them for a
# second 反證／限制 line.
SERIES_OWNED_LIMIT_FIELDS = {"P", "V", "K"}
ASSERTING_CLAIM_KINDS = {"SOURCE_STATEMENT", "OBSERVATION"}

AUTOMATED_QG_IDS = (
    "QG-01",
    "QG-02",
    "QG-03",
    "QG-07",
    "QG-08",
    "QG-09",
    "QG-10",
    "QG-11",
    "QG-12",
    "QG-13",
    "QG-15",
    "QG-16",
    "QG-17",
    "QG-18",
    "QG-20",
    "QG-21",
    "QG-23",
)
# Semantic judgement, not a missing artifact - a fixed property of these five
# gates' taxonomy, not of any one subject's run, so it is a module constant
# rather than a per-report field. It still keeps a gate a person owns
# distinguishable from qg_not_run's "nobody has looked at this yet": the
# distinction is asserted once against this constant in
# tests/test_semantic_yield_validator.py, not re-declared in every report.
HUMAN_ADMITTED_QG_IDS = ("QG-04", "QG-05", "QG-06", "QG-14", "QG-19")
ALL_QG_IDS = tuple(f"QG-{index:02d}" for index in range(1, 25))

EVIDENCE_LEDGER_VERSION = "semantic-evidence-ledger@1"
ENTRY_CONTRACT = "schemas/card-registry.schema.json#/$defs/evidenceEntry"
TRANSCRIPT_ANCHOR = "TRANSCRIPT_TIMESTAMP"
ARTIFACT_ANCHOR = "ARTIFACT_STATE"
LOCATOR_TIMESTAMP = re.compile(r"^timestamp:(\d{2}:\d{2}:\d{2})\.\.(\d{2}:\d{2}:\d{2})$")
LOCATOR_POINTER = re.compile(r"^json-pointer:(/\S*)$")
# A card writes the span next to the anchor it cites. The ledger locator and the
# card gloss must agree, or the reader is told a timestamp the ledger does not
# stand behind.
CARD_ANCHOR_SPAN = re.compile(
    r"\[\[(?P<evidence_id>EV-[A-Za-z0-9._:-]+)\]\][^\n]*?"
    r"`(?P<start>\d{2}:\d{2}:\d{2})[–-](?P<end>\d{2}:\d{2}:\d{2})`"
)
MAPPED_DISPOSITIONS = {"CARD_MAPPED", "PROJECTION_MAPPED"}
COVERAGE_DISPOSITIONS = MAPPED_DISPOSITIONS | {"DEFERRED", "IGNORED"}
# Source text that tries to address the compiler rather than describe the world.
# Every hit has to be declared in the retained manifest, and no card may repeat
# it as an instruction.
INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|above)\s+instruction", re.IGNORECASE),
    re.compile(r"disregard\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|above)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"</?(?:system|instruction)s?>", re.IGNORECASE),
    re.compile(r"\bnew\s+instructions?\s*:", re.IGNORECASE),
)


class ValidationError(RuntimeError):
    """Raised when a persisted report is stale or inputs are malformed."""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"expected JSON object: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode()
    return hashlib.sha1(header + payload).hexdigest()  # noqa: S324


def parse_json_comment(pattern: re.Pattern[str], text: str, path: Path) -> dict[str, Any]:
    match = pattern.search(text)
    if not match:
        raise ValidationError(f"missing JSON sidecar comment: {path}")
    value = json.loads(match.groupdict()[next(iter(match.groupdict()))])
    if not isinstance(value, dict):
        raise ValidationError(f"sidecar is not an object: {path}")
    return value


def parse_card(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    heading = CARD_HEADING.search(text)
    if not heading:
        raise ValidationError(f"missing card heading: {path}")
    meta = parse_json_comment(CARD_META, text, path)
    typed_start = text.find("**Typed Links**")
    typed_end = text.find("<!-- CARD_META")
    typed = text[typed_start:typed_end] if typed_start >= 0 and typed_end > typed_start else ""
    return {
        "path": path,
        "text": text,
        "stable_id": heading.group("stable_id"),
        "title": heading.group("title").strip(),
        "meta": meta,
        "typed_targets": sorted(set(TYPED_LINK_TARGET.findall(typed))),
    }


def status(
    passed: bool,
    evidence: list[str],
    failures: list[str],
    *,
    deferred: bool = False,
) -> dict[str, Any]:
    if deferred and passed:
        state = "DEFERRED"
    else:
        state = "PASS" if passed else "FAIL"
    return {"status": state, "evidence": evidence, "failures": failures}


def char_ngrams(text: str, width: int = 3) -> set[str]:
    normalized = re.sub(r"[\W_]+", "", text.lower())
    if len(normalized) < width:
        return {normalized} if normalized else set()
    return {normalized[index : index + width] for index in range(len(normalized) - width + 1)}


def max_core_similarity(cards: list[dict[str, Any]]) -> float:
    cores: list[tuple[str, set[str]]] = []
    for card in cards:
        match = re.search(r"^- \*\*核心命題\*\*[：:]\s*(.+)$", card["text"], re.MULTILINE)
        if match:
            cores.append((card["stable_id"], char_ngrams(match.group(1))))
    maximum = 0.0
    for left_index, (_, left) in enumerate(cores):
        for _, right in cores[left_index + 1 :]:
            union = left | right
            similarity = len(left & right) / len(union) if union else 0.0
            maximum = max(maximum, similarity)
    return round(maximum, 6)


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sha256_of(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class Absent:
    """A pointer that does not resolve, kept distinct from a resolved null."""

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return "ABSENT"


ABSENT = Absent()


def resolve_pointer(document: Any, pointer: str) -> Any:
    """Resolve an RFC 6901 pointer, returning ABSENT rather than raising.

    A missing anchor and an anchor whose value happens to be null are different
    findings, so they must not collapse into the same return.
    """
    node = document
    for token in pointer.lstrip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            if not token.isdigit() or int(token) >= len(node):
                return ABSENT
            node = node[int(token)]
        elif isinstance(node, dict):
            if token not in node:
                return ABSENT
            node = node[token]
        else:
            return ABSENT
    return node


def load_evidence_ledger(target: Path) -> dict[str, Any]:
    """Read the ledger, or fail closed.

    Without it QG-03 cannot separate a missing locator from an artifact anchor,
    which is the whole reason the gate was not automated before.
    """
    path = target / "evidence-ledger.json"
    if not path.is_file():
        raise ValidationError(f"missing evidence ledger: {path}")
    ledger = load_json(path)
    if ledger.get("schema_version") != EVIDENCE_LEDGER_VERSION:
        raise ValidationError(
            f"unexpected evidence ledger schema: {ledger.get('schema_version')!r}"
        )
    return ledger


def entry_schema() -> dict[str, Any]:
    """The ledger reuses the registry's evidenceEntry rather than redefining it.

    Self-located from this file's own path rather than the caller-supplied
    `root`: the schema defines this validator's own contract, not data about
    the subject being validated, so it does not vary with which target a
    caller points `--root` at. `root` can be a synthetic fixture copy that
    carries no `schemas/` directory at all (a real gap this module hit: a
    fixture-builder that predates this schema dependency has no way to learn
    about it), and this file always ships next to the real one.
    """
    registry = load_json(Path(__file__).resolve().parents[1] / "schemas" / "card-registry.schema.json")
    return dict(registry["$defs"]["evidenceEntry"])


def validate_report(value: dict[str, Any], schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).validate(value)


def build_report(
    root: Path,
    target: Path,
    *,
    created_at: str,
    schema_path: Path,
) -> dict[str, Any]:
    manifest_path = target / "card-manifest.json"
    result_path = target / "semantic-yield.result.json"
    run_state_path = target / "run-state.md"
    views_path = target / "knowledge-views.md"

    manifest = load_json(manifest_path)
    result = load_json(result_path)
    run_state = parse_json_comment(
        RUN_STATE,
        run_state_path.read_text(encoding="utf-8"),
        run_state_path,
    )
    views = views_path.read_text(encoding="utf-8")

    card_contracts = manifest.get("cards")
    if not isinstance(card_contracts, list):
        raise ValidationError("manifest.cards must be an array")

    cards: list[dict[str, Any]] = []
    integrity_failures: list[str] = []
    for contract in card_contracts:
        if not isinstance(contract, dict):
            raise ValidationError("every manifest card entry must be an object")
        path = target / str(contract["path"])
        if not path.is_file():
            integrity_failures.append(f"missing card file: {contract['path']}")
            continue
        card = parse_card(path)
        cards.append(card)
        expected_blob = str(contract.get("git_blob_sha1", ""))
        actual_blob = git_blob_sha1(path)
        if expected_blob != actual_blob:
            integrity_failures.append(
                f"{contract['path']}: blob mismatch {actual_blob} != {expected_blob}"
            )
        if card["stable_id"] != contract.get("stable_id"):
            integrity_failures.append(
                f"{contract['path']}: heading ID does not match manifest stable_id"
            )

    prompt_path = root / str(manifest["protocol"]["path"])
    prompt_blob = git_blob_sha1(prompt_path)
    expected_prompt_blob = str(manifest["protocol"]["git_blob_sha1"])
    if prompt_blob != expected_prompt_blob:
        integrity_failures.append(
            f"prompt blob mismatch {prompt_blob} != {expected_prompt_blob}"
        )

    card_ids = [card["stable_id"] for card in cards]
    expected_order = list(manifest.get("card_order", []))
    if card_ids != expected_order:
        integrity_failures.append("card file order does not match manifest.card_order")
    if len(card_ids) != manifest.get("card_count"):
        integrity_failures.append("card count does not match manifest.card_count")
    if len(card_ids) != len(set(card_ids)):
        integrity_failures.append("duplicate stable ID")

    checks: dict[str, Any] = {}
    checks["SV-01-artifact-integrity"] = status(
        not integrity_failures,
        [
            str(manifest_path.relative_to(root)),
            str(prompt_path.relative_to(root)),
            *[str(card["path"].relative_to(root)) for card in cards],
        ],
        integrity_failures,
    )

    identity_failures: list[str] = []
    card_id_set = set(card_ids)
    dependencies: set[str] = set()
    for card in cards:
        meta = card["meta"]
        if meta.get("stable_id") != card["stable_id"]:
            identity_failures.append(
                f"{card['stable_id']}: CARD_META stable_id mismatch"
            )
        if SEQUENCE_ONLY_ID.fullmatch(card["stable_id"]):
            identity_failures.append(
                f"{card['stable_id']}: sequence-only permanent ID"
            )
        if not str(meta.get("canonical_key", "")).strip():
            identity_failures.append(f"{card['stable_id']}: missing canonical_key")
        dependency = str(meta.get("source_dependency_key", "")).strip()
        if not dependency:
            identity_failures.append(
                f"{card['stable_id']}: missing source_dependency_key"
            )
        else:
            dependencies.add(dependency)
        for generic in GENERIC_LINKS:
            if generic in card["text"]:
                identity_failures.append(
                    f"{card['stable_id']}: generic typed link {generic}"
                )
        for target_id in card["typed_targets"]:
            if target_id not in card_id_set:
                identity_failures.append(
                    f"{card['stable_id']}: unresolved typed link {target_id}"
                )
    expected_dependency = str(manifest["source"]["source_dependency_key"])
    if dependencies != {expected_dependency}:
        identity_failures.append(
            f"dependency set mismatch: {sorted(dependencies)}"
        )
    checks["SV-02-identity-and-link-integrity"] = status(
        not identity_failures,
        card_ids,
        identity_failures,
    )

    payload_failures: list[str] = []
    for card in cards:
        text = card["text"]
        core = text.find("- **核心命題**")
        why = text.find("- **為什麼重要**")
        meta = text.find("<!-- CARD_META")
        if core < 0 or why < 0:
            payload_failures.append(
                f"{card['stable_id']}: missing core proposition or why-it-matters"
            )
        elif not (core < why < meta):
            payload_failures.append(
                f"{card['stable_id']}: payload-first ordering violated"
            )
    checks["SV-03-payload-first-contract"] = status(
        not payload_failures,
        card_ids,
        payload_failures,
    )

    joined_cards = "\n".join(card["text"] for card in cards)
    honesty_failures: list[str] = []
    if "CORROBORATED" in joined_cards:
        honesty_failures.append("CORROBORATED appears with one dependency origin")
    practice = next(
        (card for card in cards if card["stable_id"] == "P-trace-driven-improvement-cycle"),
        None,
    )
    verification = next(
        (card for card in cards if card["stable_id"] == "V-semantic-yield-replay"),
        None,
    )
    comparison = next(
        (card for card in cards if card["stable_id"] == "T-trace-judge-comparison"),
        None,
    )
    visual_gap = next(
        (card for card in cards if card["stable_id"] == "K-visual-identifier-evidence-gap"),
        None,
    )
    if practice is None or "**Execution Status**：UNTESTED" not in practice["text"]:
        honesty_failures.append("Practice card is not explicitly UNTESTED")
    if verification is None:
        honesty_failures.append("Verification card is missing")
    else:
        for marker in ("**Observed Result**：PARTIAL", "**Verdict**：PARTIAL"):
            if marker not in verification["text"]:
                honesty_failures.append(f"Verification card missing {marker}")
        if "**Artifacts**：NONE" in verification["text"]:
            honesty_failures.append("PARTIAL verification has no artifact")
    if result.get("status") != "CONTINUE" or run_state.get("status") != "CONTINUE":
        honesty_failures.append("result or run state falsely declares completion")
    epistemic = result.get("epistemic_contract", {})
    if epistemic.get("corroborated_claim_count") != 0:
        honesty_failures.append("corroborated_claim_count must be zero")
    if epistemic.get("practice_execution_status") != "UNTESTED":
        honesty_failures.append("result Practice status must be UNTESTED")
    if epistemic.get("raw_visual_authority") is not False:
        honesty_failures.append("raw visual authority must remain false")
    checks["SV-04-epistemic-honesty"] = status(
        not honesty_failures,
        [
            "P-trace-driven-improvement-cycle",
            "V-semantic-yield-replay",
            "semantic-yield.result.json",
            "run-state.md",
        ],
        honesty_failures,
    )

    view_failures = [
        f"missing view marker: {marker}"
        for marker in REQUIRED_VIEW_MARKERS
        if marker not in views
    ]
    checks["SV-05-knowledge-view-coverage"] = status(
        not view_failures,
        ["knowledge-views.md"],
        view_failures,
    )

    visual_failures: list[str] = []
    if "not reconstructions of the original slides" not in views:
        visual_failures.append("knowledge views lack original-slide disclaimer")
    if "raw visual text authority: false" not in views:
        visual_failures.append("knowledge views do not deny raw visual authority")
    if visual_gap is None:
        visual_failures.append("visual/identifier K card is missing")
    else:
        for marker in (
            "bbox",
            "creator slides",
            "不是對原始 slide/frame 的精確重建",
        ):
            if marker not in visual_gap["text"]:
                visual_failures.append(
                    f"visual gap card missing marker: {marker}"
                )
    checks["SV-06-visual-authority-tracking"] = status(
        not visual_failures,
        ["knowledge-views.md", "K-visual-identifier-evidence-gap"],
        visual_failures,
        deferred=True,
    )

    precision_failures: list[str] = []
    if comparison is None:
        precision_failures.append("comparison card is missing")
    else:
        if comparison["text"].count("UNKNOWN") < 4:
            precision_failures.append("comparison does not preserve UNKNOWN cells")
        for marker in ("1 或 2 個數量級", "未驗證", "PROVISIONAL"):
            if marker not in comparison["text"]:
                precision_failures.append(
                    f"comparison missing uncertainty marker: {marker}"
                )
    for pattern in NUMBER_OVERREACH:
        if pattern.search(joined_cards + "\n" + views):
            precision_failures.append(
                f"unsupported precision pattern matched: {pattern.pattern}"
            )
    checks["SV-07-unknown-safe-precision"] = status(
        not precision_failures,
        ["T-trace-judge-comparison", "knowledge-views.md"],
        precision_failures,
    )

    action_failures: list[str] = []
    if practice is None:
        action_failures.append("Practice card is missing")
    else:
        for marker in (
            "**Expected Output**",
            "**Rollback**",
            "**Failure Handling**",
            "**Execution Status**：UNTESTED",
        ):
            if marker not in practice["text"]:
                action_failures.append(f"Practice card missing {marker}")
    checks["SV-08-action-contract"] = status(
        not action_failures,
        ["P-trace-driven-improvement-cycle"],
        action_failures,
    )

    similarity = max_core_similarity(cards)
    redundancy_failures = (
        [f"maximum core-proposition similarity is {similarity}, above 0.72"]
        if similarity > 0.72
        else []
    )
    checks["SV-09-cross-card-redundancy"] = status(
        not redundancy_failures,
        [f"max_core_similarity={similarity}"],
        redundancy_failures,
    )

    required_series = {"N", "C", "S", "T", "P", "D", "V", "K"}
    series = {str(card["meta"].get("series")) for card in cards}
    batch_failures = []
    if not required_series.issubset(series):
        batch_failures.append(
            f"missing source-shaped series: {sorted(required_series - series)}"
        )
    if card_ids and not card_ids[0].startswith(("N-", "C-", "T-", "P-")):
        batch_failures.append("first card is not a human entry")
    if len(cards) > 12:
        batch_failures.append("batch exceeds MAX_CARDS_PER_BATCH")
    checks["SV-10-source-shaped-batch"] = status(
        not batch_failures,
        card_ids,
        batch_failures,
    )

    # QG-01: a factual assertion carries an anchor, or its claim kind marks it
    # as inference. INFERENCE / HYPOTHESIS / NORMATIVE are already self-marking,
    # so only the two asserting kinds need grounding.
    anchor_failures = []
    for card in cards:
        matched = CLAIM_STATUS.search(card["text"])
        if matched is None:
            anchor_failures.append(f"{card['stable_id']}: no 證據與狀態 line")
            continue
        claim_kind = matched.group(1).split("·")[0].strip()
        if claim_kind not in ASSERTING_CLAIM_KINDS:
            continue
        artifacts = ARTIFACTS_LINE.search(card["text"])
        grounded = bool(EVIDENCE_REF.search(card["text"])) or bool(
            artifacts and "NONE" not in artifacts.group(1)
        )
        if not grounded:
            anchor_failures.append(
                f"{card['stable_id']}: {claim_kind} without an evidence anchor "
                "or a persisted artifact"
            )
    checks["SV-13-evidence-anchor-coverage"] = status(
        not anchor_failures,
        card_ids,
        anchor_failures,
    )

    # QG-09: a conflict or boundary is never silently dropped. The field that
    # carries it is series specific, so the series payload contract owns P, V
    # and K, and every other series must carry 反證／限制 explicitly.
    conflict_failures = []
    for card in cards:
        series_id = str(card["meta"].get("series"))
        if series_id in SERIES_OWNED_LIMIT_FIELDS:
            continue
        matched = FALSIFIER_LINE.search(card["text"])
        if matched is None or not matched.group(1).strip():
            conflict_failures.append(
                f"{card['stable_id']}: series {series_id} carries no 反證／限制"
            )
    checks["SV-14-conflict-preservation"] = status(
        not conflict_failures,
        card_ids,
        conflict_failures,
    )

    absolute_failures = []
    for marker in ("唯一方法", "永遠有效", "100% 有效"):
        if marker in joined_cards:
            absolute_failures.append(f"unsupported absolute marker: {marker}")
    checks["SV-11-no-absolute-overreach"] = status(
        not absolute_failures,
        card_ids,
        absolute_failures,
    )

    series_failures: list[str] = []
    for card in cards:
        series_name = str(card["meta"].get("series", ""))
        required_markers = SERIES_REQUIRED_MARKERS.get(series_name, ())
        for required_marker in required_markers:
            if required_marker not in card["text"]:
                series_failures.append(
                    f"{card['stable_id']}: missing series field {required_marker}"
                )
        if series_name == "T" and "|---|---|---|" not in card["text"]:
            series_failures.append(
                f"{card['stable_id']}: missing structured comparison table"
            )
        if series_name == "P":
            if card["text"].count("Validation：") < 4:
                series_failures.append(
                    f"{card['stable_id']}: fewer than four validation anchors"
                )
            if card["text"].count("Failure Signal：") < 4:
                series_failures.append(
                    f"{card['stable_id']}: fewer than four failure signals"
                )
    checks["SV-12-series-payload-contract"] = status(
        not series_failures,
        card_ids,
        series_failures,
    )

    # ------------------------------------------------------------------
    # The retained subject and its evidence ledger.
    #
    # Everything below needs bytes that live outside the card batch: the
    # subject retained under sources/<content-id>/ and a ledger that says, per
    # anchor, what kind of thing the anchor points at. Without the second, a
    # locator rule cannot tell a missing locator from a legitimate artifact
    # anchor and would fail correct cards, which is why these gates were
    # deferred rather than written badly.
    # ------------------------------------------------------------------
    content_id = str(manifest["video_id"])
    retained_root = root / "sources" / content_id
    retained_manifest_path = retained_root / "source-manifest.json"
    ledger = load_evidence_ledger(target)
    entries: dict[str, Any] = ledger.get("evidence", {})
    entry_check = Draft202012Validator(entry_schema())

    locator_failures: list[str] = []
    if ledger.get("entry_contract") != ENTRY_CONTRACT:
        locator_failures.append(f"ledger entry_contract is not {ENTRY_CONTRACT}")
    if ledger.get("content_id") != content_id:
        locator_failures.append("ledger content_id does not match the card manifest")
    if not retained_manifest_path.is_file():
        locator_failures.append(f"retained subject manifest missing: {retained_manifest_path}")
        retained_manifest: dict[str, Any] = {"retained_artifacts": [], "sources": []}
    else:
        retained_manifest = load_json(retained_manifest_path)
    retained_digests = {
        f"sources/{content_id}/{item['path']}": item["sha256"]
        for item in retained_manifest.get("retained_artifacts", [])
    }

    resolved_sources: dict[str, dict[str, Any]] = {}
    for source_id, descriptor in sorted(ledger.get("sources", {}).items()):
        declared_path = str(descriptor.get("path", ""))
        source_path = root / declared_path
        if not source_path.is_file():
            locator_failures.append(f"{source_id}: retained source missing: {declared_path}")
            continue
        digest = sha256_of(source_path)
        if digest != descriptor.get("sha256"):
            locator_failures.append(
                f"{source_id}: bytes at {declared_path} digest {digest} "
                f"!= ledger {descriptor.get('sha256')}"
            )
            continue
        retained = retained_digests.get(declared_path)
        if retained is not None and retained != digest:
            locator_failures.append(
                f"{source_id}: ledger digest disagrees with the retention manifest"
            )
            continue
        resolved_sources[source_id] = {**descriptor, "file": source_path}

    transcript_ids = [
        source_id
        for source_id, descriptor in resolved_sources.items()
        if descriptor.get("anchor_kind") == TRANSCRIPT_ANCHOR
    ]
    cue_runs: dict[str, dict[str, Any]] = {}
    transcript_text = ""
    if len(transcript_ids) != 1:
        locator_failures.append(
            f"expected exactly one resolved {TRANSCRIPT_ANCHOR} source, got {transcript_ids}"
        )
    else:
        descriptor = resolved_sources[transcript_ids[0]]
        if descriptor.get("declared_source_id") != manifest["source"]["source_id"]:
            locator_failures.append(
                "ledger transcript is not the source the cards were compiled from"
            )
        cues = load_json(descriptor["file"]).get("cues", [])
        starts = {str(cue.get("start_label")): index for index, cue in enumerate(cues)}
        ends = {str(cue.get("end_label")): index for index, cue in enumerate(cues)}
        transcript_text = collapse(" ".join(str(cue.get("normalized_text", "")) for cue in cues))
        for start_label, first in starts.items():
            for end_label, last in ends.items():
                if first <= last:
                    cue_runs[f"{start_label}..{end_label}"] = {
                        "text": collapse(
                            " ".join(str(cue.get("normalized_text", "")) for cue in cues[first : last + 1])
                        ),
                        "cues": cues[first : last + 1],
                    }

    # Each anchor is resolved once here; the two gates below read the result.
    resolutions: dict[str, dict[str, Any]] = {}
    for evidence_id, entry in sorted(entries.items()):
        errors = sorted(entry_check.iter_errors(entry), key=lambda error: error.json_path)
        if errors:
            locator_failures.append(
                f"{evidence_id}: entry violates {ENTRY_CONTRACT}: {errors[0].message}"
            )
            continue
        if entry["evidence_id"] != evidence_id:
            locator_failures.append(f"{evidence_id}: entry evidence_id disagrees with its key")
            continue
        descriptor = resolved_sources.get(str(entry["source_id"]))
        if descriptor is None:
            locator_failures.append(f"{evidence_id}: source_id has no resolved ledger source")
            continue
        anchor_kind = descriptor.get("anchor_kind")
        locator = str(entry["locator"])
        if anchor_kind == TRANSCRIPT_ANCHOR:
            matched = LOCATOR_TIMESTAMP.match(locator)
            if not matched:
                locator_failures.append(
                    f"{evidence_id}: {TRANSCRIPT_ANCHOR} anchor without a timestamp locator: {locator}"
                )
                continue
            span = f"{matched.group(1)}..{matched.group(2)}"
            if span not in cue_runs:
                locator_failures.append(
                    f"{evidence_id}: locator {locator} is not a cue run in the retained transcript"
                )
                continue
            resolutions[evidence_id] = {"kind": anchor_kind, "text": cue_runs[span]["text"], "span": span}
        elif anchor_kind == ARTIFACT_ANCHOR:
            matched = LOCATOR_POINTER.match(locator)
            if not matched:
                locator_failures.append(
                    f"{evidence_id}: {ARTIFACT_ANCHOR} anchor without a json-pointer locator: {locator}"
                )
                continue
            value = resolve_pointer(load_json(descriptor["file"]), matched.group(1))
            if value is ABSENT:
                locator_failures.append(
                    f"{evidence_id}: locator {locator} does not resolve in {descriptor['path']}"
                )
                continue
            resolutions[evidence_id] = {"kind": anchor_kind, "value": value}
        else:
            locator_failures.append(f"{evidence_id}: unknown anchor_kind {anchor_kind!r}")

    citations: dict[str, set[str]] = {}
    for card in cards:
        for evidence_id in set(EVIDENCE_REF.findall(card["text"])):
            evidence_id = evidence_id.strip("[]")
            citations.setdefault(evidence_id, set()).add(card["stable_id"])
        for matched in CARD_ANCHOR_SPAN.finditer(card["text"]):
            evidence_id = matched.group("evidence_id")
            resolution = resolutions.get(evidence_id)
            if resolution is None or resolution["kind"] != TRANSCRIPT_ANCHOR:
                continue
            written = f"{matched.group('start')}..{matched.group('end')}"
            if written != resolution["span"]:
                locator_failures.append(
                    f"{card['stable_id']}: {evidence_id} is glossed {written} "
                    f"but the ledger locator is {resolution['span']}"
                )
    for evidence_id in sorted(set(citations) - set(entries)):
        locator_failures.append(
            f"{sorted(citations[evidence_id])[0]}: {evidence_id} has no ledger entry"
        )
    checks["SV-15-evidence-locator-integrity"] = status(
        not locator_failures,
        ["evidence-ledger.json", *sorted(resolved_sources)],
        locator_failures,
    )

    exactness_failures: list[str] = []
    for evidence_id, resolution in sorted(resolutions.items()):
        verbatim = str(entries[evidence_id]["verbatim"])
        if resolution["kind"] == TRANSCRIPT_ANCHOR:
            if collapse(verbatim) not in resolution["text"]:
                exactness_failures.append(
                    f"{evidence_id}: verbatim does not occur inside its locator span"
                )
        elif resolution["value"] != verbatim:
            exactness_failures.append(
                f"{evidence_id}: verbatim does not equal the value at its locator"
            )
    checks["SV-16-evidence-verbatim-exactness"] = status(
        not exactness_failures,
        sorted(resolutions),
        exactness_failures,
    )

    orphan_failures: list[str] = []
    for evidence_id, entry in sorted(entries.items()):
        if not isinstance(entry.get("supports"), list) or not entry["supports"]:
            orphan_failures.append(f"{evidence_id}: no assertion declares it as support")
            continue
        cited_by = citations.get(evidence_id, set())
        if not cited_by:
            orphan_failures.append(f"{evidence_id}: no card cites it")
        elif set(entry["supports"]) != cited_by:
            orphan_failures.append(
                f"{evidence_id}: supports {sorted(entry['supports'])} "
                f"but is cited by {sorted(cited_by)}"
            )
    checks["SV-17-no-orphan-evidence"] = status(
        not orphan_failures,
        sorted(entries),
        orphan_failures,
    )

    coverage_failures: list[str] = []
    coverage = load_json(target / "coverage-manifest.json")
    fixture = load_json(target / "fixture.json")
    declared_units = list(fixture.get("required", {}).get("knowledge_units", []))
    covered_units = [str(item.get("knowledge_unit_id")) for item in coverage.get("items", [])]
    if sorted(covered_units) != sorted(declared_units):
        coverage_failures.append(
            "coverage manifest does not enumerate exactly the fixture's high-signal units"
        )
    for item in coverage.get("items", []):
        unit = str(item.get("knowledge_unit_id"))
        disposition = str(item.get("disposition"))
        if disposition not in COVERAGE_DISPOSITIONS:
            coverage_failures.append(f"{unit}: unknown disposition {disposition}")
            continue
        if disposition in MAPPED_DISPOSITIONS and not item.get("card_ids"):
            coverage_failures.append(f"{unit}: {disposition} names no card")
        if disposition not in MAPPED_DISPOSITIONS and not item.get("reason"):
            coverage_failures.append(f"{unit}: {disposition} records no reason")
        for card_id in item.get("card_ids") or []:
            if card_id not in card_id_set:
                coverage_failures.append(f"{unit}: card_id {card_id} is not in this batch")
        for evidence_id in item.get("evidence_ids") or []:
            if evidence_id not in entries:
                coverage_failures.append(f"{unit}: evidence_id {evidence_id} is not in the ledger")
    checks["SV-18-high-signal-coverage"] = status(
        not coverage_failures,
        ["coverage-manifest.json", "fixture.json"],
        coverage_failures,
    )

    injection_failures: list[str] = []
    declared_injections = retained_manifest.get("injection_findings", [])
    if not isinstance(declared_injections, list):
        injection_failures.append("retained manifest injection_findings is not a list")
        declared_injections = []
    detected: list[str] = []
    for pattern in INJECTION_PATTERNS:
        for matched in pattern.finditer(transcript_text):
            detected.append(matched.group(0))
    declared_text = [collapse(str(finding.get("text", ""))) for finding in declared_injections]
    for hit in sorted(set(detected)):
        if not any(collapse(hit).lower() in text.lower() for text in declared_text):
            injection_failures.append(
                f"source instruction {hit!r} is not declared in the retention manifest"
            )
        if any(hit.lower() in card["text"].lower() for card in cards):
            injection_failures.append(f"source instruction {hit!r} is repeated by a card")
    for text in declared_text:
        if text and text.lower() not in transcript_text.lower():
            injection_failures.append(
                f"declared injection finding {text!r} is not present in the retained subject"
            )
    checks["SV-19-injection-safety"] = status(
        not injection_failures,
        [f"sources/{content_id}/source-manifest.json", *transcript_ids],
        injection_failures,
    )

    hg = {
        "HG-01": checks["SV-01-artifact-integrity"],
        "HG-02": checks["SV-05-knowledge-view-coverage"],
        "HG-03": checks["SV-06-visual-authority-tracking"],
        "HG-04": checks["SV-07-unknown-safe-precision"],
        "HG-05": checks["SV-09-cross-card-redundancy"],
        "HG-06": checks["SV-10-source-shaped-batch"],
    }
    qg_subset = {
        "QG-01": checks["SV-13-evidence-anchor-coverage"],
        "QG-02": checks["SV-16-evidence-verbatim-exactness"],
        "QG-03": checks["SV-15-evidence-locator-integrity"],
        "QG-07": checks["SV-02-identity-and-link-integrity"],
        "QG-08": checks["SV-02-identity-and-link-integrity"],
        "QG-09": checks["SV-14-conflict-preservation"],
        "QG-10": checks["SV-04-epistemic-honesty"],
        "QG-11": checks["SV-04-epistemic-honesty"],
        "QG-12": checks["SV-08-action-contract"],
        "QG-13": checks["SV-18-high-signal-coverage"],
        "QG-15": checks["SV-19-injection-safety"],
        "QG-16": checks["SV-01-artifact-integrity"],
        "QG-17": checks["SV-17-no-orphan-evidence"],
        "QG-18": checks["SV-12-series-payload-contract"],
        "QG-20": checks["SV-03-payload-first-contract"],
        "QG-21": checks["SV-10-source-shaped-batch"],
        "QG-23": checks["SV-11-no-absolute-overreach"],
    }

    all_failures = [
        failure
        for check in checks.values()
        if check["status"] == "FAIL"
        for failure in check["failures"]
    ]
    report = {
        "schema_version": SCHEMA_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "content_id": str(manifest["video_id"]),
        "created_at": created_at,
        "input": {
            "target": str(target.relative_to(root)),
            "prompt_git_blob_sha1": prompt_blob,
            "source_dependency_keys": sorted(dependencies),
            "card_count": len(cards),
            "card_order": card_ids,
        },
        "checks": checks,
        "hg": hg,
        "qg_subset": qg_subset,
        "qg_not_run": [
            qg
            for qg in ALL_QG_IDS
            if qg not in AUTOMATED_QG_IDS and qg not in HUMAN_ADMITTED_QG_IDS
        ],
        "overall_status": (
            "FAIL"
            if all_failures
            else "PASS_WITH_DEFERRED_VISUAL_AND_PARTIAL_QG"
        ),
        "failures": all_failures,
    }
    validate_report(report, schema_path)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=Path("evals/semantic-yield/CvRngaQZQ3Y"),
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("schemas/semantic-validator-report.schema.json"),
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--created-at", required=True)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    target = args.target if args.target.is_absolute() else root / args.target
    schema = args.schema if args.schema.is_absolute() else root / args.schema
    report = build_report(
        root,
        target,
        created_at=args.created_at,
        schema_path=schema,
    )
    rendered = json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    output = args.output if args.output.is_absolute() else root / args.output
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            raise ValidationError("persisted semantic validator report is stale")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
