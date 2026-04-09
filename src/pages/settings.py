"""
pages/settings.py — Theme and background configuration.
"""
import streamlit as st
from language import TEXTS


def render_settings_page():
    T = TEXTS[st.session_state.language]

    st.markdown(f"## {T.get('settings_title', 'Settings')}")
    st.markdown(
        f"<div style='color:var(--muted-color,#888);font-size:13px;margin-bottom:20px'>"
        f"{T.get('settings_subtitle', 'Customize the dashboard appearance')}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### 🤖 AI Assistant")
    api_key = st.text_input(
        "Groq API Key",
        value=st.session_state.get("groq_api_key", ""),
        type="password",
        help="Get a key at https://console.groq.com",
        key="settings_api_key",
    )
    if api_key != st.session_state.get("groq_api_key", ""):
        st.session_state.groq_api_key = api_key
        st.success("✅ API key saved! The AI Assistant can now answer any question using Groq.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### ℹ️ About")
    st.info(
        "**Smart Campus Analytics** v2.0\n\n"
        "AI-Powered Early Risk Detection System for CS Department.\n\n"
        "Built with Streamlit · Plotly · scikit-learn"
    )
