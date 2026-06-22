# System Map

## Public Surface

- `negotiation_mechanism_replay/cli.py`: package entry point for the `replay`
  command.
- `negotiation_mechanism_replay/model.py`: stable import surface for report
  dataclasses and schema loaders.
- `negotiation_mechanism_replay/scoring.py`: stable import surface for
  cross-application candidate scoring.
- `reports/*.jsonl`: checked report artifacts for downstream review.

## Implementation Modules

- `src/replay/schema.py`: validates JSON front matter and repo references.
- `src/replay/redactor.py`: scans for deny-list terms, currency tokens,
  percentage figures, and precise calendar dates.
- `src/replay/matcher.py`: matches leakage mechanism tags to
  `config/repo_index.yaml`.
- `src/replay/render.py`: renders the five-section Markdown report.
- `src/replay/cli.py`: implements `new`, `cross-apply`, `render`,
  `redact-check`, and `validate`.

## Data Flow

1. User redacts source material outside tracked raw paths.
2. CLI creates or reads a public report under `negotiations/`.
3. Redaction and schema gates validate the report.
4. Cross-application scoring maps mechanism tags to repo-index surfaces.
5. A JSONL report artifact under `reports/` records the checked result.

## Boundaries

- `data/raw/` and `data/private/` stay ignored and refused by the CLI.
- `config/redact_denylist.yaml` stays ignored; only the example template is
  tracked.
- Every cross-application names a repo slug and a file-level change.
