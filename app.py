"""
Smart Campus Analytics â€” Streamlit Dashboard
=============================================
Run:      streamlit run app.py
Install:  pip install -r requirements.txt
"""

import sys, os

# Load environment variables from .env file (if present)
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import pandas as pd
import time

# Import modules
from config import set_page_config, init_session_state, DEPARTMENTS, SEMESTERS, DEPT_FULL_NAMES
from language import TEXTS
from styles import set_styles, set_login_styles
from auth import render_login_page
from ai_agent import render_ai_agent
from pages import (
    render_home_page,
    render_predictions_page,
    render_students_page,
    render_reports_page,
    render_settings_page,
    render_year_comparison_page,
    render_student_dashboard,
)

# Set page configuration
set_page_config()

# Initialize session state
init_session_state()

if "reset" in st.query_params:
    st.session_state.page = TEXTS["English"]["nav_options"][0]
    st.query_params.clear()

# ======================================================
# LOGIN PAGE
# ======================================================
if not st.session_state.get("authenticated", False):
    set_login_styles()
    render_login_page()
    st.stop()

# ======================================================
# STUDENT DASHBOARD (restricted view)
# ======================================================
if st.session_state.get("user_role") == "student":
    T = TEXTS[st.session_state.language]
    set_styles()

    # Header
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="header-title">{T['main_title']}</div>
        <div class="header-subtitle">{T.get('student_portal_text', 'Student Portal')}</div>
    </div>
    """, unsafe_allow_html=True)
    # Top Controls Row â”€â”€
    col_spacer, col_lang, col_logout = st.columns([5, 1, 1])
    with col_lang:
        lang_options = ["English", "à¤¹à¤¿à¤¨à¥à¤¦à¥€", "à²•à²¨à³à²¨à²¡"]

        def _on_lang_change():
            st.session_state.language = st.session_state.student_language_selector

        st.selectbox(
            "Select Language",
            lang_options,
            key="student_language_selector",
            label_visibility="collapsed",
            index=lang_options.index(st.session_state.language),
            on_change=_on_lang_change,
        )
    with col_logout:
        if st.button(T["logout"], key="student_logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user_role = "teacher"
            st.session_state.student_usn = None
            st.session_state.prediction_history = []
            st.rerun()

    st.divider()

    # â”€â”€ Render Student Dashboard â”€â”€
    render_student_dashboard()

    st.markdown("<hr style='border: 1px solid var(--border);'>", unsafe_allow_html=True)
    st.caption(T["footer"])
    st.stop()

# ======================================================
# MAIN APPLICATION (Teacher / Admin)
# ======================================================
if st.session_state.get("authenticated", True):
    # Get the current language texts for the main app
    T = TEXTS[st.session_state.language]

    # 1. Apply Dynamic CSS based on state
    set_styles()

    # Header
    st.markdown(f"""
    <div class="dashboard-header" style="cursor:pointer;" onclick="window.parent.location.assign(window.parent.location.pathname + '?reset=1');">
        <div class="header-title">{T['main_title']}</div>
        <div class="header-subtitle">{T['subtitle']}</div>
    </div>
    """, unsafe_allow_html=True)
    # Top Controls Row (User Info, Language, Logout)
    col_spacer, col_user, col_lang, col_logout = st.columns([4, 1.5, 1, 1])
    with col_user:
        st.markdown(f"<p style='text-align: right; margin-top: 10px; font-weight: 600;'>{T['hi_teacher']}</p>", unsafe_allow_html=True)
    with col_lang:
        lang_options = ["English", "à¤¹à¤¿à¤¨à¥à¤¦à¥€", "à²•à²¨à³à²¨à²¡"]

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
            st.session_state.user_role = "teacher"
            st.session_state.student_usn = None
            st.session_state.prediction_history = []
            st.rerun()

    # 4. System Status â€” filtered by selected department & semester
    from config import PREDICTION_ACCURACY, DATA_PATH, CURRENT_ACADEMIC_YEAR
    from data_pro import run_pipeline, run_pipeline_from_db, get_summary_stats, filter_dataframe
    from database import get_available_years, init_db

    # Ensure DB is initialised
    init_db()

    @st.cache_data(show_spinner=False)
    def _get_full_df():
        # Try loading from SQLite first; fall back to CSV if empty
        df = run_pipeline_from_db(CURRENT_ACADEMIC_YEAR)
        if df.empty:
            df = run_pipeline(DATA_PATH)
        return df

    full_df = _get_full_df()
    sel_dept = st.session_state.selected_department
    sel_sem  = st.session_state.selected_semester
    filtered_df = filter_dataframe(full_df, sel_dept, sel_sem)
    s_stats = get_summary_stats(filtered_df)

    TOTAL_STUDENTS = s_stats['total_students']
    AT_RISK_STUDENTS = s_stats['at_risk_count']
    ON_TRACK_STUDENTS = TOTAL_STUDENTS - AT_RISK_STUDENTS

    # Show active filter label
    filter_label = ""
    if sel_dept != "All":
        filter_label += f"{sel_dept}"
    if sel_sem != "All":
        filter_label += f" Â· Sem {sel_sem}"
    if not filter_label:
        filter_label = "All Departments Â· All Semesters"

    st.markdown(f"<h3 style='color: var(--text-primary); margin-bottom: 5px;'>{T['system_status']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='color: var(--text-muted); font-size:12px; margin-bottom:12px'>ðŸ“ {filter_label}</div>", unsafe_allow_html=True)

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
        <div class="stat-card" style="border-left: 4px solid var(--accent-red); margin-bottom: 0;">
            <div class="stat-title">{T['at_risk']}</div>
            <div class="stat-number" id="stat-at-risk">{AT_RISK_STUDENTS}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="stat-card" style="border-left: 4px solid var(--accent-teal); margin-bottom: 0;">
            <div class="stat-title">{T['on_track']}</div>
            <div class="stat-number" id="stat-on-track">{ON_TRACK_STUDENTS}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="stat-card" style="border-left: 4px solid var(--accent-amber); margin-bottom: 0;">
            <div class="stat-title">{T['accuracy']}</div>
            <div class="stat-number" id="stat-accuracy">{PREDICTION_ACCURACY}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 5. Sidebar with Filters + Navigation
    with st.sidebar:
        # â”€â”€ Department & Semester Filters â”€â”€
        st.markdown("<h4 style='color: var(--text-primary); margin-bottom: 8px;'>ðŸ« Filters</h4>", unsafe_allow_html=True)

        dept_options = ["All"] + DEPARTMENTS
        def _on_dept_change():
            st.session_state.selected_department = st.session_state._sidebar_dept

        st.selectbox(
            "Department",
            dept_options,
            key="_sidebar_dept",
            index=dept_options.index(st.session_state.selected_department),
            on_change=_on_dept_change,
            format_func=lambda x: f"All Departments" if x == "All" else f"{x} â€” {DEPT_FULL_NAMES.get(x, x)}",
        )

        sem_options = ["All"] + [str(s) for s in SEMESTERS]
        def _on_sem_change():
            st.session_state.selected_semester = st.session_state._sidebar_sem

        st.selectbox(
            "Semester",
            sem_options,
            key="_sidebar_sem",
            index=sem_options.index(str(st.session_state.selected_semester)),
            on_change=_on_sem_change,
            format_func=lambda x: "All Semesters" if x == "All" else f"Semester {x}",
        )

        st.markdown("<hr style='border: 1px solid var(--border); margin: 12px 0;'>", unsafe_allow_html=True)



        # â”€â”€ Navigation â”€â”€
        st.markdown(f"<h4 style='color: var(--text-primary); margin-bottom: 8px;'>Menu</h4>", unsafe_allow_html=True)
        st.session_state.page = st.radio(
            "Navigation",
            options=T["nav_options"],
            index=TEXTS["English"]["nav_options"].index(st.session_state.page)
                  if st.session_state.page in TEXTS["English"]["nav_options"]
                  else 0,
            label_visibility="collapsed"
        )

        st.markdown("<br><br><br>", unsafe_allow_html=True)

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
    elif page_key == "Year Comparison":
        render_year_comparison_page()
    elif page_key == "Settings":
        render_settings_page()

    st.markdown("<hr style='border: 1px solid var(--border);'>", unsafe_allow_html=True)
    st.caption(T["footer"])

    # Floating AI Agent (visible on every page)
    render_ai_agent()

