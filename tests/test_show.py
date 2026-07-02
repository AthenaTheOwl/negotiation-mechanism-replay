from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

from replay.cli import main
from replay.render import render_summary
from replay.schema import ReplayReport, load_report


ROOT = Path(__file__).resolve().parents[1]


def _report(report_id: str, magnitude_tier: str, one_liner: str) -> ReplayReport:
    """Build a minimal valid report with a single leakage at a chosen tier."""
    return ReplayReport.from_dict(
        {
            "id": report_id,
            "redacted": True,
            "created_at": "2026-07",
            "redacted_summary": "synthetic report for ranking coverage.",
            "incentive_map": [
                {"actor_role": "buyer", "optimizes_for": "x", "constrained_by": "y"},
                {"actor_role": "seller", "optimizes_for": "x", "constrained_by": "y"},
            ],
            "leakages": [
                {
                    "kind": "information",
                    "direction": {"from": "buyer", "to": "seller"},
                    "magnitude_tier": magnitude_tier,
                    "mechanism_one_liner": one_liner,
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
                    "confidence": "medium",
                }
            ],
        }
    )


def test_render_summary_ranks_and_headlines() -> None:
    report = load_report(ROOT / "negotiations" / "2026-07-procurement-01.md")
    out = render_summary([(report.id, report)])

    assert "## leakages (ranked by magnitude)" in out
    assert "## cross-applications (ranked by confidence)" in out
    assert "## headline" in out
    # the single material leak should surface as the headline.
    assert "the sharpest leak is material" in out
    # highest-confidence cross-apply on this report is high (agent-routing-table).
    assert "agent-routing-table (high)" in out


def test_render_summary_orders_cross_applications_by_confidence() -> None:
    report = load_report(ROOT / "negotiations" / "2026-07-procurement-01.md")
    out = render_summary([(report.id, report)])
    lines = out.splitlines()
    # within the cross-application block, the high-confidence row precedes medium.
    high_idx = next(i for i, line in enumerate(lines) if line.startswith("high"))
    medium_idx = next(i for i, line in enumerate(lines) if line.startswith("medium"))
    assert high_idx < medium_idx


def test_render_summary_ranks_leakages_across_magnitude_tiers() -> None:
    # Two reports whose single leakages sit in different magnitude tiers. Every
    # committed report has exactly one leakage, so cross-tier ranking is only
    # exercised when more than one report is passed in.
    small = _report("2026-07-small-01", "small", "the small leak liner.")
    large = _report("2026-07-large-01", "large", "the large leak liner.")
    out = render_summary([(small.id, small), (large.id, large)])
    lines = out.splitlines()

    # In the leakage table, the large-tier row sorts ahead of the small-tier row.
    large_idx = next(i for i, line in enumerate(lines) if line.startswith("large"))
    small_idx = next(i for i, line in enumerate(lines) if line.startswith("small"))
    assert large_idx < small_idx

    # The large leak is the headline, not the small one.
    assert "the sharpest leak is large" in out
    assert "the large leak liner." in out
    assert "the sharpest leak is small" not in out


def test_render_summary_handles_no_reports() -> None:
    assert render_summary([]) == "no replay reports found.\n"


def test_show_cli_no_args_is_offline_and_exits_zero() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["show"])
    assert code == 0
    text = buffer.getvalue()
    assert "negotiation mechanism replay - show" in text
    assert "## headline" in text
