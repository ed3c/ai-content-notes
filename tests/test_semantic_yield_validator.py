from __future__ import annotations

import importlib.util
import json
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
        "QG-07",
        "QG-08",
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
