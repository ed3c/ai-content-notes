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


def load_tool() -> ModuleType:
    path = ROOT / "tools/youtube_transcript.py"
    spec = importlib.util.spec_from_file_location("youtube_transcript", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_schema() -> dict[str, object]:
    return json.loads(
        (ROOT / "schemas/youtube-transcript-manifest.schema.json").read_text(
            encoding="utf-8"
        )
    )


def test_schema_is_valid_draft_2020_12() -> None:
    Draft202012Validator.check_schema(load_schema())


def test_video_id_accepts_single_video_and_rejects_playlist() -> None:
    tool = load_tool()
    assert tool.youtube_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert tool.youtube_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    with pytest.raises(tool.TranscriptError, match="playlist"):
        tool.youtube_video_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL123456"
        )


def test_parse_webvtt_preserves_raw_text_and_stitches_rolling_caption() -> None:
    tool = load_tool()
    cues = tool.parse_webvtt(
        """WEBVTT

00:00:00.000 --> 00:00:01.000
<v Speaker>Build an MCP</v>

00:00:00.800 --> 00:00:02.000 align:start position:0%
Build an MCP gateway

00:00:02.000 --> 00:00:03.000
with OAuth &amp; tests
"""
    )
    assert [cue.text for cue in cues] == [
        "Build an MCP",
        "Build an MCP gateway",
        "with OAuth & tests",
    ]
    assert [cue.normalized_text for cue in cues] == [
        "Build an MCP",
        "gateway",
        "with OAuth & tests",
    ]
    assert cues[1].start == pytest.approx(0.8)
    assert cues[1].end == pytest.approx(2.0)


def test_caption_selection_prefers_manual_and_language_order() -> None:
    tool = load_tool()
    metadata = {
        "subtitles": {"en": [{}], "zh-Hant": [{}]},
        "automatic_captions": {"en": [{}], "ja": [{}]},
    }
    assert tool.select_caption_track(metadata, ["zh-Hant", "en"]) == (
        "manual",
        "zh-Hant",
    )


def test_caption_selection_uses_automatic_only_after_manual_exhausted() -> None:
    tool = load_tool()
    metadata = {
        "subtitles": {"fr": [{}]},
        "automatic_captions": {"en-US": [{}]},
    }
    assert tool.select_caption_track(metadata, ["en"]) == ("automatic", "en-US")


def test_validation_detects_non_monotonic_cues() -> None:
    tool = load_tool()
    cues = [
        tool.Cue(2.0, 3.0, "second", "second"),
        tool.Cue(1.0, 2.0, "first", "first"),
    ]
    result = tool.validate_cues(cues, 10.0)
    assert result["timestamps_monotonic"] is False
    assert "cue timestamps are not monotonic" in result["warnings"]


def test_rights_gate_requires_reference_and_explicit_audio_permission() -> None:
    tool = load_tool()
    args = argparse.Namespace(
        rights_basis="owned",
        rights_reference="",
        attested_by="ed3c",
        mode="captions",
        allow_audio_download=False,
        asr_model_revision=tool.DEFAULT_ASR_MODEL_REVISION,
    )
    with pytest.raises(tool.TranscriptError, match="rights-reference"):
        tool.ensure_rights(args)

    args.rights_reference = "channel-owner-record"
    args.mode = "asr"
    with pytest.raises(tool.TranscriptError, match="allow-audio-download"):
        tool.ensure_rights(args)

    args.allow_audio_download = True
    args.asr_model_revision = "main"
    with pytest.raises(tool.TranscriptError, match="40-character"):
        tool.ensure_rights(args)


