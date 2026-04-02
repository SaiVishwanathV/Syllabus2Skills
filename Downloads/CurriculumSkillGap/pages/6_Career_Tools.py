import re
import streamlit as st
from pathlib import Path

from utils.pdf_utils import (
    extract_text_by_page_from_pdf_path,
    find_resume_page_index_for_role,
)


def _safe_filename_fragment(s: str) -> str:
    slug = re.sub(r"[^\w\-_.() ]+", "_", s.strip())
    return (slug.replace(" ", "_")[:72] or "resume")


st.set_page_config(
    page_title="Career Tools",
    layout="centered",
)

if not st.session_state.get("authentication_status"):
    st.warning("Please sign in from the **Home** page (app entry).")
    st.stop()

if "career_resume_text" not in st.session_state:
    st.session_state["career_resume_text"] = ""

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; max-width: 42rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

role_options = [
    "Software Engineer",
    "Full Stack Developer",
    "Backend Developer",
    "Frontend Developer",
    "Data Analyst",
    "Machine Learning Engineer (entry-level / intern)",
    "DevOps Engineer",
    "Cloud Engineer",
    "QA Engineer / Test Engineer",
    "System Engineer / Technical Support Engineer",
]

default_role = (
    st.session_state.get("last_selected_role")
    or st.session_state.get("jd_role")
    or "Software Engineer"
)
default_index = role_options.index(default_role) if default_role in role_options else 0

selected_role = st.selectbox(
    "Select role",
    options=role_options,
    index=default_index,
)

pdf_path = Path(__file__).resolve().parent.parent / "10_Role_Resumes_FIXED (1).pdf"

if st.button("Generate Resume", type="primary", width="stretch"):
    st.session_state["last_selected_role"] = selected_role
    if not pdf_path.exists():
        st.session_state["career_resume_text"] = (
            f"PDF not found: `{pdf_path.name}`. Place it in the project root."
        )
    else:
        page_texts = extract_text_by_page_from_pdf_path(str(pdf_path))
        idx = find_resume_page_index_for_role(page_texts, selected_role)
        if idx is None:
            st.session_state["career_resume_text"] = (
                f"No page in the PDF matched role: {selected_role!r}."
            )
        else:
            st.session_state["career_resume_text"] = page_texts[idx]

st.text_area(
    "Resume (edit below)",
    height=320,
    key="career_resume_text",
    placeholder="Select a role and click Generate Resume to load text from the PDF.",
)

current_text = st.session_state.get("career_resume_text", "")
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button(
        "Download as .txt",
        data=current_text.encode("utf-8"),
        file_name=f"{_safe_filename_fragment(selected_role)}_resume.txt",
        mime="text/plain",
        width="stretch",
        disabled=not current_text.strip(),
        key="download_resume_txt",
    )
with col_dl2:
    st.download_button(
        "Download as .md",
        data=current_text.encode("utf-8"),
        file_name=f"{_safe_filename_fragment(selected_role)}_resume.md",
        mime="text/markdown",
        width="stretch",
        disabled=not current_text.strip(),
        key="download_resume_md",
    )
