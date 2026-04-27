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
        st.markdown("#### System Configuration")
        
        # Academic Year Selection
        from database import get_available_years
        from config import CURRENT_ACADEMIC_YEAR
        
        available_years = get_available_years()
        if CURRENT_ACADEMIC_YEAR not in available_years:
            available_years.insert(0, CURRENT_ACADEMIC_YEAR)
            
        selected_year = st.selectbox(
            "Active Academic Year", 
            options=available_years,
            index=available_years.index(st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR)),
            help="Select the academic year to view data for across the dashboard."
        )
        if selected_year != st.session_state.get('selected_academic_year'):
            st.session_state.selected_academic_year = selected_year
            st.cache_data.clear()
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Display Preferences**")
            st.selectbox("Theme Mode", ["Dark"], disabled=True, help="Currently locked to Dark Mode for optimal UI.")
            
        with c2:
            st.markdown("**Data Management**")
            if st.button("Clear Application Cache", use_container_width=True):
                st.cache_data.clear()
                st.success("Cache cleared successfully!")
                
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"#### {T.get('about_sys', 'About System')}")
        st.markdown("""
        **Smart Campus Analytics - Early Risk Detection System**
        - **Version**: 1.0.0
        - **Engine**: Predictive AI, Pattern Recognition, Smart Analytics (Accuracy ~91%)
        - **Database**: SQLite
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### User Profile")
        user_role = st.session_state.get('user_role', 'Unknown')
        faculty_dept = st.session_state.get('faculty_department', 'All')
        
        if user_role == 'teacher':
            if faculty_dept == 'All':
                display_role = "Global Administrator"
                dept_access = "All Departments"
            else:
                display_role = f"{faculty_dept} Department Admin"
                from config import DEPT_FULL_NAMES
                dept_access = f"{faculty_dept} - {DEPT_FULL_NAMES.get(faculty_dept, faculty_dept)}"
        elif user_role == 'student':
            display_role = "Student"
            dept_access = None
        else:
            display_role = user_role.title()
            dept_access = None

        st.markdown(f"<p><b>Role</b>: {display_role}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><b>Status</b>: Active</p>", unsafe_allow_html=True)
        if dept_access:
             st.markdown(f"<p><b>Department Access</b>: {dept_access}</p>", unsafe_allow_html=True)
        elif user_role == 'student':
             st.markdown(f"<p><b>USN</b>: {st.session_state.get('student_usn')}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
