from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

from replay.cli import main
from replay.render import render_summary
from replay.schema import load_report


ROOT = Path(__file__).resolve().parents[1]


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
