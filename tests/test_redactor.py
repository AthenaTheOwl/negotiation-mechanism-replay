from __future__ import annotations

from pathlib import Path

from replay.redactor import scan_file, scan_text


ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_DENYLIST = ROOT / "tests" / "fixtures" / "redact_denylist.synthetic.json"


def rules(text: str) -> set[str]:
    return {finding.rule for finding in scan_text(text)}


def test_checked_in_report_passes_redaction_gate() -> None:
    assert scan_file(ROOT / "negotiations" / "2026-07-procurement-01.md", SYNTHETIC_DENYLIST) == []


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


def test_percent_sign_fails() -> None:
    for text in ("a 12% discount", "cut by 12%.", "12%", "(15%)", "15 %"):
        assert "percentage-token" in rules(text), text


def test_percent_sign_before_space_period_paren_or_end_fails() -> None:
    # A trailing \b after '%' needs a word character next, so each of these
    # passed the gate while '12 percent' was caught.
    for text in ("12%", "(12%)", "0.5%.", "The fee was 12% of spend."):
        assert "percentage-token" in rules(text), text
    assert "percentage-token" in rules("12 percent")


def test_currency_symbols_and_names_fail() -> None:
    for text in ("paid €400", "paid £400", "¥300", "paid ₹400", "paid 400 euros", "paid 400 dollars"):
        assert "currency-token" in rules(text), text


def test_day_first_and_dotted_dates_fail() -> None:
    for text in ("14 July 2026", "the 14th of July", "18 Oct 2026", "18.10.2026", "Oct. 18"):
        assert "specific-date" in rules(text), text


def test_month_year_and_lowercase_may_pass() -> None:
    assert rules("The replay covers July 2026.") == set()
    assert rules("Step 2 may reveal the buyer's urgency.") == set()
