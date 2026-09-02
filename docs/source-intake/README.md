# Source Intake Registry — Stage 2 Contract/Core Leaf

This directory documents the provider-neutral preparation leaf for
[`ai-content-notes#51`](https://github.com/ed3c/ai-content-notes/issues/51).
It does not fetch or admit an external source. It defines how a GitHub, PDF,
Google Doc, Google Sheet, article, interview, or runtime source must be bound
after an owning adapter has observed it.

## Merged status

The Stage 2/3 stack this leaf was written against is on `main`:

```text
PR #52 source-registry contract and deterministic gate
       merge 3326f24fabf1cc80c65e977870ee05746e162ab6
PR #53 exact PDF bytes, page and visual-region locators
       merge 0f7f551ebbca067a02621abd8a2d538189a8855b
PR #73 atomic claims, ledgers and product-signal@1
       merge beefeb0e792a771638ad1968db126d302729256d
```

The historical preparation subject for the #52 atom was base
`6afe799f9ba01c0c7ab4a25dffe5f226c0d05d53`, tree
`6683ba605f574a40d33265cf4ca2cc223fa77dcc`, issue #51. Read the contract from
`main`, not from that base.

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
| `tools/github_source_adapter.py` | GitHub blob adapter | retained bytes + pinned descriptor | `source-registry@1` + read-back receipt | `SOURCE_INPUT_ONLY` |
| `tests/test_github_source_adapter.py` | GitHub negative-control owner | flipped bytes, branch URLs, snippet scope | executable refusal evidence | fixture/local |
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

## GitHub blob lane

`tools/github_source_adapter.py` is the GitHub half of #51. It binds retained
bytes to the exact Git object the pinned URL names by recomputing the Git blob
SHA-1 (`sha1("blob <len>\0" + bytes)`) and comparing it to the descriptor's
`blob_sha`. Git object names are content-addressed, so this read-back is exact
and needs no network: one flipped byte changes the name.

Two identity rules carry the lane:

- a `resolved_url` that does not contain the 40-hex commit names a moving
  target and is refused as `GITHUB_RESOLVED_URL_NOT_COMMIT_PINNED`;
- a mismatch between retained bytes and `blob_sha` is refused as
  `GITHUB_BLOB_SHA_MISMATCH`, which is the "GitHub URL without exact read-back"
  control from the issue body.

The committed example binds this repository's own immutable prompt payload:

```text
repository  ed3c/ai-content-notes
commit      f292deafbc0feca5dedacf27af8ce192f4a6314f
path        governance/CARD_PROTOCOL_V7_1.md
blob        7f3019f4b41a90728cd48a523d742c7c59721bf6
```

That subject was chosen because its blob identity has three independent
offline arrivals: `git hash-object`, the adapter's own recompute, and the
pre-existing `governance/CARD_PROTOCOL_CURRENT.json` pointer written by a
different tool. `tests/test_github_source_adapter.py` asserts the pointer and
the recompute agree, so a drift in either goes red. An external repository's
blob uses the identical code path with its own retained bytes.

### Declared non-target: the Google half

The Google Docs/Sheets half of #51 is **not implemented here and is not
claimed**. It stays read-frozen pending the owner decision in #41. No Google
credential, lane or authority-bearing contract file was added or edited by this
atom. `GOOGLE_DOC` and `GOOGLE_SHEET` keep their existing schema and semantic
gates in `tools/source_registry.py`; what is absent is an adapter that observes
a live Doc/Sheet, and that absence is deliberate, not an oversight.

## Next dependency

Stage 3 is no longer completion-blocked for the PDF subject: one live Stage 2
packet (`evals/source-intake/modern-web-architecture/`) was admitted on the
exact PDF subject, and Stage 3 compiled against it in
`evals/product-signal/modern-web-architecture/` at `decision: VALIDATE`.

The precondition this satisfied is general, not PDF-specific, and still
applies to any other subject: **Stage 3 compilation for a subject stays
completion-blocked until one live Stage 2 registry/source-manifest receipt is
admitted on that exact subject.** A second subject (a GitHub, Google Doc,
Sheet or other PDF) needs its own live Stage 2 receipt before Stage 3 can
compile it; the PDF's `VALIDATE` decision does not transfer.

What remains open is the Local Handoff queue, none of which CI can fabricate:

```text
#41  Google Docs/Sheets persistence authority             OWNER_DECISION_PENDING
#51  live GitHub blob adapter                             IMPLEMENTED
#51  live Google Doc/Sheet adapters                       READ_FROZEN_PENDING_#41
#54  persist and read back the Stage 3 packet             OPEN
#50  product signal export and evidence lineage           OPEN
     tools/pdf_source_adapter.py --check on the raw PDF   operator-only oracle
```

`IMPLEMENTED` above means the adapter, its negative controls and one committed
example exist and are executable. It does not close #51: the Google half is
still frozen, and issue closure remains a Human action.
