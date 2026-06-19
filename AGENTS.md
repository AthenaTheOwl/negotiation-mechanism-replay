# AGENTS.md — negotiation-mechanism-replay

Operating contract for AI agents in this repo.

## What this repo is

A typed write-up generator that turns one negotiation event into one
Markdown file with five sections: redacted summary, incentive map,
leakage list, implied equilibrium, cross-application to portfolio
repos.

This is not a journal, a CRM, or a generic note-taking app. It is the
function that converts a confidential day-job experience into a
non-confidential mechanism-design artifact that can teach the
portfolio.

## Voice constraints

- No marketing words. The portfolio voice spec banlist applies.
- No antithetical reversals as a structural device.
- Every cross-application names a specific repo by slug and a
  specific change. Vague cross-applications ("could inform our
  agent architecture") are a gate failure.
- Plain assertions. The mechanism diagram is the spine; the prose is
  scaffolding.

## Roles in tasks

| Role | What they do |
|---|---|
| `redactor` | Authors the redacted summary; first-pass content scrub |
| `mechanism-mapper` | Names the incentive + leakage + equilibrium |
| `cross-applier` | Queries `config/repo_index.yaml` for matching surfaces |
| `redact-checker` | Runs the redaction gate against the file |

## Gates (will land in spec 0002)

```bash
uv run pytest
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/redact_check.py
python scripts/validate_replay_schema.py
```

The `redact_check.py` gate fails the commit if it finds:

- Counter-party named entities (configured deny-list).
- Currency or percentage figures.
- Calendar dates more specific than the negotiation month.
- Internal project codenames (configured deny-list).

## Out of scope

- Persisting any confidential content. The redact gate is the
  contract; if it cannot guarantee a file is safe, the file is not
  committed.
- Real-time negotiation assist. v0 is post-hoc only.
- Generic mechanism-design education. The cross-application is the
  point; without a named recipient repo, an entry is incomplete.
- Multi-author. Single user.
