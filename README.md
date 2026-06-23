# Negotiation Mechanism Replay

Negotiation Mechanism Replay converts one sanitized negotiation event into one
mechanism-design report. The report has five sections:

1. Redacted summary.
2. Incentive map.
3. Leakage list.
4. Implied equilibrium.
5. Cross-application to named portfolio repos.

The repo is post-hoc only. It does not store raw day-job material and does not
operate on `data/raw/` or `data/private/`.

## Current v0.1 surface

- JSON-front-matter report format with a checked schema.
- Portfolio repo index at `config/repo_index.yaml`.
- Mechanism taxonomy at `config/mechanism_taxonomy.yaml`.
- Redaction gate for deny-listed entities, currency, percentages, precise
  calendar dates, and internal codenames.
- Tag-overlap cross-applier.
- CLI entry point named `replay`.
- Tests and gate scripts for the checked-in example and report artifact.

## Run

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
.
|-- config/
|   |-- mechanism_taxonomy.yaml
|   |-- redact_denylist.yaml.example
|   `-- repo_index.yaml
|-- docs/
|   |-- product-brief.md
|   `-- system-map.md
|-- examples/
|   `-- 2026-07-procurement-EXAMPLE.md
|-- negotiations/
|   `-- 2026-07-procurement-01.md
|-- schemas/
|   `-- replay.schema.json
|-- scripts/
|   |-- redact_check.py
|   |-- spec_check.py
|   |-- validate_replay_schema.py
|   `-- voice_lint.py
|-- specs/
|   |-- 0001-foundation/
|   `-- 0002-design/
|-- src/replay/
`-- tests/
```

## live demo

A read-only digest of the committed replay reports:

```bash
uv run replay show
```

It prints leakages ranked by magnitude, cross-applications ranked by confidence,
and a one-line headline finding. It reads only the committed reports under
`negotiations/` and `examples/`, makes no network calls, and exits 0.

A browsable version of the same view runs as a Streamlit page:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Pick a report, then read its incentive map, ranked leakages, and ranked
cross-applications.

Streamlit Community Cloud: New app -> repo
`AthenaTheOwl/negotiation-mechanism-replay`, branch `main`, main file
`streamlit_app.py`.

<!-- live-url: https://<your-app>.streamlit.app -->

## Confidentiality rule

The user performs the first redaction pass outside the repo. The repo gate is
the second pass. A file that fails the redaction gate is not a valid checked-in
artifact.

## License

MIT. See `LICENSE`.
