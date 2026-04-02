import json

import pandas as pd
import streamlit as st

from database import get_reports_for_user
from utils.ui import apply_modern_theme

st.set_page_config(page_title="History", layout="wide")

if not st.session_state.get("authentication_status"):
    st.warning("Please sign in from the **Home** page (app entry).")
    st.stop()

apply_modern_theme("Analysis History", "Search and review your saved syllabus/resume analyses.", logo="🕘")

username = st.session_state.get("username", "")
reports = get_reports_for_user(username)

if not reports:
    st.info("No analysis history found yet. Run a syllabus/JD or resume/JD analysis first.")
    st.stop()

rows = []
for report in reports:
    missing_skills = json.loads(report.missing_skills_json or "[]")
    matching_skills = json.loads(report.matching_skills_json or "[]")
    rows.append(
        {
            "timestamp": report.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_type": report.analysis_type,
            "document_name": report.syllabus_name,
            "jd_role": report.jd_role,
            "cosine_similarity_%": round(report.cosine_similarity * 100, 2),
            "gap_index_%": round(report.gap_index_score, 2),
            "missing_skills": ", ".join(missing_skills[:12]),
            "matching_skills": ", ".join(matching_skills[:12]),
        }
    )

df = pd.DataFrame(rows)

search = st.text_input(
    "Search history",
    placeholder="Filter by role, analysis type, skill, or date...",
)

if search.strip():
    needle = search.strip().lower()
    mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(needle).any(), axis=1)
    df = df[mask]

st.dataframe(df, width="stretch", hide_index=True)
