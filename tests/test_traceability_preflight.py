from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def load_verifier() -> ModuleType:
    path = ROOT / "tools" / "verify_traceability_preflight.py"
    spec = importlib.util.spec_from_file_location("verify_traceability_preflight", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def current_value() -> dict:
    path = ROOT / "docs" / "reference-registry" / "implementation-preflight.json"
    return json.loads(path.read_text(encoding="utf-8"))


def atom(value: dict, atom_id: str) -> dict:
    return next(item for item in value["atoms"] if item["id"] == atom_id)


def test_current_preflight_is_consistent() -> None:
    verifier = load_verifier()
    assert verifier.validate(current_value()) == []


def test_missing_owner_fails() -> None:
    verifier = load_verifier()
    value = deepcopy(current_value())
    atom(value, "I0")["owner"] = ""
    assert any("I0 missing owner" in error for error in verifier.validate(value))


def test_google_projection_cannot_be_marked_ready_early() -> None:
    verifier = load_verifier()
    value = deepcopy(current_value())
    atom(value, "I3")["state"] = "READY_TO_START"
    assert any("I3 must remain blocked" in error for error in verifier.validate(value))


def test_google_projection_requires_all_generic_dependencies() -> None:
    verifier = load_verifier()
    value = deepcopy(current_value())
    atom(value, "I3")["start_dependencies"].remove("ed3c/kotlin-auto-webview#123")
    assert any("I3 missing required" in error for error in verifier.validate(value))


def test_product_projection_cannot_drop_source_contract_dependency() -> None:
    verifier = load_verifier()
    value = deepcopy(current_value())
    atom(value, "I4")["start_dependencies"] = []
    assert any("I4 missing I0 dependency" in error for error in verifier.validate(value))


def test_atom_without_negative_control_fails() -> None:
    verifier = load_verifier()
    value = deepcopy(current_value())
    atom(value, "I1")["negative_controls"] = []
    assert any("I1 missing negative controls" in error for error in verifier.validate(value))


def test_global_convergence_cannot_omit_first_wave() -> None:
    verifier = load_verifier()
    value = deepcopy(current_value())
    atom(value, "G0")["start_dependencies"].remove("E1")
    assert any("G0 missing first-wave" in error for error in verifier.validate(value))


def test_exact_path_overlap_fails() -> None:
    verifier = load_verifier()
    value = deepcopy(current_value())
    atom(value, "I1")["planned_paths"].append(atom(value, "I0")["planned_paths"][0])
    assert any("exact path lease overlap" in error for error in verifier.validate(value))


def test_external_authority_cannot_disappear() -> None:
    verifier = load_verifier()
    value = deepcopy(current_value())
    value["human_external_authority"] = []
    assert any("human_external_authority" in error for error in verifier.validate(value))
