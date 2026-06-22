# Spec 0002 - Acceptance

v0.1 is accepted when these checks hold.

## Files

- `PRODUCT_BRIEF.md` exists at the repo root.
- `SYSTEM_MAP.md` exists at the repo root.
- `specs/0002-design/requirements.md` exists.
- `specs/0002-design/design.md` exists.
- `specs/0002-design/tasks.md` exists.
- `specs/0002-design/acceptance.md` exists.
- `negotiation_mechanism_replay/cli.py` exists.
- `negotiation_mechanism_replay/model.py` exists.
- `negotiation_mechanism_replay/scoring.py` exists.
- `reports/2026-07-procurement-01.jsonl` exists.

## Commands

```bash
uv run pytest
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/redact_check.py
python scripts/validate_replay_schema.py
```

All commands exit zero.

## Functional Checks

- `python -m negotiation_mechanism_replay render --negotiation-id 2026-07-procurement-01`
  renders the checked Markdown replay.
- `uv run replay cross-apply --negotiation-id 2026-07-procurement-01`
  emits repo-index candidates from mechanism tag overlap.
- The JSONL report artifact parses as one JSON object with `redacted` set to
  `true`.
