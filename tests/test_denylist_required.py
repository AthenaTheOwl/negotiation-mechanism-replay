from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from replay.cli import main
from replay.redactor import DenylistNotConfiguredError, load_denylist, scan_file


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "redact_denylist.synthetic.json"
REPORTS = [
    ROOT / "examples" / "2026-07-procurement-EXAMPLE.md",
    ROOT / "negotiations" / "2026-07-procurement-01.md",
]


def _run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


@pytest.fixture
def no_default_denylist(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    # The default deny-list path is cwd-relative; an empty cwd has none.
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_missing_denylist_refuses(no_default_denylist: Path) -> None:
    with pytest.raises(DenylistNotConfiguredError, match="--no-denylist"):
        load_denylist()
    with pytest.raises(DenylistNotConfiguredError):
        scan_file(REPORTS[1])


def test_explicit_missing_path_refuses(tmp_path: Path) -> None:
    with pytest.raises(DenylistNotConfiguredError):
        load_denylist(tmp_path / "nope.json")


def test_denylist_with_no_terms_refuses(tmp_path: Path) -> None:
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"named_entities": [], "internal_codenames": [""]}), encoding="utf-8")
    with pytest.raises(DenylistNotConfiguredError, match="no named_entities"):
        load_denylist(empty)


def test_not_required_returns_empty_lists(no_default_denylist: Path) -> None:
    assert load_denylist(required=False) == {"named_entities": [], "internal_codenames": []}


def test_cli_refuses_to_certify_without_denylist(no_default_denylist: Path) -> None:
    code, out, err = _run(["redact-check", *map(str, REPORTS)])
    assert code == 2
    assert out == ""  # nothing was certified
    assert "refuses to certify" in err and "--no-denylist" in err


def test_cli_no_denylist_flag_runs_patterns_only(no_default_denylist: Path) -> None:
    named = no_default_denylist / "named.md"
    named.write_text("Synthetic Counterparty Ltd held the fallback.\n", encoding="utf-8")
    code, out, err = _run(["redact-check", "--no-denylist", str(named)])
    assert code == 0
    assert "patterns only" in out
    assert "named-entity and internal-codename checks are skipped" in err


def test_cli_with_synthetic_denylist_catches_named_entity(no_default_denylist: Path) -> None:
    named = no_default_denylist / "named.md"
    named.write_text("Synthetic Counterparty Ltd held the PROJECT-PLACEHOLDER slot.\n", encoding="utf-8")
    code, _out, err = _run(["redact-check", "--denylist", str(FIXTURE), str(named)])
    assert code == 1
    assert "named-entity: Synthetic Counterparty Ltd" in err
    assert "internal-codename: PROJECT-PLACEHOLDER" in err


def test_cli_committed_reports_pass_with_synthetic_denylist() -> None:
    code, out, _err = _run(["redact-check", "--denylist", str(FIXTURE), *map(str, REPORTS)])
    assert code == 0
    assert out.count("ok: ") == len(REPORTS)


def test_cli_new_refuses_draft_without_denylist(no_default_denylist: Path) -> None:
    draft = no_default_denylist / "draft.md"
    draft.write_text("A buyer exposed fallback uncertainty.\n", encoding="utf-8")
    code, _out, err = _run(["new", "--negotiation-id", "2026-07-procurement-02", "--draft-path", str(draft)])
    assert code == 2
    assert "refuses to certify" in err
    assert not (no_default_denylist / "negotiations").exists()
