# CvRngaQZQ3Y｜v7.1 Live Replay

This directory contains the persisted result of the v7.1 live replay for video `CvRngaQZQ3Y`.

## Complete output

- [Complete 12-card Markdown output](card-output-v7.1.md)
- [Digest-bound card manifest](card-manifest.json)
- [Run configuration](run.json)
- [Replay result](result.json)
- [Continuation state](run-state.md)

## Persisted contract

```text
cards: 12
bytes: 43,993
sha256: 40365a668a74be3c862a27326041f004a05a5d038d4eaa7e9b580b874efeadb2
status: CONTINUE
```

Rebuild and compare the complete file:

```bash
python tools/materialize_card_batch.py \
  --manifest evals/live/CvRngaQZQ3Y/card-manifest.json \
  --output /tmp/CvRngaQZQ3Y-v7.1.md \
  --check
cmp /tmp/CvRngaQZQ3Y-v7.1.md \
  evals/live/CvRngaQZQ3Y/card-output-v7.1.md
```

The committed complete output contains the transformed knowledge-card batch and state sidecars. Source acquisition evidence is tracked separately by the run and manifest files.
