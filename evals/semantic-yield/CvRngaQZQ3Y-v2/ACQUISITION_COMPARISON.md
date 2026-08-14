# Acquisition transport comparison｜取材路徑比較

Same video, five transports, one origin.
`https://www.youtube.com/watch?v=CvRngaQZQ3Y` · 1201 s · AI Engineer channel.

Machine-readable result: [`acquisition-comparison.json`](acquisition-comparison.json).
All three acquired subjects are retained under [`sources/CvRngaQZQ3Y/`](../../../sources/CvRngaQZQ3Y/)
and bound by `source-manifest.json`.

## What ran, and what refused

| Transport | Backend | Status |
|---|---|---|
| `youtube-transcript-api` | `jdepoix/youtube-transcript-api@1.2.4` | **ACQUIRED** |
| `youtube-transcript.ai` | broker, one documented HTTPS GET | **ACQUIRED** |
| `ai-video-transcriber` | `wendy7756/AI-Video-Transcriber@ade833b7` | **ACQUIRED** |
| `yt-dlp` captions | `tools/youtube_transcript.py --mode captions` | **RIGHTS_REFUSED** |
| `faster-whisper large-v3` | `tools/youtube_transcript.py --mode asr` | **RIGHTS_REFUSED** |

The last two are not failures. `youtube_transcript.py` accepts only `owned`, `licensed`,
`creator-permission`, `public-domain` or `user-provided-media`. `AT-001` is
`user-directed-evaluation`, so the tool refuses. It downloads media and runs ASR, which is a
larger rights step than reading a caption track, and it demands a real basis for it. The
dependency was installed and the model was available; the gate is what stopped it.

Forcing it would have required inventing a rights basis. That is the one thing the allowlist
exists to prevent.

## The content converges

| Transport | Cues | Raw words | Normalized words | Rolling duplication |
|---|---:|---:|---:|---|
| `youtube-transcript-api` | 550 | 3828 | 3828 | none |
| `youtube-transcript.ai` | 39 | 11416 | 3826 | ~3× |
| `ai-video-transcriber` | 543 | 7581 | 3843 | ~2× |

Bag overlap on lowercased tokens after normalization:

```text
youtube-transcript-api  vs  youtube-transcript.ai   1.0000
youtube-transcript-api  vs  ai-video-transcriber    0.9997
youtube-transcript.ai   vs  ai-video-transcriber    1.0000
```

`normalize_rolling_transcript.py` is a **no-op** on the direct-caption output, because that
transport does not carry rolling duplication in the first place.

**Agreement here is transport fidelity, not corroboration.** All three share the same
`youtube-video:CvRngaQZQ3Y` dependency key and the same underlying automatic caption track. Three
readings of one origin remain one origin.

## The evidence precision does not converge

Every one of the v2 batch's 15 evidence anchors resolves in all three transports — no anchor is
lost. But the window each locator actually points at differs by 4.6×:

| Transport | Median anchor window | Range | Tail loss |
|---|---:|---|---:|
| `youtube-transcript-api` | **207 words** | 70–389 | 0.317 s |
| `ai-video-transcriber` | 385 words | 113–755 | 3.0 s |
| `youtube-transcript.ai` | **959 words** | 209–1481 | **19.0 s** |

A broker cue can span roughly thirty seconds and carry over a thousand words of rolling text. A
locator into it is a paragraph pointer, not a quotation pointer, which is the opposite of what
exact Shadow Evidence requires.

The broker also stops at 1182 s of a 1201 s video. The closing takeaways — "mining traces gives
you signals to hill climb on", the open-model offer, the continual-learning summary — sit in that
window. It keeps 2 cues after 19:00 where the direct transport keeps 25.

## Recommendation

Default to `youtube-transcript-api`. Same content, no rolling duplication, tightest locators, and
it reaches 1200.683 s of a 1201 s video.

Keep `ai-video-transcriber` as the pinned fallback and `youtube-transcript.ai` as the last resort;
when either is used, expect coarser locators and re-check any claim whose anchor sits after 19:40.

## The v1 artifact was recoverable

The `youtube-transcript.ai` transport, normalized, reproduces:

```text
recovered  bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462
v1 recorded bf993b8d98717284f58139bfa93955b1bbfcb0128ca386b1913e98d2a4eef462
match      True
```

Bit for bit. The v1 normalized transcript was recorded as lost and treated as permanently
unrecoverable, which made `runtime/04` look permanently blocked. It was not: the subject is
reproducible from a live transport plus a committed normalizer.

Two corrections follow from that:

- an artifact is unrecoverable only when its *source* is gone, not when the local copy is;
- `evals/live/CvRngaQZQ3Y/run.json` recorded `jdepoix/youtube-transcript-api@1.2.4` as `blocked`
  because a hosted runner's IP was blocked. The same backend at the same version succeeds locally.
  An environment fact was filed as a tool fact, and it made the whole transport look unusable.

## Cards this comparison produced

- [`D-transport-locator-precision`](cards/D-transport-locator-precision.md) — the transports agree
  on content and differ 4.6× on locator precision.
- [`V-cross-transport-convergence`](cards/V-cross-transport-convergence.md) — convergence verified,
  v1 digest reproduced, and the explicit statement that this is not independent corroboration.
