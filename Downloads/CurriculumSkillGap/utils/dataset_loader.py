"""
Loader for heterogeneous JD datasets provided as CSVs.
Dynamically locates 'Title' and 'Description/Skills' columns.
"""

from __future__ import annotations

import glob
import os

import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def get_available_datasets() -> list[str]:
    """Return a list of all CSVs in the root folder except for the skill strength one."""
    csvs = glob.glob("*.csv")
    return [c for c in csvs if c != "skill_match_dataset.csv"]

@st.cache_data(show_spinner="Loading and unifying dataset...", max_entries=5)
def load_and_unify_dataset(filename: str) -> pd.DataFrame:
    """
    Load a local CSV file and intelligently rename its primary columns
    to 'Job Title' and 'Job Description' so downstream UI can filter them.
    """
    if not os.path.exists(filename):
        return pd.DataFrame()
        
    try:
        df = pd.read_csv(filename, engine="python", on_bad_lines="skip")
    except Exception:
        return pd.DataFrame()

    if df.empty:
        return df

    columns_lower = {col: col.lower().strip() for col in df.columns}
    
    # 1. Identify best column for Job Title
    title_col = None
    for src_col, lower in columns_lower.items():
        if lower in ["job_title", "title", "job title", "role"]:
            title_col = src_col
            break

    # 2. Identify best column for Job Description / Skills
    desc_col = None
    for src_col, lower in columns_lower.items():
        if "skill" in lower or "desc" in lower or "req" in lower or "sum" in lower:
            desc_col = src_col
            # Prefer 'skills' if it explicitly appears to avoid generic summaries
            if "skill" in lower:
                break

    if not title_col or not desc_col:
        return pd.DataFrame()

    unified = pd.DataFrame({
        "Job Title": df[title_col].astype(str),
        "Job Description": df[desc_col].astype(str)
    })
    
    # Clean up empty rows
    unified = unified.dropna()
    unified = unified[unified["Job Title"].str.strip() != ""]
    return unified

def aggregate_text_by_role(df: pd.DataFrame, role_query: str) -> str:
    """
    Filters unified DF by the query and concatenates descriptions.
    """
    if df.empty or not role_query:
        return ""
    
    query = role_query.lower().strip()
    mask = df["Job Title"].str.lower().str.contains(query, na=False)
    filtered = df[mask]
    
    if filtered.empty:
        return ""
        
    return " ".join(filtered["Job Description"].tolist())

def aggregate_from_all_datasets(role_query: str) -> str:
    """
    Searches across all available benchmark CSVs, unifying and
    concatenating any Job Descriptions that match the requested role.
    """
    if not role_query:
        return ""
        
    datasets = get_available_datasets()
    combined_texts = []
    
    for ds in datasets:
        df = load_and_unify_dataset(ds)
        if not df.empty:
            text = aggregate_text_by_role(df, role_query)
            if text:
                combined_texts.append(text)
                
    return " ".join(combined_texts)
