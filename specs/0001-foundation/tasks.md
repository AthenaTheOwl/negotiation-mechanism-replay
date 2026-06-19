# Spec 0001 — Tasks

Ordered for the first 2-3 PRs.

## PR 1 — schemas and registries

- [ ] Write `schemas/replay.schema.json` (R-NMR-002, R-NMR-003,
      R-NMR-004, R-NMR-005 as nested defs).
- [ ] Write `src/replay/schema.py` Pydantic mirrors.
- [ ] Write `config/repo_index.yaml` with 4-6 placeholder entries
      and `mechanism_surfaces[]` tags (R-NMR-006).
- [ ] Write `config/mechanism_taxonomy.yaml` with 6-10 named
      failures (R-NMR-007).
- [ ] Write `config/redact_denylist.yaml.example` template
      (R-NMR-008).
- [ ] Write `examples/2026-07-procurement-EXAMPLE.md` (R-NMR-010).
- [ ] Write `tests/test_schemas.py`.

## PR 2 — redaction gate and cross-applier

- [ ] Write `src/replay/redactor.py` (R-NMR-008).
- [ ] Write `src/replay/matcher.py` (R-NMR-006 tag overlap).
- [ ] Write `src/replay/render.py` with round-trippable front matter
      (R-NMR-009).
- [ ] Write `scripts/redact_check.py` as a thin CLI over
      `redactor.py`.
- [ ] Write `tests/test_redactor.py` covering each rule in
      R-NMR-008.
- [ ] Write `tests/test_matcher.py`.
- [ ] Write `tests/test_render_roundtrip.py`.

## PR 3 — gates and out-of-scope guard

- [ ] Copy `scripts/voice_lint.py` from portfolio (R-NMR-011).
- [ ] Write `scripts/spec_check.py` (R-NMR-011).
- [ ] Wire the `data/raw/` and `data/private/` refusal in
      `src/replay/cli.py` (R-NMR-012).
- [ ] Write `pyproject.toml`.
- [ ] Confirm all gates exit zero on the example file.
