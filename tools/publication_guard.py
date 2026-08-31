#!/usr/bin/env python3
"""Deterministic publication guard for rendered v7.1 card batches.

`governance/CARD_PROTOCOL_V7_1.md` carries 24 quality gates and 16 invariants,
all of them enforced by asking a model to obey them. An instruction-layer ban is
its own re-offense: the carrier has to be CI. This guard moves the mechanically
checkable subset into a script, so a red card cannot reach `main`.

The protocol file is the single owner of the rule list. Rule ids are parsed out
of it and every gate implemented here must resolve against that parse; a
renamed, renumbered or deleted rule makes the guard exit FATAL rather than keep
guarding a rule the protocol no longer states. There is no second hand-kept QG
list to drift.

Implemented subset, with the protocol clause each one carries:

    QG-03  Locator Integrity   provenance carries a real locator, or the
                               declared TEXT_MATCH / LOCATOR_MISSING fallback
    QG-07  Stable Identity     one canonical key binds one stable id, and a
                               persisted registry's binding is reused
    QG-08  Typed Links         every typed link resolves, or is UNRESOLVED::
                               with a K card standing for it
    QG-10  Test Honesty        P/V execution markers exist, use the protocol's
                               own vocabulary, and anything claiming a run
                               names its artifacts
    QG-16  Version Consistency every card has a CARD_META sidecar of the shape
                               `schemas/card-registry.schema.json` accepts
    QG-24  Idempotency         reconciling an unchanged batch a second time is
                               byte-identical and does not advance the revision
    I-06   Shadow Evidence     a card quotes the shortest necessary original;
                               a retained source body pasted into a card is not
                               a quote

Everything else in the protocol stays prompt-enforced, and is listed as such in
the report rather than silently omitted.

A batch that ships `card-registry-gap-report.json` is in a recorded-gap state:
the guard verifies the recorded gap has not drifted, exactly as
`reconcile_card_registry.py --check` does, instead of demanding a zero it was
never promised. A batch that ships `card-registry.json` must reconcile clean.

Usage:
    python3 tools/publication_guard.py [--root PATH]

`--root` defaults to this file's own repository, so trusted guard bytes can be
pointed at a candidate tree: `python3 .trusted/tools/publication_guard.py
--root .candidate`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import reconcile_card_registry as registry  # noqa: E402

PROTOCOL = Path("governance/CARD_PROTOCOL_V7_1.md")
REGISTRY_SCHEMA = Path("schemas/card-registry.schema.json")
BATCH_ROOT = Path("evals")
BATCH_GLOB = "*/*/cards"
SOURCES = Path("sources")

QUALITY_GATE = re.compile(r"^(QG-\d{2})\s+([^\t\n]+)\t", re.M)
INVARIANT = re.compile(r"^(I-\d{2})｜(.+)$", re.M)
EXECUTION_VOCABULARY = re.compile(r"^-\s*\*\*Execution Status\*\*[：:]\s*(.+)$", re.M)
VERDICT_VOCABULARY = re.compile(r"^-\s*\*\*Verdict\*\*[：:]\s*(.+)$", re.M)

STABLE_ID = re.compile(r"^[A-Z]-[a-z0-9][a-z0-9-]*$")
WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
UNRESOLVED = "UNRESOLVED::"
LOCATOR_FIELD = re.compile(r"#(timestamp|page|line|section|path|commit):\S")
DIGEST_LOCATOR = re.compile(r"^sha256:[0-9a-f]{64}$")
ARTIFACT_LOCATOR = "artifact:"

# I-06 bounds a card's verbatim to the shortest necessary original. 200
# characters is far above every quote the rendered batches carry and far below
# any pasted body, so the window separates a quote from a transcript without
# having to judge either.
# ponytail: fixed window, and a naive window-by-window scan of every card
# against every retained byte (~2s for the two batches and ~200KB of retained
# captions). Shingle-hash the haystack if retention grows an order of magnitude.
BODY_WINDOW = 200
SOURCE_TEXT_SUFFIXES = {".txt", ".vtt", ".md", ".json"}

# Inputs the reconciler needs but that carry no identity or idempotency
# meaning: the guard supplies its own, so it never has to guess a batch's
# real source digest to answer an identity question.
GUARD_SOURCE_ID = "publication-guard"
GUARD_SOURCE_DIGEST = "sha256:" + "0" * 64
GUARD_UPDATED_AT = "1970-01-01T00:00:00Z"


class GuardError(RuntimeError):
    """Raised when the guard cannot run at all; never a card verdict."""


class Card(NamedTuple):
    path: Path
    body: str  # the card with its CARD_META sidecar removed
    meta: dict[str, Any] | None
    series: str


class Batch(NamedTuple):
    name: str
    cards: list[Card]
    reconciled: dict[str, Any] | None  # None while a gap or a refusal stands
    gaps: list[str]
    reconcile_error: str | None
    persisted: dict[str, Any] | None
    recorded_gaps: list[str] | None

    @property
    def ids(self) -> set[str]:
        known = {card.path.stem for card in self.cards}
        if self.persisted:
            known |= set(self.persisted.get("cards", {}))
        return known


def rule_index(text: str) -> dict[str, str]:
    """Rule id to title, parsed out of the protocol. The only rule list there is."""
    rules = {rule: title.strip() for rule, title in QUALITY_GATE.findall(text)}
    rules.update({rule: title.strip() for rule, title in INVARIANT.findall(text)})
    return rules


def vocabulary(pattern: re.Pattern[str], text: str, name: str) -> set[str]:
    """The allowed values for a marker, read off the protocol's own template."""
    for line in pattern.findall(text):
        values = {item.strip() for item in line.split("|") if item.strip()}
        if len(values) > 1:
            return values
    raise GuardError(f"PROTOCOL_VOCABULARY_ABSENT:{name}")


