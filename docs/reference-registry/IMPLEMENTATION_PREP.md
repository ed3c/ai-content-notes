# Traceability implementation preflight

Review date: 2026-08-19  
Owner: `#69`  
Global trace audit: `#61`

## Stage verdict

Target phase state:

```text
TRACEABILITY_PREIMPLEMENTATION_READY
```

This phase is complete only when the implementation DAG, ownership, path leases, oracles, negative controls and evidence ceilings are frozen and the exact prep head passes the repository's existing CI. It does **not** mean source snapshots, public/private parity, CodexDoc semantic closure or Google projection are implemented.

## Exact consumed-byte documentation/test Stack

```text
main
└── PR #58  docs/reference-url-registry-private
    head 37ae45a68b7ad66de36dc17163280e6b8972ec63
    └── PR #60  docs/repo-url-directory-index
        head 7ba9e1a6d4e5ab5da0cbab3e44187fe9c1d88afd
        └── PR #65  docs/codexdoc-trace-index
            head 2c87fc77a693da1be0122566a335ed6ff864e16f
            └── PR #66  docs/context-reference-backfill-private
                head 876c45806449074fd3e10b7b29d016479566e97e
                └── PR #67  test/reference-traceability-graph
                    head 0b27678f9c5d924d5676d29a9e3e028231a2f8dd
                    └── #69 docs/traceability-implementation-preflight
```

The Stack above is Git ancestry because each child consumes unmerged parent bytes. Cross-repository dependencies below are process/start/completion edges only.

## Authority graph

```text
private source/REF truth     ai-content-notes
public reference projection  kotlin-auto-webview
product/CodexDoc projection  ai-product-notes
GitHub work truth            owning GitHub repository
Google Docs/Sheets           human projection / read-back substrate
conversation                 discovery provenance only
```

## Start-readiness DAG

```text
PR #67 exact graph/verifier baseline
│
├─ I0 #51 source-registry@1                  READY_TO_START
├─ I1 #57 private/public REF parity          READY_TO_START
├─ I2 #68 CodexDoc semantic triage           READY_TO_START
└─ E1 KAW #130 public hygiene/parity         READY_TO_START in KAW

I0 exact immutable output
├─ I3 #55 note Google projection             BLOCKED_BY_I0_AND_KAW_W0_W1_W3
└─ I4 ai-product-notes #48 projection        BLOCKED_BY_I0

KAW #120
→ KAW #121
→ KAW #123
→ I3 #55

I0 + I1 + I2 + E1 + applicable I3/I4 receipts
→ #61 global convergence
```

GitHub supports explicit sub-issue and blocking dependency relationships, but this repository's machine DAG must still preserve its own typed `start_dependencies` and `completion_dependencies` because Git parentage, issue hierarchy and evidence dependency are different edge classes.

## Completion-readiness

### I0 — source-registry@1 / #51

Expected output:

```text
source manifest
+ canonical locator
+ provider external identity
+ revision/commit when available
+ digest
+ retrieved/observed time
+ rights/completeness state
+ locator map
+ read-back receipt
```

Positive oracle: GitHub Markdown, PDF, Google Doc and Google Sheet can each produce deterministic manifest/read-back artifacts for exact test subjects.

Must turn red for: title/snippet-only input, stale Drive export, duplicate file identity, missing Sheet range, GitHub URL without exact subject read-back, omitted PDF visual/table lane, credential-shaped URL.

Evidence ceiling: source identity/completeness/read-back only; not claim truth or rights beyond recorded basis.

### I1 — REF parity / #57

Positive oracle: stable REF parity across private inventory, repo namespaces and exact public registry snapshot; private URLs remain private.

Must turn red for: missing opaque public/private counterpart, duplicate external ID under different REF, private locator in public snapshot, stale/tombstoned record silently deleted.

Evidence ceiling: registry consistency only.

### I2 — CodexDoc semantic triage / #68

Each current `PARTIAL|UNBOUND` item must become exactly one of:

```text
TRACE_CLOSED_SOURCE_ONLY
IMPLEMENTATION_REQUIREMENT_BOUND
NO_IMPLEMENTATION_REQUIREMENT
PARTIAL_MISSING_REVISION
PARTIAL_MISSING_ISSUE
PARTIAL_MISSING_PR
PARTIAL_MISSING_RECEIPT
```

No source-only artifact is forced to have a PR. Same-title distinct Drive files remain distinct until digest/read-back proves an alias.

Evidence ceiling: semantic ownership/routing only.

### E1 — public KAW parity / KAW #130

Public KAW may read opaque private REF IDs and public snapshots only. No private Google/private-repo locator bytes are inputs.

Evidence ceiling: public registry hygiene and opaque-ref parity.

### I3 — note Google projection / #55

Start condition:

```text
#51 exact identity/digest fields admitted
AND
KAW #120 federation contract admitted
AND
KAW #121 durable outbox semantics admitted
AND
KAW #123 generic projection contract admitted
```

Required state machine:

```text
GIT_CANONICAL_PERSISTED
→ PROJECTION_REQUESTED
→ TARGET_ID_REVISION_BOUND
→ WRITE_ATTEMPTED
→ READ_BACK
→ VERIFIED | RETRY | CONFLICT | BLOCKED
```

A Google write ACK can never satisfy `VERIFIED`.

### I4 — product CodexDoc/Sheet projection / ai-product-notes #48

Requires #51 source identity/digest contract. Must bind folder/file ID, observed revision, export digest and GitHub pointer. Partial Google failure remains `PARTIAL`; canonical state stays reconstructable without Google.

## Cross-repository binding

KAW-side readiness is tracked by `ed3c/kotlin-auto-webview#134`:

```text
#120 → #121 → #123 → ai-content-notes#55
#130 ↔ ai-content-notes#57
```

This is a process DAG, not a cross-repository Git Stack.

## Shadow Architect block register

L3 block when any occurs:

1. `URL_INDEXED` promoted to `READ_BACK_VERIFIED` without exact revision/digest evidence.
2. Same title is used to merge two distinct Google file IDs.
3. Private Google/repository locator leaves the private evidence realm.
4. Public KAW verifier requires private locator bytes rather than opaque REF identity.
5. Google write ACK is called `SYNCED` without read-back.
6. Projection changes claim/issue/Skill state directly.
7. `UNBOUND` CodexDoc item is "fixed" by inventing a fake consumer issue/PR.
8. Source-only research is required to have implementation work.
9. Start dependency is counted as a completion receipt.
10. CI from an older head is reused after branch movement.

## Worker fan-out after this phase

Parallel-safe first wave:

```text
Worker S — #51 source registry contract + fixtures
Worker P — #57 private/public parity verifier
Worker C — #68 CodexDoc semantic triage
Worker K — KAW #130 public hygiene/parity
```

Do not start #55 or ai-product #48 implementation until their exact prerequisites exist.

## Global convergence law

`#61` can close only when every material indexed source is either source-trace closed, implementation-bound with exact evidence expectations, or carries a specific missing-edge state. Closure of #69 is only implementation readiness.
