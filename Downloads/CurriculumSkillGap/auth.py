"""
Authentication bootstrap shared across Streamlit pages.
"""

from __future__ import annotations

import streamlit as st
import streamlit_authenticator as stauth

from database import credentials_dict_for_authenticator, init_db

COOKIE_NAME = "curriculum_skill_gap_auth"


def _cookie_key() -> str:
    try:
        return str(st.secrets["auth"]["cookie_key"])
    except (KeyError, FileNotFoundError, TypeError):
        return "dev_only_set_streamlit_secrets_auth_cookie_key____"


def get_authenticator() -> stauth.Authenticate:
    init_db()
    credentials = credentials_dict_for_authenticator()
    return stauth.Authenticate(
        credentials,
        COOKIE_NAME,
        _cookie_key(),
        cookie_expiry_days=30.0,
        auto_hash=True,
    )
