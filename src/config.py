"""
config.py - Page configuration, session-state init, and global constants.
"""
import os
import streamlit as st

# Paths
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, 'data', 'student_data.csv')
DB_PATH    = os.path.join(BASE_DIR, 'data', 'campus_analytics.db')

# Academic Year
CURRENT_ACADEMIC_YEAR = '2025-26'

PREDICTION_ACCURACY = 0.924

# Multi-Department / Multi-Semester Constants
DEPARTMENTS = ['CSE', 'ECE', 'ME', 'CE', 'ISE']
SEMESTERS   = [1, 2, 3, 4]

DEPT_FULL_NAMES = {
    'CSE': 'Computer Science & Engineering',
    'ECE': 'Electronics & Communication Engineering',
    'ME':  'Mechanical Engineering',
    'CE':  'Civil Engineering',
    'ISE': 'Information Science & Engineering',
}


def set_page_config():
    st.set_page_config(
        page_title="CampusInsight",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def init_session_state():
    defaults = {
        'language':              'English',
        'authenticated':         False,
        'user_role':             'teacher',   # 'teacher' or 'student'
        'student_usn':           None,        # USN of logged-in student
        'registered_users':      {},
        'page':                  'Home',
        'prediction_history':    [],
        'selected_department':   'All',
        'selected_semester':     'All',
        'selected_academic_year': CURRENT_ACADEMIC_YEAR,
        'theme_mode':            'Dark',
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
