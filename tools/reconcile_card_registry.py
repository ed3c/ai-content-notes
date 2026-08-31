#!/usr/bin/env python3
"""Reconcile rendered v7.1 cards into a card registry, or report the gap.

`schemas/card-registry.schema.json` has existed without an implementation, so
stable-ID reuse, collision detection, SUPERSEDES handling and identical-input
NOOP replay were contract text rather than behaviour.

The reconciler reads rendered card files, not a model response. It reuses a
stable id by exact canonical key, refuses to mint a second id for a key it has
already seen, and refuses to let one id carry two keys. A card whose CARD_META
is short of what the registry contract requires is reported as a gap; nothing
is invented to fill it, and no registry is written while any gap stands.

Revision is content-addressed. Re-running against unchanged cards and the same
prior registry reproduces the same bytes and does not advance
`registry_revision`, which is the NOOP replay the completion contract needs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path("schemas/card-registry.schema.json")
PROTOCOL = "zettelkasten-v7.0-evidence-first-loop-safe"
SCHEMA_VERSION = "zettelkasten-card-registry@1"

CARD_META = re.compile(r"<!--\s*CARD_META\s*(\{.*?\})\s*-->", re.S)
STATUS = re.compile(r"-\s*\*\*證據與狀態\*\*[：:]\s*(.+)")
TYPED_LINKS = re.compile(r"-\s*\*\*Typed Links\*\*[：:](.*?)(?=\n-\s*\*\*|\n\n|\Z)", re.S)
LINK = re.compile(
    r"(ROOT|FLOW|CONFLICT|ANALOGY|INSTANCE_OF|IMPLEMENTS|VALIDATED_BY|SUPERSEDES"
    r"|DEPENDS_ON|MITIGATES)\s*(→|←|->|<-)\s*\[\[([^\]]+)\]\]"
)
EVIDENCE_REF = re.compile(r"\[\[(EV-[A-Za-z0-9._:-]+)\]\]")

REQUIRED_META = (
    "stable_id",
    "canonical_key",
    "series",
    "lifecycle",
    "revision",
    "scope",
    "confidence_basis",
    "source_provenance",
)
CLAIM_KINDS = {"SOURCE_STATEMENT", "OBSERVATION", "INFERENCE", "HYPOTHESIS", "NORMATIVE"}
VERIFICATIONS = {
    "UNCHECKED",
    "SUPPORTED",
    "CORROBORATED",
    "TESTED",
    "CONTESTED",
    "FALSIFIED",
}
CONFIDENCES = {"HIGH", "MEDIUM", "LOW"}
LIFECYCLES = {"ACTIVE", "SUPERSEDED", "DEPRECATED"}


class RegistryError(RuntimeError):
    """Raised when reconciliation cannot proceed without inventing something."""


def _sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _payload(text: str) -> str:
    """Card body with the machine sidecar removed, so the digest tracks content."""
    return CARD_META.sub("", text).strip()


def parse_card(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    """Return (entry, gaps). An entry is produced only when no gap is found."""
    text = path.read_text(encoding="utf-8")
    gaps: list[str] = []

    match = CARD_META.search(text)
    if match is None:
        return None, [f"{path.name}: no CARD_META sidecar"]
    try:
        meta = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        return None, [f"{path.name}: CARD_META is not valid JSON: {exc}"]

    missing = [key for key in REQUIRED_META if key not in meta]
    if missing:
        gaps.append(f"{path.name}: CARD_META missing {', '.join(missing)}")

    status = STATUS.search(text)
    if status is None:
        gaps.append(f"{path.name}: no 證據與狀態 line")
        claim_kind = verification = confidence = None
    else:
        parts = [item.strip() for item in re.split(r"[·・]", status.group(1)) if item.strip()]
        if len(parts) != 3:
            gaps.append(f"{path.name}: 證據與狀態 is not kind · verification · confidence")
            claim_kind = verification = confidence = None
        else:
            claim_kind, verification, confidence = parts
            if claim_kind not in CLAIM_KINDS:
                gaps.append(f"{path.name}: unknown claim kind {claim_kind}")
            if verification not in VERIFICATIONS:
                gaps.append(f"{path.name}: unknown verification {verification}")
            if confidence not in CONFIDENCES:
                gaps.append(f"{path.name}: unknown confidence {confidence}")

    if meta.get("lifecycle") not in LIFECYCLES:
        gaps.append(f"{path.name}: unknown lifecycle {meta.get('lifecycle')}")
    if meta.get("stable_id") != path.stem:
        gaps.append(f"{path.name}: stable_id {meta.get('stable_id')!r} does not match the filename")
    if gaps:
        return None, gaps

    block = TYPED_LINKS.search(text)
    typed_links = []
    supersedes = []
    for edge_type, arrow, target in LINK.findall(block.group(1) if block else ""):
        typed_links.append(
            {
                "edge_type": edge_type,
                "relation": "inbound" if arrow in {"←", "<-"} else "outbound",
                "target": target,
            }
        )
        if edge_type == "SUPERSEDES" and arrow in {"→", "->"}:
            supersedes.append(target)

    entry = {
        "stable_id": meta["stable_id"],
        "canonical_key": meta["canonical_key"],
        "series": meta["series"],
        "lifecycle_status": meta["lifecycle"],
        "revision": int(meta["revision"]),
        "claim_kind": claim_kind,
        "verification": verification,
        "confidence": confidence,
        "confidence_basis": meta["confidence_basis"],
        "scope": meta["scope"],
        "content_digest": _sha256_text(_payload(text)),
        "evidence_ids": sorted(set(EVIDENCE_REF.findall(text))),
        "typed_links": typed_links,
        "supersedes": sorted(set(supersedes)),
    }
    return entry, []


def content_identity(value: dict[str, Any]) -> str:
    """Registry content with every wall-clock field and the revision removed.

    Public because it is the only wall-clock-free identity of a registry, and a
    loop that chains rounds by digest has to hash content rather than the
    minute a round happened to run in.
    """
    stripped = {
        key: item
        for key, item in value.items()
        if key not in {"updated_at", "registry_revision"}
    }
    stripped["cards"] = {
        stable_id: {
            field: entry[field] for field in sorted(entry) if field != "updated_at"
        }
        for stable_id, entry in value.get("cards", {}).items()
    }
    return json.dumps(stripped, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _bind_identity(entries: list[dict[str, Any]], prior: dict[str, Any] | None) -> None:
    """Reuse stable ids by exact canonical key; reject every other identity shape."""
    by_key: dict[str, str] = dict((prior or {}).get("canonical_index", {}))
    by_id: dict[str, str] = {
        stable_id: key for key, stable_id in by_key.items()
    }
    for entry in entries:
        key, stable_id = entry["canonical_key"], entry["stable_id"]
        known = by_key.get(key)
        if known is not None and known != stable_id:
            raise RegistryError(
                f"canonical key already bound to {known}, card declares {stable_id}: {key}"
            )
        held = by_id.get(stable_id)
        if held is not None and held != key:
            raise RegistryError(
                f"stable id collision: {stable_id} already binds a different canonical key"
            )
        by_key[key] = stable_id
        by_id[stable_id] = key


def reconcile(
    card_paths: list[Path],
    source_id: str,
    source_digest: str,
    updated_at: str,
    prior: dict[str, Any] | None = None,
    evidence: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    entries: list[dict[str, Any]] = []
    gaps: list[str] = []
    for path in sorted(card_paths):
        entry, card_gaps = parse_card(path)
        gaps.extend(card_gaps)
        if entry is not None:
            entries.append(entry)
    if gaps:
        return None, sorted(gaps)

    seen_ids = [entry["stable_id"] for entry in entries]
    if len(set(seen_ids)) != len(seen_ids):
        raise RegistryError("duplicate stable_id across the card batch")
    _bind_identity(entries, prior)

    prior_cards = dict((prior or {}).get("cards", {}))
    superseded: set[str] = set()
    for entry in entries:
        for target in entry["supersedes"]:
            if target not in prior_cards and target not in seen_ids:
                raise RegistryError(f"{entry['stable_id']} supersedes an unknown card: {target}")
            superseded.add(target)

    merged: dict[str, dict[str, Any]] = {
        stable_id: dict(item) for stable_id, item in prior_cards.items()
    }
    for entry in entries:
        merged[entry["stable_id"]] = dict(entry, updated_at=updated_at)
    for stable_id in superseded:
        if stable_id in merged:
            merged[stable_id] = dict(
                merged[stable_id], lifecycle_status="SUPERSEDED", updated_at=updated_at
            )

    cards = {stable_id: merged[stable_id] for stable_id in sorted(merged)}
    registry = {
        "schema_version": SCHEMA_VERSION,
        "protocol": PROTOCOL,
        "source_id": source_id,
        "registry_revision": (prior or {}).get("registry_revision", 1),
        "source_digest": source_digest,
        "cards": cards,
        "canonical_index": {
            item["canonical_key"]: item["stable_id"] for item in cards.values()
        },
        "evidence": evidence or {},
        "updated_at": updated_at,
    }
    # NOOP replay: identical cards against the same prior registry must not
    # advance the revision. Only a content change does, so the comparison
    # ignores every wall-clock field and the revision counter itself.
    if prior is not None:
        if content_identity(registry) == content_identity(prior):
            registry["registry_revision"] = prior["registry_revision"]
            registry["updated_at"] = prior["updated_at"]
            registry["cards"] = {
                stable_id: dict(entry, updated_at=prior["cards"][stable_id]["updated_at"])
                for stable_id, entry in cards.items()
            }
        else:
            registry["registry_revision"] = prior["registry_revision"] + 1
    return registry, []


def validate(registry: dict[str, Any], schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(registry),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        rendered = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors
        )
        raise RegistryError(f"registry failed schema validation: {rendered}")


def render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cards", required=True, type=Path, help="directory of rendered cards")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-digest", required=True)
    parser.add_argument("--updated-at", required=True)
    parser.add_argument("--prior", type=Path)
    parser.add_argument("--evidence-ledger", type=Path)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--gap-report", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if not args.cards.is_dir():
        raise RegistryError(f"missing card directory: {args.cards}")
    prior = json.loads(args.prior.read_text(encoding="utf-8")) if args.prior else None
    evidence = (
        json.loads(args.evidence_ledger.read_text(encoding="utf-8"))
        if args.evidence_ledger
        else None
    )

    registry, gaps = reconcile(
        sorted(args.cards.glob("*.md")),
        args.source_id,
        args.source_digest,
        args.updated_at,
        prior,
        evidence,
    )

    if gaps:
        report = {
            "schema_version": "card-registry-gap-report@1",
            "source_id": args.source_id,
            "card_directory": str(args.cards),
            "registry_written": False,
            "gap_count": len(gaps),
            "gaps": gaps,
        }
        if args.check:
            # --check verifies the recorded state, whatever that state is. A gap
            # that still matches its persisted report is a successful
            # verification; a gap that drifted is a hard failure.
            if not args.gap_report or not args.gap_report.is_file():
                raise RegistryError("--check needs a persisted --gap-report while a gap stands")
            if args.gap_report.read_text(encoding="utf-8") != render(report):
                raise RegistryError("persisted gap report is stale")
            print(render(report), end="")
            return 0
        if args.gap_report:
            args.gap_report.parent.mkdir(parents=True, exist_ok=True)
            args.gap_report.write_text(render(report), encoding="utf-8")
        print(render(report), end="")
        # Outside --check a standing gap is never a pass.
        return 1

    validate(registry, args.schema)
    rendered = render(registry)
    if args.check:
        if not args.output or not args.output.is_file():
            raise RegistryError("--check needs a persisted --output registry")
        if args.output.read_text(encoding="utf-8") != rendered:
            raise RegistryError("persisted registry is stale")
    elif args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")

    print(
        json.dumps(
            {
                "card_count": len(registry["cards"]),
                "registry_revision": registry["registry_revision"],
                "gap_count": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RegistryError as error:
        print(f"registry reconciliation refused: {error}", file=sys.stderr)
        raise SystemExit(2) from error
