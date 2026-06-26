# negotiation-mechanism-replay

A buyer let slip that his fallback might not hold. Supplier-1 heard it, stopped
improving the offer, and waited. That one leaked sentence is now a row in a report
that says where it leaked, how badly, and which of your other repos has the same
hole.

## What it does

Every negotiation leaves a residue: who optimized for what, what got revealed too
early, where the stable move was to stall. The residue is usually lost the moment
the call ends. This tool catches one sanitized negotiation after the fact and turns
it into a mechanism-design report — a redacted summary, an incentive map per role,
a ranked list of leakages, the equilibrium those leakages imply, and a set of fixes
pointed at named portfolio repos that share the same failure surface.

It is post-hoc only, and it does not trust you. The user runs the first redaction
pass by hand, outside the repo; the gate runs the second. A file that fails the
redaction check — deny-listed entities, currency, percentages, precise dates,
internal codenames — is not a valid checked-in artifact. The tool also refuses any
path under `data/raw/` or `data/private/`, so raw day-job material never has a way
in.

## Try it

One command, reads only the committed reports, no network, exits 0:

```bash
uv run replay show
```

```
negotiation mechanism replay - show

2 replay report(s) loaded from committed artifacts.

## leakages (ranked by magnitude)

tier      report                  kind         direction            tags
--------  ----------------------  -----------  -------------------  -----------------------------------------
material  2026-07-procurement-01  information  buyer -> supplier-1  signaling-leakage, commitment-credibility
material  2026-07-procurement-99  information  buyer -> supplier-1  signaling-leakage

## cross-applications (ranked by confidence)

conf    report                  repo                  failing surface
------  ----------------------  --------------------  ------------------------------------------------------------------------------
high    2026-07-procurement-01  agent-routing-table   handoff payloads expose urgency fields before a receiving agent needs them
high    2026-07-procurement-99  agent-routing-table   handoff payloads expose urgency fields before a receiving agent needs them
medium  2026-07-procurement-01  prompt-budget-ledger  budget commitments are recorded after the model call has already spent context

## headline

the sharpest leak is material (information, buyer -> supplier-1) in 2026-07-procurement-01: Fallback uncertainty leaked before supplier-1 committed a concrete option.
highest-confidence cross-apply: agent-routing-table (high) - handoff payloads expose urgency fields before a receiving agent needs them
```

Leakages ranked by magnitude, cross-applications by confidence, and one headline
that names the sharpest leak in the pile.

## Live demo

A browsable version of the same view runs as a Streamlit page. Pick a report, then
read its incentive map, ranked leakages, and ranked cross-applications.

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Streamlit Community Cloud: New app -> repo
`AthenaTheOwl/negotiation-mechanism-replay`, branch `main`, main file
`streamlit_app.py`.

<!-- live-url: https://<your-app>.streamlit.app -->

## How it connects

The cross-applier carries a finding out of one negotiation and into the repos that
share its mechanism. A leaked urgency field is the same hole whether it's a supplier
reading a buyer or a router forwarding a payload it shouldn't:

- [agent-routing-table](https://github.com/AthenaTheOwl/agent-routing-table) —
  handoff payloads that ship urgency before the receiving agent has a need for it.
  The signaling leak, in code.
- [prompt-budget-ledger](https://github.com/AthenaTheOwl/prompt-budget-ledger) —
  budget commitments recorded after the spend, so the spender and the approver never
  see the same constraint.
- [eval-harness-lab](https://github.com/AthenaTheOwl/eval-harness-lab) — grader
  reward tangled up with self-reported completion; the hidden-action surface.
- [permission-boundary-kit](https://github.com/AthenaTheOwl/permission-boundary-kit)
  — tool arguments that reveal private terms; adverse selection at the scope check.
- [procurement-simulator](https://github.com/AthenaTheOwl/procurement-simulator) —
  the winner's curse and holdup, modeled before a supplier is picked.

The repo index lives at `config/repo_index.yaml`; the mechanism taxonomy at
`config/mechanism_taxonomy.yaml`. Tag overlap is what links a leak to a repo.

## Run it in full

```bash
uv run pytest
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/redact_check.py
python scripts/validate_replay_schema.py
```

Target a single report:

```bash
python scripts/redact_check.py negotiations/2026-07-procurement-01.md
python scripts/validate_replay_schema.py negotiations/2026-07-procurement-01.md
uv run replay cross-apply --negotiation-id 2026-07-procurement-01
```

Create a skeleton from a sanitized draft:

```bash
uv run replay new --negotiation-id 2026-07-procurement-02 --draft-path negotiations/_drafts/safe-summary.md
```

The CLI refuses paths under `data/raw/` and `data/private/`.

## Layout

```text
config/    repo index, mechanism taxonomy, redaction denylist
docs/      product brief, system map
examples/  the checked-in example report
negotiations/  the committed report artifacts
schemas/   replay.schema.json
scripts/   redact_check, spec_check, validate_replay_schema, voice_lint
specs/     0001-foundation, 0002-design
src/replay/  the cli and engine
tests/
```

## License

MIT. See `LICENSE`.
