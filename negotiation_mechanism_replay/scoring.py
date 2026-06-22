"""Cross-application scoring helpers for the contract package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from replay.matcher import load_repo_index, match_cross_applications
from replay.schema import ReplayReport, load_report


ReportInput = ReplayReport | str | Path
RepoIndexInput = dict[str, Any] | str | Path


def score_cross_applications(
    report: ReportInput,
    repo_index: RepoIndexInput = "config/repo_index.yaml",
) -> list[dict[str, Any]]:
    loaded_report = load_report(report) if isinstance(report, (str, Path)) else report
    loaded_index = load_repo_index(repo_index) if isinstance(repo_index, (str, Path)) else repo_index
    return match_cross_applications(loaded_report, loaded_index)


__all__ = ["load_repo_index", "match_cross_applications", "score_cross_applications"]
