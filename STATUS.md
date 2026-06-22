# STATUS

## Current state

- v0.1 has a runnable Python CLI, schema loader, renderer, redaction gate, and tag-overlap cross-applier.
- `negotiations/2026-07-procurement-01.md` is the checked-in safe report artifact.
- `examples/2026-07-procurement-EXAMPLE.md` is the worked fictional example for gate coverage.
- Gate commands are `uv run pytest`, `python scripts/voice_lint.py`, `python scripts/spec_check.py`, `python scripts/redact_check.py`, and `python scripts/validate_replay_schema.py`.

## Known limits

- Config files use JSON syntax in `.yaml` files so the v0.1 runtime can stay dependency-light.
- The cross-applier is tag overlap only and does not rank candidates.
- The redaction gate catches configured names and token patterns; it cannot prove that a paraphrase is safe.
- The CLI creates a skeleton report, not an interactive authoring flow.

## Next feature queue

- Add an accept-or-discard workflow for cross-application candidates.
- Add a stricter role-name lint that flags proper nouns in `actor_role` fields.
- Add a fixture suite for raw/private path refusal.
- Add a report index that lists all checked-in replay artifacts by month and mechanism tag.

- Resolve factory defect: missing PRODUCT_BRIEF.md,SYSTEM_MAP.md
- Resolve factory defect: missing reports/*.jsonl
- Resolve factory defect: PRODUCT_BRIEF.md is required for active repos
- Resolve factory defect: SYSTEM_MAP.md is required for active repos
- Resolve factory defect: expected file 'PRODUCT_BRIEF.md' is missing
- Resolve factory defect: expected file 'SYSTEM_MAP.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/requirements.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/design.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/tasks.md' is missing
- Resolve factory defect: expected file 'specs/0002-design/acceptance.md' is missing
- Resolve factory defect: expected file 'negotiation_mechanism_replay/cli.py' is missing
- Resolve factory defect: expected glob 'reports/*.jsonl' matched no files
- Resolve factory defect: module 'cli' declares source 'negotiation_mechanism_replay/cli.py', but it is missing
- Resolve factory defect: module 'model' declares source 'negotiation_mechanism_replay/model.py', but it is missing
- Resolve factory defect: module 'report' declares source 'negotiation_mechanism_replay/scoring.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
