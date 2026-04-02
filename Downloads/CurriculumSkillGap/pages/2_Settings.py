import streamlit as st
from auth import get_authenticator
from database import clear_reports_for_user
from utils.ui import apply_modern_theme

st.set_page_config(page_title="Settings", layout="wide")

if not st.session_state.get("authentication_status"):
    st.warning("Please sign in from the **Home** page (app entry).")
    st.stop()

apply_modern_theme("Settings", "Manage account, history, and app preferences.", logo="⚙️")

authenticator = get_authenticator()

st.markdown("### Account")
authenticator.logout("Log out", location="main", key="logout_settings")

st.markdown("### History Controls")
st.write("Clear analysis artifacts from the current session and saved report history.")
if st.button("Clear History", type="secondary"):
    removable_keys = {
        "syllabus_raw_text",
        "syllabus_clean_text",
        "industry_raw_text",
        "industry_clean_text",
        "analysis_result",
        "analysis_count",
    }
    removable_keys.update(
        {key for key in st.session_state.keys() if key.startswith("analysis_")}
    )
    for key in removable_keys:
        st.session_state.pop(key, None)
    clear_reports_for_user(st.session_state.get("username", ""))
    st.success("Session and database history cleared.")

st.markdown("### Theme")
st.success("Light theme is active across the app for better readability.")
