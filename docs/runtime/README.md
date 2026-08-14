# Semantic Yield runtime leaves

This directory documents repository-owned runtime components extracted from the monolithic draft PR #13. The shared `git-town-stacked-pr-worker` Skill owns the portable branching method; this repository owns task packets, path leases, schemas, builders, tests, CI, receipts and merge decisions.

## Current leaf

Issue #23 starts:

```text
runtime/01-source-pack-and-run-receipt
```

Leaf 01 owns only deterministic source-pack and model-run identity contracts:

```text
schemas/multimodal-source-pack-descriptor.schema.json
schemas/multimodal-source-pack.schema.json
schemas/model-run-receipt-descriptor.schema.json
schemas/model-run-receipt.schema.json
tools/build_multimodal_source_pack.py
tools/build_model_run_receipt.py
tests/test_source_pack_and_run_receipt.py
```

It does **not** invoke a model, acquire media, download a video, extract frames, run OCR, build a relation graph, choose a thesis, render cards, modify the v7.1 prompt or declare QG completion.

## Source-pack state transition

```text
typed descriptor
  -> Draft 2020-12 validation
  -> normalized relative-path guard
  -> regular-file / no-symlink guard
  -> source-dependency and modality consistency
  -> artifact SHA-256 + byte count
  -> canonical source-set digest
  -> schema-validated multimodal-source-pack@1
```

The receipt proves artifact identity, declared modality availability, source dependency and declared authority. It does not prove source accuracy, claim truth, visual fidelity or permission beyond the recorded authority fields.

## Model-run receipt transition

```text
typed run descriptor
  -> prompt/source/raw/compiled path guard
  -> prompt Git-blob identity check when supplied
  -> source-pack schema validation
  -> exact artifact SHA-256 + byte count
  -> provider/model/sampling/execution binding
  -> canonical subject digest
  -> schema-validated model-run-receipt@1
```

The builder consumes already-persisted artifacts. It never accepts inline raw-response content and never invokes a provider. `created_at`, execution timestamps and all provider/model fields are supplied explicitly; the builder does not invent them.

## Usage

```bash
python tools/build_multimodal_source_pack.py \
  --descriptor <source-pack-descriptor.json> \
  --root <artifact-root> \
  --output <source-pack.json> \
  --created-at <RFC3339 timestamp>

python tools/build_model_run_receipt.py \
  --descriptor <model-run-descriptor.json> \
  --root <artifact-root> \
  --output <model-run-receipt.json> \
  --created-at <RFC3339 timestamp>
```

Use `--check` to compare a persisted receipt byte-for-byte with a fresh deterministic rebuild. A stale subject, descriptor, digest, byte count or explicit timestamp fails closed.

## Negative controls

Leaf 01 rejects:

- absolute, traversal, non-canonical and backslash artifact paths;
- missing files, directories and any symlink component;
- duplicate artifact IDs or paths;
- undeclared or unused `source_dependency_key` values;
- modality status that disagrees with the artifact set;
- unverified visual reconstruction, note completion or raw publication authority;
- prompt Git blob mismatch;
- aliased prompt/source/raw/compiled paths;
- completed runs without bounded timestamps or with an error type;
- failed/cancelled runs without an error type;
- stale persisted receipts in `--check` mode.

## Stack boundary

```text
main
└── runtime/01-source-pack-and-run-receipt   # this leaf
    └── runtime/02-relation-graph-and-thesis-ranking
```

Leaf 02 remains blocked until these contracts stabilize. Visual and provider invocation work use independent roots and converge only in `runtime/04-convergence-and-cvrngaqzq3y-replay`.

Git Town executable admission remains `ABSENT / BLOCKED_POLICY`; live `git town sync`, worktree/lease and conflict canaries remain `NOT_EXERCISED`. GitHub branch/PR publication and Human Admit are separate evidence lanes.
