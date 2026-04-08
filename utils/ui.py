from __future__ import annotations

import streamlit as st


def apply_modern_theme(page_title: str, subtitle: str = "", logo: str = "✨") -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #f8fbff 0%, #eef6ff 45%, #f4f7ff 100%);
            color: #0f172a;
        }
        .block-container {
            padding-top: 1.1rem;
            font-size: 1.05rem;
        }
        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #dbeafe;
        }
        div[data-testid="metric-container"] {
            background: linear-gradient(135deg, #eef2ff, #e0f2fe);
            border: 1px solid #bfdbfe;
            border-radius: 14px;
            padding: 0.8rem 1rem;
        }
        .stButton > button {
            background: linear-gradient(90deg, #6366f1, #06b6d4);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            font-size: 1rem;
            padding: 0.5rem 0.9rem;
        }
        .stButton > button:hover {
            filter: brightness(1.07);
        }
        div[data-testid="stExpander"] {
            border: 1px solid #bfdbfe;
            border-radius: 10px;
            background: #f8fbff;
        }
        .cg-hero {
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1.05rem 1.2rem;
            margin-bottom: 1rem;
            background: linear-gradient(120deg, #e0e7ff, #dbeafe, #cffafe);
            box-shadow: 0 6px 18px rgba(30, 64, 175, 0.12);
        }
        .cg-hero h2 {
            margin: 0;
            font-size: 2rem;
            line-height: 1.2;
            font-weight: 800;
            background: linear-gradient(90deg, #4f46e5, #0284c7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .cg-hero p {
            margin: .45rem 0 0;
            color: #1e3a8a;
            font-size: 1.06rem;
            font-weight: 500;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        p, li, label, .stMarkdown, .stCaption {
            color: #0f172a !important;
            font-size: 1rem !important;
        }
        .stDataFrame, .stTable {
            font-size: 0.97rem;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        .cg-logo {
            font-size: 1.55rem;
            margin-right: .45rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="cg-hero">
            <h2><span class="cg-logo">{logo}</span>{page_title}</h2>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
