# Source Intake Registry — Stage 2 Contract/Core Leaf

This directory documents the provider-neutral preparation leaf for
[`ai-content-notes#51`](https://github.com/ed3c/ai-content-notes/issues/51).
It does not fetch or admit an external source. It defines how a GitHub, PDF,
Google Doc, Google Sheet, article, interview, or runtime source must be bound
after an owning adapter has observed it.

## Exact preparation subject

```text
repository  ed3c/ai-content-notes
base        6afe799f9ba01c0c7ab4a25dffe5f226c0d05d53
base tree   6683ba605f574a40d33265cf4ca2cc223fa77dcc
issue       #51
atom        C/K/E source-registry contract and deterministic gate
```

The repository already owns `source-manifest.schema.json`, retained-subject
verification, visual-evidence receipts, rights vocabulary, source-pack
contracts and their tests. This leaf composes those authorities; it does not
fork or replace them.

## Directory → State Machine → data flow

| Path | Owner | Input | Output / evidence | Ceiling |
|---|---|---|---|---|
| `schemas/source-registry.schema.json` | contract owner | provider-neutral pointer | `source-registry@1` shape | structural only |
| `tools/source_registry.py` | deterministic gate | registry + schema | canonical packet + PASS/FAIL report | identity/rights/read-back consistency |
| `tests/test_source_registry.py` | negative-control owner | positive and mutated packets | executable refusal evidence | fixture/local |
| `examples/source-registry/` | fixture owner | synthetic GitHub/PDF/Doc/Sheet records | zero-secret examples | `CONTRACT_FIXTURE_ONLY` |
| `docs/source-intake/` | navigation/Shadow owner | code, issue and repository facts | read order, State Machine and blockers | prose is not PASS |

```text
SOURCE_REFERENCED
→ IDENTITY_RESOLVED
→ RIGHTS_AND_COMPLETENESS_REVIEWED
→ SNAPSHOT_CAPTURED
→ LOCATORS_BOUND
→ DIGESTED
→ READ_BACK_VERIFIED
→ ADMITTED | BLOCKED
```

```text
adapter observation
→ immutable or revision-bound identity
→ rights and completeness decision
→ content/export digest
→ page/line/path/range/visual locators
→ post-boundary read-back
→ deterministic registry digest
→ downstream source-manifest candidate
```

## Hard boundaries

- A title or search snippet is `BLOCKED`; it cannot be snapshotted or admitted.
- Public visibility is not a rights basis.
- A GitHub blob binds repository, commit, blob SHA and path.
- A Drive change notification triggers refetch only; it is not content proof.
- A Google Doc binds document ID, observed revision, exported digest and
  read-back.
- A Sheet binds file ID, observed revision, exact range, row key and range
  read-back.
- A PDF with material diagrams or tables binds a page and visual-region
  locator plus an explicit visual-review state.
- Fixture packets never become source evidence or `ADMITTED` subjects.
- Source identity/read-back does not prove source accuracy, product internals,
  implementation, market demand, payment, merge or release.

## Shadow Architect findings

1. The attached design PDF proposes a reusable architecture pattern, but its
   mappings to named YC products remain source statements or hypotheses.
2. Issue #41 still owns the Human decision over Google persistence authority.
   This leaf uses `OWNER_DECISION_PENDING` and does not edit any of the nine
   authority-bearing Google contract files.
3. The current connector can publish code and receive hosted CI, but it cannot
   claim a local worktree, Git Town, Forgejo or independent Shadow context.
4. An example packet demonstrates the contract only. A live PDF receipt still
   requires exact retained/exported bytes, digest, rights and visual read-back.

## Verification

```bash
python -m pip install -r requirements-contracts.txt
ruff check tools/source_registry.py tests/test_source_registry.py
python -m py_compile tools/source_registry.py tests/test_source_registry.py
pytest -q tests/test_source_registry.py
python tools/source_registry.py \
  --registry examples/source-registry/example-source-registry.json \
  --check
```

The invalid fixture must return non-zero:

```bash
python tools/source_registry.py \
  --registry examples/source-registry/invalid-title-snippet.json
```

## Next dependency

This C/K/E leaf can be reviewed independently. Live GitHub/PDF/Google adapters
remain sibling A-atoms. Stage 3 product-signal compilation remains
completion-blocked until one live Stage 2 registry/source-manifest receipt is
admitted on the exact source subject.
