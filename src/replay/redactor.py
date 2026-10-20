from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CURRENCY_RE = re.compile(
    r"[$€£¥₹]|\b(?:USD|EUR|GBP|INR|JPY|CAD|AUD)\b"
    r"|\b\d[\d,.]*\s*(?:dollars?|euros?|pounds? sterling|rupees?|yen)\b",
    re.IGNORECASE,
)
PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|(?:percent|percentage points?)\b)", re.IGNORECASE)
PRECISE_DATE_RES = [
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),
    re.compile(r"\b\d{1,2}\.\d{1,2}\.\d{4}\b"),
    re.compile(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"[a-z]*\.?\s+\d{1,2}(?:,\s*\d{4})?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b"
    ),
]
DEFAULT_DENYLIST_PATH = Path("config/redact_denylist.yaml")


@dataclass(frozen=True)
class RedactionFinding:
    rule: str
    line: int
    matched_text: str
    message: str


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _term_regex(term: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(term)}(?![A-Za-z0-9_-])", re.IGNORECASE)


class DenylistNotConfiguredError(ValueError):
    """Raised when the gate is asked to certify a file without a deny-list."""


EMPTY_DENYLIST: dict[str, list[str]] = {"named_entities": [], "internal_codenames": []}


def _not_configured(denylist_path: Path, reason: str) -> DenylistNotConfiguredError:
    return DenylistNotConfiguredError(
        f"redaction gate refuses to certify: {reason} ({denylist_path}). "
        "Without it the named-entity and internal-codename checks have nothing "
        "to match, so every counter-party name passes. Copy "
        "config/redact_denylist.yaml.example to config/redact_denylist.yaml "
        "(git-ignored) and list the real names there, or pass --denylist PATH. "
        "To run only the pattern checks (currency, percentages, dates) and "
        "certify nothing about names, pass --no-denylist."
    )


def load_denylist(path: str | Path | None = None, *, required: bool = True) -> dict[str, list[str]]:
    """Load the deny-list; fail closed when it is missing or empty.

    With ``required=False`` a missing file returns empty lists. Only the
    explicit ``--no-denylist`` CLI flag should take that path.
    """
    denylist_path = Path(path) if path else DEFAULT_DENYLIST_PATH
    if not denylist_path.exists():
        if required:
            raise _not_configured(denylist_path, "no deny-list found")
        return {key: [] for key in EMPTY_DENYLIST}
    data = json.loads(denylist_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"denylist must contain an object: {denylist_path}")
    denylist = {
        "named_entities": [str(term) for term in data.get("named_entities", []) if term],
        "internal_codenames": [str(term) for term in data.get("internal_codenames", []) if term],
    }
    if required and not any(denylist.values()):
        raise _not_configured(denylist_path, "the deny-list has no named_entities or internal_codenames")
    return denylist


def scan_text(text: str, denylist: dict[str, Iterable[str]] | None = None) -> list[RedactionFinding]:
    """Scan one string. A missing ``denylist`` checks patterns only."""
    denylist = denylist or EMPTY_DENYLIST
    findings: list[RedactionFinding] = []

    for match in CURRENCY_RE.finditer(text):
        findings.append(
            RedactionFinding("currency-token", _line_number(text, match.start()), match.group(0), "currency token")
        )
    for match in PERCENT_RE.finditer(text):
        findings.append(
            RedactionFinding("percentage-token", _line_number(text, match.start()), match.group(0), "percentage figure")
        )
    for precise_date_re in PRECISE_DATE_RES:
        for match in precise_date_re.finditer(text):
            findings.append(
                RedactionFinding(
                    "specific-date",
                    _line_number(text, match.start()),
                    match.group(0),
                    "date is more precise than negotiation month",
                )
            )

    for rule, message in (
        ("named-entity", "configured counter-party named entity"),
        ("internal-codename", "configured internal codename"),
    ):
        denylist_key = "named_entities" if rule == "named-entity" else "internal_codenames"
        for term in denylist.get(denylist_key, []):
            if not term:
                continue
            for match in _term_regex(str(term)).finditer(text):
                findings.append(RedactionFinding(rule, _line_number(text, match.start()), match.group(0), message))

    return sorted(findings, key=lambda item: (item.line, item.rule, item.matched_text.lower()))


def scan_file(
    path: str | Path,
    denylist_path: str | Path | None = None,
    *,
    require_denylist: bool = True,
) -> list[RedactionFinding]:
    text = Path(path).read_text(encoding="utf-8")
    return scan_text(text, load_denylist(denylist_path, required=require_denylist))


def format_findings(path: str | Path, findings: list[RedactionFinding]) -> list[str]:
    return [
        f"{path}:{finding.line}: {finding.rule}: {finding.matched_text} ({finding.message})"
        for finding in findings
    ]
