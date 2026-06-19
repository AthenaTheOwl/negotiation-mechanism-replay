# Spec 0001 — Design

## Shape

A schema, a redaction gate, a small cross-application matcher, a
renderer. The redaction gate is the load-bearing piece; everything
else assumes the input is already safe.

```
schemas/replay.schema.json     # R-NMR-002 plus 003/004/005 sub-schemas
config/
  repo_index.yaml              # R-NMR-006
  mechanism_taxonomy.yaml      # R-NMR-007
  redact_denylist.yaml.example # template; real file is gitignored
src/replay/
  cli.py                       # new / cross-apply / redact-check / render
  schema.py                    # Pydantic mirrors
  redactor.py                  # the deny-list + token rules (R-NMR-008)
  matcher.py                   # leakage tags -> repo surfaces (R-NMR-006)
  render.py                    # replay -> Markdown
negotiations/                  # one file per event (R-NMR-009)
  _drafts/                     # user sanitization staging; not committed
examples/
  2026-07-procurement-EXAMPLE.md  # R-NMR-010
scripts/
  voice_lint.py
  spec_check.py
  redact_check.py
tests/
  test_schemas.py
  test_redactor.py
  test_matcher.py
  test_render_roundtrip.py
```

## Data flow

1. User writes a sanitized draft into `negotiations/_drafts/`. The
   draft is fully redacted by hand; the gate is a second line of
   defense, not the first.
2. `replay new --negotiation-id <id>` reads the draft, slots it into
   the schema template, runs `redactor.py` as a check, refuses to
   write the final file if the gate fails.
3. `replay cross-apply --negotiation-id <id>` reads the leakages and
   queries `config/repo_index.yaml` for repos whose `mechanism_surfaces`
   tags overlap. The matcher emits candidate cross-applications; the
   user accepts or discards each.
4. `replay render --negotiation-id <id>` produces the final Markdown
   with round-trippable front matter at `negotiations/<id>.md`.

## Why a two-layer redaction discipline

The user is the first redactor; the gate is the second. Either alone
is unsafe: humans miss things, and an automated scrub can be tricked
by paraphrase. The repo's contract is that both must agree the
content is safe before a file enters version control.

## Why repo_index has tags, not free text

The cross-application matcher is intentionally dumb. Tag overlap is
trivially auditable; embedding-based matching is not. v0 uses tag
overlap; later specs may add an embedding suggestion layer behind a
flag, but the typed tags remain the contract.

## What is not in spec 0001

- Outcome scoring (did the cross-applied fix actually work?). Spec
  0003.
- Mechanism-failure embedding suggestions. Spec 0004.
- Auto-tagging of legacy entries. Not planned.

Spec 0002 lands the redactor + matcher + first real worked example.
