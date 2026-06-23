from __future__ import annotations

import json
from pathlib import Path

from replay.schema import ReplayReport


def render_report(report: ReplayReport) -> str:
    lines = [
        "---",
        json.dumps(report.to_dict(), indent=2),
        "---",
        "",
        f"# Negotiation Mechanism Replay: {report.id}",
        "",
        "## Redacted summary",
        "",
        report.redacted_summary,
        "",
        "## Incentive map",
        "",
    ]

    for item in report.incentive_map:
        lines.append(
            f"- `{item.actor_role}` optimizes for {item.optimizes_for}; constrained by {item.constrained_by}."
        )

    lines.extend(["", "## Leakage list", ""])
    for leakage in report.leakages:
        tags = ", ".join(leakage.mechanism_tags)
        lines.append(
            "- "
            f"{leakage.kind} from `{leakage.direction['from']}` to `{leakage.direction['to']}` "
            f"({leakage.magnitude_tier}): {leakage.mechanism_one_liner} Tags: {tags}."
        )

    lines.extend(
        [
            "",
            "## Implied equilibrium",
            "",
            f"- Observed behavior: {report.equilibrium.observed_behavior}",
            f"- Stable strategy: {report.equilibrium.stable_strategy}",
            f"- Failure mode: {report.equilibrium.failure_mode}",
            "",
            "## Cross-application to portfolio repos",
            "",
        ]
    )

    for item in report.cross_applications:
        lines.extend(
            [
                f"### {item.repo_slug}",
                "",
                f"- Failing surface: {item.failing_surface}",
                f"- Recommendation: {item.recommendation}",
                "- One-sprint fix:",
            ]
        )
        for fix in item.one_sprint_fix:
            lines.append(f"  - {fix}")
        lines.extend([f"- Confidence: {item.confidence}", ""])

    return "\n".join(lines).rstrip() + "\n"


def write_report(report: ReplayReport, path: str | Path) -> None:
    Path(path).write_text(render_report(report), encoding="utf-8")


_MAGNITUDE_RANK = {"large": 3, "material": 2, "small": 1}
_CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}


def _pad(value: str, width: int) -> str:
    return value if len(value) >= width else value + " " * (width - len(value))


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    out = ["  ".join(_pad(h, widths[i]) for i, h in enumerate(headers))]
    out.append("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in rows:
        out.append("  ".join(_pad(cell, widths[i]) for i, cell in enumerate(row)))
    return out


def render_summary(reports: list[tuple[str, ReplayReport]]) -> str:
    """Render a ranked, readable digest across one or more replay reports.

    Leakages are ranked by magnitude tier; cross-applications by confidence.
    Both rankings feed a single headline finding.
    """
    if not reports:
        return "no replay reports found.\n"

    lines: list[str] = []
    lines.append("negotiation mechanism replay - show")
    lines.append("")
    lines.append(
        f"{len(reports)} replay report(s) loaded from committed artifacts."
    )
    lines.append("")

    # Collect all leakages and cross-applications across reports, with source id.
    leak_rows: list[tuple[int, str, list[str]]] = []
    cross_rows: list[tuple[int, str, list[str]]] = []
    for report_id, report in reports:
        for leak in report.leakages:
            rank = _MAGNITUDE_RANK.get(leak.magnitude_tier, 0)
            direction = f"{leak.direction['from']} -> {leak.direction['to']}"
            leak_rows.append(
                (
                    rank,
                    leak.mechanism_one_liner,
                    [
                        leak.magnitude_tier,
                        report_id,
                        leak.kind,
                        direction,
                        ", ".join(leak.mechanism_tags),
                    ],
                )
            )
        for cross in report.cross_applications:
            rank = _CONFIDENCE_RANK.get(cross.confidence, 0)
            cross_rows.append(
                (
                    rank,
                    cross.failing_surface,
                    [cross.confidence, report_id, cross.repo_slug, cross.failing_surface],
                )
            )

    leak_rows.sort(key=lambda r: (-r[0], r[2][1]))
    cross_rows.sort(key=lambda r: (-r[0], r[2][1]))

    lines.append("## leakages (ranked by magnitude)")
    lines.append("")
    lines.extend(
        _table(
            ["tier", "report", "kind", "direction", "tags"],
            [row[2] for row in leak_rows],
        )
    )
    lines.append("")

    lines.append("## cross-applications (ranked by confidence)")
    lines.append("")
    lines.extend(
        _table(
            ["conf", "report", "repo", "failing surface"],
            [row[2] for row in cross_rows],
        )
    )
    lines.append("")

    # Headline finding: the highest-magnitude leakage, with its sharpest fix.
    lines.append("## headline")
    lines.append("")
    if leak_rows:
        top = leak_rows[0]
        lines.append(
            f"the sharpest leak is {top[2][0]} ({top[2][2]}, {top[2][3]}) "
            f"in {top[2][1]}: {top[1]}"
        )
    if cross_rows:
        top_cross = cross_rows[0]
        lines.append(
            f"highest-confidence cross-apply: {top_cross[2][2]} "
            f"({top_cross[2][0]}) - {top_cross[1]}"
        )
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"
