# Private Reference URL Registry

Owners: `ed3c/ai-content-notes#56` / parent `#51`  
Public privacy-safe counterpart: `ed3c/kotlin-auto-webview#129`  
Implementation preflight: `#69`

## Start here

Before changing any reference/source/projection implementation in this directory:

1. [`AGENTS.md`](AGENTS.md)
2. [`IMPLEMENTATION_PREP.md`](IMPLEMENTATION_PREP.md)
3. [`implementation-preflight.json`](implementation-preflight.json)
4. [`codexdoc-index.json`](codexdoc-index.json)
5. the applicable global/private registry and `/<repo_name>/urls.json`
6. `tools/verify_reference_traceability.py` and its tests
7. the exact owning Issue, PR/branch/head/check graph, and cross-repository contract owner

Current prep state is `TRACEABILITY_PREIMPLEMENTATION_READY` only after #69's exact prep head passes the existing repository CI. This state is implementation readiness, not source/projection/runtime completion.

## Purpose

This private registry stores full locators that must not be committed to the public `kotlin-auto-webview` repository:

- user Google Docs / Sheets / Drive URLs;
- private GitHub repository URLs;
- private canonical Skill / prompt / method URLs;
- their stable shared `REF-*` identities;
- role, visibility, current indexing state and downstream issue links.

Machine inventories and prep contracts:

- [`reference-index.private.json`](reference-index.private.json) — Google assets and private repositories;
- [`reference-index.private.methods.json`](reference-index.private.methods.json) — canonical private Skills/methods and prompt pointers;
- [`repo-directory-index.json`](repo-directory-index.json) — root-level `/<repo_name>/urls.json` navigation map;
- [`codexdoc-index.json`](codexdoc-index.json) — CodexDoc folder/child inventory plus Issue/PR trace status;
- [`implementation-preflight.json`](implementation-preflight.json) — implementation atoms, dependency classes, outputs, controls and evidence ceilings.

## Implementation readiness

Issue `#69` freezes the implementation start/completion DAG without pretending the open implementation owners are complete:

```text
PR #67 baseline
├─ #51 source-registry@1                         READY_TO_START
├─ #57 private/public REF parity                 READY_TO_START
├─ #68 CodexDoc semantic triage                  READY_TO_START
└─ KAW #130 public hygiene/parity                READY_TO_START in KAW

#51 admitted subject
├─ #55 note Google projection                    blocked on #51 + KAW #120/#121/#123
└─ ai-product-notes #48 projection               blocked on #51

applicable receipts
→ #61 global convergence
```

The detailed path leases, planted controls and evidence ceilings are in `IMPLEMENTATION_PREP.md`. Cross-repository dependencies are process/completion edges, not fabricated Git ancestry.

## Repository-name URL namespaces

Issue `#59` adds one root-level directory per important repository:

```text
/<repo_name>/urls.json
```

Examples:

```text
/kotlin-auto-webview/urls.json
/ai-content-notes/urls.json
/ai-product-notes/urls.json
/skills-shared/urls.json
/bettor-arena/urls.json
/runtime-env/urls.json
/Skill.md-native/urls.json
```

Each repo-scoped file stores that repository's canonical URL plus the important GitHub, Google Doc/Sheet/Drive, Skill, prompt or evidence URLs directly related to that repo. Stable `REF-*` remains the cross-repository identity; the repo directory is a navigation projection.

```text
repo name
→ /<repo_name>/urls.json
→ REF-*
→ global reference registry
→ future revision/digest/read-back
→ claim / requirement / implementation / evidence
```

Do not invent a new `REF-*` merely because one URL is projected into several repo directories. Duplicate repo-local projections are allowed when the same source materially supports multiple repositories.

## CodexDoc trace inventory

Issue `#62` binds the private `CodexDoc` Drive folder and its current children to `REF-1300+` identities in [`codexdoc-index.json`](codexdoc-index.json).

```text
CodexDoc folder/file
→ REF-13xx
→ BOUND | PARTIAL | UNBOUND | NO_IMPLEMENTATION_REQUIREMENT
→ consumer repository / owning Issue
→ PR/exact evidence where implementation already exists
```

