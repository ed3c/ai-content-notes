"""ed3c/ai-content-notes#57 - the private reference registry's hard laws.

The registry this verifies is #56's artifact:

    docs/reference-registry/reference-index.private.json

It is not on `main`. #56 was closed by a receipt comment naming a head on a
still-draft chain, and `tools/closure_audit.py` already reports that closure as
`ABSENT`. #96 is the open successor that will actually materialize this path
(consumption-scoped, no Drive access) and reconcile the seven false closures;
this module verifies whatever lands there, under whichever issue number gets
it there. So this module does two separable things, and keeping them separable
is the point:

1. it states the laws as predicates over a registry document and proves each
   one refuses a violating registry, using synthetic records only;
2. it binds to the committed registry the moment one exists, and until then
   requires the absence to agree with the closure audit rather than passing
   quietly.

A test that only says "the file is missing" is a tautology. A test that only
runs on synthetic data never touches the artifact. This does both, and the
second is what makes the first arm itself when the draft chain lands.

Two of the six laws below have a half this repository cannot reach, because
the public index lives in `ed3c/kotlin-auto-webview`. What is enforceable here
is the private side of each: that the projection this repository would hand to
a public index carries no locator, and that every `REF-*` id it publishes
resolves to exactly one record here. The KAW-side half stays uncovered and is
named as such rather than approximated.

## Reconciled with #96 (contract conflict, resolved 2026-09-03)

#96 named a live conflict between its own producer contract and this module's
first draft: a `visibility` field in the public projection's field set, and
`ADMITTED` versus `RIGHTS_ADMITTED` as the strong-claim state name. #96 is the
producer of the artifact this module verifies, and its rationale is grounded
in a measured defect (the closed chain's `reference-index.private.json` had 6
of 19 rows with `visibility` wrong in both directions - PRIVATE claimed for
repositories the provider reports PUBLIC, and the reverse). This module now
conforms to #96's contract rather than the other way round:

- `PUBLIC_PROJECTION_FIELDS` carries no `visibility` - #96 requirement 2,
  "Visibility is derived or absent. No hand-written `visibility` field.";
- a new law, `law_no_persisted_visibility_field`, refuses a hand-written
  `visibility` key anywhere in the document, not only in the public
  projection - a committed JSON file cannot prove a value was derived at
  read time rather than typed once and left to drift, so the only
  mechanically checkable rule is that the persisted document carries no such
  key at all, which is exactly the defect #96 measured;
- the strong-claim state is `RIGHTS_ADMITTED`, and `STATE_CEILING` states all
  six rungs #96's requirement 3 names (`URL_INDEXED != IDENTITY_RESOLVED !=
  REVISION_BOUND != READ_BACK_VERIFIED != RIGHTS_ADMITTED != CLAIM_VERIFIED`),
  so this module recognizes and enforces all six rather than refusing the
  four #96 owns and this module never previously named.

This module does not re-derive `tools/verify_reference_traceability.py` (400
lines, `refs/pull/72/head` at `40a77ed1`) even though #96 requirement 5 asks
for exactly that: #96 already claims that re-derivation as its own atom's
work. Doing it here too would be a third verifier for one registry, which is
the failure this reconciliation is trying to reduce, not add to. This module's
five original laws plus the visibility law are a different, narrower
denominator (the private inventory's own hard laws) than that graph's repo-
wide URL traceability; a later reviewer should decide whether any of the two
denominators' overlapping checks (secret-shaped query parameters, one
`external_id` under two `REF-*` ids) collapse to a single owner once both are
landed. That decision is not this module's to make.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from closure_audit import ABSENT, DEFAULT_LEDGER, audit, load_ledger  # noqa: E402

REGISTRY_ISSUE = 56
REGISTRY_SCHEMA = "reference-index.private@1"

# The full state ceiling ed3c/ai-content-notes#96 names (requirement 3) and
# says was correct in the closed chain. The closed chain only ever emitted
# URL_INDEXED, so URL_INDEXED is the one name this module inherits; the other
# five are stated here for the first time against a landed subject.
STATE_CEILING = (
    "URL_INDEXED",
    "IDENTITY_RESOLVED",
    "REVISION_BOUND",
    "READ_BACK_VERIFIED",
    "RIGHTS_ADMITTED",
    "CLAIM_VERIFIED",
)
# The state an inventory starts in. Anything stronger is a claim about bytes
# that were read back, so it needs an immutable revision and a digest - this
# module has no grounds narrower than "stronger than URL_INDEXED" for any of
# the five, since only IMMUTABLE_STATES' two original members have a fixture
# and a planted-defect control; see test_identity_resolved_without_a_digest_fails
# for the first control on a state this module previously refused outright.
URL_INDEXED = STATE_CEILING[0]
IMMUTABLE_STATES = set(STATE_CEILING[1:])
UNKNOWN = "UNKNOWN"
MUTABLE_REVISIONS = {UNKNOWN, "main_MUTABLE", "HEAD"}

# Fields a public index may receive: id, role and state - #96 requirement 1
# ("the public row carries the id, the role and the state, never the
# locator") and requirement 2 (no visibility field, hand-written or
# otherwise; see law_no_persisted_visibility_field). A locator reaching this
# set is the leak the private plane exists to prevent.
PUBLIC_PROJECTION_FIELDS = ("id", "role", "state")
LOCATOR_FIELDS = ("url", "external_id")
# Below this, a locator value is short enough to appear inside an enum by
# accident, so containment stops being evidence of a leak. Real Drive file IDs
# are 33 characters and up.
LOCATOR_MIN_LENGTH = 8

SECRET_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authuser",
    "code",
    "id_token",
    "key",
    "password",
    "pwd",
    "refresh_token",
    "session",
    "sessionid",
    "sig",
    "signature",
    "token",
}
PROVIDERS_KEYED_BY_FILE_ID = {"GOOGLE_DRIVE"}
REF_ID = re.compile(r"^REF-[0-9]{4}$")


# --------------------------------------------------------------------------
# The six laws, as predicates over a registry document.
# --------------------------------------------------------------------------


def public_projection(record: dict) -> dict:
    """What a public index may receive for one private record."""
    return {field: record[field] for field in PUBLIC_PROJECTION_FIELDS if field in record}


def law_no_persisted_visibility_field(registry: dict) -> list[str]:
    """Visibility is derived or absent, never a hand-written field (#96 #2).

    A static JSON file cannot attest that a value was computed at read time
    rather than typed once and left to drift - #96 measured exactly that
    drift in the closed chain (6 of 19 rows wrong, in both directions). The
    only law this repository can mechanically enforce is narrower and
    stronger: the persisted document carries no `visibility` key at all. A
    tool that wants to show visibility computes it from the provider when it
    reads the registry; it does not commit the answer to `main`.
    """
    return [
        f"{record.get('id')}: hand-written visibility field {record['visibility']!r}"
        for record in registry["references"]
        if "visibility" in record
    ]


def law_no_locator_in_public_projection(registry: dict) -> list[str]:
    """A public index receives opaque ids, never the locator behind them.

    The check reads the projection's values rather than its key set, so it also
    catches a file ID that arrived through `role` - a field whose name does not
    say "locator" but whose value can be one.

    Containment is only used for values long enough to be a locator. A short
    identifier matches enum noise: a one-character external_id `X` is inside
    `URL_INDEXED`, and that false positive would make the law unusable rather
    than strict.
    """
    findings = []
    for record in registry["references"]:
        projected = [str(value) for value in public_projection(record).values()]
        for field in LOCATOR_FIELDS:
            value = str(record.get(field) or "")
            if not value:
                continue
            if any(
                value == item or (len(value) >= LOCATOR_MIN_LENGTH and value in item)
                for item in projected
            ):
                findings.append(f"{record.get('id')}: public projection carries the {field}")
        if not REF_ID.match(str(record.get("id", ""))):
            findings.append(f"{record.get('id')!r}: not an opaque REF id")
    return findings


def law_every_public_ref_resolves_here(registry: dict) -> list[str]:
    """Each `REF-*` a public index cites resolves to exactly one record."""
    findings = []
    seen: dict[str, int] = {}
    for record in registry["references"]:
        seen[str(record.get("id"))] = seen.get(str(record.get("id")), 0) + 1
    for ref_id, count in sorted(seen.items()):
        if count != 1:
            findings.append(f"{ref_id}: resolves to {count} records, not one")
    return findings


def resolve(registry: dict, ref_id: str) -> dict | object:
    """Resolve one `REF-*`, returning ABSENT rather than raising.

    A public reference this repository cannot resolve is a finding the caller
    has to see, not a KeyError that reads like a bug in the caller.
    """
    matches = [record for record in registry["references"] if record.get("id") == ref_id]
    return matches[0] if len(matches) == 1 else ABSENT


def law_inventory_stays_url_indexed(registry: dict) -> list[str]:
    """`URL_INDEXED` until a digest exists, and never on a mutable revision.

    Applies to all five states above `URL_INDEXED` on `STATE_CEILING`, not
    only the two (`READ_BACK_VERIFIED`, `RIGHTS_ADMITTED`) this module has a
    fixture for - any of the five makes a claim stronger than "a URL was
    found", so none of them should be reachable on a mutable pointer either.

    The two clauses are not symmetric, and the docstring used to imply they
    were - it said a stronger state "needs an immutable revision and a digest"
    while the predicate was a blocklist of three mutable names, so a row that
    omitted `revision` entirely reached `READ_BACK_VERIFIED` without naming one
    and a 40-hex string nothing produced passed too (ed3c/ai-content-notes#115).

    What is enforced, deliberately, is:

    - **the digest is required.** It is the only binding this repository can
      re-resolve: `tools/verify_reference_registry.py` re-reads the bytes under
      judgment on every verifier run.
    - **`revision` is optional, and unverified when present.** Nothing here can
      resolve a commit that is not `HEAD` - `verify.yml` checks out at
      `fetch-depth: 1` and the verifier has no network - so requiring a
      revision would require a field whose only property is that nobody checks
      it.
    - **the blocklist stays** because `UNKNOWN`, `main_MUTABLE` and `HEAD`
      claim a binding they do not have. Refusing a name that advertises
      mutability is worth doing even where absence is admitted; it is a
      narrower claim than "an immutable revision was verified", and it is the
      one this function can actually make.

    This docstring owns what the predicate enforces. The decision itself, and
    the half of #115 it leaves open, are owned by
    `docs/reference-registry/README.md` beside the ten rows that rely on them.
    """
    findings = []
    for record in registry["references"]:
        state = record.get("state")
        if state == URL_INDEXED:
            continue
        if state not in IMMUTABLE_STATES:
            findings.append(f"{record.get('id')}: unknown state {state!r}")
            continue
        if record.get("revision") in MUTABLE_REVISIONS:
            findings.append(f"{record.get('id')}: {state} on revision {record.get('revision')!r}")
        # `or UNKNOWN` so absent, null and empty reach the same refusal as the
        # literal name: the required half must not be silent about absence
        # either, which is the sibling instance of the #115 hole in this same
        # predicate.
        if (record.get("digest") or UNKNOWN) == UNKNOWN:
            findings.append(f"{record.get('id')}: {state} without a digest")
    return findings


def law_no_credential_bearing_url(registry: dict) -> list[str]:
    """A locator that carries a credential is not a locator, it is a secret."""
    findings = []
    for record in registry["references"]:
        url = str(record.get("url", ""))
        parts = urlsplit(url)
        if "@" in parts.netloc:
            findings.append(f"{record.get('id')}: url carries userinfo")
        for source in (parts.query, parts.fragment):
            for key, _ in parse_qsl(source, keep_blank_values=True):
                if key.lower() in SECRET_QUERY_KEYS:
                    findings.append(f"{record.get('id')}: url carries {key}")
    return findings


def law_duplicate_titles_need_distinct_identity(registry: dict) -> list[str]:
    """Display title is not identity; the file ID is.

    Two records may share a title, and must then differ by file ID. Two records
    that share a file ID are the same asset indexed twice, whatever they are
    called.
    """
    findings = []
    by_external: dict[str, list[str]] = {}
    for record in registry["references"]:
        external_id = record.get("external_id")
        if external_id is None:
            if record.get("provider") in PROVIDERS_KEYED_BY_FILE_ID:
                findings.append(f"{record.get('id')}: Drive record without a file ID")
            continue
        by_external.setdefault(str(external_id), []).append(str(record.get("id")))
    for external_id, ref_ids in sorted(by_external.items()):
        if len(ref_ids) > 1:
            findings.append(f"{external_id}: indexed under {sorted(ref_ids)}")
    return findings


LAWS = (
    law_no_persisted_visibility_field,
    law_no_locator_in_public_projection,
    law_every_public_ref_resolves_here,
    law_inventory_stays_url_indexed,
    law_no_credential_bearing_url,
    law_duplicate_titles_need_distinct_identity,
)


def violations(registry: dict) -> list[str]:
    return [finding for law in LAWS for finding in law(registry)]


# --------------------------------------------------------------------------
# Synthetic records. No locator here points at a real private asset.
# --------------------------------------------------------------------------


def lawful_registry() -> dict:
    return {
        "schema": REGISTRY_SCHEMA,
        "references": [
            {
                "id": "REF-9001",
                "title": "Duplicate display title",
                "url": "https://docs.google.com/document/d/EXAMPLE-FILE-A/edit?usp=drivesdk",
                "external_id": "EXAMPLE-FILE-A",
                "provider": "GOOGLE_DRIVE",
                "state": URL_INDEXED,
                "revision": UNKNOWN,
                "digest": UNKNOWN,
                "role": "EXAMPLE_SOURCE",
            },
            {
                "id": "REF-9002",
                "title": "Duplicate display title",
                "url": "https://docs.google.com/document/d/EXAMPLE-FILE-B/edit?usp=drivesdk",
                "external_id": "EXAMPLE-FILE-B",
                "provider": "GOOGLE_DRIVE",
                "state": URL_INDEXED,
                "revision": UNKNOWN,
                "digest": UNKNOWN,
                "role": "EXAMPLE_SOURCE",
            },
            {
                "id": "REF-9101",
                "title": "ed3c/example-private-repo",
                "url": "https://github.com/ed3c/example-private-repo",
                "external_id": "0000000000",
                "provider": "GITHUB",
                "state": URL_INDEXED,
                "revision": "main_MUTABLE",
                "digest": UNKNOWN,
                "role": "EXAMPLE_AUTHORITY",
            },
        ],
    }


def mutated(**changes) -> dict:
    registry = lawful_registry()
    index = changes.pop("index", 0)
    registry["references"][index].update(changes)
    return registry


# --------------------------------------------------------------------------
# Controls. Each law must refuse something.
# --------------------------------------------------------------------------


def test_the_synthetic_baseline_satisfies_every_law() -> None:
    """Two records share a title on purpose: that is legal, and must stay legal."""
    registry = lawful_registry()
    titles = [record["title"] for record in registry["references"]]
    assert len(titles) != len(set(titles))
    assert violations(registry) == []


def test_a_hand_written_visibility_field_fails() -> None:
    """#96 requirement 2: no hand-written `visibility` field, public or not.

    Planted on the private side (not through the public projection) to prove
    the law reads the source record, not the projected view - the exact
    field #96 measured wrong in both directions in the closed chain.
    """
    findings = law_no_persisted_visibility_field(mutated(visibility="PRIVATE"))
    assert any("hand-written visibility field 'PRIVATE'" in item for item in findings)
    assert law_no_persisted_visibility_field(lawful_registry()) == []


def test_a_file_id_smuggled_through_a_public_field_fails() -> None:
    """`role` is published. A file ID placed in it leaves this repository."""
    findings = law_no_locator_in_public_projection(mutated(role="DOC_EXAMPLE-FILE-A"))
    assert any("public projection carries the external_id" in item for item in findings)


def test_a_short_identifier_is_not_read_as_a_leak() -> None:
    """Regression: `X` is inside `URL_INDEXED`, and that is not a leak.

    Found by planting a synthetic registry at the real path before this module
    was committed. A law that fires on enum noise gets switched off, not fixed.
    """
    registry = mutated(external_id="X", url="https://docs.google.com/document/d/X/edit")
    assert not any(
        "public projection carries" in item
        for item in law_no_locator_in_public_projection(registry)
    )


def test_the_public_projection_of_a_lawful_record_is_only_opaque_fields() -> None:
    record = lawful_registry()["references"][0]
    assert set(public_projection(record)) == set(PUBLIC_PROJECTION_FIELDS)
    rendered = json.dumps(public_projection(record))
    assert record["url"] not in rendered and record["external_id"] not in rendered


def test_a_non_opaque_public_id_fails() -> None:
    findings = law_no_locator_in_public_projection(mutated(id="EXAMPLE-FILE-A"))
    assert any("not an opaque REF id" in item for item in findings)


def test_a_ref_id_that_resolves_twice_fails() -> None:
    registry = lawful_registry()
    registry["references"][1]["id"] = "REF-9001"
    assert any("resolves to 2 records" in item for item in law_every_public_ref_resolves_here(registry))
    assert resolve(registry, "REF-9001") is ABSENT
    assert resolve(registry, "REF-9999") is ABSENT
    assert resolve(lawful_registry(), "REF-9002")["external_id"] == "EXAMPLE-FILE-B"


def test_read_back_verified_without_an_immutable_revision_fails() -> None:
    findings = law_inventory_stays_url_indexed(
        mutated(state="READ_BACK_VERIFIED", revision="main_MUTABLE", digest="sha256:" + "0" * 64)
    )
    assert any("on revision 'main_MUTABLE'" in item for item in findings)


def test_read_back_verified_without_a_digest_fails() -> None:
    findings = law_inventory_stays_url_indexed(
        mutated(state="READ_BACK_VERIFIED", revision="rev-17", digest=UNKNOWN)
    )
    assert any("without a digest" in item for item in findings)


def test_an_immutable_revision_with_a_digest_is_allowed_to_leave_url_indexed() -> None:
    """The law bounds the claim; it must not make the claim unreachable."""
    assert (
        law_inventory_stays_url_indexed(
            mutated(state="READ_BACK_VERIFIED", revision="rev-17", digest="sha256:" + "0" * 64)
        )
        == []
    )


def test_a_record_with_no_revision_key_is_admitted_on_its_digest_alone() -> None:
    """ed3c/ai-content-notes#115: the third line of that issue's table, pinned.

    An absent `revision` passing was an accident of `None not in
    MUTABLE_REVISIONS`, not a decision. It is now the decision - option 1 of
    the two #115 names - and this control is what makes it one: requiring a
    revision here turns this red, and whoever does it has to mean it.
    """
    record = {
        "id": "REF-9001",
        "role": "EXAMPLE",
        "state": "READ_BACK_VERIFIED",
        "digest": "sha256:" + "a" * 64,
    }
    assert "revision" not in record
    assert law_inventory_stays_url_indexed({"references": [record]}) == []

    # ...and this is the shape the committed rows actually have, so the
    # decision is pinned against a live subject rather than a synthetic one.
    path = registry_json_path()
    if path.exists():
        committed = json.loads(path.read_text(encoding="utf-8"))
        assert [
            row
            for row in committed["references"]
            if row.get("state") != URL_INDEXED and "revision" not in row
        ], "no committed row relies on this clause any more; revisit the decision"


def test_the_other_direction_a_missing_digest_is_still_refused() -> None:
    """Absence is admitted on the optional half only. Both halves, one fixture.

    Without this, "an absent key passes" would read as a property of the law
    rather than of one clause, and the required half could rot the same way.
    """
    base = {"id": "REF-9001", "role": "EXAMPLE", "state": "READ_BACK_VERIFIED"}
    for digest in ({}, {"digest": UNKNOWN}, {"digest": None}, {"digest": ""}):
        findings = law_inventory_stays_url_indexed({"references": [dict(base, **digest)]})
        assert any("without a digest" in item for item in findings), digest


def test_an_unresolvable_revision_is_admitted_and_a_mutable_name_is_not() -> None:
    """The blocklist refuses claims of a binding, not unverified strings.

    Nothing in this repository resolves a revision - `verify.yml` checks out at
    `fetch-depth: 1` and the verifier has no network - so a 40-hex string here
    is unchecked either way. The narrow claim the law can make is that a row
    does not *advertise* mutability, and that is the claim it makes.
    """
    base = {"id": "REF-9001", "role": "EXAMPLE", "state": "READ_BACK_VERIFIED",
            "digest": "sha256:" + "a" * 64}
    assert law_inventory_stays_url_indexed({"references": [dict(base, revision="0" * 40)]}) == []
    for name in sorted(MUTABLE_REVISIONS):
        findings = law_inventory_stays_url_indexed({"references": [dict(base, revision=name)]})
        assert any(f"on revision {name!r}" in item for item in findings), name


def test_identity_resolved_without_a_digest_fails() -> None:
    """#96's STATE_CEILING names four rungs this module had no fixture for.

    Before reconciliation those four names (including `IDENTITY_RESOLVED`)
    fell into `unknown state`, so this module would have refused #96's own
    registry the moment it used one - control-inverted from what a registry
    verifier is for. This proves the broadened `IMMUTABLE_STATES` both
    recognizes the name and still enforces the immutable-revision-and-digest
    requirement on it, the same as the two previously-named states.
    """
    findings = law_inventory_stays_url_indexed(
        mutated(state="IDENTITY_RESOLVED", revision="rev-3", digest=UNKNOWN)
    )
    assert any("without a digest" in item for item in findings)
    assert not any("unknown state" in item for item in findings)


def test_every_state_ceiling_rung_is_a_recognized_state() -> None:
    """No name on #96's ceiling can fall through to `unknown state`."""
    for state in STATE_CEILING[1:]:
        findings = law_inventory_stays_url_indexed(
            mutated(state=state, revision="rev-3", digest="sha256:" + "0" * 64)
        )
        assert findings == [], (state, findings)


def test_a_session_bearing_url_fails() -> None:
    findings = law_no_credential_bearing_url(
        mutated(url="https://docs.google.com/document/d/EXAMPLE-FILE-A/edit?access_token=abc123")
    )
    assert any("carries access_token" in item for item in findings)


def test_a_url_with_userinfo_fails() -> None:
    findings = law_no_credential_bearing_url(
        mutated(url="https://user:secret@docs.google.com/document/d/EXAMPLE-FILE-A/edit")
    )
    assert any("carries userinfo" in item for item in findings)


def test_the_benign_drive_query_parameter_is_not_a_credential() -> None:
    """usp=drivesdk is on every Drive share link; flagging it would make the law noise."""
    assert law_no_credential_bearing_url(lawful_registry()) == []


def test_one_file_indexed_under_two_ref_ids_fails() -> None:
    registry = lawful_registry()
    registry["references"][1]["external_id"] = "EXAMPLE-FILE-A"
    findings = law_duplicate_titles_need_distinct_identity(registry)
    assert any("indexed under ['REF-9001', 'REF-9002']" in item for item in findings)


def test_a_drive_record_without_a_file_id_fails() -> None:
    registry = lawful_registry()
    del registry["references"][0]["external_id"]
    findings = law_duplicate_titles_need_distinct_identity(registry)
    assert any("Drive record without a file ID" in item for item in findings)


# --------------------------------------------------------------------------
# Binding to the committed registry.
# --------------------------------------------------------------------------


def registry_paths() -> list[str]:
    """The paths #56's own body names, read from the closure-audit ledger.

    Hardcoding them here would let this module and the audit drift apart and
    still both look green.
    """
    ledger = load_ledger(DEFAULT_LEDGER)
    row = next(row for row in ledger["closures"] if row["issue"] == REGISTRY_ISSUE)
    return list(row["artifacts"])


def registry_json_path() -> Path:
    paths = [path for path in registry_paths() if path.endswith(".json")]
    assert len(paths) == 1, paths
    return ROOT / paths[0]


def test_the_named_registry_artifact_is_the_one_this_module_checks() -> None:
    assert "docs/reference-registry/reference-index.private.json" in registry_paths()


def test_registry_presence_agrees_with_the_closure_audit() -> None:
    """Absence is a state this module states, not one it assumes."""
    row = next(
        row
        for row in audit(load_ledger(DEFAULT_LEDGER), ROOT)["rows"]
        if row["issue"] == REGISTRY_ISSUE
    )
    present = all((ROOT / path).exists() for path in registry_paths())
    assert (row["status"] == ABSENT) is not present


def check_registry_file(path: Path) -> list[str]:
    """Read a registry from disk and return its findings."""
    registry = json.loads(path.read_text(encoding="utf-8"))
    if registry.get("schema") != REGISTRY_SCHEMA:
        return [f"unexpected registry schema: {registry.get('schema')!r}"]
    return violations(registry)


def test_reading_a_registry_from_disk_reports_its_findings(tmp_path: Path) -> None:
    """The branch that arms when #56's artifact lands, exercised now.

    Without this the on-disk path is code no test has ever run, and the module
    would first execute it against the real registry - the one moment it must
    not be discovering its own bugs.
    """
    lawful = tmp_path / "lawful.json"
    lawful.write_text(json.dumps(lawful_registry()), encoding="utf-8")
    assert check_registry_file(lawful) == []

    unlawful = tmp_path / "unlawful.json"
    unlawful.write_text(
        json.dumps(mutated(url="https://docs.google.com/document/d/EXAMPLE-FILE-A/edit?token=abc")),
        encoding="utf-8",
    )
    assert any("carries token" in item for item in check_registry_file(unlawful))

    wrong_schema = tmp_path / "wrong.json"
    wrong_schema.write_text(json.dumps({"schema": "something-else@1", "references": []}), encoding="utf-8")
    assert check_registry_file(wrong_schema) == ["unexpected registry schema: 'something-else@1'"]


def test_the_committed_registry_is_either_absent_or_lawful() -> None:
    path = registry_json_path()
    if not path.exists():
        # ed3c/ai-content-notes#57 cannot be closed on this tree: the artifact
        # it verifies is on the draft chain #58 -> ... -> #72, not on main.
        row = next(
            row
            for row in audit(load_ledger(DEFAULT_LEDGER), ROOT)["rows"]
            if row["issue"] == REGISTRY_ISSUE
        )
        assert row["status"] == ABSENT
        return
    assert check_registry_file(path) == []
