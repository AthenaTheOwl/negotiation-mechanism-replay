from __future__ import annotations

from pathlib import Path

from replay.render import render_report
from replay.schema import load_report, parse_report_text


ROOT = Path(__file__).resolve().parents[1]


def test_render_roundtrips_front_matter() -> None:
    report = load_report(ROOT / "examples" / "2026-07-procurement-EXAMPLE.md")
    rendered = render_report(report)
    reparsed = parse_report_text(rendered)
    assert reparsed.to_dict() == report.to_dict()
    for heading in [
        "## Redacted summary",
        "## Incentive map",
        "## Leakage list",
        "## Implied equilibrium",
        "## Cross-application to portfolio repos",
    ]:
        assert heading in rendered
