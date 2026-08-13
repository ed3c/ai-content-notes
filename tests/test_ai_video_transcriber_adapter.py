from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load_adapter() -> ModuleType:
    path = ROOT / "tools" / "ai_video_transcriber_adapter.py"
    spec = importlib.util.spec_from_file_location("ai_video_transcriber_adapter", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_upstream_markdown_preserves_rendered_timestamps_and_text() -> None:
    adapter = load_adapter()
    text = """# Video Transcription

**Detected Language:** en

## Transcription Content

**[00:07 - 00:10]**

First exact phrase.

**[01:02 - 01:05]**

Second phrase with API-V2 and 41%.
"""
    cues = adapter.parse_upstream_markdown(text)
    assert len(cues) == 2
    assert cues[0].start_label == "00:00:07"
    assert cues[1].start_label == "00:01:02"
    assert cues[1].text == "Second phrase with API-V2 and 41%."


def test_parse_upstream_markdown_rejects_non_monotonic_timestamps() -> None:
    adapter = load_adapter()
    text = """**[00:10 - 00:12]**
First.

**[00:05 - 00:07]**
Second.
"""
    with pytest.raises(adapter.AdapterError, match="non-monotonic"):
        adapter.parse_upstream_markdown(text)


def test_unverified_evaluation_cannot_claim_verified_rights() -> None:
    adapter = load_adapter()
    args = argparse.Namespace(
        authorization_status="unverified-evaluation-only",
        rights_basis="licensed",
        rights_reference="reference",
        attested_by="tester",
    )
    with pytest.raises(adapter.AdapterError, match="user-directed-evaluation"):
        adapter.validate_authorization(args)


def test_adapter_manifest_template_is_schema_valid() -> None:
    adapter = load_adapter()
    args = argparse.Namespace(
        authorization_status="unverified-evaluation-only",
        rights_basis="user-directed-evaluation",
        rights_reference="chat-request:test",
        attested_by="tester",
        languages="en,zh",
    )
    manifest = adapter.base_manifest(args, "CvRngaQZQ3Y", "2026-08-13T00:00:00Z")
    schema = json.loads(
        (ROOT / "schemas" / "ai-video-transcriber-evidence.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator.check_schema(schema)
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest)
    )
    assert errors == []
    assert manifest["authority"]["may_complete_note"] is False
    assert manifest["authorization"]["status"] == "unverified-evaluation-only"


def test_video_url_rejects_playlist_parameter() -> None:
    adapter = load_adapter()
    with pytest.raises(adapter.AdapterError, match="playlist"):
        adapter.youtube_video_id(
            "https://www.youtube.com/watch?v=CvRngaQZQ3Y&list=PL123"
        )
