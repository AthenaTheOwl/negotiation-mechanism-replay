from __future__ import annotations

from pathlib import Path

from replay.matcher import load_repo_index, match_cross_applications
from replay.schema import load_report


ROOT = Path(__file__).resolve().parents[1]


def test_cross_apply_uses_tag_overlap() -> None:
    report = load_report(ROOT / "negotiations" / "2026-07-procurement-01.md")
    repo_index = load_repo_index(ROOT / "config" / "repo_index.yaml")
    candidates = match_cross_applications(report, repo_index)
    slugs = {candidate["repo_slug"] for candidate in candidates}
    assert "agent-routing-table" in slugs
    assert "prompt-budget-ledger" in slugs
    assert all(candidate["one_sprint_fix"][0].count(":") >= 1 for candidate in candidates)
