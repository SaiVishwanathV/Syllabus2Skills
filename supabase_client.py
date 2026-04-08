"""
Supabase client singleton.
Reads SUPABASE_URL and SUPABASE_KEY from st.secrets (or env vars as fallback).
"""

from __future__ import annotations

import os

import streamlit as st
from supabase import Client, create_client


@st.cache_resource(show_spinner=False)
def get_supabase() -> Client:
    """Return a cached Supabase client. Called once per Streamlit session."""
    url: str = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
    key: str = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
    if not url or not key:
        raise RuntimeError(
            "Supabase credentials are missing. "
            "Add SUPABASE_URL and SUPABASE_KEY to .streamlit/secrets.toml."
        )
    return create_client(url, key)
