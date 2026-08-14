# Rights attestations｜取材權利認證紀錄

This file records what the repository owner has actually stated about source
rights, verbatim in effect, with the date and the exact scope. It is the
`rights_reference` target that entries in
[`RIGHTS_ALLOWLIST.json`](RIGHTS_ALLOWLIST.json) cite.

Recording an attestation here does not grant acquisition authority. Only an
allowlist entry with `authorization_status: verified` does, and
`tools/rights_allowlist.py` blocks everything else.

## AT-001｜aiDotEngineer channel, user-directed evaluation

```text
attested_on:    2026-08-14
attestor:       repository owner (ed3c)
scope:          https://www.youtube.com/@aiDotEngineer/videos
stated:         "都可以" — any video on this channel may be used
rights_basis:   user-directed-evaluation
status:         evaluation-only
```

### What this is

The owner directed that material on this channel may be used. This is the same
basis already recorded for the first live evaluation batch, where
`evals/live/CvRngaQZQ3Y/run.json` carries `rights_basis:
user-directed-evaluation` and `authorization_status:
unverified-evaluation-only`.

### What this is not

The owner does not own this channel. A direction to use material is not a
statement about who holds rights in it, so this attestation is **not**
`owned`, `licensed`, `public-domain`, `user-provided` or
`creator-permission`.

`schemas/rights-allowlist.schema.json` pins `user-directed-evaluation` to
`authorization_status: evaluation-only`, and `resolve()` permits only
`verified`. An allowlist entry citing AT-001 therefore **blocks**, by
construction rather than by discipline.

Concretely, under AT-001 alone:

- no automated caption or ASR acquisition is authorized;
- no accuracy benchmark result may be published as a rights-qualified run;
- no note may reach completion on this material;
- `evals/live/**` style unverified evaluation remains what it always was.

### What would upgrade it

A separate attestation stating **which** basis applies and on what evidence:

- `creator-permission` — a non-secret reference to permission from the channel
  owner, naming the granting party and date;
- `licensed` — the licence the videos are published under, per video, with a
  reference that can be read back;
- `public-domain` — the basis for that status;
- `owned` / `user-provided` — the owner holds or supplies the media directly.

Issue #7's admission thresholds also require a human-reviewed gold transcript
per evaluated item before any accuracy number is quoted. AT-001 does not
substitute for that.
