from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from source_registry import git_blob_sha1  # noqa: E402

PROMPT = ROOT / "governance/CARD_PROTOCOL_V7_1.md"
POINTER = ROOT / "governance/CARD_PROTOCOL_CURRENT.json"
EVAL_DIR = ROOT / "evals/prompt-ab/v7_0-v7_1"
EXPECTED_PROMPT_BLOB = "7f3019f4b41a90728cd48a523d742c7c59721bf6"


def load_evaluator() -> ModuleType:
    path = ROOT / "tools/evaluate_prompt_ab.py"
    spec = importlib.util.spec_from_file_location("evaluate_prompt_ab", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(instance: object, schema_name: str) -> list[str]:
    schema = load_json(ROOT / "schemas" / schema_name)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in sorted(validator.iter_errors(instance), key=str)]


def test_v7_1_prompt_is_locked_without_prompt_rewrite() -> None:
    pointer = load_json(POINTER)
    assert pointer["canonical_path"] == "governance/CARD_PROTOCOL_V7_1.md"
    assert pointer["git_blob_sha1"] == EXPECTED_PROMPT_BLOB
    assert pointer["immutable_prompt_payload"] is True
    assert git_blob_sha1(PROMPT.read_bytes()) == EXPECTED_PROMPT_BLOB


def test_v7_1_prompt_contains_dual_plane_and_all_gates() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")
    markers = [
        "Evidence-First / Narrative-Alive / Dual-Plane Cyberpunk Edition",
        "COMPILE_ORDER: EVIDENCE_FIRST",
        "RENDER_ORDER: TASK_VALUE_FIRST",
        "RENDER_MODE: PAYLOAD_FIRST",
        "SOURCE_DEPENDENCY_CHECK: ON",
        "ANTI_FRAGMENTATION: ON",
        "QG-24",
        "Idempotency",
        "不得讓 v7.1 輸出比 v6.6 更難讀",
    ]
    for marker in markers:
        assert marker in prompt


def test_saved_prompt_ab_result_is_deterministic_and_v7_1_wins() -> None:
    evaluator = load_evaluator()
    actual = evaluator.build_result(
        EVAL_DIR / "fixture.json",
        EVAL_DIR / "output-a-v7.0.md",
        EVAL_DIR / "output-b-v7.1.md",
        EVAL_DIR / "run.json",
    )
    persisted = load_json(EVAL_DIR / "result.json")
    assert actual == persisted
    assert actual["a"]["deterministic_score_0_to_100"] == 60
    assert actual["b"]["deterministic_score_0_to_100"] == 100
    assert actual["delta_b_minus_a"] == 40
    assert actual["verdict"] == "B_OUTPERFORMS_ON_THIS_SMOKE_FIXTURE"


def test_ab_preserves_fidelity_and_test_honesty_in_both_arms() -> None:
    result = load_json(EVAL_DIR / "result.json")
    for arm in ("a", "b"):
        checks = result[arm]["checks"]
        assert checks["shadow_evidence_recall"]["pass"] is True
        assert checks["locator_integrity"]["pass"] is True
        assert checks["test_honesty"]["pass"] is True
        assert checks["source_independence"]["pass"] is True
    assert result["a"]["checks"]["payload_first"]["pass"] is False
    assert result["b"]["checks"]["payload_first"]["pass"] is True
    assert result["a"]["checks"]["reader_efficiency"]["visible_admin_metadata_ratio"] == 0.393
    assert result["b"]["checks"]["reader_efficiency"]["visible_admin_metadata_ratio"] == 0


def test_v7_1_contract_schemas_and_templates_validate() -> None:
    pairs = [
        ("COMPILER_STATE_TEMPLATE_V7_1.json", "compiler-state-v7.1.schema.json"),
        ("SOURCE_MANIFEST_TEMPLATE_V7_1.json", "source-manifest.schema.json"),
        ("ASSERTION_REPORT_TEMPLATE_V7_1.json", "assertion-report-v7.1.schema.json"),
        ("CARD_PATCH_TEMPLATE_V7_1.json", "card-patch-v7.1.schema.json"),
    ]
    for template_name, schema_name in pairs:
        assert validate(load_json(ROOT / "templates" / template_name), schema_name) == []
    assert validate(load_json(EVAL_DIR / "result.json"), "prompt-ab-result.schema.json") == []


def test_note_template_is_payload_first_and_hides_full_admin_metadata() -> None:
    template = (ROOT / "templates/NOTE_TEMPLATE_V7_1.md").read_text(encoding="utf-8")
    visible = re.sub(r"<!--.*?-->", "", template, flags=re.DOTALL)
    assert visible.index("**核心命題**") < visible.index("**證據與狀態**")
    assert "**Canonical Key**" not in visible
    assert "<!-- CARD_META" in template
    assert EXPECTED_PROMPT_BLOB in template


def test_operational_entrypoints_select_v7_1_without_erasing_baselines() -> None:
    for path in ("AGENTS.md", "CLAUDE.md", "README.md", "INTEGRATION_REQUIREMENTS.md"):
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "CARD_PROTOCOL_CURRENT.json" in text
        assert "CARD_PROTOCOL_V7_1.md" in text
    assert (ROOT / "governance/CARD_PROTOCOL_V7_0.md").exists()
    assert (ROOT / "governance/CARD_PROTOCOL_V6_6.md").exists()
