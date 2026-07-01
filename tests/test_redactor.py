from __future__ import annotations

from pathlib import Path

from replay.redactor import scan_file, scan_text


ROOT = Path(__file__).resolve().parents[1]


def rules(text: str) -> set[str]:
    return {finding.rule for finding in scan_text(text)}


def test_checked_in_report_passes_redaction_gate() -> None:
    assert scan_file(ROOT / "negotiations" / "2026-07-procurement-01.md") == []


def test_currency_percentage_and_specific_date_fail() -> None:
    found = rules("The term was USD with 12 percent exposure on 2026-07-14.")
    assert {"currency-token", "percentage-token", "specific-date"} <= found


def test_finding_reports_the_line_of_the_match() -> None:
    # A currency token sits on the second line; the finding must report line 2,
    # so an off-by-one in _line_number would be caught.
    findings = scan_text("clean first line\nthe term was USD here")
    currency = [f for f in findings if f.rule == "currency-token"]
    assert len(currency) == 1
    assert currency[0].line == 2


def test_denylist_terms_fail() -> None:
    found = scan_text(
        "Supplier used CounterpartyName and InternalCodename.",
        {"named_entities": ["CounterpartyName"], "internal_codenames": ["InternalCodename"]},
    )
    assert {item.rule for item in found} == {"named-entity", "internal-codename"}
