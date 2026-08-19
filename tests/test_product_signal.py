from __future__ import annotations
import copy, json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import product_signal as ps  # noqa: E402

SOURCE_ID = "pdf:test"
SOURCE_DIGEST = "sha256:" + "1" * 64
DEP = "drive-file:test"


def registry():
    return {
        "schema_version": "source-registry@1",
        "evidence_mode": "LIVE",
        "registry_digest": "sha256:" + "2" * 64,
        "entries": [{
            "source_id": SOURCE_ID,
            "state": "ADMITTED",
            "authority_ceiling": "SOURCE_INPUT_ONLY",
            "source_dependency_key": DEP,
            "content": {"digest": SOURCE_DIGEST},
            "readback": {"status": "PASS"},
            "rights": {"decision": "PASS"},
            "completeness": {"status": "COMPLETE"},
        }],
    }


def evidence():
    return {
        "schema_version": "evidence-ledger@1",
        "source_binding": {},
        "entries": [{
            "evidence_id": "e1",
            "kind": "SOURCE_TEXT",
            "source_id": SOURCE_ID,
            "source_digest": SOURCE_DIGEST,
            "dependency_key": DEP,
            "locator": {"kind": "PAGE", "page": 1, "value": "x"},
        }],
    }


def claim(cls="SOURCE_STATEMENT", verification="SUPPORTED", risk=None):
    return {
        "schema_version": "atomic-claim@1",
        "claim_id": "claim:a",
        "claim_class": cls,
        "statement": "A sufficiently long source-bound claim.",
        "source_id": SOURCE_ID,
        "locator": {"kind": "PAGE", "page": 1, "value": "x"},
        "evidence_refs": ["e1"],
        "verification": verification,
        "risk_tags": risk or [],
        "signal_refs": [{
            "signal_id": "signal:a",
            "signal_class": "SOURCE_PATTERN",
            "title": "A",
        }],
        "required_evidence": [],
    }


def contradictions():
    other = copy.deepcopy(claim())
    other["claim_id"] = "claim:b"
    return [claim(), other], {
        "schema_version": "contradiction-ledger@1",
        "entries": [{
            "contradiction_id": "contradiction:a",
            "claim_ids": ["claim:a", "claim:b"],
            "status": "UNRESOLVED",
            "statement": "Two source statements remain in tension.",
            "required_evidence": ["independent check"],
        }],
    }


class ProductSignalTests(unittest.TestCase):
    def test_positive_compiles_and_is_stable(self):
        claims, contra = contradictions()
        self.assertEqual(ps.validate_inputs(claims, evidence(), contra, registry()), [])
        a = ps.compile_signal(claims, evidence(), contra, registry())
        b = ps.compile_signal(
            copy.deepcopy(claims), copy.deepcopy(evidence()),
            copy.deepcopy(contra), copy.deepcopy(registry())
        )
        self.assertEqual(ps.canonical(a), ps.canonical(b))
        self.assertEqual(a["decision"], "VALIDATE")
        self.assertEqual(a["authority_ceiling"], "SOURCE_EVIDENCE_ONLY")
        self.assertTrue(a["unresolved_contradictions"])

    def test_unanchored_claim_rejected(self):
        claims, contra = contradictions()
        claims[0]["evidence_refs"] = []
        failures = ps.validate_inputs(claims, evidence(), contra, registry())
        self.assertTrue(any("UNANCHORED_CLAIM" in x for x in failures))

    def test_source_statement_cannot_be_tested(self):
        claims, contra = contradictions()
        claims[0]["verification"] = "TESTED"
        failures = ps.validate_inputs(claims, evidence(), contra, registry())
        self.assertTrue(any("SOURCE_STATEMENT_OVERPROMOTED" in x for x in failures))

    def test_high_risk_fact_needs_stronger_evidence(self):
        claims, contra = contradictions()
        claims[0] = claim("FACT", "SUPPORTED", ["INTERNAL_ARCHITECTURE"])
        failures = ps.validate_inputs(claims, evidence(), contra, registry())
        self.assertTrue(any("HIGH_RISK_FACT_WITHOUT_STRONG_EVIDENCE" in x for x in failures))

    def test_source_digest_drift_rejected(self):
        claims, contra = contradictions()
        ev = evidence()
        ev["entries"][0]["source_digest"] = "sha256:" + "9" * 64
        failures = ps.validate_inputs(claims, ev, contra, registry())
        self.assertTrue(any("SOURCE_DIGEST_DRIFT" in x for x in failures))

    def test_out_of_range_page_rejected(self):
        claims, contra = contradictions()
        claims[0]["locator"]["page"] = 99
        failures = ps.validate_inputs(claims, evidence(), contra, registry())
        self.assertTrue(any("LOCATOR_PAGE_RANGE" in x for x in failures))

    def test_contradiction_denominator_required(self):
        claims, _ = contradictions()
        contra = {"schema_version": "contradiction-ledger@1", "entries": []}
        failures = ps.validate_inputs(claims, evidence(), contra, registry())
        self.assertIn("CONTRADICTION_DENOMINATOR_EMPTY", failures)

    def test_privacy_field_rejected(self):
        claims, contra = contradictions()
        claims[0]["private_note_body"] = "no"
        failures = ps.validate_inputs(claims, evidence(), contra, registry())
        self.assertTrue(any("PRIVACY_FIELD" in x for x in failures))


if __name__ == "__main__":
    unittest.main()
