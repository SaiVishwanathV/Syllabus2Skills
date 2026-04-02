import json

import streamlit as st

from analysis_engine import analyze_gap, predictive_suggestions
from ai_processor import verify_results
from database import create_report
from utils.nlp_utils import clean_text, ensure_nltk_resources
from utils.pdf_utils import extract_text_from_pdf_bytes
from utils.reporting import render_gauge, render_top_skills_bar
from utils.dataset_loader import get_available_datasets, load_and_unify_dataset, aggregate_text_by_role, aggregate_from_all_datasets
from utils.ui import apply_modern_theme

st.set_page_config(page_title="Syllabus vs JD", layout="wide")
MAX_ANALYSIS_CHARS = 40000

if not st.session_state.get("authentication_status"):
    st.warning("Please sign in from the **Home** page (app entry).")
    st.stop()

ensure_nltk_resources()

apply_modern_theme(
    "Syllabus vs Industry JD Analysis",
    "Upload syllabus + JD and uncover skill coverage gaps with precision categories.",
    logo="📘",
)

st.markdown("### 1) Syllabus Input")
uploaded_syllabi = st.file_uploader(
    "Upload one or more syllabus PDFs",
    type=["pdf"],
    accept_multiple_files=True,
    help="PDF text is extracted and preprocessed before analysis.",
)

syllabus_name = st.text_input(
    "Syllabus Name",
    placeholder="e.g. B.Tech CSE Semester 6 Curriculum",
)

syllabus_raw_text = ""
if uploaded_syllabi:
    extracted_blocks = []
    for file in uploaded_syllabi:
        text = extract_text_from_pdf_bytes(file.getvalue())
        if text:
            extracted_blocks.append(text)
    syllabus_raw_text = "\n".join(extracted_blocks).strip()
    if syllabus_raw_text:
        st.success(f"Extracted text from {len(uploaded_syllabi)} file(s).")
    else:
        st.error("Could not extract text from uploaded PDF(s). Please verify file content.")

st.markdown("### 2) Industry Input")
industry_mode = st.radio(
    "Choose JD input mode",
    ["Full Job Description", "Direct Skills List", "Auto-generate Industry Benchmark"],
    horizontal=True,
)

jd_role = st.text_input(
    "JD Name / Role",
    placeholder="e.g. Data Scientist Intern",
)

jd_text = ""
if industry_mode == "Full Job Description":
    jd_text = st.text_area(
        "Paste full Job Description",
        height=180,
        placeholder="Paste a complete job description here...",
    )
elif industry_mode == "Direct Skills List":
    skills_text = st.text_area(
        "Enter comma-separated skills",
        height=120,
        placeholder="python, machine learning, sql, nlp, deep learning",
    )
    jd_text = skills_text.replace(",", " ")
else:
    st.info("The system will automatically search all uploaded market datasets in the background to build a massive industry benchmark for the role you specify above!")

if st.button("Run Skill Gap Analysis", type="primary", width="stretch"):
    if industry_mode == "Auto-generate Industry Benchmark":
        with st.spinner(f"Scanning all datasets to auto-generate benchmark for '{jd_role}'..."):
            jd_text = aggregate_from_all_datasets(jd_role)
            if not jd_text:
                st.error(f"No postings found for '{jd_role}' across any of the market datasets. Try a broader search.")
                st.stop()
            st.success(f"Aggregated market data for {jd_role} successfully!")

    if not syllabus_raw_text:
        st.error("Please upload a syllabus before running analysis.")
        st.stop()
    if not jd_text.strip():
        st.error("Please provide JD text, skills, or select a valid dataset before running analysis.")
        st.stop()
    if not syllabus_name.strip():
        st.error("Please provide a syllabus name.")
        st.stop()
    if not jd_role.strip():
        st.error("Please provide a JD name/role.")
        st.stop()

    syllabus_for_analysis = syllabus_raw_text[:MAX_ANALYSIS_CHARS]
    jd_for_analysis = jd_text[:MAX_ANALYSIS_CHARS]
    with st.spinner("Analyzing curriculum data and cross-referencing industry standards..."):
        baseline_result = analyze_gap(syllabus_for_analysis, jd_for_analysis, top_k=40)
        result = verify_results(
            baseline_result,
            {"syllabus_text": syllabus_raw_text, "jd_text": jd_text},
        )
    st.session_state["latest_analysis_result"] = result
    st.session_state["latest_analysis_type"] = "syllabus_vs_jd"
    st.session_state["analysis_count"] = st.session_state.get("analysis_count", 0) + 1
    st.session_state["jd_role"] = jd_role.strip()
    st.session_state["syllabus_raw_text"] = syllabus_raw_text
    st.session_state["industry_raw_text"] = jd_text
    st.session_state["syllabus_clean_text"] = clean_text(syllabus_for_analysis)
    st.session_state["industry_clean_text"] = clean_text(jd_for_analysis)

    create_report(
        username=st.session_state.get("username", ""),
        analysis_type="syllabus_vs_jd",
        syllabus_name=syllabus_name.strip(),
        jd_role=jd_role.strip(),
        cosine_similarity=float(result["cosine_similarity"]),
        gap_index_score=float(result["skill_gap_index"]),
        missing_skills_json=json.dumps(result["missing_skills"]),
        matching_skills_json=json.dumps(result["matching_skills"]),
    )
    st.success("Analysis complete and saved to history.")

result = st.session_state.get("latest_analysis_result")
if result and st.session_state.get("latest_analysis_type") == "syllabus_vs_jd":
    st.markdown("## Skill Coverage Analysis")
    coverage_score = 100.0 - float(result["skill_gap_index"])
    render_gauge(coverage_score, title="Skill Coverage (%)")

    st.markdown("### Top Skills Comparison")
    render_top_skills_bar(
        syllabus_skills=result.get("syllabus_top_skills", []),
        jd_skills=result.get("jd_top_skills", []),
    )

    left, right = st.columns(2)
    with left:
        st.markdown("### Missing Skills")
        missing = result.get("missing_skills", [])
        if missing:
            st.write(missing)
        else:
            st.caption("No skills in this category.")
    with right:
        st.markdown("### Skill Match Categories")
        strong = result.get("strong_match", result.get("good_matches", []))
        partial = result.get("partial_match", [])
        weak = result.get("weak_match", result.get("partial_matches", []))
        st.markdown("**Strong Match**")
        if strong:
            st.write(strong)
        else:
            st.caption("No skills in this category.")
        st.markdown("**Partial Match**")
        if partial:
            st.write(partial)
        else:
            st.caption("No skills in this category.")
        st.markdown("**Weak Match**")
        if weak:
            st.write(weak)
        else:
            st.caption("No skills in this category.")

    with st.expander("Matched skill strength details"):
        st.write(result.get("skill_strength", {}))

    st.markdown("### Match Quality")
    st.write(
        {
            "strong_match": result.get("strong_match", result.get("good_matches", [])),
            "partial_match": result.get("partial_match", []),
            "weak_match": result.get("weak_match", result.get("partial_matches", [])),
        }
    )

    st.markdown("### Predictive Suggestions")
    for item in predictive_suggestions(result.get("missing_skills", [])):
        st.markdown(f"- {item}")
