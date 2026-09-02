#!/usr/bin/env python3
"""Materialize and verify the CvRngaQZQ3Y semantic-yield evidence ledger.

The evidence tables below (`QUOTE_SPANS`, `POINTER_FACTS`) are a human
curation: each entry names a transcript span or a JSON-pointer fact a card
already cites. This script's job is mechanical, not editorial - it re-derives
the ledger bytes from retained source bytes and asserts every field against
them, so `evidence-ledger.json` is never hand-edited even when the edit would
be factually right (ed3c/ai-content-notes wave22 monitor finding: a ledger
with no committed generator can only be hand-edited the next time a cited
source changes).

Run with `--check` to verify the committed ledger still matches what these
tables produce against the current retained bytes; run without it to
regenerate the file after a table entry or a retained source changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Sequence

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTENT_ID = "CvRngaQZQ3Y"
SUBJECT_DIR = ROOT / "evals" / "semantic-yield" / CONTENT_ID
SOURCE_DIR = ROOT / "sources" / CONTENT_ID

TRANSCRIPT = SOURCE_DIR / "broker" / "captions.normalized.en.json"
MANIFEST = SOURCE_DIR / "source-manifest.json"
NORMREPORT = SOURCE_DIR / "broker" / "normalization-report.json"

TRANSCRIPT_SOURCE = "youtube:cvrngaqzq3y:youtube-transcript-ai"
MANIFEST_SOURCE = "artifact:cvrngaqzq3y:source-manifest"
NORMREPORT_SOURCE = "artifact:cvrngaqzq3y:normalization-report"

DEFAULT_OUTPUT = SUBJECT_DIR / "evidence-ledger.json"


class LedgerError(RuntimeError):
    """Raised when a curated evidence entry does not match retained bytes."""


# entry suffix -> (start_label, end_label, verbatim, context, supports)
QUOTE_SPANS: dict[str, tuple[str, str, str, str, list[str]]] = {
    "stage-ship": (
        "00:00:44",
        "00:01:17",
        "the first step in building a successful agent is shipping it",
        "Recipe step 1 of the four-stage improvement loop.",
        ["D-four-stage-trace-loop"],
    ),
    "stage-collect": (
        "00:01:17",
        "00:01:47",
        "The second step is collect a ton of traces.",
        "Recipe step 2: every tool call, output message, API and CLI call is stored.",
        ["D-four-stage-trace-loop"],
    ),
    "stage-mine-experiment": (
        "00:01:47",
        "00:02:17",
        "we're going to do data mining over that",
        "Recipe steps 3 and 4: mine the stored traces, then run data-driven experiments.",
        ["D-four-stage-trace-loop"],
    ),
    "observability-learning": (
        "00:02:17",
        "00:03:17",
        "there's a very tight coupling between what observability is and what continual learning is",
        "The speaker's stated link between trace observability and continual learning.",
        ["N-autonomy-trace-mining"],
    ),
    "trace-questions": (
        "00:04:48",
        "00:05:50",
        "Does the agent get really dumb after the first compaction?",
        "One of the decision questions the speaker sends agents into traces to answer.",
        ["N-autonomy-trace-mining"],
    ),
    "trace-scale": (
        "00:06:21",
        "00:07:22",
        "reading traces at scale is super expensive",
        "The first of the two scale problems; the second is that a long trace does not fit in another agent's context.",
        ["D-trace-scale-bottleneck", "N-autonomy-trace-mining"],
    ),
    "model-cost-path": (
        "00:07:53",
        "00:10:25",
        "we start with Opus",
        "The stated cost path: strongest model first, then look back at traces for a cheaper open model.",
        ["T-trace-judge-comparison"],
    ),
    "open-model-cost-claim": (
        "00:08:25",
        "00:08:55",
        "the answer is roughly yes at like an order or like two orders of magnitude cheaper",
        "The only cost magnitude the source states; it carries no absolute figure, which is why the comparison card keeps UNKNOWN cells.",
        ["T-trace-judge-comparison"],
    ),
    "harness-ceiling": (
        "00:08:55",
        "00:09:55",
        "you hit a threshold of intelligence",
        "The harness-engineering ceiling that motivates fine-tuning.",
        ["S-harness-finetune-harness"],
    ),
    "fit-concept": (
        "00:12:57",
        "00:14:28",
        "the way that they apply is what I like to call model harness task fit",
        "The source names the fit function over model, harness and task.",
        ["C-model-harness-task-fit"],
    ),
    "auto-research-risk": (
        "00:14:28",
        "00:14:58",
        "They might cheat a little bit and you need to like check them on some stuff.",
        "The stated failure mode of score-maximising auto research.",
        ["C-model-harness-task-fit"],
    ),
    "sandwich": (
        "00:15:58",
        "00:16:59",
        "try harness engineering, try to do fine-tuning to sort of like break through that ceiling, and then do more harness engineering again if you need to",
        "The sandwich sequence the strategy card renders.",
        ["S-harness-finetune-harness"],
    ),
    "three-state-planes": (
        "00:16:59",
        "00:18:30",
        "you're going to have to do it across all three axes",
        "Training data, harness updates and memory are the three planes the concept card names.",
        ["C-continual-learning-state-planes"],
    ),
    "memory-not-append-only": (
        "00:17:59",
        "00:19:00",
        "we are not append-only logs of information",
        "The memory constraint that separates the memory plane from trace storage.",
        ["C-continual-learning-state-planes"],
    ),
}

# entry suffix -> (source_id, json_pointer, verbatim, source_type, context, supports)
POINTER_FACTS: dict[str, tuple[str, str, object, str, str, list[str]]] = {
    "source-manifest": (
        MANIFEST_SOURCE,
        "/completeness/status",
        "needs-review",
        "dataset",
        "The retained-subject manifest declares the acquisition unreviewed, which is why identifier and frame identity stay unavailable.",
        ["K-visual-identifier-evidence-gap"],
    ),
    "normalization-report": (
        NORMREPORT_SOURCE,
        "/rules/5",
        "no proper-noun, punctuation, grammar, or semantic correction",
        "log",
        "Normalization removed provable duplication and transport metadata only; it did not repair vocabulary.",
        ["K-visual-identifier-evidence-gap"],
    ),
}


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def span_text(cues: list[dict], start: str, end: str) -> str:
    starts = [n for n, cue in enumerate(cues) if cue["start_label"] == start]
    ends = [n for n, cue in enumerate(cues) if cue["end_label"] == end]
    if not starts or not ends:
        raise LedgerError(f"span label not found in retained cues: {start}..{end}")
    if starts[0] > ends[0]:
        raise LedgerError(f"span end precedes start: {start}..{end}")
    return collapse(" ".join(cue["normalized_text"] for cue in cues[starts[0] : ends[0] + 1]))


def resolve_pointer(doc: object, pointer: str) -> object:
    node = doc
    for part in pointer.strip("/").split("/"):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def build_evidence() -> dict[str, dict]:
    cues = load_json(TRANSCRIPT)["cues"]
    manifest_doc = load_json(MANIFEST)
    normreport_doc = load_json(NORMREPORT)
    docs_by_source = {MANIFEST_SOURCE: manifest_doc, NORMREPORT_SOURCE: normreport_doc}

    evidence: dict[str, dict] = {}

    for suffix, (start, end, verbatim, context, supports) in QUOTE_SPANS.items():
        text = span_text(cues, start, end)
        if collapse(verbatim) not in text:
            raise LedgerError(f"verbatim not found in retained span: {suffix}")
        evidence[f"EV-cvrngaqzq3y-{suffix}"] = {
            "evidence_id": f"EV-cvrngaqzq3y-{suffix}",
            "source_id": TRANSCRIPT_SOURCE,
            "source_type": "transcript",
            "locator": f"timestamp:{start}..{end}",
            "evidence_kind": "quote",
            "verbatim": verbatim,
            "context": context,
            "supports": supports,
            "challenges": [],
            "secondary": True,
        }

    for suffix, (source_id, pointer, verbatim, source_type, context, supports) in POINTER_FACTS.items():
        node = resolve_pointer(docs_by_source[source_id], pointer)
        if node != verbatim:
            raise LedgerError(f"pointer value mismatch: {suffix}: {node!r} != {verbatim!r}")
        evidence[f"EV-cvrngaqzq3y-{suffix}"] = {
            "evidence_id": f"EV-cvrngaqzq3y-{suffix}",
            "source_id": source_id,
            "source_type": source_type,
            "locator": f"json-pointer:{pointer}",
            "evidence_kind": "datum",
            "verbatim": verbatim,
            "context": context,
            "supports": supports,
            "challenges": [],
            "secondary": False,
        }

    return evidence


def check_card_references(evidence: dict[str, dict]) -> None:
    """Every card reference must resolve to an entry, and every entry must be cited."""
    referenced: dict[str, set[str]] = {}
    for card in sorted((SUBJECT_DIR / "cards").glob("*.md")):
        for ref in set(re.findall(r"\[\[(EV-[A-Za-z0-9._:-]+)\]\]", card.read_text(encoding="utf-8"))):
            referenced.setdefault(ref, set()).add(card.stem)
    if set(referenced) != set(evidence):
        raise LedgerError(f"card references and ledger entries disagree: {set(referenced) ^ set(evidence)}")
    for evidence_id, entry in evidence.items():
        if set(entry["supports"]) != referenced[evidence_id]:
            raise LedgerError(
                f"{evidence_id}: supports {entry['supports']} does not match citing cards {sorted(referenced[evidence_id])}"
            )


def check_entry_schema(evidence: dict[str, dict]) -> None:
    registry_schema = load_json(ROOT / "schemas" / "card-registry.schema.json")
    entry_schema = dict(registry_schema["$defs"]["evidenceEntry"])
    validator = Draft202012Validator(entry_schema)
    for entry in evidence.values():
        validator.validate(entry)
    id_pattern = re.compile(registry_schema["properties"]["evidence"]["propertyNames"]["pattern"])
    for evidence_id in evidence:
        if not id_pattern.fullmatch(evidence_id):
            raise LedgerError(f"evidence id does not satisfy the registry's id pattern: {evidence_id}")


def build_ledger() -> dict:
    evidence = build_evidence()
    check_card_references(evidence)
    check_entry_schema(evidence)
    card_manifest = load_json(SUBJECT_DIR / "card-manifest.json")
    return {
        "schema_version": "semantic-evidence-ledger@1",
        "content_id": CONTENT_ID,
        "source_dependency_key": f"youtube-video:{CONTENT_ID}",
        "entry_contract": "schemas/card-registry.schema.json#/$defs/evidenceEntry",
        "sources": {
            TRANSCRIPT_SOURCE: {
                "anchor_kind": "TRANSCRIPT_TIMESTAMP",
                "declared_source_id": card_manifest["source"]["source_id"],
                "path": str(TRANSCRIPT.relative_to(ROOT)),
                "sha256": sha256_file(TRANSCRIPT),
            },
            MANIFEST_SOURCE: {
                "anchor_kind": "ARTIFACT_STATE",
                "path": str(MANIFEST.relative_to(ROOT)),
                "sha256": sha256_file(MANIFEST),
            },
            NORMREPORT_SOURCE: {
                "anchor_kind": "ARTIFACT_STATE",
                "path": str(NORMREPORT.relative_to(ROOT)),
                "sha256": sha256_file(NORMREPORT),
            },
        },
        "evidence": evidence,
    }


def render(ledger: dict) -> str:
    return json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the output file already matches the regenerated bytes; write nothing",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rendered = render(build_ledger())
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"LEDGER_DRIFT: {args.output} does not match the tables in this script")
            return 1
        print(f"LEDGER_CURRENT: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output} entries={len(json.loads(rendered)['evidence'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
