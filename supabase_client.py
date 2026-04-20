"""
Supabase client singleton.
Reads SUPABASE_URL and SUPABASE_KEY from st.secrets (or env vars as fallback).
"""

from __future__ import annotations

import streamlit as st
from supabase import Client, create_client


@st.cache_resource(show_spinner=False)
def get_supabase() -> Client:
    """Return a cached Supabase client. Called once per Streamlit session."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    
    print("Supabase URL:", url)
    
    if not url or not key:
        raise RuntimeError(
            "Supabase credentials are missing. "
            "Add SUPABASE_URL and SUPABASE_KEY to .streamlit/secrets.toml."
        )
    return create_client(url, key)
