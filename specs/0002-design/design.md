# Spec 0002 - Design

## Shape

Spec 0002 adds the contract paths expected by the factory while preserving the
working implementation under `src/replay/`.

```text
PRODUCT_BRIEF.md
SYSTEM_MAP.md
negotiation_mechanism_replay/
  cli.py
  model.py
  scoring.py
reports/
  2026-07-procurement-01.jsonl
specs/0002-design/
  requirements.md
  design.md
  tasks.md
  acceptance.md
  ledger.md
```

## Package Boundary

The `negotiation_mechanism_replay` package is the stable import surface. It
delegates to the existing `src/replay` modules so the current tests and CLI
logic keep a single source of behavior.

## Report Artifact

The JSONL artifact is a downstream data record, not the authored report. The
Markdown replay remains the source artifact under `negotiations/`; the JSONL
line records safe metadata for review and batch ingestion.

## Packaging

Setuptools discovers both `negotiation_mechanism_replay` and `replay`. The
`replay` console command points at `negotiation_mechanism_replay.cli:main`,
which then calls the implementation CLI.
