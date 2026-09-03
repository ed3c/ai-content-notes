# Consumption-scoped reference registry

Owner: `ed3c/ai-content-notes#96`.

One machine artifact lives here, `reference-index.private.json`, and one reader
verifies it, `tools/verify_reference_registry.py`. Everything below states what
the registry is allowed to claim and what it is not.

## What a row is

A row binds one opaque `REF-*` id to one path **this repository carries**, at
the sha256 of the bytes at that path. Nothing else. The row is the whole claim:

```text
id            REF-0001            opaque, stable, the only thing a public index receives
role          SOURCE_INTAKE_REGISTRY
state         READ_BACK_VERIFIED  see the state ceiling below
title         human-readable; no reader resolves it
subject_path  evals/source-intake/modern-web-architecture/source-registry.json
provider      THIS_REPOSITORY
digest        sha256 of the bytes at that path
```

Seven keys, and six of them have a reader. `subject_path` and `digest` are
`REG-02`/`REG-03` in the verifier; `id`, `role` and `state` are read by three
of the six document laws; `provider` is what makes
`law_duplicate_titles_need_distinct_identity` demand a file ID from a
`GOOGLE_DRIVE` row — which is why a row here declares `THIS_REPOSITORY` rather
than omitting the key. `title` is for people and nothing resolves it.

**`subject_path`, not `external_id`.** On `main`, `external_id` means
*provider file ID*: `law_duplicate_titles_need_distinct_identity` requires a
`GOOGLE_DRIVE` record to carry one, and `law_no_locator_in_public_projection`
reads its value as a locator. A repository path under that name would put two
kinds of row under one law. `REG-05` refuses the key outright, so the
separation is a check rather than a convention.

**No `revision` key.** An earlier draft of these rows carried the 40-hex
commit that last changed each subject, and nothing read it: `verify.yml`
checks out at `fetch-depth: 1` and this reader has no network, so no reader in
this repository can resolve a commit that is not HEAD, and a wrong 40-hex
string would have passed every check. The binding that survives is the digest,
re-read on the tree under judgment.

That leaves a hole in a law this registry does not own: `main`'s
`law_inventory_stays_url_indexed` refuses a mutable `revision` for any state
above `URL_INDEXED`, but a row with no `revision` key at all reaches that
clause as `None` and passes it. These rows are carried by the law's *digest*
clause, not its revision clause. Filed as `ed3c/ai-content-notes#115`.

## Three rules this directory exists to keep

**No locator.** No Google Drive or Docs identifier, no private repository URL,
no private skill path, and — stricter than any of those — no URI of any scheme
at all. `REG-04` in the verifier refuses the whole class rather than a
blocklist of the hosts someone remembered. A private source, if one is ever
referenced here, is referenced by opaque `REF-*` id whose resolution lives
outside this repository.

**No hand-written visibility.** A committed JSON file cannot attest that a
value was computed at read time rather than typed once and left to drift. The
closed draft chain measured that drift exactly: of 19 `github-repository` rows
across 12 distinct repositories in `reference-index.private.json` and
`reference-index.private.methods.json` at `37ae45a68b7ad66de36dc17163280e6b8972ec63`,
6 rows over 4 repositories claimed `PRIVATE` for repositories the provider
reports `PUBLIC`. A field wrong in both directions is not a containment
control. `law_no_persisted_visibility_field` refuses the key outright.

**No root-namespace expansion.** Everything stays under this directory. The
closed chain's PR #60 created twenty top-level `<repo_name>/` directories at
the repository root; #61's rescope reversed that scope, and nothing here
reintroduces it.

## State ceiling

The ladder has exactly one declaration, `STATE_CEILING` in
`tests/test_reference_registry_inventory.py`, and this file does not restate
it — a prose copy of a tuple is a copy that goes stale when the tuple gains a
rung, with nothing going red.

Every current row is `READ_BACK_VERIFIED`, and that is a claim the verifier
re-earns on every run: the bytes at the subject path hash to the recorded
digest. Nothing here is `RIGHTS_ADMITTED` or `CLAIM_VERIFIED`; this registry
proves that a path exists with known bytes, never that its contents are true,
licensed, fresh or ever read by anything but the verifier.

## Who checks what

Two readers, one law each, deliberately not overlapping.

| Reader | Owns | Runs |
|---|---|---|
| `tests/test_reference_registry_inventory.py` | the six document laws — opaque ids, no persisted `visibility`, the state ceiling, credential-bearing URLs, one file under two ids, one id resolving twice | the trusted suite, against every candidate tree |
| `tools/verify_reference_registry.py` | the five binding refusals — dangling REF, absent subject, stale digest, published locator, provider file-ID key | `tests/test_reference_registry.py`, each with a planted defect red before green |

The first module settled its public-projection contract against #96 in PR #103
(merge `3039adde19fc7d10f024325fd86ff68508408e2b`): `PUBLIC_PROJECTION_FIELDS`
is `("id", "role", "state")`, `STATE_CEILING` carries `RIGHTS_ADMITTED`, and
`law_no_persisted_visibility_field` exists. Those are the landed bytes this
directory conforms to.

## What is not here, and why

- **No `codexdoc-index.json`.** The only such index is at `2c87fc77a693da1be0122566a335ed6ff864e16f`
  on closed PR #65, and its 14,021 bytes carry 27 Google Drive locator lines.
  Materializing it here would be the `Required behavior #13` violation this
  directory exists to refuse. #68 stays blocked on #41, not on this registry.
- **No `context-reference-backfill.json`, no `repo-directory-index.json`, no
  `AGENTS.md`.** Closed PR #71 introduced a second Agent contract in this
  directory; routing stays owned by the root `AGENTS.md`.
- **No Drive row of any kind.** The Google lane is `OWNER_DECISION_PENDING`
  under #41 and #51. Note for whoever adjudicates it: a Drive-backed row
  cannot be lawful here as the contracts currently stand.
  `law_duplicate_titles_need_distinct_identity` requires a record with
  `provider: GOOGLE_DRIVE` to carry its file ID, and #96 requirement 1 forbids
  publishing that ID. The only consistent resolution is that no row in this
  repository declares that provider.

## The locators already on `main`, which this registry does not add

Seven tracked files carry the Drive file identifier of the Stage 2 PDF
subject, 24 occurrences in all, and one of them additionally carries a Docs
document identifier:

```text
evals/product-signal/modern-web-architecture/evidence-ledger.json      5
evals/product-signal/modern-web-architecture/product-signal.json       1
evals/product-signal/modern-web-architecture/readback-receipt.json     1
evals/source-intake/modern-web-architecture/readback-receipt.json      3
evals/source-intake/modern-web-architecture/source-descriptor.json     4
evals/source-intake/modern-web-architecture/source-registry.json       5
examples/source-registry/example-source-registry.json                  5
```

They arrived with the merged Product Reverse lane (PR #52, #53, #73) and with
the schema example, not with this directory. `REG-04` is therefore scoped to
this directory: a check scoped to the whole tree would be red on arrival and
switched off within a wave, which is worse than a narrow check that stays
armed. Removing them is #41's decision, not this registry's.

## Running it

```bash
python3 tools/verify_reference_registry.py          # exit 1 on any finding
python3 tools/verify_reference_registry.py --json
```

`tests/test_reference_registry.py::test_the_committed_registry_verifies_clean`
runs it on every candidate tree, so there is no separate CI wiring to keep in
sync.

To add a row, write it with any digest and run the verifier: a `DIGEST_STALE`
finding reports the `actual` value for that path. There is deliberately no
generator script — the digest has exactly one authority, which is the bytes,
and a second producer would be a second thing to keep honest.
