# AI-Video-Transcriber Integration

## Purpose

This integration lets `ed3c/ai-content-notes` evaluate the subtitle-first path from
`wendy7756/AI-Video-Transcriber` without granting it note-completion, claim-evidence,
or Skill-routing authority.

Pinned upstream:

```text
repository: wendy7756/AI-Video-Transcriber
commit: ade833b790d482f7a5c0a722c67bc33f71e9d2b5
license: Apache-2.0
module: backend/video_processor.py
entrypoint: VideoProcessor.fetch_subtitles
```

The adapter verifies the exact checkout and license before importing the module.
No unpinned `main` execution is allowed.

## Data flow

```text
single YouTube URL
  -> canonical video ID
  -> pinned upstream checkout verification
  -> AI-Video-Transcriber fetch_subtitles
  -> returned Markdown preserved as private artifact
  -> timestamped cue parser
  -> transcript JSON/text + digests
  -> v7.1 source-manifest@2
  -> human review / private card-compiler evaluation
```

The upstream application normally proceeds to LLM optimization and summarization.
This adapter stops before those stages. Optimized text is not acceptable as evidence
because corrections and paragraphing can alter names, numbers, quotation boundaries,
and causal language.

## Trust boundary

The integration records two authorization states:

- `verified`: requires `owned`, `licensed`, `creator-permission`, `public-domain`, or
  `user-provided-media` plus a reviewable reference.
- `unverified-evaluation-only`: requires `user-directed-evaluation`; artifacts remain
  private and transient, and the note cannot become `completed`.

Public visibility alone is not treated as permission.

## Evidence limitations inherited from upstream

`VideoProcessor.fetch_subtitles` returns formatted Markdown and deletes the temporary
VTT/SRT directory. Therefore:

- the returned Markdown is preserved and hashed;
- raw platform VTT/SRT is not claimed as retained;
- timestamps have the upstream renderer's whole-second precision;
- names, figures, quotations, identifiers, and timeline coverage require review;
- any successful run remains `needs-review`.

The native `tools/youtube_transcript.py` backend remains the stronger option when raw
caption retention and millisecond cue evidence are required.

## Usage

```bash
python tools/ai_video_transcriber_adapter.py \
  --url 'https://www.youtube.com/watch?v=<video-id>' \
  --output-dir transcript-evidence \
  --upstream-root vendor/AI-Video-Transcriber \
  --upstream-commit ade833b790d482f7a5c0a722c67bc33f71e9d2b5 \
  --prompt-path governance/CARD_PROTOCOL_V7_1.md \
  --authorization-status unverified-evaluation-only \
  --rights-basis user-directed-evaluation \
  --rights-reference 'chat-request:<reference>' \
  --attested-by 'github:<actor>'
```

Outputs:

```text
manifest.json
source-manifest.json
raw_upstream_transcript.md
transcript.json
transcript.txt
```

Full transcripts stay in private workflow artifacts. Git commits should contain only
manifests, digests, transformed card output, tests, and non-verbatim evaluation notes.
