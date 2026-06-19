# Spec 0001 — Foundation

## R-NMR-001 — repo scaffold
Repo at `e:/claude_code/random-apps/negotiation-mechanism-replay`. MIT
license. README, AGENTS.md, LICENSE, .gitignore at the root.
`.gitignore` excludes `data/raw/` and `data/private/` so unsanitized
notes cannot be committed.

## R-NMR-002 — replay file schema
`schemas/replay.schema.json` defines a single negotiation write-up:
`id` (`YYYY-MM-<context>-<nn>`), `redacted: true` flag,
`redacted_summary`, `incentive_map[]`, `leakages[]`, `equilibrium`,
`cross_applications[]`, `created_at`.

## R-NMR-003 — incentive map schema
Each `incentive_map` entry: `actor_role` (no actor names; roles only,
e.g. `buyer`, `supplier-1`, `internal-finance`), `optimizes_for`,
`constrained_by`.

## R-NMR-004 — leakage schema
Each `leakages` entry: `kind` (information / value / option),
`direction` (from / to actor role), `magnitude_tier` (small / material
/ large), `mechanism_one_liner`.

## R-NMR-005 — cross-application schema
Each `cross_applications` entry: `repo_slug` (must exist in
`config/repo_index.yaml`), `failing_surface`, `recommendation`,
`one_sprint_fix` (bulleted file-level changes), `confidence`
(low / medium / high).

## R-NMR-006 — repo index
`config/repo_index.yaml` lists portfolio repos with `slug` and
`mechanism_surfaces[]` — short tags such as `multi-agent-handoff`,
`tool-permission-leakage`, `eval-incentive`, `prompt-budget`. The
cross-applier matches negotiation leakages against these tags.

## R-NMR-007 — mechanism taxonomy
`config/mechanism_taxonomy.yaml` enumerates named mechanism failures
(adverse-selection, hidden-action, signaling-leakage,
commitment-credibility, etc.) with `id`, `name`, `summary`,
`exemplar_surfaces[]`.

## R-NMR-008 — redaction gate
`scripts/redact_check.py` scans a candidate file and fails if it
finds named entities from a deny-list, currency tokens (`$`, `USD`,
`EUR`, etc.), percentage tokens (`%`), specific calendar dates more
precise than month-year, or internal codename matches. The deny-list
lives at `config/redact_denylist.yaml` and is itself git-ignored
beyond a placeholder template.

## R-NMR-009 — file naming
Files live at `negotiations/<id>.md` with round-trippable front
matter.

## R-NMR-010 — example
`examples/2026-07-procurement-EXAMPLE.md` ships a worked, fully-
fictional example. The example uses generic actor roles, no
currency, no dates more precise than `2026-07`, and one
cross-application to a placeholder repo slug.

## R-NMR-011 — voice lint + spec check
Same gates as the rest of the portfolio. Both ship as stubs in v0
and assertively run by spec 0002.

## R-NMR-012 — out-of-scope guard
v0 refuses to operate on `data/raw/` content; the CLI errors if any
input path resolves inside `data/raw/` or `data/private/`. The user
copies sanitized fragments into `negotiations/_drafts/` manually.
