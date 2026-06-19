# First PR after the scaffold

Title: `feat: replay schema, repo-index, mechanism-taxonomy, redact-denylist template`

## Scope

This PR lands the schema, the two config registries, the redact-
denylist template, the worked fictional example, and the schema
tests. No redactor logic yet; no matcher yet; no renderer yet.

## Files added

- `schemas/replay.schema.json` — R-NMR-002 plus nested defs for
  incentive_map (R-NMR-003), leakages (R-NMR-004), and
  cross_applications (R-NMR-005). The top-level `redacted: true`
  flag is required.
- `src/replay/__init__.py`
- `src/replay/schema.py` — Pydantic mirrors.
- `config/repo_index.yaml` — 4-6 placeholder entries with `slug`
  and 1-3 `mechanism_surfaces` tags each. Tags use the controlled
  vocabulary listed in `config/mechanism_taxonomy.yaml`.
- `config/mechanism_taxonomy.yaml` — 6-10 named failures:
  `adverse-selection`, `hidden-action`, `signaling-leakage`,
  `commitment-credibility`, `winner's-curse`, `holdup`,
  `multi-agent-handoff`, `tool-permission-leakage`,
  `eval-incentive`, `prompt-budget`. Each with `id`, `name`,
  `summary`, `exemplar_surfaces[]`.
- `config/redact_denylist.yaml.example` — placeholder template
  listing the file's expected sections (`named_entities`,
  `internal_codenames`, `currency_tokens`, `percentage_tokens`,
  `date_precision_max`). The real file is gitignored.
- `examples/2026-07-procurement-EXAMPLE.md` — fully fictional
  worked example. Uses roles only (`buyer`, `supplier-1`,
  `internal-finance`). No currency, no calendar precision beyond
  `2026-07`, no real repo slug. One leakage tagged
  `signaling-leakage`, one cross-application targeting placeholder
  repo `repo-alpha`.
- `tests/test_schemas.py` — required-field tests, the
  `redacted: true` invariant, and the cross-application
  `repo_slug` referential integrity check against a fixture
  repo_index.
- `pyproject.toml` — `pydantic`, `pyyaml`, `jsonschema`, `pytest`,
  `ruff`.

## Files changed

None. First PR after scaffold.

## Verification

```bash
uv sync
uv run pytest -v
uv run python -c "import json, jsonschema; \
  jsonschema.Draft202012Validator.check_schema( \
    json.load(open('schemas/replay.schema.json')))"
```

`pytest -v` shows at least 6 passing tests.

## What this PR does not do

- No `redactor.py` (PR 2).
- No `matcher.py` (PR 2).
- No `render.py` (PR 2).
- No voice_lint or spec_check (PR 3).
- No CLI behavior beyond `--help`.

## Review checklist

- [ ] Schema validates against Draft 2020-12.
- [ ] Pydantic mirrors do not drift (round-trip tests pin this).
- [ ] Example uses zero real names, zero currency tokens, zero
      dates more precise than `2026-07`, zero real repo slugs.
- [ ] The redact-denylist template ships only structure, no real
      deny-list values.
- [ ] No file under `data/raw/` or `data/private/` is tracked.
