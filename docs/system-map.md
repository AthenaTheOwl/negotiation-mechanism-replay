# System Map

## Components

- `src/replay/schema.py`: validates the report contract and parses JSON front
  matter.
- `src/replay/redactor.py`: scans report text for configured deny-list terms,
  currency tokens, percentage figures, and precise dates.
- `src/replay/matcher.py`: matches leakage mechanism tags to
  `config/repo_index.yaml`.
- `src/replay/render.py`: renders a report back to Markdown with five required
  sections.
- `src/replay/cli.py`: exposes `new`, `cross-apply`, `render`,
  `redact-check`, and `validate`.
- `scripts/*.py`: thin gate wrappers used by the factory.

## Data flow

1. User writes a sanitized draft outside tracked raw paths.
2. `replay new` creates a report skeleton or reads the sanitized draft.
3. `scripts/redact_check.py` scans the candidate report.
4. `scripts/validate_replay_schema.py` checks the typed report and repo
   references.
5. `replay cross-apply` maps leakage tags to candidate portfolio changes.
6. The checked-in report becomes a reusable mechanism artifact.

## Boundary

- `data/raw/` and `data/private/` are ignored and refused by the CLI.
- `config/redact_denylist.yaml` is ignored; only the template is tracked.
- Checked-in reports must contain roles, repo slugs, mechanism tags, and
  file-level fixes.
