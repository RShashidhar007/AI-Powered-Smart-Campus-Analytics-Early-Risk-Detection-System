"""
styles.py - CSS injection helpers for login and main dashboard.
"""
import streamlit as st
from ui_theme import get_page_css


def set_login_styles():
    """Inject CSS specific to the login page."""
    st.markdown(get_page_css(st.session_state.get('theme_mode', 'Dark')), unsafe_allow_html=True)


def set_styles():
    """Inject CSS for the main dashboard"""
    st.markdown(get_page_css(st.session_state.get('theme_mode', 'Dark')), unsafe_allow_html=True)
