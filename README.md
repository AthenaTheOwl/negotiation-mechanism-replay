# Negotiation Mechanism Replay

After each significant day-job negotiation, this repo emits a typed
mechanism-design write-up: incentive map, leakage points, equilibrium. Then
it queries the AI-build portfolio for any system currently violating the
same equilibrium principle and emits cross-applied fix recommendations.

## What this is

The user runs procurement, capacity, and escalation negotiations at the
day job. The same negotiations expose mechanism-design failures —
information leakage, incentive misalignment, off-equilibrium play — that
also show up in agent systems and software architectures. Today these
lessons are lost to memory. This repo turns them into typed artifacts.

For each registered negotiation event, the repo emits one Markdown file:

1. A redacted summary (no confidential content; mechanism only).
2. An incentive map — who benefits from what action.
3. A leakage list — where information or value escapes.
4. The implied equilibrium — what each side actually optimizes for.
5. A cross-application section — named portfolio repos that exhibit the
   same mechanism failure, with a concrete one-sprint fix per repo.

## Status

v0 scaffold. No write-ups, no portfolio query engine. Spec 0001 defines
the redaction discipline, the mechanism-write-up schema, the
cross-application rubric, and the gates that land in spec 0002.

## How to run

Placeholder. Spec 0002 will ship the CLI:

```bash
uv run replay new --negotiation-id 2026-07-procurement-01
uv run replay cross-apply --negotiation-id 2026-07-procurement-01
uv run replay redact-check --negotiation-id 2026-07-procurement-01
```

## Layout

```
.
├── AGENTS.md
├── LICENSE
├── README.md
├── docs/
│   └── first-pr.md
└── specs/
    └── 0001-foundation/
        ├── acceptance.md
        ├── design.md
        ├── requirements.md
        └── tasks.md
```

Planned directories:

- `negotiations/` — one Markdown file per negotiation event.
- `src/replay/` — schema, CLI, redact-check, cross-applier.
- `config/`
  - `repo_index.yaml` — portfolio repos and their mechanism-shaped
    surfaces.
  - `mechanism_taxonomy.yaml` — named mechanism failures the rubric
    knows.
- `tests/` — schema + redaction + cross-application tests.

## Why this exists

Three-way intersection: Amazon TPM negotiation flow, MIT mechanism-design
literacy, and a personally-owned AI-build portfolio to apply lessons to.
The output is not a journal. It is a typed pull from one domain into
another, with a named recipient repo and a one-sprint fix per
recommendation.

## Confidentiality

Source material is the user's day job. The repo never persists
counter-party names, monetary terms, or any content that could identify
a negotiation. The schema enforces a `redacted: true` flag and a
`redact-check` gate runs against every entry. If the gate fails, the
file does not commit.

## License

MIT. See `LICENSE`.
