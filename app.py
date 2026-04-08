"""
Curriculum–Industry Skill Gap Analysis — main entry (Phase 1).
Run: streamlit run app.py
"""

from __future__ import annotations

import random

import streamlit as st
from streamlit_authenticator.utilities import Hasher, Validator

from auth import get_authenticator
from database import (
    create_user,
    email_exists,
    username_exists,
)
from utils.email_utils import send_otp_email
from utils.nlp_utils import ensure_nltk_resources
from utils.ui import apply_modern_theme


st.set_page_config(
    page_title="Curriculum–Industry Skill Gap",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

authenticator = get_authenticator()


def _render_signup() -> None:
    validator = Validator()

    if "registration_step" not in st.session_state:
        st.session_state["registration_step"] = "form"

    if st.session_state["registration_step"] == "otp":
        st.subheader("Verify your email")
        st.info(f"We sent a 6-digit verification code to **{st.session_state['registration_data']['email']}**.")
        with st.form("otp_form"):
            user_otp = st.text_input("Enter 6-digit code", max_chars=6)
            col1, col2 = st.columns(2)
            with col1:
                verify_btn = st.form_submit_button("Verify & Create Account")
            with col2:
                cancel_btn = st.form_submit_button("Cancel / Back")
        
        if cancel_btn:
            st.session_state["registration_step"] = "form"
            st.rerun()
            
        if verify_btn:
            if user_otp.strip() == st.session_state["registration_otp"]:
                data = st.session_state["registration_data"]
                create_user(
                    username=data["username"],
                    email=data["email"],
                    password_hash=Hasher.hash(data["password"]),
                    display_name=data["display_name"],
                )
                st.session_state["registration_step"] = "form"
                
                st.success("Account created and verified! You can now sign in under **Log in**.")
                st.balloons()
            else:
                st.error("Incorrect verification code. Please try again.")
        return

    st.caption("Password: 8–20 characters, with upper, lower, digit, and special character.")
    with st.form("signup_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="e.g. janesmith",
            help="Up to 20 characters: letters, digits, _ or -",
        )
        display_name = st.text_input("Display name", placeholder="e.g. Jane Smith")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        password_2 = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Send Verification Code")

    if not submitted:
        return

    username = username.strip()
    display_name = display_name.strip()
    email = email.strip()

    if not username or not display_name or not email or not password:
        st.error("Please fill in all fields.")
        return
    if not validator.validate_username(username):
        st.error("Username format is invalid.")
        return
    if not validator.validate_name(display_name):
        st.error("Display name must be 2–100 characters (letters, spaces, common punctuation).")
        return
    if not validator.validate_email(email):
        st.error("Please enter a valid email address.")
        return
    if not validator.validate_password(password):
        st.error(validator.diagnose_password(password))
        return
    if password != password_2:
        st.error("Passwords do not match.")
        return
    if username_exists(username):
        st.error("That username is already registered.")
        return
    if email_exists(email):
        st.error("That email is already registered.")
        return

    with st.spinner("Sending code..."):
        otp_code = str(random.randint(100000, 999999))
        if send_otp_email(email, otp_code):
            st.session_state["registration_step"] = "otp"
            st.session_state["registration_data"] = {
                "username": username,
                "display_name": display_name,
                "email": email,
                "password": password
            }
            st.session_state["registration_otp"] = otp_code
            st.rerun()


def main() -> None:
    apply_modern_theme(
        "From Syllabus to Skills",
        "NLP-driven curriculum vs industry gap analysis with smart career tools.",
        logo="🎓",
    )

    if st.session_state.get("authentication_status"):
        try:
            ensure_nltk_resources()
            st.session_state["nlp_ready"] = True
        except Exception:
            st.session_state["nlp_ready"] = False
        with st.sidebar:
            st.markdown("### Account")
            st.caption(f"**{st.session_state.get('name', '')}** (`{st.session_state.get('username', '')}`)")
            authenticator.logout("Log out", location="sidebar", key="logout_sidebar")
            st.markdown("---")
            st.markdown("### Navigation")
            st.info(
                "Use the **pages list** in the sidebar (above) to open **Dashboard** or **Settings**."
            )
        st.success(f"Welcome, {st.session_state.get('name', 'user')}.")
        st.markdown(
            "- Open **Dashboard** for your analysis home and NLP status.\n"
            "- Open **Settings** for account controls and app preferences."
        )
        return

    login_tab, signup_tab = st.tabs(["Log in", "Sign up"])
    with login_tab:
        authenticator.login(location="main", key="Login")
        if st.session_state.get("authentication_status") is False:
            st.error("Username or password is incorrect.")

    with signup_tab:
        _render_signup()


if __name__ == "__main__":
    main()
