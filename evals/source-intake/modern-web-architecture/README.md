# Modern Web Architecture PDF — Stage 2 Live Source Canary

This directory is the issue-leased PDF adapter canary for `ai-content-notes#51`.
It consumes the unmerged `source-registry@1` contract from parent PR #52 and is
therefore a true child Stack PR, not an independent sibling.

## State Machine

```text
DRIVE_FILE_OBSERVED
→ RAW_BYTES_DOWNLOADED
→ LOCAL_HASH_AND_SIZE_BOUND
→ PDF_STRUCTURE_CHECKED
→ PAGE_COUNT_BOUND
→ MATERIAL_VISUALS_REVIEWED
→ LIVE_REGISTRY_GENERATED
→ PARENT_REGISTRY_VALIDATED
→ EXACT_HEAD_HOSTED_VERIFIED | BLOCKED
```

## Data flow

```text
Google Drive PDF URL
  → raw stored-file download
  → local byte hash / size / PDF header / EOF / page-object count
  → owner-provided rights and complete-page review
  → page + visual-region locators
  → source-registry@1 LIVE packet
  → read-back receipt
  → Stage 3 completion-dependency candidate
```

## Authority boundary

The canary may establish `SOURCE_INPUT_ONLY` for the exact PDF bytes. It cannot
upgrade source statements about YC products, internal libraries, costs,
performance, licenses, product value, paid demand, merge, or release.

The raw PDF is not committed in this leaf. Its retained identity is the Drive
file ID, observed revision tuple, exact byte size, SHA-256, 34-page count, and
reviewed visual locators. Google persistence authority remains
`OWNER_DECISION_PENDING` under issue #41.

## Regeneration

```bash
python tools/pdf_source_adapter.py \
  --pdf /absolute/path/to/現代網頁設計架構擴充建議.pdf \
  --descriptor evals/source-intake/modern-web-architecture/source-descriptor.json \
  --output evals/source-intake/modern-web-architecture/source-registry.json \
  --receipt evals/source-intake/modern-web-architecture/readback-receipt.json

python tools/pdf_source_adapter.py \
  --pdf /absolute/path/to/現代網頁設計架構擴充建議.pdf \
  --descriptor evals/source-intake/modern-web-architecture/source-descriptor.json \
  --output evals/source-intake/modern-web-architecture/source-registry.json \
  --receipt evals/source-intake/modern-web-architecture/readback-receipt.json \
  --check
```

The second command is the Local Handoff oracle. It requires the exact raw file;
CI validates the committed packet and deterministic unit controls but does not
fabricate access to the external PDF bytes.
