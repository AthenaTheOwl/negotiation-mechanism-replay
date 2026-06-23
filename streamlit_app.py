"""negotiation-mechanism-replay - live demo (Streamlit Community Cloud).

Reads the committed replay reports under negotiations/*.md and examples/*.md and
shows one mechanism-design replay at a time: incentive map, leakages ranked by
magnitude, and cross-applications to portfolio repos ranked by confidence. No
network, no secrets - it parses the committed report front matter directly.

Deploy: Streamlit Community Cloud -> New app -> repo
AthenaTheOwl/negotiation-mechanism-replay, branch main, main file
streamlit_app.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parent

# Make the real engine importable: the package under src/replay/ imports as
# `replay`. On Streamlit Cloud the `.` line in requirements.txt installs it; for a
# plain checkout we add src/ to the path so the same imports resolve locally.
_SRC = REPO / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

MAGNITUDE_RANK = {"large": 3, "material": 2, "small": 1}
CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}


def load_reports() -> dict[str, dict]:
    """Parse committed reports (JSON front matter) keyed by report id."""
    paths = sorted((REPO / "examples").glob("*.md")) + sorted(
        (REPO / "negotiations").glob("*.md")
    )
    reports: dict[str, dict] = {}
    for path in paths:
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        lines = text.split("\n")
        if not lines or lines[0] != "---":
            continue
        try:
            end = lines.index("---", 1)
        except ValueError:
            continue
        try:
            data = json.loads("\n".join(lines[1:end]))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "id" in data:
            reports[data["id"]] = data
    return reports


st.set_page_config(
    page_title="negotiation-mechanism-replay", layout="wide"
)
st.title("negotiation-mechanism-replay")
st.caption(
    "one sanitized negotiation event, replayed as a mechanism-design report: "
    "who optimizes for what, where information leaked, and how that pattern shows "
    "up in named portfolio repos."
)

reports = load_reports()
if not reports:
    st.warning("no replay reports found under negotiations/*.md or examples/*.md")
    st.stop()

report_id = st.selectbox("replay report", sorted(reports), index=0)
report = reports[report_id]

leakages = report.get("leakages", [])
cross = report.get("cross_applications", [])
incentives = report.get("incentive_map", [])

top_tier = "-"
if leakages:
    top = max(leakages, key=lambda l: MAGNITUDE_RANK.get(l.get("magnitude_tier"), 0))
    top_tier = top.get("magnitude_tier", "-")

c1, c2, c3 = st.columns(3)
c1.metric("roles in play", len(incentives))
c2.metric("leakages", len(leakages))
c3.metric("sharpest leak", top_tier, help="highest magnitude tier in this replay")

st.markdown(f"**redacted summary:** {report.get('redacted_summary', '')}")

st.subheader("incentive map")
st.dataframe(
    [
        {
            "role": i.get("actor_role"),
            "optimizes for": i.get("optimizes_for"),
            "constrained by": i.get("constrained_by"),
        }
        for i in incentives
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("leakages (ranked by magnitude)")
leak_sorted = sorted(
    leakages, key=lambda l: MAGNITUDE_RANK.get(l.get("magnitude_tier"), 0), reverse=True
)
st.dataframe(
    [
        {
            "tier": l.get("magnitude_tier"),
            "kind": l.get("kind"),
            "direction": f"{l.get('direction', {}).get('from')} -> {l.get('direction', {}).get('to')}",
            "mechanism": l.get("mechanism_one_liner"),
            "tags": ", ".join(l.get("mechanism_tags", [])),
        }
        for l in leak_sorted
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("cross-application to portfolio repos (ranked by confidence)")
cross_sorted = sorted(
    cross, key=lambda c: CONFIDENCE_RANK.get(c.get("confidence"), 0), reverse=True
)
st.dataframe(
    [
        {
            "confidence": c.get("confidence"),
            "repo": c.get("repo_slug"),
            "failing surface": c.get("failing_surface"),
            "recommendation": c.get("recommendation"),
        }
        for c in cross_sorted
    ],
    use_container_width=True,
    hide_index=True,
)

eq = report.get("equilibrium", {})
if leak_sorted:
    head = leak_sorted[0]
    st.info(
        f"**headline:** the sharpest leak is {head.get('magnitude_tier')} "
        f"({head.get('kind')}, {head.get('direction', {}).get('from')} -> "
        f"{head.get('direction', {}).get('to')}): {head.get('mechanism_one_liner')} "
        f"stable strategy: {eq.get('stable_strategy', '')}"
    )

with st.expander("implied equilibrium"):
    st.markdown(
        f"- observed behavior: {eq.get('observed_behavior', '')}\n"
        f"- stable strategy: {eq.get('stable_strategy', '')}\n"
        f"- failure mode: {eq.get('failure_mode', '')}"
    )

st.divider()

# ---------------------------------------------------------------------------
# interactive: drive the real engine on your own input
# ---------------------------------------------------------------------------
# Above this line we render a committed report. Below, the user edits a real
# replay report (JSON front matter) and we run the ACTUAL package code:
#   - replay.schema.parse_report_text  -> the real schema validator (pass/fail + why)
#   - replay.matcher.match_cross_applications -> the real cross-application engine
#     (maps the report's leakage mechanism_tags to repo-index surfaces and emits
#      file-level fixes). No lookup, no hardcoded output.

from replay.matcher import load_repo_index, match_cross_applications  # noqa: E402
from replay.schema import ReplayValidationError, parse_report_text  # noqa: E402

st.header("replay your own negotiation")
st.caption(
    "edit the JSON front matter below and run it through the real engine. the "
    "schema validator (`replay.schema.parse_report_text`) checks the contract live; "
    "the matcher (`replay.matcher.match_cross_applications`) recomputes "
    "cross-applications by intersecting your leakage `mechanism_tags` with the "
    "committed repo index. change a tag, a magnitude, a role -> the result moves."
)

# pre-fill with a committed example's front matter so the editor starts valid.
def _example_front_matter() -> str:
    example = (REPO / "examples" / "2026-07-procurement-EXAMPLE.md")
    if example.exists():
        text = example.read_text(encoding="utf-8").replace("\r\n", "\n")
        lines = text.split("\n")
        if lines and lines[0] == "---":
            try:
                end = lines.index("---", 1)
                return "---\n" + "\n".join(lines[1:end]) + "\n---\n"
            except ValueError:
                pass
    # fall back to a minimal valid skeleton if the example is missing.
    return json.dumps(
        {
            "id": "2026-07-procurement-42",
            "redacted": True,
            "created_at": "2026-07",
            "redacted_summary": "A buyer leaked priority through sequencing language.",
            "incentive_map": [
                {"actor_role": "buyer", "optimizes_for": "optionality", "constrained_by": "approval path"},
                {"actor_role": "supplier-1", "optimizes_for": "early commitment", "constrained_by": "uncertain fallback"},
            ],
            "leakages": [
                {
                    "kind": "information",
                    "direction": {"from": "buyer", "to": "supplier-1"},
                    "magnitude_tier": "material",
                    "mechanism_one_liner": "Sequencing language revealed priority before a trade.",
                    "mechanism_tags": ["signaling-leakage"],
                }
            ],
            "equilibrium": {
                "observed_behavior": "supplier waits for urgency",
                "stable_strategy": "keep signals role-level",
                "failure_mode": "urgency becomes leverage",
            },
            "cross_applications": [
                {
                    "repo_slug": "agent-routing-table",
                    "failing_surface": "handoff payloads expose urgency fields",
                    "recommendation": "keep handoffs role-level",
                    "one_sprint_fix": ["src/router/handoff_policy.py: drop urgency fields"],
                    "confidence": "high",
                }
            ],
        },
        indent=2,
    )


# surface the catalog of tags the matcher can actually fire on, so edits are informed.
try:
    _repo_index = load_repo_index(str(REPO / "config" / "repo_index.yaml"))
    _surfaces = sorted(
        {
            tag
            for repo in _repo_index.get("repos", [])
            if isinstance(repo, dict)
            for tag in repo.get("mechanism_surfaces", [])
        }
    )
except (ReplayValidationError, OSError, ValueError) as exc:
    _repo_index = {"repos": []}
    _surfaces = []
    st.warning(f"could not load repo index: {exc}")

if _surfaces:
    st.markdown(
        "**mechanism tags the matcher knows** (put one of these in a leakage's "
        "`mechanism_tags` to make the engine fire): "
        + ", ".join(f"`{t}`" for t in _surfaces)
    )

edited = st.text_area(
    "replay report (JSON front matter, between `---` fences)",
    value=_example_front_matter(),
    height=320,
)

if st.button("validate + recompute cross-applications", type="primary"):
    # the body after the front matter is optional for the validator; wrap the
    # edited front matter so parse_report_text sees a well-formed document.
    document = edited if edited.lstrip().startswith("---") else f"---\n{edited}\n---\n"
    try:
        report = parse_report_text(document)  # REAL validator
    except ReplayValidationError as exc:
        st.error(f"schema gate FAILED: {exc}")
        st.caption(
            "this is the actual contract from `replay.schema` — fix the field it "
            "names and run again."
        )
    except (json.JSONDecodeError, ValueError) as exc:
        st.error(f"could not parse front matter: {exc}")
    else:
        st.success(f"schema gate PASSED — report `{report.id}` is contract-valid")

        leak_tags = sorted(
            {tag for leak in report.leakages for tag in leak.mechanism_tags}
        )
        st.markdown("**your leakage mechanism tags:** " + (
            ", ".join(f"`{t}`" for t in leak_tags) or "_(none)_"
        ))

        # REAL cross-application engine on the parsed report.
        candidates = match_cross_applications(report, _repo_index)
        st.subheader("cross-applications (recomputed live by the matcher)")
        if candidates:
            st.dataframe(
                [
                    {
                        "confidence": c.get("confidence"),
                        "repo": c.get("repo_slug"),
                        "matched tag": ", ".join(c.get("matched_tags", [])),
                        "failing surface": c.get("failing_surface"),
                        "recommendation": c.get("recommendation"),
                    }
                    for c in candidates
                ],
                use_container_width=True,
                hide_index=True,
            )
            st.info(
                f"the matcher fired **{len(candidates)}** file-level fix(es) by "
                "intersecting your tags with the repo index. remove the tag and the "
                "rows disappear; add `holdup` or `eval-incentive` and new repos light up."
            )
        else:
            st.warning(
                "no cross-applications fired: none of your leakage `mechanism_tags` "
                "match a repo surface in the index. try one of: "
                + ", ".join(f"`{t}`" for t in _surfaces)
            )

st.caption(
    "v0.1 ships committed replay reports AND drives the real engine on your input: "
    "the schema validator and cross-application matcher live in `src/replay/`; this "
    "page calls them directly (no reimplementation). "
    "repo: github.com/AthenaTheOwl/negotiation-mechanism-replay"
)