def load_card(path: Path) -> Card:
    text = path.read_text(encoding="utf-8")
    match = registry.CARD_META.search(text)
    meta: dict[str, Any] | None = None
    if match is not None:
        try:
            meta = json.loads(match.group(1))
        except json.JSONDecodeError:
            meta = None
    return Card(
        path=path,
        body=registry.CARD_META.sub("", text),
        meta=meta,
        series=path.stem.split("-", 1)[0],
    )


def load_batch(cards_dir: Path) -> Batch:
    batch = cards_dir.parent
    manifest = batch / "card-manifest.json"
    if not manifest.is_file():
        raise GuardError(f"BATCH_MANIFEST_ABSENT:{batch}")

    card_paths = sorted(cards_dir.glob("*.md"))
    if not card_paths:
        raise GuardError(f"BATCH_HAS_NO_CARDS:{cards_dir}")

    registry_path = batch / "card-registry.json"
    report_path = batch / "card-registry-gap-report.json"
    persisted = (
        json.loads(registry_path.read_text(encoding="utf-8"))
        if registry_path.is_file()
        else None
    )
    recorded = (
        json.loads(report_path.read_text(encoding="utf-8"))["gaps"]
        if report_path.is_file()
        else None
    )
    if persisted is None and recorded is None:
        raise GuardError(f"BATCH_STATE_ABSENT:{batch}")

    reconciled: dict[str, Any] | None = None
    gaps: list[str] = []
    error: str | None = None
    try:
        reconciled, gaps = registry.reconcile(
            card_paths,
            GUARD_SOURCE_ID,
            GUARD_SOURCE_DIGEST,
            GUARD_UPDATED_AT,
        )
    except registry.RegistryError as failure:
        error = str(failure)

    return Batch(
        name=f"{batch.parent.name}/{batch.name}",
        cards=[load_card(path) for path in card_paths],
        reconciled=reconciled,
        gaps=gaps,
        reconcile_error=error,
        persisted=persisted,
        recorded_gaps=recorded,
    )


def check_sidecars(batch: Batch, root: Path) -> list[str]:
    """QG-16: every card carries a CARD_META the registry schema accepts."""
    findings: list[str] = []
    for card in batch.cards:
        if card.meta is None:
            findings.append(f"{card.path.name}: CARD_META sidecar absent or not JSON")

    if batch.recorded_gaps is not None:
        # A recorded gap is a state, not a pass. Drift in either direction is red.
        for gap in sorted(set(batch.gaps) - set(batch.recorded_gaps)):
            findings.append(f"gap not in the recorded report: {gap}")
        for gap in sorted(set(batch.recorded_gaps) - set(batch.gaps)):
            findings.append(f"recorded gap no longer reproduced: {gap}")
        return findings

    findings.extend(batch.gaps)
    if batch.reconciled is not None:
        try:
            registry.validate(batch.reconciled, root / REGISTRY_SCHEMA)
        except registry.RegistryError as failure:
            findings.append(str(failure))
    return findings


