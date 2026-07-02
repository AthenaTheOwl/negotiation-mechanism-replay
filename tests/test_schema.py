from __future__ import annotations

import json
from pathlib import Path

import pytest

from replay.schema import (
    ReplayReport,
    ReplayValidationError,
    load_json_object,
    load_report,
    validate_repo_references,
)


ROOT = Path(__file__).resolve().parents[1]


def _valid_report_dict() -> dict:
    """A minimal dict that ReplayReport.from_dict accepts, used as a base to
    mutate one rule at a time in the negative-path tests below."""
    return {
        "id": "2026-07-procurement-01",
        "redacted": True,
        "created_at": "2026-07",
        "redacted_summary": "a redacted summary.",
        "incentive_map": [
            {"actor_role": "buyer", "optimizes_for": "x", "constrained_by": "y"},
            {"actor_role": "seller", "optimizes_for": "x", "constrained_by": "y"},
        ],
        "leakages": [
            {
                "kind": "information",
                "direction": {"from": "buyer", "to": "seller"},
                "magnitude_tier": "material",
                "mechanism_one_liner": "a leak.",
                "mechanism_tags": ["signaling-leakage"],
            }
        ],
        "equilibrium": {
            "observed_behavior": "x",
            "stable_strategy": "y",
            "failure_mode": "z",
        },
        "cross_applications": [
            {
                "repo_slug": "agent-routing-table",
                "failing_surface": "x",
                "recommendation": "y",
                "one_sprint_fix": ["src/a.py: change it"],
                "confidence": "high",
            }
        ],
    }


def test_valid_report_dict_parses() -> None:
    # Guards the negative-path fixture: the base dict must parse, otherwise the
    # rejection tests below would pass for the wrong reason.
    assert ReplayReport.from_dict(_valid_report_dict()).id == "2026-07-procurement-01"


def test_from_dict_rejects_unredacted_report() -> None:
    data = _valid_report_dict()
    data["redacted"] = False
    with pytest.raises(ReplayValidationError, match="redacted must be true"):
        ReplayReport.from_dict(data)


def test_from_dict_rejects_malformed_id() -> None:
    data = _valid_report_dict()
    data["id"] = "nope"
    with pytest.raises(ReplayValidationError, match="id must match"):
        ReplayReport.from_dict(data)


def test_from_dict_rejects_single_item_incentive_map() -> None:
    data = _valid_report_dict()
    data["incentive_map"] = [data["incentive_map"][0]]
    with pytest.raises(ReplayValidationError, match="incentive_map"):
        ReplayReport.from_dict(data)


def test_from_dict_rejects_unknown_leakage_kind() -> None:
    data = _valid_report_dict()
    data["leakages"][0]["kind"] = "unknown-kind"
    with pytest.raises(ReplayValidationError, match="kind"):
        ReplayReport.from_dict(data)


def test_from_dict_accepts_every_valid_leakage_kind() -> None:
    # Pins the accepted set so dropping a real kind (e.g. "option") is caught,
    # which a single unknown-kind rejection test would miss.
    for kind in ("information", "value", "option"):
        data = _valid_report_dict()
        data["leakages"][0]["kind"] = kind
        assert ReplayReport.from_dict(data).leakages[0].kind == kind


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
