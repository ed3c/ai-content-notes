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
    path = ROOT / "tools" / "youtube_transcript_ai_adapter.py"
    spec = importlib.util.spec_from_file_location(
        "youtube_transcript_ai_adapter", path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sample_response() -> str:
    return """# Transcript: Sample agent systems interview

Source video: https://www.youtube.com/watch?v=CvRngaQZQ3Y
Language: English · Duration: 1:05 · Words: 12
Other available languages: Chinese (Traditional)

## Transcript

[0:00] First exact phrase with API-V2.

[0:05] Second phrase with 41% and CASE-001.

[1:02] Final phrase.
"""


def test_parse_broker_response_preserves_headers_timestamps_and_tokens() -> None:
    adapter = load_adapter()
    parsed = adapter.parse_broker_response(sample_response(), "CvRngaQZQ3Y")
    assert parsed.title == "Sample agent systems interview"
    assert parsed.language == "English"
    assert parsed.duration_seconds == 65
    assert parsed.declared_word_count == 12
    assert len(parsed.cues) == 3
    assert parsed.cues[0].start_label == "00:00:00"
    assert parsed.cues[0].end_label == "00:00:05"
    assert parsed.cues[1].text == "Second phrase with 41% and CASE-001."
    assert parsed.cues[-1].end_label == "00:01:05"


def test_parse_broker_response_rejects_source_video_mismatch() -> None:
    adapter = load_adapter()
    with pytest.raises(adapter.BrokerTranscriptError, match="source mismatch"):
        adapter.parse_broker_response(sample_response(), "dQw4w9WgXcQ")


def test_parse_broker_response_rejects_non_monotonic_timestamps() -> None:
    adapter = load_adapter()
    response = """# Transcript: Bad order
Source video: https://www.youtube.com/watch?v=CvRngaQZQ3Y
Language: English · Duration: 0:30 · Words: 4

[0:20] Later.
[0:10] Earlier.
"""
    with pytest.raises(adapter.BrokerTranscriptError, match="non-monotonic"):
        adapter.parse_broker_response(response, "CvRngaQZQ3Y")


def test_unverified_base_manifest_is_schema_valid_and_non_authoritative() -> None:
    adapter = load_adapter()
    args = argparse.Namespace(
        authorization_status="unverified-evaluation-only",
        rights_basis="user-directed-evaluation",
        rights_reference="chat-request:test",
        attested_by="tester",
    )
    manifest = adapter.base_manifest(args, "CvRngaQZQ3Y", "2026-08-13T00:00:00Z")
    schema = json.loads(
        (ROOT / "schemas" / "youtube-transcript-ai-evidence.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator.check_schema(schema)
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            manifest
        )
    )
    assert errors == []
    assert manifest["transport"]["authentication_used"] is False
    assert manifest["transport"]["cookies_supplied"] is False
    assert manifest["transport"]["proxy_supplied"] is False
    assert manifest["transport"]["audio_requested"] is False
    assert manifest["authority"]["may_complete_note"] is False
    assert (
        manifest["authority"]["may_count_as_independent_corroboration"]
        is False
    )


def test_unverified_evaluation_cannot_claim_verified_rights() -> None:
    adapter = load_adapter()
    args = argparse.Namespace(
        authorization_status="unverified-evaluation-only",
        rights_basis="licensed",
        rights_reference="reference",
        attested_by="tester",
    )
    with pytest.raises(adapter.BrokerTranscriptError, match="user-directed-evaluation"):
        adapter.validate_authorization(args)


def test_url_parser_rejects_playlist() -> None:
    adapter = load_adapter()
    with pytest.raises(adapter.BrokerTranscriptError, match="playlist"):
        adapter.youtube_video_id(
            "https://www.youtube.com/watch?v=CvRngaQZQ3Y&list=PL123"
        )
