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
