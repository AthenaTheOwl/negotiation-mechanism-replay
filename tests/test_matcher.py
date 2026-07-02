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

    # Every generated candidate carries the hardcoded confidence. render_summary
    # ranks cross-applications by confidence, so a silent flip would reorder them
    # without any other test noticing.
    assert all(candidate["confidence"] == "medium" for candidate in candidates)

    # Pin the failing_surface and recommendation f-string shapes for a known
    # tag/repo pairing so the wording cannot drift undetected.
    routing = next(c for c in candidates if c["repo_slug"] == "agent-routing-table")
    assert routing["matched_tags"] == ["signaling-leakage"]
    assert routing["failing_surface"] == "signaling-leakage on agent-routing-table"
    assert routing["recommendation"] == (
        "Constrain src/router/handoff_policy.py so it can "
        "drop urgency and preference fields from outbound handoff payloads."
    )
