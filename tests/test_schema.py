from __future__ import annotations

import json
from pathlib import Path

from replay.schema import ReplayValidationError, load_json_object, load_report, validate_repo_references


ROOT = Path(__file__).resolve().parents[1]


def test_checked_in_reports_validate_against_repo_index() -> None:
    repo_index = load_json_object(ROOT / "config" / "repo_index.yaml")
    for path in [
        ROOT / "examples" / "2026-07-procurement-EXAMPLE.md",
        ROOT / "negotiations" / "2026-07-procurement-01.md",
    ]:
        report = load_report(path)
        validate_repo_references(report, repo_index)
        assert report.redacted is True
        assert len(report.incentive_map) >= 2
        assert len(report.leakages) >= 1
        assert len(report.cross_applications) >= 1


def test_schema_file_is_json_and_requires_redacted_true() -> None:
    schema = json.loads((ROOT / "schemas" / "replay.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["redacted"] == {"const": True}
    assert "cross_applications" in schema["required"]


def test_report_rejects_unknown_repo_slug() -> None:
    report = load_report(ROOT / "examples" / "2026-07-procurement-EXAMPLE.md")
    try:
        validate_repo_references(report, {"repos": [{"slug": "different-repo"}]})
    except ReplayValidationError as exc:
        assert "repo_slug" in str(exc)
    else:
        raise AssertionError("expected repo reference validation to fail")
