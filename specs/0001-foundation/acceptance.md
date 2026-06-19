# Spec 0001 — Acceptance

v0 is done when the following hold.

## Repo shape

- README, LICENSE, AGENTS.md, .gitignore at the root.
- `.gitignore` excludes `data/raw/` and `data/private/` and
  `config/redact_denylist.yaml` (only the `.example` template is
  tracked).
- `specs/0001-foundation/` complete.
- `docs/first-pr.md` concrete and file-level.

## Commands

After PR 1-3 land:

```bash
uv run pytest
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/redact_check.py examples/2026-07-procurement-EXAMPLE.md
python scripts/validate_replay_schema.py examples/2026-07-procurement-EXAMPLE.md
```

All five exit zero.

## Functional gates

- The example replay validates against the schema; contains at least
  2 incentive_map entries, 1 leakage, an `equilibrium` block, and 1
  cross_application targeting a real entry in
  `config/repo_index.yaml`.
- `redact_check.py` against the example passes; the same script
  against a deliberately-broken fixture (currency token present)
  fails with a non-zero exit and a named rule.
- `replay cross-apply` against the example produces at least one
  candidate suggestion driven by tag overlap from
  `config/repo_index.yaml`.
- `spec_check.py` confirms every `R-NMR-NNN` reference is defined.

## Out of scope for v0 acceptance

- Outcome scoring (did fixes work?).
- Embedding-based matching.
- Anything that touches `data/raw/` directly.

Those land in later specs.
