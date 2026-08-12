# YouTube Transcript Pipeline｜高精度逐字稿證據管線

## Purpose

This tool acquires a **reviewable transcript candidate** for the private evidence workflow. It does not claim that platform captions or ASR output are verbatim-perfect, and it never marks a note `completed` by itself.

```text
rights attestation
  -> one-video canonicalization
  -> metadata and caption inventory
  -> manual captions when available
  -> platform automatic captions otherwise
  -> explicit ASR fallback on an authorized GPU runner
  -> raw-source digest + timestamped transcript artifacts
  -> quality checks
  -> human review of names, figures, quotations and code terms
  -> complete-source gate for v6.6 note generation
```

## Compliance boundary

Run the workflow only for media that is:

- owned by the operator;
- covered by an applicable license;
- covered by explicit creator permission;
- public domain; or
- uploaded/provided by an authorized user for transcription.

A publicly viewable video is not, by itself, a rights basis. The tool deliberately has no cookie, proxy, browser-session, PO-token-provider or anti-bot bypass interface. When YouTube or a rights boundary prevents acquisition, the result must remain `blocked`.

Full third-party transcripts and downloaded audio are data-plane artifacts. They are not committed automatically. GitHub Actions stores the generated evidence bundle as a short-retention private artifact. Audio is deleted after ASR unless `--keep-audio` is explicitly supplied.

## Quality hierarchy

| Grade | Source | Meaning |
|---|---|---|
| `manual-caption` | creator/uploader caption track | strongest automated acquisition candidate; still review names, numbers and quotes |
| `platform-auto-caption` | YouTube automatic caption track | complete-text candidate; technical terms and punctuation need review |
| `asr-unreviewed` | `faster-whisper` `large-v3` by default | fallback candidate with word timestamps, VAD and glossary hints; human review mandatory |
| `blocked` | no authorized/complete source | do not generate a completed note |

For authoritative exactness, prefer an uploader-provided transcript or a caption track downloaded through an owner-authorized YouTube API flow, then perform a human comparison against the audio.

## Local caption acquisition

```bash
python -m pip install -r requirements-youtube-transcript.txt

python tools/youtube_transcript.py \
  --url 'https://www.youtube.com/watch?v=<video-id>' \
  --output-dir /secure/transcripts/<video-id> \
  --mode captions \
  --languages 'en,zh-Hant,zh-TW,zh' \
  --rights-basis creator-permission \
  --rights-reference 'permission-record-or-ticket' \
  --attested-by '<operator>'
```

## Authorized ASR fallback

Use a self-hosted GPU runner or another explicitly paid/isolated GPU execution environment.

```bash
python -m pip install -r requirements-youtube-transcript-asr.txt

python tools/youtube_transcript.py \
  --url 'https://www.youtube.com/watch?v=<video-id>' \
  --output-dir /secure/transcripts/<video-id> \
  --mode asr \
  --allow-audio-download \
  --asr-model large-v3 \
  --asr-model-revision edaa852ec7e145841d8ffdb056a99866b5f0a478 \
  --asr-device cuda \
  --asr-compute-type float16 \
  --glossary /secure/input/technical-terms.txt \
  --rights-basis owned \
  --rights-reference 'channel-owner-record' \
  --attested-by '<operator>'
```

The default `large-v3` CTranslate2 model is pinned to Hugging Face revision `edaa852ec7e145841d8ffdb056a99866b5f0a478`; changing it is an evidence-impacting change that must be recorded.

The glossary should contain product names, people, acronyms, code symbols and domain-specific terms. It is passed as both an initial prompt and hotword hint. It is represented in the manifest by SHA-256, not copied into the manifest.

## Outputs

```text
<output-dir>/
├── manifest.json        # provenance, authorization, backend, quality, digests, failure
├── transcript.json      # complete cue/word data
├── transcript.txt       # timestamped review text
└── raw/
    └── <video>.<lang>.vtt  # caption mode only; audio is deleted by default
```

`manifest.json` is governed by `schemas/youtube-transcript-manifest.schema.json`. It never contains the full transcript body and always keeps these authorities false:

```json
{
  "may_complete_note": false,
  "may_raise_claim_evidence": false,
  "may_enable_skill_routing": false
}
```

## GitHub Actions

Use **Actions → YouTube transcript evidence → Run workflow**.

- `captions` runs on `ubuntu-latest` and never downloads audio.
- `asr` requires a self-hosted runner with labels `self-hosted`, `linux`, `x64`, `gpu`, and `youtube-transcript`.
- The workflow uses `contents: read`, does not commit transcript output, and uploads the evidence directory for seven days.
- Failure still uploads `manifest.json`, so the daily note workflow can write an exact blocked reason and continue to the next ranked item.

The workflow is manual by design. A scheduled caller may be added only for an explicit rights allowlist; channel popularity or public visibility is not an allowlist.

## Human review gate

Before using the result as a complete source:

1. Verify title, video ID, channel, publication date and rights reference.
2. Compare technical proper nouns, company/person names, dates, figures, code identifiers and quotations against the audio.
3. Inspect low-coverage and timestamp warnings.
4. Preserve corrections as a separate reviewed derivative; never silently overwrite raw captions.
5. Bind the reviewed transcript digest to the resulting note/claim map.
6. Keep the note state blocked until the complete-source gate passes.
