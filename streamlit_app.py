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
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parent

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

st.caption(
    "v0.1 ships committed replay reports. the schema + cli live in `src/replay/`; "
    "this page reads the committed reports directly. "
    "repo: github.com/AthenaTheOwl/negotiation-mechanism-replay"
)
