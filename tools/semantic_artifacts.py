"""Extract deterministic semantic-yield coverage sets from runtime artifacts."""

from __future__ import annotations

from typing import Any

ACCOUNTED_VISUAL_STATES = {
    "RENDERED",
    "CARD_MAPPED",
    "DEFERRED",
    "BLOCKED_WITH_K_CARD",
}


def relation_ids(graph: dict[str, Any]) -> set[str]:
    return {item["relation_id"] for item in graph.get("relations", [])}


def projection_kinds(bundle: dict[str, Any]) -> set[str]:
    return {item["projection_kind"] for item in bundle.get("projections", [])}


def question_tags(bundle: dict[str, Any]) -> set[str]:
    return {
        tag
        for item in bundle.get("projections", [])
        for tag in item.get("question_tags", [])
    }


def projection_ids(bundle: dict[str, Any]) -> set[str]:
    return {item["projection_id"] for item in bundle.get("projections", [])}


def accounted_visual_ids(ledger: dict[str, Any]) -> set[str]:
    return {
        item["visual_id"]
        for item in ledger.get("items", [])
        if item.get("disposition") in ACCOUNTED_VISUAL_STATES
    }


def rendered_visual_ids(ledger: dict[str, Any]) -> set[str]:
    return {
        item["visual_id"]
        for item in ledger.get("items", [])
        if item.get("disposition") == "RENDERED"
    }


def mapped_knowledge_units(manifest: dict[str, Any]) -> set[str]:
    accepted = {"CARD_MAPPED", "PROJECTION_MAPPED"}
    return {
        item["knowledge_unit_id"]
        for item in manifest.get("items", [])
        if item.get("disposition") in accepted
    }
