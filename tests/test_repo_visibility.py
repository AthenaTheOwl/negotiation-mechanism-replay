from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from replay.cli import main
from replay.matcher import load_repo_index, match_cross_applications
from replay.render import render_report, render_summary
from replay.schema import (
    ReplayValidationError,
    extract_front_matter,
    load_report,
    repo_visibility,
    validate_repo_references,
)


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "config" / "repo_index.yaml"
REPORTS = [
    ROOT / "examples" / "2026-07-procurement-EXAMPLE.md",
    ROOT / "negotiations" / "2026-07-procurement-01.md",
]
EXTERNAL = "(external: private or unpublished, not in the public portfolio)"


def _run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


def test_every_index_entry_declares_visibility() -> None:
    visibility = repo_visibility(load_repo_index(INDEX))
    # None of the five targets is a published repo in the owner's portfolio.
    assert visibility == {
        "agent-routing-table": "external",
        "eval-harness-lab": "external",
        "prompt-budget-ledger": "external",
        "permission-boundary-kit": "external",
        "procurement-simulator": "external",
    }


def test_index_entry_without_visibility_is_rejected(tmp_path: Path) -> None:
    index = tmp_path / "repo_index.yaml"
    index.write_text(json.dumps({"repos": [{"slug": "agent-routing-table"}]}), encoding="utf-8")
    with pytest.raises(ReplayValidationError, match="must declare visibility"):
        load_repo_index(index)


@pytest.mark.parametrize("path", REPORTS, ids=lambda p: p.name)
def test_committed_reports_label_every_external_target(path: Path) -> None:
    repo_index = load_repo_index(INDEX)
    report = load_report(path)
    _front_matter, body = extract_front_matter(path.read_text(encoding="utf-8"))
    validate_repo_references(report, repo_index, body)
    for item in report.cross_applications:
        assert f"### {item.repo_slug} {EXTERNAL}" in body.splitlines()


def test_validate_rejects_an_unlabeled_external_heading() -> None:
    path = REPORTS[1]
    report = load_report(path)
    _front_matter, body = extract_front_matter(path.read_text(encoding="utf-8"))
    bare = body.replace(f" {EXTERNAL}", "")
    with pytest.raises(ReplayValidationError, match="heading must read"):
        validate_repo_references(report, load_repo_index(INDEX), bare)


def test_render_and_matcher_label_external_targets() -> None:
    repo_index = load_repo_index(INDEX)
    visibility = repo_visibility(repo_index)
    report = load_report(REPORTS[1])
    assert f"### agent-routing-table {EXTERNAL}" in render_report(report, visibility)
    candidates = match_cross_applications(report, repo_index)
    assert candidates and all(c["repo_visibility"] == "external" for c in candidates)
    summary = render_summary([(report.id, report)], visibility)
    assert "agent-routing-table [external]" in summary
    assert "no public link to follow" in summary


def test_cli_show_and_validate_use_the_labels(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)
    code, out, _err = _run(["show"])
    assert code == 0
    assert "highest-confidence cross-apply: agent-routing-table [external] (high)" in out
    code, out, _err = _run(["validate"])
    assert code == 0
    assert out.count("ok: ") == len(REPORTS)
