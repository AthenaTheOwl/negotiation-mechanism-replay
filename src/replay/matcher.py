from __future__ import annotations

from pathlib import Path
from typing import Any

from replay.schema import ReplayReport, ReplayValidationError, load_json_object


def load_repo_index(path: str | Path = "config/repo_index.yaml") -> dict[str, Any]:
    repo_index = load_json_object(path)
    repos = repo_index.get("repos")
    if not isinstance(repos, list):
        raise ReplayValidationError("repo index must contain repos[]")
    return repo_index


def match_cross_applications(report: ReplayReport, repo_index: dict[str, Any]) -> list[dict[str, Any]]:
    leakage_tags = {tag for leakage in report.leakages for tag in leakage.mechanism_tags}
    candidates: list[dict[str, Any]] = []

    for repo in repo_index.get("repos", []):
        if not isinstance(repo, dict):
            continue
        slug = repo.get("slug")
        surfaces = set(repo.get("mechanism_surfaces", []))
        if not isinstance(slug, str):
            continue
        for tag in sorted(leakage_tags & surfaces):
            change = _change_for_tag(repo, tag)
            if not change:
                continue
            candidates.append(
                {
                    "repo_slug": slug,
                    "matched_tags": [tag],
                    "failing_surface": f"{tag} on {slug}",
                    "recommendation": f"Constrain {change['file']} so it can {change['change']}.",
                    "one_sprint_fix": [f"{change['file']}: {change['change']}"],
                    "confidence": "medium",
                }
            )

    return candidates


def _change_for_tag(repo: dict[str, Any], tag: str) -> dict[str, str] | None:
    for change in repo.get("candidate_changes", []):
        if isinstance(change, dict) and change.get("tag") == tag:
            file_name = change.get("file")
            change_text = change.get("change")
            if isinstance(file_name, str) and isinstance(change_text, str):
                return {"file": file_name, "change": change_text}
    return None
