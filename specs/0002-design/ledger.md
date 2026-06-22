# Spec 0002 - Design Ledger

## Decisions

| ID | Status | Decision | Reason |
|---|---|---|---|
| D-0002-001 | accepted | Use JSON front matter inside Markdown reports. | The repo can parse and render reports without a runtime YAML dependency. |
| D-0002-002 | accepted | Keep config files as JSON-compatible `.yaml`. | The names match the planned contract while v0.1 stays dependency-light. |
| D-0002-003 | accepted | Require `one_sprint_fix` entries to start with a file path and colon. | Cross-application must name a specific repo change. |
| D-0002-004 | accepted | Make redaction a blocking gate, not a transformer. | Unsafe content should fail instead of being rewritten in place. |
| D-0002-005 | accepted | Use tag overlap for v0.1 cross-application. | The match is auditable and easy to test. |

## Gate contract

- `uv run pytest`
- `python scripts/voice_lint.py`
- `python scripts/spec_check.py`
- `python scripts/redact_check.py`
- `python scripts/validate_replay_schema.py`

## Follow-up queue

- Add candidate review state.
- Add report indexing by mechanism tag.
- Add stricter proper-noun detection after the deny-list format settles.
