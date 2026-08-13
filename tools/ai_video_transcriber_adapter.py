#!/usr/bin/env python3
"""Acquire review-only YouTube caption evidence through AI-Video-Transcriber.

The pinned upstream project performs subtitle discovery and parsing. This adapter
verifies the checkout, preserves the returned Markdown, binds evidence digests,
and emits v7.1 source-manifest input. It never enables audio fallback, cookies,
proxies, browser sessions, or note-completion authority.
"""

from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path
from typing import Any, Sequence

from ai_video_transcriber_contract import (
    AUTHORIZATION_STATUSES,
    DEFAULT_UPSTREAM_COMMIT,
    AdapterError,
    base_manifest,
    build_source_manifest,
    build_validation,
    canonical_video_url,
    caption_kind,
    artifact_entry,
    parse_upstream_markdown,
    published_date,
    utc_now,
    validate_authorization,
    write_json,
    write_transcript_artifacts,
    youtube_video_id,
)
from ai_video_transcriber_upstream import (
    fetch_metadata_async,
    fetch_upstream_subtitles,
    verify_upstream,
)

__all__ = [
    "AdapterError",
    "base_manifest",
    "parse_upstream_markdown",
    "validate_authorization",
    "youtube_video_id",
]


async def acquire(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    validate_authorization(args)
    video_id = youtube_video_id(args.url)
    canonical_url = canonical_video_url(video_id)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    created_at = utc_now()
    manifest = base_manifest(args, video_id, created_at)
    manifest_path = output_dir / "manifest.json"

    try:
        existing = [path for path in output_dir.iterdir() if path.name != "manifest.json"]
        if existing:
            raise AdapterError("output directory must be empty for an atomic acquisition")
        upstream_root = Path(args.upstream_root).resolve()
        prompt_path = Path(args.prompt_path).resolve()
        if not prompt_path.is_file():
            raise AdapterError("v7.1 prompt path does not exist")
        manifest["upstream"] = verify_upstream(upstream_root, args.upstream_commit)
        metadata = await fetch_metadata_async(canonical_url)
        if metadata.get("id") and metadata["id"] != video_id:
            raise AdapterError("resolved video ID does not match requested URL")
        upstream_markdown, title, language = await fetch_upstream_subtitles(
            upstream_root, canonical_url, output_dir / "upstream-work"
        )
        cues = parse_upstream_markdown(upstream_markdown)
        duration = float(metadata["duration"]) if metadata.get("duration") is not None else None
        kind = caption_kind(metadata, language)
        artifacts = write_transcript_artifacts(
            output_dir,
            upstream_markdown=upstream_markdown,
            cues=cues,
            video_id=video_id,
            canonical_url=canonical_url,
        )
        source_manifest = build_source_manifest(
            output_dir=output_dir,
            video_id=video_id,
            caption_type=kind,
            upstream_commit=args.upstream_commit,
            cues=cues,
            artifacts=artifacts,
            prompt_path=prompt_path,
            created_at=created_at,
            authorization_status=args.authorization_status,
        )
        source_manifest_path = output_dir / "source-manifest.json"
        artifacts["source_manifest"] = artifact_entry(source_manifest_path, output_diŠBˆX[šY™\İÈšY[È—K\]JˆÂˆ]Hˆ]HÜˆY]Y]K™Ù]
]HŠKˆ˜Ú[›™[ˆY]Y]K™Ù]
˜Ú[›™[ŠHÜˆY]Y]K™Ù]
\ØY\ˆŠKˆ˜Ú[›™[ÚYˆY]Y]K™Ù]
˜Ú[›™[ÚYŠHÜˆY]Y]K™Ù]
\ØY\—ÚYŠKˆ™\˜][Û—ÜÙXÛÛ™Èˆ\˜][Û‹ˆœX›\ÚYØ]ˆX›\ÚYÙ]JY]Y]JKˆBˆ
BˆX[šY™\İÈ˜XÜ]Z\Ú][Ûˆ—K\]JÈ˜Ø\[Û—ÚÚ[™ˆÚ[™›[™İXYÙHˆ[™İXYÙ_JBˆX[šY™\İÈ˜[Y][Ûˆ—HHZ[İ˜[Y][ÛŠİY\Ë\˜][ÛŠBˆYˆ[™İXYÙH[™[™İXYÙH›İ[ˆX[šY™\İÈ˜XÜ]Z\Ú][Ûˆ—VÈœ™\]Y\İYÛ[™İXYÙ\È—N‚ˆX[šY™\İÈ˜[Y][Ûˆ—VÈØ\›š[™ÜÈ—K˜\[™
ˆ\İ™X[H[™İXYÙHš[Üš]HÙ[XİYH˜XÚÈİ]ÚYHH™\]Y\İY\İ‚ˆ
BˆYˆ\™ÜË˜]]Üš^˜][Û—Üİ]\ÈOH™\šYšYY‚ˆX[šY™\İÈ˜[Y][Ûˆ—VÈØ\›š[™ÜÈ—K˜\[™
ˆ˜]]Üš^˜][Ûˆ\È[™\šYšYYY]˜[X][Û‹[Û›NÈÈ›İX\šÈH›İHÛÛ\]Y‚ˆ
BˆX[šY™\İÈ˜\Y˜XİÈ—HH\Y˜XİÂˆX[šY™\İÈœİ]\È—HH›™YYË\™]šY]È‚ˆX[šY™\İÈ™\œ›Üˆ—HH›Û™BˆX[šY™\İÈœÛİ\˜ÙWÛX[šY™\İÙYÙ\İ—HHˆœÚLMØ\Y˜XİÖÉÜÛİ\˜ÙWÛX[šY™\İ	×VÉÜÚLM‰×_H‚ˆX[šY™\İÈœÛİ\˜ÙWÛX[šY™\İÚY—HHÛİ\˜ÙWÛX[šY™\İÈ›X[šY™\İÚY—BˆÜš]WÚœÛÛŠX[šY™\İÜ]X[šY™\İ
Bˆ™]\›ˆX[šY™\İˆ^Ù\^Ù\[Ûˆ\È^ÎˆÈ›ÜXNˆ“LHHÛÛ™\[[YH˜Z[\™\ÈÈ›ØÚÙY]šY[˜ÙBˆX[šY™\İÈœİ]\È—HH˜›ØÚÙY‚ˆX[šY™\İÈ™\œ›Üˆ—HHÂˆ\Hˆ\J^ÊK—×Û˜[YW×Ëˆ›Y\ÜØYÙHˆ™KœİXŠˆ—ÊÈ‹ˆ‹İŠ^ÊJKœİš\

VÎŒŒKˆBˆX[šY™\İÈ˜[Y][Ûˆ—VÈØ\›š[™ÜÈ—HHÂˆ˜XÜ]Z\Ú][Ûˆ˜Z[YÛÜÙYÈÈ›İÛÛ\[HHÛÛ\]Y›İHœ›ÛH\È[ˆ‚ˆBˆÜš]WÚœÛÛŠX[šY™\İÜ]X[šY™\İ
Bˆ™]\›ˆX[šY™\İ‚‚‚™YˆZ[Ü\œÙ\Š
HOˆ\™Ü\œÙK\™İ[Y[\œÙ\‚ˆ\œÙ\ˆH\™Ü\œÙK\™İ[Y[\œÙ\Š\ØÜš\[ÛW×ÙØ××ÊBˆ\œÙ\‹˜YØ\™İ[Y[
‹K]\›‹™\]Z\™YUYJBˆ\œÙ\‹˜YØ\™İ[Y[
‹K[İ]]Y\ˆ‹™\]Z\™YUYJBˆ\œÙ\‹˜YØ\™İ[Y[
‹K]\İ™X[K\›Ûİ‹™\]Z\™YUYJBˆ\œÙ\‹˜YØ\™İ[Y[
‹K]\İ™X[KXÛÛ[Z]‹Y˜][QQUSÕTÕ‘PSWĞÓÓSRU
Bˆ\œÙ\‹˜YØ\™İ[Y[
‹K\›Û\\]‹™\]Z\™YUYJBˆ\œÙ\‹˜YØ\™İ[Y[
‹K[[™İXYÙ\È‹Y˜][H™[‹šR[šUËš˜HŠBˆ\œÙ\‹˜YØ\™İ[Y[
ˆ‹KX]]Üš^˜][Û‹\İ]\È‹ˆÚÚXÙ\Ï\ÛÜY
UUÔ’VUSÓ—ÔÕUTÑTÊKˆ™\]Z\™YUYKˆ
Bˆ\œÙ\‹˜YØ\™İ[Y[
‹K\šYÚËX˜\Ú\È‹™\]Z\™YUYJBˆ\œÙ\‹˜YØ\™İ[Y[
‹K\šYÚË\™Y™\™[˜ÙH‹™\]Z\™YUYJBˆ\œÙ\‹˜YØ\™İ[Y[
‹KX]\İYXH‹™\]Z\™YUYJBˆ™]\›ˆ\œÙ\‚‚‚™YˆXZ[Š\™İˆÙ\]Y[˜ÙVÜİ—H›Û™HH›Û™JHOˆ[‚ˆ\™ÜÈHZ[Ü\œÙ\Š
Kœ\œÙWØ\™ÜÊ\™İŠBˆË™]\›—ØÛÙHH\Ş[˜Ú[Ëœ[ŠXÜ]Z\™J\™ÜÊJBˆ™]\›ˆ™]\›—ØÛÙB‚‚šYˆ×Û˜[YW×ÈOH—×ÛXZ[—×È‚ˆ˜Z\ÙHŞ\İ[Q^]
XZ[Š
JB