# Guard verdicts

`tools/publication_guard.py` is the external gate that decides whether a
rendered batch may ship. The operator-visible behavior is a verdict: a JSON
report naming which rules were enforced, which stayed prompt-enforced, and every
finding, with the exit code carrying the answer. The guard never trusts a
model-authored `PASS`; `.github/workflows/verify.yml` runs the **default
branch's** guard bytes against a candidate tree, so a pull request cannot ship a
red card by shipping a guard that likes it.

## Sub-features

- `guard-verdict` reports findings per rule over every batch in a tree, exit `0` clean and `1` with findings.
- `guard-scope` names its enforced subset and lists what stays prompt-enforced rather than silently omitting it.
- `guard-root` guards a tree other than its own, which is how trusted bytes judge a candidate.
- `guard-fatal` exits `2` rather than guarding when it cannot run at all.

## How to get to it (user POV)

- Run `python3 tools/publication_guard.py` to guard this checkout.
- Run `python3 tools/publication_guard.py --root <tree>` to guard another tree with these bytes.
- Read `findings`, `finding_count`, `enforced`, `prompt_enforced_only` and `batches` from the printed JSON.
- In CI, the same verdict arrives as the `verify` workflow's "Run the trusted publication guard against the candidate tree" step.

## Driving it with the card pipeline CLI

Preconditions:

- Both doctor commands pass. (The first doctor command is this feature's clean verdict; drive it here as the feature rather than assuming it.)
- `$VERIFY_RUN` is exported.
- The commands below run from the repository root.

- **Take the verdict on this checkout.** Run `python3 tools/publication_guard.py`.
  Exit `0`. `"finding_count"` is `0`, `"findings"` is `{}`, and `"batches"` lists
  exactly `loop-batches/sqlite-testing`, `semantic-yield/CvRngaQZQ3Y` and
  `semantic-yield/CvRngaQZQ3Y-v2`. A batch missing from that list was not
  guarded, whatever the exit code says.

- **Read the scope, not just the verdict.** The same report's `enforced` names
  seven rules (`QG-03`, `QG-07`, `QG-08`, `QG-10`, `QG-16`, `QG-24`, `I-06`)
  with the title each carries in `governance/CARD_PROTOCOL_V7_1.md`, and
  `prompt_enforced_only` lists the eighteen `QG-` rules the guard does not
  enforce. A green guard is evidence about those seven, and about nothing else.

- **Guard a foreign tree with these bytes.** Run
  `python3 tools/publication_guard.py --root .` from the repository root and
  confirm the report's `"root"` field is the absolute path of this checkout.
  This is the shape CI uses (`python3 .trusted/tools/publication_guard.py --root .candidate`):
  the guard bytes and the guarded tree are separate arguments, so a candidate
  never supplies its own judge.

- **Prove it fails closed.** Point the guard at a tree with no protocol:

  ```sh
  mkdir -p "$VERIFY_RUN/empty-tree"
  python3 tools/publication_guard.py --root "$VERIFY_RUN/empty-tree"
  ```

  Exit `2`, stderr `publication guard cannot run: PROTOCOL_ABSENT:<path>/governance/CARD_PROTOCOL_V7_1.md`.
  Exit `2` is "cannot guard", never "nothing wrong found"; a verification run
  that treats non-`1` as a pass would read this as green.

- **Proof.** Save the full JSON report from the first drive — it is the verdict,
  the scope and the batch list in one artifact — plus the exit codes and stderr
  of the fail-closed drive.

## Gotchas

- Exit `1` is findings; exit `2` is the guard refusing to run (`PROTOCOL_ABSENT`, `PROTOCOL_RULE_LIST_UNPARSEABLE`, `RULE_ABSENT_FROM_PROTOCOL`, `NO_CARD_BATCHES`, `BATCH_MANIFEST_ABSENT`). Collapsing them loses the fail-closed behavior.
- Findings for a rule the guard implements are the *only* thing a green verdict speaks to. `prompt_enforced_only` is eighteen of the twenty-four gates, and no card in this repository has ever been machine-checked against them.
- Guarding a synthetic verification batch is not possible by copying cards into a scratch tree: the guard requires each batch to carry its manifest and either a registry or a gap report, and exits `2` (`BATCH_MANIFEST_ABSENT`) otherwise. The reds-when-it-should evidence for each enforced rule is the planted-defect suite at `tests/test_publication_guard.py:185-334`, one test per rule; this map does not re-derive it.
- Never park a verification run directory under `evals/*/*/cards`. The guard would pick it up as a publication candidate and gate a synthetic batch as if it were a product.
- The guard reads retained bodies under `sources/` for I-06. In a tree without `sources/`, `retained_source_text` reads `ABSENT` and I-06 is silently vacuous — check that field before believing an I-06 pass.