The folder is a navigation/source-projection substrate, not a DAG authority. A child file is not considered traced merely because it is inside CodexDoc. `BOUND` requires an observed consuming Issue/decision; implementation-bearing sources additionally need real PR/head/receipt edges before implementation closure can be claimed.

The global audit owner is `#61`; conversation-only source backfill is `#63`; the deterministic graph verifier is `#64`; semantic terminal-state triage is `#68`.

## Authority boundary

```text
URL_INDEXED
!= IDENTITY_RESOLVED
!= REVISION_BOUND
!= READ_BACK_VERIFIED
!= RIGHTS_ADMITTED
!= CLAIM_VERIFIED
!= IMPLEMENTED
```

This registry is an inventory/provenance layer. `ai-content-notes#51` remains responsible for the stronger `source-registry@1` snapshot/read-back contract.

## Public/private federation

```text
private full locator
        ↓
reference-index.private*.json / codexdoc-index.json
        ↓ same stable REF-* ID
public KAW reference-index.public*.json
        ↓
opaque private reference only
```

The public KAW index may expose a stable opaque REF ID; it must not contain the corresponding Google file ID or private repository/Skill URL.

## Indexed private Google assets

| REF | Title | Kind | State |
|---|---|---|---|
| REF-1001 | KMP 導航線渲染與通訊架構研究 | Google Doc | URL_INDEXED |
| REF-1002 | KMP 整合 OpenClaw 架構指南 | Google Doc | URL_INDEXED |
| REF-1003 | KMP 整合 OpenClaw 架構指南 — distinct file | Google Doc | URL_INDEXED |
| REF-1004 | AgentOS KMP 架構創新演進.pdf | Drive PDF | URL_INDEXED |
| REF-1005 | AI Solopreneur Tracks & Gaps Master Database (2026) | Google Sheet | URL_INDEXED |
| REF-1006 | AI高價值內容知識變現潛力排行榜 | Google Sheet | URL_INDEXED |
| REF-1007 | SkillBench_Research_and_Market_Gaps_Tracker | Google Sheet | URL_INDEXED |
| REF-1008 | AI Operation：開發戰力倍增器 | Google Doc | URL_INDEXED |
| REF-1009 | Android Engineering Note｜2026-08-07｜Google Play API 36 Deadline Playbook | Google Doc | URL_INDEXED |
| REF-1010 | Android 工程師轉型指南 — file A | Google Doc | URL_INDEXED |
| REF-1011 | Android 工程師轉型指南 — file B | Google Doc | URL_INDEXED |
| REF-1012 | Android 工程師轉型指南 — file C | Google Doc | URL_INDEXED |
| REF-1013 | SkillBench 整合研究與市場實作 Gap 追蹤表 | Google Sheet | URL_INDEXED |

Duplicate titles are intentionally retained as separate identities. File IDs, revisions and future digests—not titles—determine identity.

## Indexed private repositories

`REF-1101`–`REF-1112` currently cover private evidence, product, methods, orchestration, routing, runtime and device-support repositories. Their full URLs remain in the machine inventory and must not be projected into the public KAW registry. Public `enterprise_agent_system` is separately indexed through `REF-0012` and its repo-name namespace.

## Indexed canonical private methods

`REF-1201`–`REF-1207` cover the current `skills-shared` methods and `ai-content-notes` card-protocol pointers used by Tech Lead / Shadow / Stack-PR / evidence compilation. Mutable `main` paths are locator discovery only; later admission must pin exact commits/trees/blobs without changing the stable REF identity.

## Future enrichment

`#51` should enrich each applicable record without changing its stable REF identity:

```text
external stable ID
→ exact revision / commit / tree
→ exported or fetched digest
→ observed-at timestamp
→ rights basis
→ retention/model-egress class
→ read-back receipt
→ locators
→ downstream claim/requirement/capability edges
```

If access is revoked, a document is deleted, or a repository/source is superseded, retain the REF row and change availability/freshness state. Traceability history must not be silently deleted.

## Security rules

- Never store credentials, OAuth grants, access tokens, session cookies, signed bearer URLs or password-reset URLs.
- Private locator access does not imply ownership, model-egress authorization or publication rights.
- Do not copy complete restricted source content merely to make the index self-contained.
- Public output may contain stable opaque REF IDs but not private locator fields.
