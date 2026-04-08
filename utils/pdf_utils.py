"""
PDF extraction helpers.
"""

from __future__ import annotations

from io import BytesIO

import pdfplumber
import streamlit as st


@st.cache_data(show_spinner=False)
def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)
    return "\n".join(text_parts).strip()


@st.cache_data(show_spinner=False)
def extract_text_by_page_from_pdf_path(pdf_path: str) -> list[str]:
    page_texts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_texts.append((page.extract_text() or "").strip())
    return page_texts


def find_resume_page_index_for_role(page_texts: list[str], role: str) -> int | None:
    """Match role to a resume page: prefer header/title lines, then full-page phrase."""
    selected = role.strip().lower()
    if not selected:
        return None
    for idx, page_text in enumerate(page_texts):
        lines = [line.strip() for line in page_text.splitlines() if line.strip()]
        header_window = "\n".join(lines[:8]).lower()
        if selected in header_window:
            return idx
    for idx, page_text in enumerate(page_texts):
        if selected in page_text.lower():
            return idx
    return None
