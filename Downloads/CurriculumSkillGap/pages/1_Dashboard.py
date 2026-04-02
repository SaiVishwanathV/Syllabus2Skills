import streamlit as st
from database import get_reports_for_user
from utils.nlp_utils import ensure_nltk_resources
from utils.reporting import render_gauge, render_top_skills_bar
from utils.ui import apply_modern_theme

st.set_page_config(page_title="Dashboard", layout="wide")

if not st.session_state.get("authentication_status"):
    st.warning("Please sign in from the **Home** page (app entry).")
    st.stop()

apply_modern_theme("Dashboard", "Track coverage, reports, and analysis health at a glance.", logo="📊")

if "nlp_ready" not in st.session_state:
    try:
        ensure_nltk_resources()
        st.session_state["nlp_ready"] = True
    except Exception:
        st.session_state["nlp_ready"] = False

st.subheader(f"Welcome, {st.session_state.get('name', 'User')}")
st.caption("This page is visible only after login.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Auth Status", "Active")
with col2:
    st.metric("NLP Engine", "Ready" if st.session_state.get("nlp_ready") else "Not Ready")
with col3:
    st.metric("Analyses Run", st.session_state.get("analysis_count", 0))

st.markdown("### Workspace")
st.info(
    "Use the side pages to upload syllabus/resume, run analysis, and inspect history."
)



latest = st.session_state.get("latest_analysis_result")
if latest:
    st.markdown("## Latest Analysis Snapshot")
    coverage = 100.0 - float(latest.get("skill_gap_index", 100.0))
    render_gauge(coverage, title="Skill Coverage (%)")
    render_top_skills_bar(
        syllabus_skills=latest.get("syllabus_top_skills", []),
        jd_skills=latest.get("jd_top_skills", []),
    )
    s1, s2 = st.columns(2)
    with s1:
        st.markdown("**Missing Skills**")
        st.write(latest.get("missing_skills", [])[:12] or ["None"])
    with s2:
        st.markdown("**Matching Skills**")
        st.write(latest.get("matching_skills", [])[:12] or ["None"])

st.markdown("## Recent Saved Reports")
username = st.session_state.get("username", "")
reports = get_reports_for_user(username)
if reports:
    st.write(
        [
            {
                "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "type": r.analysis_type,
                "document": r.syllabus_name,
                "role": r.jd_role,
                "sgi": round(r.gap_index_score, 2),
            }
            for r in reports[:5]
        ]
    )
else:
    st.info("No saved reports yet. Run an analysis to populate history.")
