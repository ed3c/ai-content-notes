from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load_adapter() -> ModuleType:
    path = ROOT / "tools" / "youtube_direct_caption_adapter.py"
    spec = importlib.util.spec_from_file_location("youtube_direct_caption_adapter", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass
class FakeTranscript:
    language_code: str
    language: str
    is_generated: bool


@dataclass
class FakeSnippet:
    text: str
    start: float
    duration: float


def test_select_transcript_prefers_manual_then_language_order() -> None:
    adapter = load_adapter()
    transcripts = [
        FakeTranscript("en", "English", True),
        FakeTranscript("zh-TW", "Chinese (Taiwan)", False),
        FakeTranscript("en", "English", False),
    ]
    selected, outside = adapter.select_transcript(transcripts, ["en", "zh-TW"])
    assert selected.language_code == "en"
    assert selected.is_generated is False
    assert outside is False


def test_select_transcript_uses_available_track_without_translation() -> None:
    adapter = load_adapter()
    selected, outside = adapter.select_transcript(
        [FakeTranscript("ko", "Korean", True)], ["en", "zh-TW"]
    )
    assert selected.language_code == "ko"
    assert selected.is_generated is True
    assert outside is True


def test_build_cues_preserves_fractional_timing_and_exact_tokens() -> None:
    adapter = load_adapter()
    cues = adapter.build_cues(
        [
            FakeSnippet("API-V2 is 41% faster.", 1.234, 2.5),
            FakeSnippet("CASE-001", 3.734, 0.5),
        ]
    )
    assert cues[0].start_label == "00:00:01.234"
    assert cues[0].end_label == "00:00:03.734"
    assert cues[0].text == "API-V2 is 41% faster."
    assert cues[1].text == "CASE-001"


def test_build_cues_rejects_non_monotonic_timestamps() -> None:
    adapter = load_adapter()
    with pytest.raises(adapter.DirectCaptionError, match="non-monotonic"):
        adapter.build_cues(
            [
                FakeSnippet("later", 5.0, 1.0),
                FakeSnippet("earlier", 4.0, 1.0),
            ]
        )


def test_unverified_manifest_is_schema_valid_and_non_authoritative() -> None:
    adapter = load_adapter()
    args = argparse.Namespace(
        authorization_status="unverified-evaluation-only",
        rights_basis="user-directed-evaluation",
        rights_reference="chat-request:test",
        attested_by="tester",
        languages="en,zh-TW",
    )
    manifest = adapter.base_manifest(args, "CvRngaQZQ3Y", "2026-08-13T00:00:00Z")
    schema = json.loads(
        (ROOT / "schemas" / "youtube-direct-caption-evidence.schema.json").read_text(
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
    assert manifest["acquisition"]["cookies_used"] is False
    assert manifest["acquisition"]["proxy_used"] is False
    assert manifest["acquisition"]["audio_used"] is False
    assert manifest["authority"]["may_complete_note"] is False


def test_url_parser_rejects_playlist() -> None:
    adapter = load_adapter()
    with pytest.raises(adapter.DirectCaptionError, match="playlist"):
        adapter.youtube_video_id(
            "https://www.youtube.com/watch?v=CvRngaQZQ3Y&list=PL123"
        )
