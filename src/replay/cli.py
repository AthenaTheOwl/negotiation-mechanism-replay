from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from replay.matcher import load_repo_index, match_cross_applications
from replay.redactor import format_findings, scan_file
from replay.render import render_report, render_summary, write_report
from replay.schema import (
    CrossApplication,
    Equilibrium,
    IncentiveEntry,
    LeakageEntry,
    ReplayReport,
    ReplayValidationError,
    load_json_object,
    load_report,
    validate_repo_references,
)


ROOT = Path.cwd()
PRIVATE_DIRS = [ROOT / "data" / "raw", ROOT / "data" / "private"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="replay")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="create a redacted replay skeleton")
    new_parser.add_argument("--negotiation-id", required=True)
    new_parser.add_argument("--draft-path")
    new_parser.add_argument("--force", action="store_true")

    cross_parser = subparsers.add_parser("cross-apply", help="emit repo-index matches for a replay")
    cross_parser.add_argument("--negotiation-id", required=True)
    cross_parser.add_argument("--repo-index", default="config/repo_index.yaml")

    render_parser = subparsers.add_parser("render", help="render a replay from front matter")
    render_parser.add_argument("--negotiation-id", required=True)

    redact_parser = subparsers.add_parser("redact-check", help="run the redaction gate")
    redact_parser.add_argument("paths", nargs="*")
    redact_parser.add_argument("--denylist")

    validate_parser = subparsers.add_parser("validate", help="validate replay schema and repo references")
    validate_parser.add_argument("paths", nargs="*")
    validate_parser.add_argument("--repo-index", default="config/repo_index.yaml")

    show_parser = subparsers.add_parser(
        "show", help="print a ranked, readable digest of committed replay reports"
    )
    show_parser.add_argument("paths", nargs="*")

    args = parser.parse_args(argv)
    try:
        if args.command == "new":
            return _new(args)
        if args.command == "cross-apply":
            return _cross_apply(args)
        if args.command == "render":
            report = load_report(_report_path(args.negotiation_id))
            sys.stdout.write(render_report(report))
            return 0
        if args.command == "redact-check":
            return _redact_check(args.paths, args.denylist)
        if args.command == "validate":
            return _validate(args.paths, args.repo_index)
        if args.command == "show":
            return _show(args.paths)
    except (ReplayValidationError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


def _new(args: argparse.Namespace) -> int:
    output_path = _report_path(args.negotiation_id)
    _guard_public_path(output_path)
    if output_path.exists() and not args.force:
        raise ReplayValidationError(f"refusing to overwrite existing report: {output_path}")

    summary = "A redacted negotiation event exposed a role-level incentive mismatch."
    if args.draft_path:
        draft_path = Path(args.draft_path)
        _guard_public_path(draft_path)
        findings = scan_file(draft_path)
        if findings:
            for line in format_findings(draft_path, findings):
                print(line, file=sys.stderr)
            return 1
        summary = draft_path.read_text(encoding="utf-8").strip()

    report = ReplayReport(
        id=args.negotiation_id,
        redacted=True,
        created_at=args.negotiation_id[:7],
        redacted_summary=summary,
        incentive_map=[
            IncentiveEntry("buyer", "credible optionality", "limited safe disclosure"),
            IncentiveEntry("supplier-1", "early commitment", "uncertain buyer fallback"),
        ],
        leakages=[
            LeakageEntry(
                "information",
                {"from": "buyer", "to": "supplier-1"},
                "small",
                "Sequencing language exposed priority before an exchange.",
                ["signaling-leakage"],
            )
        ],
        equilibrium=Equilibrium(
            "Each side waits for the other to reveal urgency.",
            "Disclose only role-level constraints until a trade is explicit.",
            "Early urgency signals become free leverage.",
        ),
        cross_applications=[
            CrossApplication(
                "agent-routing-table",
                "handoff payloads expose urgency fields before a receiving agent needs them",
                "Use role-level state in the handoff boundary.",
                ["src/router/handoff_policy.py: drop urgency and preference fields from outbound handoff payloads"],
                "medium",
            )
        ],
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_report(report, output_path)
    print(output_path)
    return 0


def _cross_apply(args: argparse.Namespace) -> int:
    report = load_report(_report_path(args.negotiation_id))
    repo_index = load_repo_index(args.repo_index)
    candidates = match_cross_applications(report, repo_index)
    sys.stdout.write(json.dumps({"candidates": candidates}, indent=2) + "\n")
    return 0 if candidates else 1


def _redact_check(paths: list[str], denylist: str | None) -> int:
    target_paths = _default_report_paths() if not paths else [Path(path) for path in paths]
    had_findings = False
    for path in target_paths:
        _guard_public_path(path)
        findings = scan_file(path, denylist)
        if findings:
            had_findings = True
            for line in format_findings(path, findings):
                print(line, file=sys.stderr)
        else:
            print(f"ok: {path}")
    return 1 if had_findings else 0


def _validate(paths: list[str], repo_index_path: str) -> int:
    target_paths = _default_report_paths() if not paths else [Path(path) for path in paths]
    repo_index = load_json_object(repo_index_path)
    for path in target_paths:
        _guard_public_path(path)
        report = load_report(path)
        validate_repo_references(report, repo_index)
        print(f"ok: {path}")
    return 0


def _show(paths: list[str]) -> int:
    target_paths = _default_report_paths() if not paths else [Path(path) for path in paths]
    reports = []
    for path in target_paths:
        _guard_public_path(path)
        report = load_report(path)
        reports.append((report.id, report))
    sys.stdout.write(render_summary(reports))
    return 0


def _default_report_paths() -> list[Path]:
    paths = sorted(Path("examples").glob("*.md")) + sorted(Path("negotiations").glob("*.md"))
    if not paths:
        raise ReplayValidationError("no replay files found")
    return paths


def _report_path(negotiation_id: str) -> Path:
    return Path("negotiations") / f"{negotiation_id}.md"


def _guard_public_path(path: str | Path) -> None:
    resolved = Path(path).resolve()
    for private_dir in PRIVATE_DIRS:
        private_resolved = private_dir.resolve()
        try:
            if resolved == private_resolved or resolved.is_relative_to(private_resolved):
                raise ReplayValidationError(f"refusing to read or write private path: {path}")
        except AttributeError:
            if str(resolved).startswith(str(private_resolved)):
                raise ReplayValidationError(f"refusing to read or write private path: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
