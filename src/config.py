"""
config.py — Page configuration, session-state init, and global constants.
"""
import os
import streamlit as st

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, 'data', 'student_data_500.csv')

# ── Constants (sidebar stats) ────────────────────────────────────────────────
TOTAL_STUDENTS      = 500
AT_RISK_STUDENTS    = 127
ON_TRACK_STUDENTS   = 373
PREDICTION_ACCURACY = 0.924


def set_page_config():
    st.set_page_config(
        page_title="Smart Campus Analytics",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def init_session_state():
    defaults = {
        'language':           'English',
        'authenticated':      False,
        'registered_users':   {},
        'theme':              'Dark',
        'background_url':     '',
        'page':               'Home',
        'prediction_history': [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
