# Claude Code repository contract

## Mandatory entrypoint

Before collecting a source, creating or editing a note, changing claim mappings, updating the Google Sheet, or integrating with Atlas, read [`INTEGRATION_REQUIREMENTS.md`](INTEGRATION_REQUIREMENTS.md) in full. Then read the governance documents and the exact note/schema/exporter paths affected by the task.

If a referenced file, note, migration path, source anchor, Git blob, schema, or Sheet URL cannot be read back from its declared authority, report a materialization gap. Do not infer completion from README text, expected paths, issue comments, PR bodies, or prior conversations.

## Required behavior

1. Require sufficiently complete source text; title/search-snippet-only inputs must be blocked.
2. Preserve v6.6 One Case One Card, Shadow Evidence, and D/P/N completeness.
3. Separate `Fact`, `Invariant`, `Inference`, and `Assumption` claim candidates.
4. Bind note identity to exact repository path, Git blob SHA, source commit, canonical URL, source version/date, digest, and anchors.
5. Keep complete private note bodies out of downstream deltas and public exports.
6. Treat Google Sheet as the ranking/status control plane and GitHub Markdown as the note-body source of truth.
7. Never write an expected note URL to the Sheet before commit and GitHub read-back succeed.
8. Never raise Atlas Claim admission, runtime Evidence Grade, Skill lifecycle, production routability, or implicit invocation from this repository.
9. Report note completion, claim candidacy, Atlas admission, qualification, and production routing as separate states.