def test_manifest_is_body_free_and_authority_fail_closed(tmp_path: Path) -> None:
    tool = load_tool()
    args = argparse.Namespace(
        rights_basis="creator-permission",
        rights_reference="permission-ticket-42",
        attested_by="ed3c",
        mode="captions",
    )
    manifest = tool.base_manifest(args, "dQw4w9WgXcQ", "2026-08-12T00:00:00Z")
    encoded = json.dumps(manifest, ensure_ascii=False)
    assert "transcript_text" not in encoded
    assert manifest["authority"] == {
        "may_complete_note": False,
        "may_raise_claim_evidence": False,
        "may_enable_skill_routing": False,
    }

    errors = list(
        Draft202012Validator(
            load_schema(), format_checker=FormatChecker()
        ).iter_errors(manifest)
    )
    assert errors == []


def test_transcript_artifacts_are_digest_bound(tmp_path: Path) -> None:
    tool = load_tool()
    cues = [tool.Cue(0.0, 1.0, "Hello world", "Hello world")]
    artifacts = tool.write_transcript_artifacts(
        tmp_path,
        cues,
        [],
        video_id="dQw4w9WgXcQ",
        canonical_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )
    assert set(artifacts) == {"transcript_json", "transcript_text"}
    assert (tmp_path / "transcript.json").exists()
    assert (tmp_path / "transcript.txt").read_text(encoding="utf-8").startswith(
        "[00:00:00.000 --> 00:00:01.000] Hello world"
    )
    for artifact in artifacts.values():
        assert len(artifact["sha256"]) == 64


def _args(tool: ModuleType, tmp_path: Path, *, mode: str = "captions") -> argparse.Namespace:
    return argparse.Namespace(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        output_dir=str(tmp_path),
        mode=mode,
        languages="en,zh-Hant",
        rights_basis="owned",
        rights_reference="channel-owner-record",
        attested_by="ed3c",
        allow_audio_download=mode in {"asr", "auto"},
        keep_audio=False,
        asr_model="large-v3",
        asr_model_revision=tool.DEFAULT_ASR_MODEL_REVISION,
        asr_language="auto",
        asr_device="cuda",
        asr_compute_type="float16",
        glossary=None,
    )


def test_acquire_caption_candidate_is_schema_valid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load_tool()
    args = _args(tool, tmp_path)
    metadata = {
        "id": "dQw4w9WgXcQ",
        "title": "Authorized sample",
        "channel": "Owner channel",
        "channel_id": "UC123",
        "duration": 4,
        "upload_date": "20260812",
        "subtitles": {"en": [{"ext": "vtt"}]},
        "automatic_captions": {},
    }
    monkeypatch.setattr(tool, "fetch_metadata", lambda _: metadata)

    def fake_download(
        _url: str, video_id: str, _kind: str, language: str, raw_dir: Path
    ) -> Path:
        raw_dir.mkdir(parents=True, exist_ok=True)
        path = raw_dir / f"{video_id}.{language}.vtt"
        path.write_text(
            "WEBVTT\n\n00:00:00.000 --> 00:00:03.500\nAuthorized transcript\n",
            encoding="utf-8",
        )
        return path

    monkeypatch.setattr(tool, "download_caption", fake_download)
    manifest, code = tool.acquire(args)
    assert code == 0
    assert manifest["status"] == "needs-review"
    assert manifest["validation"]["quality_grade"] == "manual-caption"
    assert manifest["authority"]["may_complete_note"] is False
    errors = list(
        Draft202012Validator(
            load_schema(), format_checker=FormatChecker()
        ).iter_errors(manifest)
    )
    assert errors == []


def test_acquire_without_caption_materializes_blocked_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load_tool()
    args = _args(tool, tmp_path)
    metadata = {
        "id": "dQw4w9WgXcQ",
        "title": "No captions",
        "duration": 60,
        "subtitles": {},
        "automatic_captions": {},
    }
    monkeypatch.setattr(tool, "fetch_metadata", lambda _: metadata)
    manifest, code = tool.acquire(args)
    assert code == 2
    assert manifest["status"] == "blocked"
    assert "no manual or automatic caption" in manifest["error"]["message"]
    persisted = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert persisted["status"] == "blocked"
    errors = list(
        Draft202012Validator(
            load_schema(), format_checker=FormatChecker()
        ).iter_errors(persisted)
    )
    assert errors == []
