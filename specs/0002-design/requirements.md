# Spec 0002 - Requirements

## R-NMR-013 root product documents

The repo root contains `PRODUCT_BRIEF.md` and `SYSTEM_MAP.md`. These files are
the contract-level entry points for the product shape and implementation map.

## R-NMR-014 design ledger package

`specs/0002-design/` contains `requirements.md`, `design.md`, `tasks.md`,
`acceptance.md`, and `ledger.md`. The ledger records accepted decisions, while
the other files state the shipped v0.1 contract.

## R-NMR-015 package import surface

The installable package exposes `negotiation_mechanism_replay/cli.py`,
`negotiation_mechanism_replay/model.py`, and
`negotiation_mechanism_replay/scoring.py`. The package can be imported by
tests and used by the `replay` console script.

## R-NMR-016 checked report artifact

At least one JSONL artifact exists under `reports/`. Each line is a JSON object
that names the source replay, mechanism tags, cross-application repo slugs, and
redaction state.

## R-NMR-017 uv packaging contract

`pyproject.toml` keeps dev tools under `[dependency-groups]` and sets
`[tool.uv] package = true` so `uv run` installs the project itself.
