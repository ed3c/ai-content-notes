from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def load_verifier() -> ModuleType:
    path = ROOT / "tools" / "verify_reference_traceability.py"
    spec = importlib.util.spec_from_file_location("verify_reference_traceability", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def minimal_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    registry = root / "docs" / "reference-registry"
    write_json(
        registry / "reference-index.private.json",
        {
            "references": [
                {
                    "id": "REF-1001",
                    "title": "private source",
                    "url": "https://docs.google.com/document/d/file-a/edit?usp=drivesdk",
                    "external_id": "file-a",
                    "state": "URL_INDEXED",
                }
            ]
        },
    )
    write_json(registry / "reference-index.private.methods.json", {"references": []})
    write_json(
        registry / "context-reference-backfill.json",
        {
            "records": [
                {
                    "ref_id": "CTX-0001",
                    "title": "unmaterialized chat artifact",
                    "url": None,
                    "source_origin": "PRIOR_CONVERSATION_FILE_CONTEXT",
                    "state": "NO_CANONICAL_URL_MATERIALIZED",
                    "trace_status": "UNBOUND",
                }
            ]
        },
    )
    write_json(
        registry / "codexdoc-index.json",
        {
            "folder": {
                "ref_id": "REF-1300",
                "title": "CodexDoc",
                "url": "https://drive.google.com/drive/folders/folder-a",
                "external_id": "folder-a",
                "trace_status": "BOUND",
            },
            "items": [
                {
                    "ref_id": "REF-1301",
                    "title": "bound source",
                    "role": "SOURCE_PROPOSAL",
                    "url": "https://drive.google.com/file/d/source-a/view",
                    "external_id": "source-a",
                    "trace_status": "BOUND",
                    "issues": ["EAS#1"],
                    "prs": ["EAS#21"],
                },
                {
                    "ref_id": "REF-1302",
                    "title": "unbound source",
                    "role": "SOURCE_PROPOSAL",
                    "url": "https://drive.google.com/file/d/source-b/view",
                    "external_id": "source-b",
                    "trace_status": "UNBOUND",
                    "issues": ["AI-CONTENT#61", "AI-CONTENT#62"],
                },
            ],
            "summary": {
                "item_count": 2,
                "bound": 1,
                "partial": 0,
                "unbound": 1,
                "no_implementation_requirement": 0,
                "global_verdict": "PARTIAL_TRACE",
            },
        },
    )
    write_json(
        registry / "repo-directory-index.json",
        {
            "repositories": [
                {
                    "repo_name": "enterprise_agent_system",
                    "path": "enterprise_agent_system/urls.json",
                    "repository_ref_id": "REF-0012",
                    "visibility": "PUBLIC",
                }
            ]
        },
    )
    write_json(
        root / "enterprise_agent_system" / "urls.json",
        {
            "repo_name": "enterprise_agent_system",
            "repository_url": "https://github.com/ed3c/enterprise_agent_system",
            "repository_ref_id": "REF-0012",
            "urls": [],
        },
    )
    return root


def test_current_reference_traceability_graph_is_consistent() -> None:
    verifier = load_verifier()
    report = verifier.build_report(ROOT)
    assert report["overall_status"] == "PASS_WITH_EXTERNAL_PARITY_NOT_EXERCISED"
    assert all(
        check["status"] in {"PASS", "NOT_EXERCISED"}
        for check in report["checks"].values()
    )


def test_codexdoc_denominator_mismatch_fails(tmp_path: Path) -> None:
    verifier = load_verifier()
    root = minimal_repo(tmp_path)
    path = root / "docs" / "reference-registry" / "codexdoc-index.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["summary"]["bound"] = 99
    write_json(path, value)
    report = verifier.build_report(root)
    check = report["checks"]["TR-02-codexdoc-denominator-and-edges"]
    assert check["status"] == "FAIL"
    assert any("summary bound" in failure for failure in check["failures"])


def test_duplicate_external_id_under_different_ref_fails(tmp_path: Path) -> None:
    verifier = load_verifier()
    root = minimal_repo(tmp_path)
    path = root / "docs" / "reference-registry" / "context-reference-backfill.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["records"].append(
        {
            "ref_id": "REF-1999",
            "title": "duplicate file identity",
            "url": "https://docs.google.com/document/d/file-a/edit?usp=drivesdk",
            "external_id": "file-a",
            "source_origin": "TEST",
            "state": "URL_INDEXED",
            "trace_status": "PARTIAL",
        }
    )
    write_json(path, value)
    report = verifier.build_report(root)
    check = report["checks"]["TR-01-reference-identity"]
    assert check["status"] == "FAIL"
    assert any("multiple refs" in failure for failure in check["failures"])


def test_bound_source_without_work_evidence_fails(tmp_path: Path) -> None:
    verifier = load_verifier()
    root = minimal_repo(tmp_path)
    path = root / "docs" / "reference-registry" / "codexdoc-index.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["items"][0].pop("prs")
    write_json(path, value)
    report = verifier.build_report(root)
    check = report["checks"]["TR-02-codexdoc-denominator-and-edges"]
    assert check["status"] == "FAIL"
    assert any("lacks issue plus PR/evidence edge" in failure for failure in check["failures"])


def test_missing_repo_namespace_fails(tmp_path: Path) -> None:
    verifier = load_verifier()
    root = minimal_repo(tmp_path)
    (root / "enterprise_agent_system" / "urls.json").unlink()
    report = verifier.build_report(root)
    check = report["checks"]["TR-03-repo-namespace-coverage"]
    assert check["status"] == "FAIL"
    assert any("namespace missing" in failure for failure in check["failures"])


def test_secret_shaped_query_parameter_fails(tmp_path: Path) -> None:
    verifier = load_verifier()
    root = minimal_repo(tmp_path)
    path = root / "docs" / "reference-registry" / "reference-index.private.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["references"][0]["url"] = "https://example.com/source?access_token=secret"
    write_json(path, value)
    report = verifier.build_report(root)
    check = report["checks"]["TR-04-url-hygiene"]
    assert check["status"] == "FAIL"
    assert any("secret-shaped" in failure for failure in check["failures"])


def test_public_registry_parity_detects_missing_public_repo_ref(tmp_path: Path) -> None:
    verifier = load_verifier()
    root = minimal_repo(tmp_path)
    public = tmp_path / "public.json"
    write_json(public, {"references": [{"id": "REF-0001"}]})
    report = verifier.build_report(root, public_registry_paths=[public])
    check = report["checks"]["TR-06-public-private-parity"]
    assert check["status"] == "FAIL"
    assert any("REF-0012" in failure for failure in check["failures"])
