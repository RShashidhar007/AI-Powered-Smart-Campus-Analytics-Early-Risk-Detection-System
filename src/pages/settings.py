"""
pages/settings.py - System settings and configuration.
"""
import streamlit as st
import os

from language import TEXTS
from ui_theme import get_page_css, GRADE_COL, RISK_COL, DEPT_COL, PL as _PL, PL, kpi_card as _kpi, section_header as _sh

# Design system

def render_settings_page():
    st.markdown(get_page_css(st.session_state.get('theme_mode', 'Dark')), unsafe_allow_html=True)
    T = TEXTS[st.session_state.language]

    st.markdown(f'<div class="page-title">{T.get("settings_title", " System Settings")}</div>', unsafe_allow_html=True)
    st.markdown(
        f"<div class='page-subtitle'>"
        f"{T.get('settings_subtitle', 'Manage API keys, user profile, and system configuration')}</div>",
        unsafe_allow_html=True,
    )

    t1, t2 = st.tabs([T.get("tab_general", " General Config"), T.get("tab_profile", " Profile")])

    with t1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.session_state.theme_mode = "Dark"
        st.caption("Current theme: Dark")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"#### {T.get('about_sys', 'About System')}")
        st.markdown("""
        **Smart Campus Analytics - Early Risk Detection System**
        - **Version**: 1.0.0
        - **Models**: Regression, SVM, Random Forest (Accuracy ~91%)
        - **Database**: SQLite
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### User Profile")
        st.markdown(f"<p><b>Role</b>: {st.session_state.get('user_role', 'Unknown').title()}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><b>Status</b>: Active</p>", unsafe_allow_html=True)
        if st.session_state.get('user_role') == 'teacher':
             st.markdown(f"<p><b>Department Access</b>: All Departments</p>", unsafe_allow_html=True)
        else:
             st.markdown(f"<p><b>USN</b>: {st.session_state.get('student_usn')}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
