# Relation graph and thesis-ranking runtime

Runtime Leaf 02 consumes one exact `multimodal-source-pack@1` receipt from merged Leaf 01 and materializes a deterministic `relation-graph@1`.

It does not invoke a model, acquire media, reconstruct slides, render cards, select a batch, run HG gates, or modify the immutable v7.1 prompt.

## State transition

```text
multimodal-source-pack@1
  + relation-graph-input@1
  -> source-pack file SHA-256 and identity read-back
  -> typed anchor registry
  -> deterministic node IDs
  -> deterministic relation IDs
  -> grounding and epistemic checks
  -> deterministic thesis scoring
  -> relation-graph@1
```

## Input contract

`relation-graph-input@1` contains:

- an exact source-pack path, file SHA-256, `pack_id`, descriptor digest and source-set digest;
- typed anchors bound to source-pack artifact IDs;
- nodes with normalized semantic canonical keys;
- relations with a canonical key derived from subject, relation kind, normalized predicate and object;
- thesis candidates that reference relation canonical keys;
- optional explicit graph/node/relation/thesis IDs that must match the deterministic identity.

Canonical keys are normalized lowercase identity text. The builder rejects hidden duplicate identities and explicit ID drift rather than accepting arbitrary aliases.

## Grounding contract

Anchor kinds have different authorities:

```text
evidence
  -> non-visual source-pack artifact

visual
  -> video-frame or visual-evidence artifact

execution
  -> audit-artifact
```

Relations enforce:

```text
SUPPORTED
  -> at least one evidence or visual anchor

CORROBORATED
  -> at least two independent source_dependency_key values

TESTED
  -> at least one execution artifact

FALSIFIED
  -> evidence, visual or execution grounding
```

Every relation also requires a decision use and falsifier. A thesis candidate cannot silently include a relation marked uncertain, contested or falsified.

## Deterministic identity

```text
node_id
  = hash(normalized node canonical key)

relation canonical key
  = subject key | relation kind | normalized predicate | object key

relation_id
  = hash(relation canonical key)

candidate_id
  = hash(thesis canonical key)

graph_id
  = hash(source-pack identity + anchors + nodes + relations + ranking)
```

Input array order does not change graph identity, ranking or output bytes. `created_at` is supplied explicitly; the builder never reads the wall clock.

## Thesis score

The deterministic score uses:

```text
causal reach       0.25
graph centrality   0.20
source recurrence  0.15
decision impact    0.15
source emphasis    0.10
novelty            0.10
evidence strength  0.05
```

`source_recurrence` counts independent source dependency keys, not repeated anchors from one origin. Evidence strength combines declared verification and confidence without upgrading claim truth.

## Usage

```bash
python tools/build_relation_graph.py \
  --input <relation-graph-input.json> \
  --root <artifact-root> \
  --output <relation-graph.json> \
  --created-at <RFC3339 timestamp>
```

Use `--check` to rebuild and compare a persisted graph byte-for-byte.

## Negative controls

Leaf 02 rejects:

- stale or mutated source-pack files;
- source-pack artifacts that reference undeclared dependencies;
- traversal, absolute, non-canonical or symlink source-pack paths;
- unknown artifacts, anchors, nodes, relations or dependency keys;
- anchor-kind and artifact-modality mismatches;
- duplicate canonical nodes, relations or thesis candidates;
- explicit ID drift;
- `SUPPORTED` without grounding;
- single-origin `CORROBORATED`;
- artifact-free `TESTED`;
- thesis candidates that hide uncertain, contested or falsified relations;
- stale persisted output in `--check` mode;
- implicit wall-clock timestamps.

## Evidence boundary

A green Leaf 02 result proves:

- exact source-pack subject binding;
- typed anchor and relation integrity;
- deterministic semantic IDs;
- declared epistemic constraints;
- reproducible thesis ranking.

It does not prove:

- the source statement is true;
- the inferred causal relation is valid;
- the source dependencies are genuinely independent beyond their declared receipt identity;
- visual fidelity;
- model quality;
- card correctness;
- HG or QG completion;
- production admission.

## Stack boundary

```text
Merged PR #24  runtime/01-source-pack-and-run-receipt
  -> runtime/02-relation-graph-and-thesis-ranking
       ├── runtime/03a-knowledge-view-projections
       ├── runtime/03b-source-driven-batch-planner
       └── runtime/03c-semantic-yield-evaluator
```

Leaves `03a`, `03b` and `03c` remain blocked until this relation contract is reviewed and merged. They are siblings with disjoint path leases.

Git Town executable admission remains `ABSENT / BLOCKED_POLICY`; live sync, worktree/lease and conflict canaries remain `NOT_EXERCISED`.
