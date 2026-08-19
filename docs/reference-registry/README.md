# Private Reference URL Registry

Owners: `ed3c/ai-content-notes#56` / parent `#51`  
Public privacy-safe counterpart: `ed3c/kotlin-auto-webview#129`

## Purpose

This private registry stores full locators that must not be committed to the public `kotlin-auto-webview` repository:

- user Google Docs / Sheets / Drive URLs;
- private GitHub repository URLs;
- private canonical Skill / prompt / method URLs;
- their stable shared `REF-*` identities;
- role, visibility, current indexing state and downstream issue links.

Machine inventories:

- [`reference-index.private.json`](reference-index.private.json) — Google assets and private repositories;
- [`reference-index.private.methods.json`](reference-index.private.methods.json) — canonical private Skills/methods and prompt pointers.

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

This first registry is an inventory/provenance layer. `ai-content-notes#51` remains responsible for the stronger `source-registry@1` snapshot/read-back contract.

## Public/private federation

```text
private full locator
        ↓
reference-index.private*.json
        ↓ same stable REF-* ID
public KAW reference-index.public*.json
        ↓
opaque private reference only
```

The public KAW index may say `REF-1001` or `REF-1201`; it must not contain the corresponding Google file ID or private repository/Skill URL.

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

Duplicate titles are intentionally retained as separate identities. File IDs, revisions and future digests—not titles—determine identity.

## Indexed private repositories

`REF-1101`–`REF-1112` currently cover private evidence, product, methods, orchestration, routing, runtime and device-support repositories. Their full URLs remain in the machine inventory and must not be projected into the public KAW registry.

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
