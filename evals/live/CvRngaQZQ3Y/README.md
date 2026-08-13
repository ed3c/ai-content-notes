# CvRngaQZQ3Y｜v7.1 Live Replay

This directory records one review-only transcript acquisition and one first-batch replay of the immutable card compiler v7.1.

## Authority boundary

The source was acquired under:

```text
authorization_status: unverified-evaluation-only
rights_basis: user-directed-evaluation
```

Therefore this directory is an **evaluation artifact**, not a completed canonical note. It cannot publish the raw transcript, raise downstream Claim evidence, complete a Google Doc note, qualify a Skill, or enable routing.

The complete raw transcript and acquisition manifests remain in a private GitHub Actions artifact with seven-day retention. They are not committed to Git.

## Acquisition chain

```text
CvRngaQZQ3Y
  -> pinned wendy7756/AI-Video-Transcriber
       blocked on hosted runner; audio fallback disabled
  -> youtube-transcript-api 1.2.4
       blocked by YouTube hosted-runner IP policy; cookies/proxies disabled
  -> youtube-transcript.ai
       needs-review secondary transport candidate
       source_dependency_key = youtube-video:CvRngaQZQ3Y
       independent corroboration authority = false
```

The selected candidate is `en (auto-generated)`, 19:42, and requires human review of names, model versions, products, acronyms, figures, punctuation and quotation boundaries.

## Deterministic normalization

The raw broker response remains authoritative. `tools/normalize_rolling_transcript.py` created a derivative using only:

- HTML entity decoding;
- isolation of a known transport footer;
- exact adjacent repeated-token-block collapse;
- exact cross-cue suffix/prefix overlap removal.

It did **not** correct words, identifiers, grammar, punctuation or meaning.

Observed metrics:

| Metric | Value |
|---|---:|
| Input / output cues | 39 / 39 |
| Raw subject words | 11,290 |
| Normalized words | 3,797 |
| Exact adjacent duplicate tokens removed | 7,214 |
| Exact cross-cue overlap tokens removed | 279 |
| Exact collapse events | 542 |
| Transport footer characters isolated | 240 |

## v7.1 batch

The immutable prompt is:

```text
governance/CARD_PROTOCOL_V7_1.md
git blob: 7f3019f4b41a90728cd48a523d742c7c59721bf6
sha256: 9388c4f17172dc970f7228ded2f0df54a1111b22047faa11f8e7db36579165dd
```

The first balanced batch contains 12 cards in task-value-first order:

```text
N / C / S / P / C / C / D / D / D / V / K / K
```

Highlights:

- trace data becomes useful only through a ship → collect → mine → experiment → update loop;
- trace mining is decision-shaped feedback extraction rather than passive logging;
- model, harness and task/data require joint fit under one frozen evaluation contract;
- long-lived continual learning needs separate data, harness and memory state planes;
- the source-reported open-model versus Opus cost claim remains LOW confidence;
- the practice card is `UNTESTED` and the verification card is `NOT_RUN` with `Artifacts: NONE`.

The batch status is `CONTINUE`, because rights, proper nouns, raw-caption provenance, independent external QG-01..QG-24 evidence and canonical registry/read-back are unresolved.

## Materialization

The card body is split into digest-bound repository parts to avoid transport corruption. Rebuild and verify the logical output with:

```bash
python tools/materialize_card_batch.py \
  --manifest evals/live/CvRngaQZQ3Y/card-manifest.json \
  --output /tmp/CvRngaQZQ3Y-v7.1.md \
  --check
```

Expected logical output:

```text
cards: 12
bytes: 43,993
sha256: 4eb91ca518ef5078d8c485fb84e6921ca9ed45aff6c7b24f0b0a8a62fdac0b78
status: CONTINUE
```

Machine-readable context is in:

```text
card-manifest.json
run.json
result.json
run-state.md
```
