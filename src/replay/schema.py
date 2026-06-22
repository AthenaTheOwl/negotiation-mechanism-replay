from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^\d{4}-\d{2}-[a-z0-9-]+-\d{2}$")
MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
ROLE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
FIX_RE = re.compile(r"^[A-Za-z0-9_./-]+: .+")


class ReplayValidationError(ValueError):
    """Raised when a replay report violates the repository contract."""


def _string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ReplayValidationError(f"{key} must be a non-empty string")
    return value


def _list(data: dict[str, Any], key: str, min_items: int = 0) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list) or len(value) < min_items:
        raise ReplayValidationError(f"{key} must be a list with at least {min_items} item(s)")
    return value


def _choice(value: str, key: str, choices: set[str]) -> str:
    if value not in choices:
        raise ReplayValidationError(f"{key} must be one of {sorted(choices)}")
    return value


def _role(value: str, key: str) -> str:
    if not ROLE_RE.match(value):
        raise ReplayValidationError(f"{key} must be a role slug, not a named entity")
    return value


@dataclass(frozen=True)
class IncentiveEntry:
    actor_role: str
    optimizes_for: str
    constrained_by: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IncentiveEntry":
        return cls(
            actor_role=_role(_string(data, "actor_role"), "actor_role"),
            optimizes_for=_string(data, "optimizes_for"),
            constrained_by=_string(data, "constrained_by"),
        )


@dataclass(frozen=True)
class LeakageEntry:
    kind: str
    direction: dict[str, str]
    magnitude_tier: str
    mechanism_one_liner: str
    mechanism_tags: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LeakageEntry":
        direction = data.get("direction")
        if not isinstance(direction, dict):
            raise ReplayValidationError("direction must be an object with from and to")
        from_role = _role(_string(direction, "from"), "direction.from")
        to_role = _role(_string(direction, "to"), "direction.to")
        tags = _list(data, "mechanism_tags", min_items=1)
        if not all(isinstance(tag, str) and tag.strip() for tag in tags):
            raise ReplayValidationError("mechanism_tags must contain non-empty strings")
        return cls(
            kind=_choice(_string(data, "kind"), "kind", {"information", "value", "option"}),
            direction={"from": from_role, "to": to_role},
            magnitude_tier=_choice(
                _string(data, "magnitude_tier"),
                "magnitude_tier",
                {"small", "material", "large"},
            ),
            mechanism_one_liner=_string(data, "mechanism_one_liner"),
            mechanism_tags=list(tags),
        )


@dataclass(frozen=True)
class Equilibrium:
    observed_behavior: str
    stable_strategy: str
    failure_mode: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Equilibrium":
        if not isinstance(data, dict):
            raise ReplayValidationError("equilibrium must be an object")
        return cls(
            observed_behavior=_string(data, "observed_behavior"),
            stable_strategy=_string(data, "stable_strategy"),
            failure_mode=_string(data, "failure_mode"),
        )


@dataclass(frozen=True)
class CrossApplication:
    repo_slug: str
    failing_surface: str
    recommendation: str
    one_sprint_fix: list[str]
    confidence: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CrossApplication":
        fixes = _list(data, "one_sprint_fix", min_items=1)
        if not all(isinstance(fix, str) and FIX_RE.match(fix) for fix in fixes):
            raise ReplayValidationError("one_sprint_fix items must be file-level changes")
        return cls(
            repo_slug=_role(_string(data, "repo_slug"), "repo_slug"),
            failing_surface=_string(data, "failing_surface"),
            recommendation=_string(data, "recommendation"),
            one_sprint_fix=list(fixes),
            confidence=_choice(_string(data, "confidence"), "confidence", {"low", "medium", "high"}),
        )


@dataclass(frozen=True)
class ReplayReport:
    id: str
    redacted: bool
    created_at: str
    redacted_summary: str
    incentive_map: list[IncentiveEntry]
    leakages: list[LeakageEntry]
    equilibrium: Equilibrium
    cross_applications: list[CrossApplication]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReplayReport":
        report_id = _string(data, "id")
        if not ID_RE.match(report_id):
            raise ReplayValidationError("id must match YYYY-MM-<context>-<nn>")
        if data.get("redacted") is not True:
            raise ReplayValidationError("redacted must be true")
        created_at = _string(data, "created_at")
        if not MONTH_RE.match(created_at):
            raise ReplayValidationError("created_at must be YYYY-MM")
        return cls(
            id=report_id,
            redacted=True,
            created_at=created_at,
            redacted_summary=_string(data, "redacted_summary"),
            incentive_map=[
                IncentiveEntry.from_dict(item) for item in _list(data, "incentive_map", min_items=2)
            ],
            leakages=[LeakageEntry.from_dict(item) for item in _list(data, "leakages", min_items=1)],
            equilibrium=Equilibrium.from_dict(data.get("equilibrium")),
            cross_applications=[
                CrossApplication.from_dict(item)
                for item in _list(data, "cross_applications", min_items=1)
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def extract_front_matter(text: str) -> tuple[dict[str, Any], str]:
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0] != "---":
        raise ReplayValidationError("report must start with JSON front matter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ReplayValidationError("report front matter is not closed") from exc
    front_matter = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])
    try:
        data = json.loads(front_matter)
    except json.JSONDecodeError as exc:
        raise ReplayValidationError(f"front matter must be JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ReplayValidationError("front matter must decode to an object")
    return data, body


def parse_report_text(text: str) -> ReplayReport:
    data, _body = extract_front_matter(text)
    return ReplayReport.from_dict(data)


def load_report(path: str | Path) -> ReplayReport:
    return parse_report_text(Path(path).read_text(encoding="utf-8"))


def load_json_object(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ReplayValidationError(f"{path} must contain a JSON object")
    return data


def validate_repo_references(report: ReplayReport, repo_index: dict[str, Any]) -> None:
    repos = repo_index.get("repos")
    if not isinstance(repos, list):
        raise ReplayValidationError("repo index must contain repos[]")
    slugs = {repo.get("slug") for repo in repos if isinstance(repo, dict)}
    for item in report.cross_applications:
        if item.repo_slug not in slugs:
            raise ReplayValidationError(f"cross_application repo_slug not in repo_index: {item.repo_slug}")
