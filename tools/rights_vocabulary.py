"""The one rights vocabulary every stage of the pipeline speaks.

Before this module the repository carried three incompatible dialects:

    acquisition adapters   owned licensed creator-permission public-domain user-provided-media
    allowlist / receipts   owned licensed creator-permission public-domain user-provided
    frame sampler          authorized-local-file creator-provided user-provided

The first and third shared **no** value at all, so a video acquired under
`creator-permission` could never satisfy the frame sampler's gate, and an
allowlist entry written as `user-provided` could never be handed to any
adapter. A rights record could not flow through its own pipeline.

`tests/test_rights_vocabulary.py` binds every constant and every schema enum
to the sets below, so a fourth dialect fails a test instead of being found
later by a run that mysteriously blocks.

## What each basis requires

None of these are satisfied by a video being public, by a paid viewing
subscription, or by the material being interesting. See
`governance/LICENSE_POLICY.md` for the full statement and its sources.

- `owned` — the repository owner holds the copyright in the material.
- `licensed` — a licence covering this use exists and can be read back from a
  non-secret reference. Note that a Creative Commons licence on a platform
  video licenses the *copyright*; it does not by itself authorize retrieving
  the file from that platform.
- `creator-permission` — the rights holder gave permission for this use,
  recorded with the granting party and date.
- `public-domain` — the material is out of copyright or dedicated to the
  public domain, with the basis stated.
- `user-provided-media` — the operator supplies the media through a channel
  they are authorized to use.

`user-directed-evaluation` is not in that list. It records that the owner
pointed at material they do not own. It can never be `verified`, and the
schemas pin it to `evaluation-only`.
"""

from __future__ import annotations

# Bases that can carry authorization_status: verified.
VERIFIED_RIGHTS_BASES: frozenset[str] = frozenset(
    {
        "owned",
        "licensed",
        "creator-permission",
        "public-domain",
        "user-provided-media",
    }
)

# A direction to use material, not a statement about who holds rights in it.
EVALUATION_ONLY_BASIS = "user-directed-evaluation"

ALL_RIGHTS_BASES: frozenset[str] = VERIFIED_RIGHTS_BASES | {EVALUATION_ONLY_BASIS}

AUTHORIZATION_STATUSES: frozenset[str] = frozenset(
    {"verified", "evaluation-only", "blocked"}
)


def may_acquire_media(rights_basis: str, authorization_status: str) -> bool:
    """Whether a stage that retrieves or decodes media may proceed.

    Reading a caption track and downloading a video are not the same act. This
    returns True only for a verified basis, which is why the ASR path refuses
    an evaluation-only record.
    """
    return (
        authorization_status == "verified" and rights_basis in VERIFIED_RIGHTS_BASES
    )
