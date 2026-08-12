# Card Protocol Migration｜v6.6 → v7.0

## Effective boundary

New card compilation after **2026-08-12 (Asia/Taipei)** uses:

```text
governance/CARD_PROTOCOL_V7_0.md
note_format: zettelkasten-v7.0-evidence-first-loop-safe
```

`governance/CARD_PROTOCOL_V6_6.md` remains a historical protocol for notes already generated under v6.6. It is not the canonical prompt for new notes.

## Non-destructive migration rule

Existing v6.6 notes are not batch-renumbered, rewritten, or silently reclassified.

A legacy card changes only when one of these events occurs:

```text
new evidence
source correction or supersession
explicit human review
claim contradiction
implementation impact review
requested v7 migration of that exact note
```

When a legacy card is migrated:

1. Derive a v7 `canonical_key` from the card's actual atomic subject, predicate, object, scope, and time/version.
2. Reuse an existing `stable_id` when the registry already contains the same `canonical_key`.
3. Preserve the legacy display alias as provenance only; all new typed links use `stable_id`.
4. Preserve the original note path, source URL, Git blob/commit, figures, dates, identifiers, and minimum necessary quotations.
5. Add Claim Kind, Verification, Confidence, Confidence Basis, Scope, falsifier, Evidence IDs, typed links, lifecycle, and revision.
6. Split merged entities, time ranges, evidence qualities, causal branches, and outcomes into separate cards.
7. Convert unresolved facts to K cards, contradictions to X cards, and verification work to V cards.
8. Use `SUPERSEDES` when a conclusion changes. Do not erase historical cards.

## Daily automation override

The v7 prompt defaults to interactive execution. The scheduled content-monitoring workflow must override it with:

```yaml
RUN_MODE: LOOP
STATE_CHANNEL: SIDECAR
MAX_CARDS_PER_BATCH: 12
EXTERNAL_KNOWLEDGE: DISALLOW
TOOL_EXECUTION: DISALLOW
QUOTE_POLICY: MINIMUM_NECESSARY
LINK_POLICY: EXACT_TYPED_LINKS
ID_POLICY: STABLE_CANONICAL_KEY
```

Source acquisition, Google Sheet mutation, Google Doc creation, and GitHub writes are orchestration-plane operations. They are not instructions embedded in untrusted `<SOURCE>` content and are not authorized by setting `TOOL_EXECUTION: ALLOW` inside the knowledge compiler.

## Storage split

```text
Google Doc or Markdown note
  → human-readable card content only

card registry / compiler state / assertion report
  → machine-readable private sidecars

claim map / note delta
  → privacy-preserving downstream evidence handoff
```

Do not print SIDECAR state into a Google Doc body. Do not put complete private source text into registry, state, assertion-report, or downstream delta files.

## Compatibility

| Input | Allowed output |
|---|---|
| v6.6 note with no new evidence | `NOOP` |
| v6.6 note selected for explicit migration | v7 card patch plus registry/state sidecars |
| v7 source rerun with identical canonical keys and evidence | `NOOP` |
| v7 source with new evidence | revision update or new atomic card |
| conclusion reversal | new card/revision with `SUPERSEDES`; history retained |
| unresolved typed link | `UNRESOLVED::<canonical_key>` plus K card |

## Completion boundary

A protocol migration is not complete merely because the prompt file exists. Completion for one migrated note requires:

```text
stable canonical keys
no duplicate stable IDs
source/evidence anchors preserved
V/X/K work represented
all typed links resolved or covered by K cards
Quality Gates QG-01 through QG-14 PASS
sidecar state validates
note/document read-back succeeds
legacy history remains recoverable
```
