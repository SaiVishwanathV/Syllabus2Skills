"""
Rendering helpers for analysis reports.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_gauge(percentage: float, title: str = "Skill Coverage (%)") -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=percentage,
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#1f77b4"},
                "steps": [
                    {"range": [0, 40], "color": "#fdecea"},
                    {"range": [40, 70], "color": "#fff4e5"},
                    {"range": [70, 100], "color": "#e8f5e9"},
                ],
            },
        )
    )
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, width="stretch")


def render_top_skills_bar(syllabus_skills: list[str], jd_skills: list[str]) -> None:
    rows = []
    for skill in syllabus_skills[:10]:
        rows.append({"skill": skill, "source": "Syllabus", "count": 1})
    for skill in jd_skills[:10]:
        rows.append({"skill": skill, "source": "JD", "count": 1})
    if not rows:
        st.info("Not enough data to render top skills comparison.")
        return
    df = pd.DataFrame(rows)
    pivot_df = df.pivot_table(index="skill", columns="source", values="count", aggfunc="sum", fill_value=0)
    if "JD" not in pivot_df.columns:
        pivot_df["JD"] = 0
    if "Syllabus" not in pivot_df.columns:
        pivot_df["Syllabus"] = 0
    pivot_df = pivot_df.sort_values(by=["JD", "Syllabus"], ascending=False).head(10)
    st.bar_chart(pivot_df)