def check_identity(batch: Batch, root: Path) -> list[str]:
    """QG-07: one canonical key binds one stable id, and a persisted binding is reused."""
    del root
    findings: list[str] = []
    by_key: dict[str, str] = {}
    by_id: dict[str, str] = {}
    index = dict((batch.persisted or {}).get("canonical_index", {}))

    for card in batch.cards:
        stable_id = card.path.stem
        key = (card.meta or {}).get("canonical_key")
        if not key:
            continue  # a missing sidecar field is QG-16's finding, not this one
        if by_key.setdefault(key, stable_id) != stable_id:
            findings.append(
                f"{card.path.name}: canonical key already bound to {by_key[key]}: {key}"
            )
        if by_id.setdefault(stable_id, key) != key:
            findings.append(f"{card.path.name}: stable id carries a second canonical key")
        bound = index.get(key)
        if bound is not None and bound != stable_id:
            findings.append(
                f"{card.path.name}: registry binds {key} to {bound}, card declares {stable_id}"
            )
        if (card.meta or {}).get("stable_id") not in (None, stable_id):
            findings.append(f"{card.path.name}: CARD_META stable_id does not match the filename")

    if batch.reconcile_error is not None:
        findings.append(batch.reconcile_error)
    return findings


def check_idempotency(batch: Batch, root: Path) -> list[str]:
    """QG-24: a second reconciliation of an unchanged batch is a NOOP."""
    del root
    first = batch.reconciled
    if first is None:
        return []
    second, _ = registry.reconcile(
        [card.path for card in batch.cards],
        GUARD_SOURCE_ID,
        GUARD_SOURCE_DIGEST,
        GUARD_UPDATED_AT,
        prior=first,
    )
    findings: list[str] = []
    if second["registry_revision"] != first["registry_revision"]:
        findings.append(
            "re-running an unchanged batch advanced registry_revision "
            f"{first['registry_revision']} -> {second['registry_revision']}"
        )
    if registry.render(second) != registry.render(first):
        findings.append("re-running an unchanged batch did not reproduce the same registry")
    return findings


def check_typed_links(batch: Batch, root: Path) -> list[str]:
    """QG-08: no generic or dangling link; an unbuilt target is UNRESOLVED:: plus a K card."""
    del root
    findings: list[str] = []
    known = batch.ids
    has_k_card = any(card.series == "K" for card in batch.cards)

    for card in batch.cards:
        block = registry.TYPED_LINKS.search(card.body)
        if block is None:
            findings.append(f"{card.path.name}: no Typed Links block")
            continue
        text = block.group(1)
        typed = registry.LINK.findall(text)
        for _edge, _arrow, target in typed:
            text = text.replace(f"[[{target}]]", "", 1)
            if target in known:
                continue
            if target.startswith(UNRESOLVED):
                if not has_k_card:
                    findings.append(
                        f"{card.path.name}: {target} has no K card standing for it"
                    )
                continue
            findings.append(
                f"{card.path.name}: link target [[{target}]] resolves to no card "
                "and is not marked UNRESOLVED::"
            )
        for leftover in WIKILINK.findall(text):
            findings.append(f"{card.path.name}: untyped or generic link [[{leftover}]]")
    return findings


def _locator_gap(entry: str, root: Path) -> str | None:
    """None when the entry carries a locator; otherwise why it does not."""
    if entry == "LOCATOR_MISSING":
        return None
    if entry.startswith("TEXT_MATCH::") and len(entry) > len("TEXT_MATCH::"):
        return None
    if DIGEST_LOCATOR.match(entry):
        return None
    if LOCATOR_FIELD.search(entry):
        return None
    if entry.startswith(ARTIFACT_LOCATOR):
        # A path locator is only a locator while the path is readable; an
        # unreadable one is fabricated precision (I-05), not a fallback.
        relative = entry[len(ARTIFACT_LOCATOR) :]
        if relative and (root / relative).exists():
            return None
        return f"artifact locator does not resolve: {entry}"
    return f"provenance without a locator: {entry}"


def check_locators(batch: Batch, root: Path) -> list[str]:
    """QG-03: a locator comes from the source, or says which fallback it is."""
    findings: list[str] = []
    for card in batch.cards:
        provenance = (card.meta or {}).get("source_provenance")
        if provenance is None:
            continue  # an absent field is QG-16's finding
        if not provenance:
            findings.append(f"{card.path.name}: source_provenance is empty")
            continue
        for entry in provenance:
            gap = _locator_gap(str(entry), root)
            if gap is not None:
                findings.append(f"{card.path.name}: {gap}")
    return findings


