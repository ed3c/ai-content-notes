# Reference traceability implementation Agent contract

Owner: `ed3c/ai-content-notes#69`  
Evidence-prep owner: `#70`  
Global convergence: `#61`

This directory is the implementation entrypoint for the URL / REF / CodexDoc / Google / GitHub traceability system. It does not grant source truth, rights, Google authority, merge authority, or user-outcome authority.

## Mandatory read order

1. root `AGENTS.md` and `INTEGRATION_REQUIREMENTS.md`;
2. `docs/reference-registry/README.md`;
3. `docs/reference-registry/IMPLEMENTATION_PREP.md`;
4. `docs/reference-registry/implementation-preflight.json`;
5. `docs/reference-registry/codexdoc-index.json`;
6. `docs/reference-registry/reference-index.private.json` and `reference-index.private.methods.json`;
7. `docs/reference-registry/repo-directory-index.json` and the affected `/<repo_name>/urls.json`;
8. `tools/verify_reference_traceability.py` and its tests;
9. the exact owning Issue plus current PR/branch/check graph;
10. cross-repository contract owner when the atom leaves this repository.

## Authority laws

```text
conversation provenance != source truth
URL != identity
REF != revision/read-back
folder membership != requirement edge
source read-back != claim verification
Issue state != PR/receipt state
Google write ACK != projection sync
Google projection != Git canonical authority
CI PASS != legal/runtime/user outcome
```

## Execution roles

### Tech Lead
Owns decomposition, start/completion DAGs, one-writer leases, interfaces, oracles, evidence ceilings and convergence. It does not silently implement a blocked external-authority transition.

### Shadow Architect
Monitors `IDENTITY_DELTA`, `AUTHORITY_DELTA`, `PRIVATE_EGRESS_DELTA`, `DAG_DELTA`, `EVIDENCE_PROMOTION_DELTA`, `GOOGLE_PROJECTION_DELTA` and `SOURCE_RIGHTS_DELTA`.

Interventions:

```text
L0 OBSERVE
L1 WARN
L2 REQUIRE_RECONCILIATION
L3 BLOCK_TRANSITION
```

L3 applies when a private locator enters a public artifact, title replaces file identity, an implementation claim lacks an owning Issue/PR/receipt, Google projection is promoted to canonical state, or a source-only reference is forced into fake implementation work.

## Implementation order

```text
START NOW, path-disjoint:
  I0  #51 source-registry@1
  I1  #57 private/public REF parity verifier
  I2  #68 CodexDoc semantic triage
  EXT KAW #130 public registry hygiene/parity

BLOCKED UNTIL IMMUTABLE INPUTS EXIST:
  I3  #55 note Google projection
      requires #51 identity/digest fields + admitted KAW #120/#121/#123 contracts
  I4  ai-product-notes #48 CodexDoc/Sheet projection
      requires #51 source identity/digest contract

GLOBAL CONVERGENCE:
  #61 only after applicable exact receipts are readable
```

## Path lease laws

- `#51` owns source-registry schemas/adapters/manifests/receipts, not projection writes.
- `#57` owns parity/hygiene verifier paths and verification outputs, not source truth.
- `#68` owns CodexDoc semantic terminal-state routing, not fake PR creation.
- `#55` owns note/card Google projection only after its dependencies are admitted.
- `ai-product-notes#48` owns product/CodexDoc/Sheet projection in that repository.
- KAW `#130` owns the public side of REF hygiene; private URL bytes never cross into KAW.
- shared root prompt/governance files are not writable unless a separate owning issue explicitly leases them.

## Required Worker output

Every implementation Worker returns:

```text
exact repo/base/head/tree
owning issue + path lease
contracts consumed/produced with digests
changed paths
positive tests
negative/mutation controls
commands + exits
receipt paths/digests
cleanup/residue
maximum evidence claim
blocked/unknown/external-authority states
next eligible atom(s)
```

No Worker may merge, release, accept provider/legal terms, widen permissions, or relabel an unexercised lane as PASS.
