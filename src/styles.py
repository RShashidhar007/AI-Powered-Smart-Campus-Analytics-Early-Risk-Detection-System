"""
styles.py — CSS injection helpers for login and main dashboard.
"""
import streamlit as st
from ui_theme import PAGE_CSS


def set_login_styles():
    """Inject CSS specific to the login page."""
    st.markdown(PAGE_CSS, unsafe_allow_html=True)


def set_styles():
    """Inject CSS for the main dashboard"""
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