def check_test_honesty(batch: Batch, root: Path) -> list[str]:
    """QG-10: unrun work says so, in the protocol's own words, and a run names artifacts."""
    protocol = (root / PROTOCOL).read_text(encoding="utf-8")
    statuses = vocabulary(EXECUTION_VOCABULARY, protocol, "Execution Status")
    verdicts = vocabulary(VERDICT_VOCABULARY, protocol, "Verdict")
    ran = (verdicts - {"NOT_RUN"}) | {"TESTED"}

    findings: list[str] = []
    for card in batch.cards:
        claimed: list[str] = []
        if card.series == "P":
            found = EXECUTION_VOCABULARY.findall(card.body)
            if len(found) != 1:
                findings.append(f"{card.path.name}: expected one Execution Status, found {len(found)}")
            for value in found:
                if value.strip() not in statuses:
                    findings.append(f"{card.path.name}: Execution Status {value.strip()!r} is not in the protocol vocabulary")
                claimed.append(value.strip())
        if card.series == "V":
            found = VERDICT_VOCABULARY.findall(card.body)
            if len(found) != 1:
                findings.append(f"{card.path.name}: expected one Verdict, found {len(found)}")
            if "**Observed Result**" not in card.body:
                findings.append(f"{card.path.name}: Verdict without an Observed Result")
            for value in found:
                if value.strip() not in verdicts:
                    findings.append(f"{card.path.name}: Verdict {value.strip()!r} is not in the protocol vocabulary")
                claimed.append(value.strip())
        if any(value in ran for value in claimed) and "**Artifacts**" not in card.body:
            findings.append(f"{card.path.name}: claims a run without naming artifacts")
    return findings


def retained_source_text(root: Path) -> str:
    """Every retained source body, normalized, as one haystack. Empty when none is retained."""
    sources = root / SOURCES
    if not sources.is_dir():
        return ""
    chunks: list[str] = []
    for path in sorted(sources.rglob("*")):
        if path.is_file() and path.suffix in SOURCE_TEXT_SUFFIXES:
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return _normalize("\n".join(chunks))


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).casefold()


def check_no_raw_body(batch: Batch, root: Path, haystack: str | None = None) -> list[str]:
    """I-06: a card quotes the shortest necessary original, never a retained body."""
    source = retained_source_text(root) if haystack is None else haystack
    if not source:
        return []
    findings: list[str] = []
    for card in batch.cards:
        text = _normalize(card.body)
        for start in range(0, max(0, len(text) - BODY_WINDOW) + 1):
            window = text[start : start + BODY_WINDOW]
            if len(window) == BODY_WINDOW and window in source:
                findings.append(
                    f"{card.path.name}: {BODY_WINDOW} characters copied verbatim from a "
                    f"retained source body at offset {start}"
                )
                break
    return findings


CHECKS = (
    ("QG-03", check_locators),
    ("QG-07", check_identity),
    ("QG-08", check_typed_links),
    ("QG-10", check_test_honesty),
    ("QG-16", check_sidecars),
    ("QG-24", check_idempotency),
    ("I-06", check_no_raw_body),
)


def run(root: Path) -> dict[str, Any]:
    protocol_path = root / PROTOCOL
    if not protocol_path.is_file():
        raise GuardError(f"PROTOCOL_ABSENT:{protocol_path}")
    rules = rule_index(protocol_path.read_text(encoding="utf-8"))
    if not rules:
        raise GuardError(f"PROTOCOL_RULE_LIST_UNPARSEABLE:{protocol_path}")
    for rule, _check in CHECKS:
        if rule not in rules:
            raise GuardError(f"RULE_ABSENT_FROM_PROTOCOL:{rule}")

    card_dirs = sorted((root / BATCH_ROOT).glob(BATCH_GLOB))
    if not card_dirs:
        raise GuardError(f"NO_CARD_BATCHES:{root / BATCH_ROOT}")

    haystack = retained_source_text(root)
    findings: dict[str, list[str]] = {rule: [] for rule, _ in CHECKS}
    batches = []
    for cards_dir in card_dirs:
        batch = load_batch(cards_dir)
        batches.append(batch.name)
        for rule, check in CHECKS:
            found = (
                check_no_raw_body(batch, root, haystack)
                if check is check_no_raw_body
                else check(batch, root)
            )
            findings[rule].extend(f"{batch.name}: {item}" for item in found)

    return {
        "schema_version": "publication-guard@1",
        "root": str(root),
        "batches": batches,
        "retained_source_text": "PRESENT" if haystack else "ABSENT",
        "enforced": {rule: rules[rule] for rule, _ in CHECKS},
        "prompt_enforced_only": sorted(
            rule for rule in rules if rule.startswith("QG-") and rule not in dict(CHECKS)
        ),
        "finding_count": sum(len(items) for items in findings.values()),
        "findings": {rule: items for rule, items in findings.items() if items},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic v7.1 publication guard")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="tree to guard; defaults to this script's own repository",
    )
    args = parser.parse_args(argv)

    report = run(args.root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if report["finding_count"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GuardError as error:
        print(f"publication guard cannot run: {error}", file=sys.stderr)
        raise SystemExit(2) from error
