from __future__ import annotations

import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "evals" / "semantic-yield" / "CvRngaQZQ3Y"
REPORT = TARGET / "semantic-validator-report.json"
SCHEMA = ROOT / "schemas" / "semantic-validator-report.schema.json"
CREATED_AT = "2026-08-14T01:15:00Z"


def load_validator() -> ModuleType:
    path = ROOT / "tools" / "validate_semantic_yield_artifacts.py"
    spec = importlib.util.spec_from_file_location(
        "validate_semantic_yield_artifacts",
        path,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def copy_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    repository = tmp_path / "repo"
    target = repository / "evals" / "semantic-yield" / "CvRngaQZQ3Y"
    target.parent.mkdir(parents=True)
    shutil.copytree(TARGET, target)

    prompt = repository / "governance" / "CARD_PROTOCOL_V7_1.md"
    prompt.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "governance" / "CARD_PROTOCOL_V7_1.md", prompt)

    schema = repository / "schemas" / SCHEMA.name
    schema.parent.mkdir(parents=True)
    shutil.copy2(SCHEMA, schema)
    return repository, target, schema


def update_manifest_blob(
    validator: ModuleType,
    target: Path,
    stable_id: str,
) -> None:
    manifest_path = target / "card-manifest.json"
    manifest = load_json(manifest_path)
    cards = manifest["cards"]
    assert isinstance(cards, list)
    for contract in cards:
        assert isinstance(contract, dict)
        if contract["stable_id"] == stable_id:
            path = target / str(contract["path"])
            contract["git_blob_sha1"] = validator.git_blob_sha1(path)
            break
    else:
        raise AssertionError(f"missing manifest card: {stable_id}")
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_persisted_semantic_validator_report_is_current() -> None:
    validator = load_validator()
    report = validator.build_report(
        ROOT,
        TARGET,
        created_at=CREATED_AT,
        schema_path=SCHEMA,
    )
    assert report == load_json(REPORT)
    assert report["overall_status"] == (
        "PASS_WITH_DEFERRED_VISUAL_AND_PARTIAL_QG"
    )
    assert report["hg"]["HG-03"]["status"] == "DEFERRED"
    assert set(report["qg_subset"]) == {
        "QG-01",
        "QG-07",
        "QG-08",
        "QG-09",
        "QG-10",
        "QG-11",
        "QG-12",
        "QG-16",
        "QG-18",
        "QG-20",
        "QG-21",
        "QG-23",
    }


def test_sequence_only_permanent_id_fails_closed(tmp_path: Path) -> None:
    validator = load_validator()
    repository, target, schema = copy_fixture(tmp_path)

    manifest_path = target / "card-manifest.json"
    manifest = load_json(manifest_path)
    first = manifest["cards"][0]
    assert isinstance(first, dict)
    path = target / str(first["path"])
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "### N-autonomy-trace-mining｜",
        "### N-01｜",
        1,
    ).replace(
        '"stable_id": "N-autonomy-trace-mining"',
        '"stable_id": "N-01"',
        1,
    )
    path.write_text(text, encoding="utf-8")
    first["stable_id"] = "N-01"
    manifest["card_order"][0] = "N-01"
    first["git_blob_sha1"] = validator.git_blob_sha1(path)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report = validator.build_report(
        repository,
        target,
        created_at=CREATED_AT,
        schema_path=schema,
    )
    assert report["overall_status"] == "FAIL"
    identity = report["checks"]["SV-02-identity-and-link-integrity"]
    assert identity["status"] == "FAIL"
    assert any("sequence-only" in item for item in identity["failures"])


def test_unsupported_precision_fails_closed(tmp_path: Path) -> None:
    validator = load_validator()
    repository, target, schema = copy_fixture(tmp_path)

    stable_id = "T-trace-judge-comparison"
    path = target / "cards" / f"{stable_id}.md"
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\nUnsupported estimate: $80/day.\n",
        encoding="utf-8",
    )
    update_manifest_blob(validator, target, stable_id)

    report = validator.build_report(
        repository,
        target,
        created_at=CREATED_AT,
        schema_path=schema,
    )
    assert report["overall_status"] == "FAIL"
    precision = report["checks"]["SV-07-unknown-safe-precision"]
    assert precision["status"] == "FAIL"
    assert any("unsupported precision" in item for item in precision["failures"])


def test_an_unanchored_source_statement_fails_closed(tmp_path: Path) -> None:
    """QG-01: an asserting claim kind may not stand without an anchor."""
    validator = load_validator()
    repository, target, schema = copy_fixture(tmp_path)

    path = target / "cards" / "D-trace-scale-bottleneck.md"
    text = path.read_text(encoding="utf-8")
    stripped = re.sub(r"\[\[EV-[A-Za-z0-9._:-]+\]\]", "(anchor removed)", text)
    assert stripped != text
    path.write_text(stripped, encoding="utf-8")

    report = validator.build_report(
        repository, target, created_at=CREATED_AT, schema_path=schema
    )
    check = report["checks"]["SV-13-evidence-anchor-coverage"]
    assert check["status"] == "FAIL"
    assert any("SOURCE_STATEMENT without an evidence anchor" in item for item in check["failures"])
    assert report["qg_subset"]["QG-01"]["status"] == "FAIL"


def test_a_dropped_boundary_fails_closed(tmp_path: Path) -> None:
    """QG-09: a conflict or boundary is never silently dropped."""
    validator = load_validator()
    repository, target, schema = copy_fixture(tmp_path)

    path = target / "cards" / "C-model-harness-task-fit.md"
    text = path.read_text(encoding="utf-8")
    stripped = re.sub(r"- \*\*反證／限制\*\*[：:].*", "", text)
    assert stripped != text
    path.write_text(stripped, encoding="utf-8")

    report = validator.build_report(
        repository, target, created_at=CREATED_AT, schema_path=schema
    )
    check = report["checks"]["SV-14-conflict-preservation"]
    assert check["status"] == "FAIL"
    assert any("carries no 反證／限制" in item for item in check["failures"])
    assert report["qg_subset"]["QG-09"]["status"] == "FAIL"


def test_series_that_own_their_boundary_are_not_asked_twice() -> None:
    """P, V and K state the boundary through fields SV-12 already requires."""
    validator = load_validator()
    report = validator.build_report(
        ROOT, TARGET, created_at=CREATED_AT, schema_path=SCHEMA
    )
    assert report["checks"]["SV-14-conflict-preservation"]["status"] == "PASS"
    assert validator.SERIES_OWNED_LIMIT_FIELDS == {"P", "V", "K"}
    # The P card genuinely has no 反證／限制 line; it carries Rollback and
    # Failure Handling instead, which is why the exemption is not cosmetic.
    practice = (TARGET / "cards" / "P-trace-driven-improvement-cycle.md").read_text(
        encoding="utf-8"
    )
    assert "**反證／限制**" not in practice
    assert "**Rollback**" in practice and "**Failure Handling**" in practice
