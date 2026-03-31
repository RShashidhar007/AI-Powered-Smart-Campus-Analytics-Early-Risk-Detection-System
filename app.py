"""
Smart Campus Analytics — Streamlit Dashboard
=============================================
Run:      streamlit run app.py
Install:  pip install streamlit plotly scikit-learn pandas numpy openpyxl qrcode
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import pandas as pd
import time

# Import modules
from config import set_page_config, init_session_state
from language import TEXTS
from styles import set_styles, set_login_styles
from auth import render_login_page
from ai_agent import render_ai_agent
from pages import (
    render_home_page,
    render_predictions_page,
    render_students_page,
    render_reports_page,
    render_settings_page
)

# Set page configuration
set_page_config()

# Initialize session state
init_session_state()

# ======================================================
# LOGIN PAGE
# ======================================================
if not st.session_state.get("authenticated", False):
    set_login_styles()
    render_login_page()
    st.stop()

# ======================================================
# MAIN APPLICATION
# ======================================================
if st.session_state.get("authenticated", True):
    # Get the current language texts for the main app
    T = TEXTS[st.session_state.language]

    # 1. Apply Dynamic CSS based on state
    set_styles(st.session_state.theme, st.session_state.background_url)

    # 2. Professional Header Section with Logo (clickable → Home)
    header_col1, header_col2 = st.columns([0.5, 5])
    with header_col1:
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "yangzhou_logo.png")
        if os.path.exists(logo_path):
            if st.button("🏠", key="logo_home_btn", help="Go to Home"):
                st.session_state.page = T["nav_options"][0]
                st.rerun()
            st.image(logo_path, width=80)
        else:
            if st.button("🎓", key="logo_home_btn2", help="Go to Home"):
                st.session_state.page = T["nav_options"][0]
                st.rerun()
    with header_col2:
        st.markdown(f"""
        <div class="dashboard-header" style="cursor:pointer;" onclick="window.location.reload();">
            <div class="header-title">{T['main_title']}</div>
            <div class="header-subtitle">{T['subtitle']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🏠 Home", key="title_home_btn", type="tertiary"):
            st.session_state.page = T["nav_options"][0]
            st.rerun()

    # 3. Top Controls Row (User Info, Language, Logout)
    col_spacer, col_user, col_lang, col_logout = st.columns([4, 1.5, 1, 1])
    with col_user:
        st.markdown(f"<p style='text-align: right; margin-top: 10px; font-weight: 600;'>{T['hi_teacher']}</p>", unsafe_allow_html=True)
    with col_lang:
        lang_options = ["English", "हिन्दी", "ಕನ್ನಡ"]

        def _on_lang_change():
            st.session_state.language = st.session_state.dashboard_language_selector

        st.selectbox(
            "Select Language",
            lang_options,
            key="dashboard_language_selector",
            label_visibility="collapsed",
            index=lang_options.index(st.session_state.language),
            on_change=_on_lang_change,
        )
    with col_logout:
        if st.button(T["logout"], key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.prediction_history = []
            st.rerun()

    # 4. System Status (previously in sidebar, now at top of main view)
    from config import PREDICTION_ACCURACY, DATA_PATH
    from data_pro import run_pipeline, get_summary_stats
    
    @st.cache_data(show_spinner=False)
    def _get_system_stats():
        _df = run_pipeline(DATA_PATH)
        return get_summary_stats(_df)
        
    s_stats = _get_system_stats()
    TOTAL_STUDENTS = s_stats['total_students']
    AT_RISK_STUDENTS = s_stats['at_risk_count']
    ON_TRACK_STUDENTS = TOTAL_STUDENTS - AT_RISK_STUDENTS
    
    st.markdown(f"<h3 style='color: var(--main-text-color); margin-bottom: 15px;'>{T['system_status']}</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="stat-card" style="margin-bottom: 0;">
            <div class="stat-title">{T['total_students']}</div>
            <div class="stat-number" id="stat-total">{TOTAL_STUDENTS}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="stat-card" style="border-left: 6px solid #C0392B; margin-bottom: 0;">
            <div class="stat-title">{T['at_risk']}</div>
            <div class="stat-number" id="stat-at-risk">{AT_RISK_STUDENTS}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="stat-card" style="border-left: 6px solid #27AE60; margin-bottom: 0;">
            <div class="stat-title">{T['on_track']}</div>
            <div class="stat-number" id="stat-on-track">{ON_TRACK_STUDENTS}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="stat-card" style="border-left: 6px solid #F39C12; margin-bottom: 0;">
            <div class="stat-title">{T['accuracy']}</div>
            <div class="stat-number" id="stat-accuracy">{PREDICTION_ACCURACY}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 5. Sidebar with Navigation (previously in main view)
    with st.sidebar:
        st.markdown(f"<h3 style='color: var(--main-text-color); margin-bottom: 15px;'>Menu</h3>", unsafe_allow_html=True)
        # We don't need horizontal=True here since it's in the vertical sidebar
        st.session_state.page = st.radio(
            "Navigation",
            options=T["nav_options"],
            index=TEXTS["English"]["nav_options"].index(st.session_state.page)
                  if st.session_state.page in TEXTS["English"]["nav_options"]
                  else 0,
            label_visibility="collapsed"
        )
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid var(--border-color);'>", unsafe_allow_html=True)
        st.caption(f"Current Theme: **{st.session_state.theme}**")

    # 6. Render Selected Page Content
    page_index = T["nav_options"].index(st.session_state.page)
    page_key = TEXTS["English"]["nav_options"][page_index]

    if page_key == "Home":
        render_home_page()
    elif page_key == "Predictions":
        render_predictions_page()
    elif page_key == "Students":
        render_students_page()
    elif page_key == "Reports":
        render_reports_page()
    elif page_key == "Settings":
        render_settings_page()

    st.markdown("<hr style='border: 1px solid #2874A6;'>", unsafe_allow_html=True)
    st.caption(T["footer"])

    # Floating AI Agent (visible on every page)
    render_ai_agent()
