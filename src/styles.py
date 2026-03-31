"""
styles.py — CSS injection helpers for login and main dashboard.
"""
import streamlit as st


def set_login_styles():
    """Inject CSS specific to the login page."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding: 2rem 2rem;
        max-width: 900px;
        margin: auto;
    }

    /* Login box */
    .login-box {
        margin-top: 2rem;
        margin-bottom: 0.5rem;
    }
    .login-title {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .login-subtitle {
        font-size: 14px;
        color: #b0b0c0;
        margin-bottom: 12px;
    }

    .teacher-header {
        font-size: 20px;
        font-weight: 600;
        color: #e0e0f0;
        margin-bottom: 18px;
    }

    .footer {
        text-align: center;
        font-size: 12px;
        color: #666;
        margin-top: 30px;
    }

    /* Dark sidebar for login */
    [data-testid="stSidebar"] { background: #0f0f13; border-right: 1px solid #1e1e2e; }
    [data-testid="stSidebar"] * { color: #c9c9d4 !important; }

    /* Overall dark background */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    }
    </style>
    """, unsafe_allow_html=True)


def set_styles(theme: str = "Dark", background_url: str = ""):
    """Inject CSS for the main dashboard, respecting theme and optional background."""

    if theme == "Dark":
        bg_color       = "#0b1437"
        card_bg        = "#111c44"
        text_color     = "#ffffff"
        muted_color    = "#8f9bba"
        border_color   = "rgba(255, 255, 255, 0.05)"
        accent         = "#4318ff"
        sidebar_bg     = "#0b1437"
        sidebar_border = "rgba(255, 255, 255, 0.05)"
        box_shadow     = "none"
    else:
        bg_color       = "#f4f7fe"
        card_bg        = "#ffffff"
        text_color     = "#2b3674"
        muted_color    = "#a3aed1"
        border_color   = "transparent"
        accent         = "#4318ff"
        sidebar_bg     = "#ffffff"
        sidebar_border = "#e2e8f0"
        box_shadow     = "0px 18px 40px rgba(112, 144, 176, 0.12)"

    bg_image = f"url('{background_url}')" if background_url else "none"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

    :root {{
        --main-bg: {bg_color};
        --card-bg: {card_bg};
        --main-text-color: {text_color};
        --muted-color: {muted_color};
        --border-color: {border_color};
        --accent: {accent};
        --box-shadow: {box_shadow};
    }}

    html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
    #MainMenu, footer {{ visibility: hidden; }}

    /* Sidebar collapse/expand button — always visible, fixed top-left */
    header {{ visibility: visible !important; }}
    [data-testid="stHeader"] {{
        background: transparent !important;
        pointer-events: none;
    }}
    button[kind="header"] {{
        pointer-events: auto;
    }}
    [data-testid="collapsedControl"] {{
        display: flex !important;
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 99999;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 6px;
        box-shadow: var(--box-shadow);
        pointer-events: auto;
    }}
    [data-testid="collapsedControl"] svg {{
        fill: var(--main-text-color) !important;
        width: 20px;
        height: 20px;
    }}

    .stApp {{
        background: var(--main-bg);
        background-image: {bg_image};
        background-size: cover;
        color: var(--main-text-color);
    }}

    .block-container {{
        padding: 2rem 3rem 2rem;
        max-width: 1500px;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {sidebar_bg};
        border-right: 1px solid {sidebar_border};
    }}
    [data-testid="stSidebar"] * {{ color: var(--main-text-color) !important; }}

    /* Dashboard header */
    .dashboard-header {{
        margin-bottom: 20px;
    }}
    .header-title {{
        font-size: 34px;
        font-weight: 700;
        color: var(--main-text-color);
        letter-spacing: -0.02em;
    }}
    .header-subtitle {{
        font-size: 15px;
        color: var(--muted-color);
        margin-top: 4px;
    }}

    /* Navigation */
    .nav-container {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 8px 16px;
        box-shadow: var(--box-shadow);
    }}
    
    /* Override Streamlit Radio styling for Navigation to look like modern pills */
    div.stRadio > div[role="radiogroup"] > label {{
        background: transparent !important;
        border: none !important;
        color: var(--muted-color) !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border-radius: 12px !important;
    }}
    div.stRadio > div[role="radiogroup"] > label[data-checked="true"] {{
        background: var(--accent) !important;
        color: white !important;
    }}
    div.stRadio > div[role="radiogroup"] > label:hover {{
        color: var(--main-text-color) !important;
    }}

    /* Stat cards (sidebar) */
    .stat-card {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 18px 22px;
        margin-bottom: 16px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: var(--box-shadow);
        border-left: 6px solid var(--accent);
    }}
    .stat-card:hover {{
        transform: translateY(-3px);
    }}
    .stat-title {{
        font-size: 13px;
        color: var(--muted-color);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
    }}
    .stat-number {{
        font-size: 32px;
        font-weight: 700;
        color: var(--main-text-color);
        margin-top: 6px;
        letter-spacing: -0.02em;
    }}

    /* KPI cards */
    .kpi {{
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 24px 28px;
        box-shadow: var(--box-shadow);
        transition: transform 0.2s ease;
    }}
    .kpi:hover {{
        transform: translateY(-3px);
    }}
    .kv {{ 
        font-size: 36px; 
        font-weight: 700; 
        line-height: 1.1; 
        margin-bottom: 6px; 
        letter-spacing: -0.02em;
    }}
    .kl {{ 
        font-size: 13px; 
        color: var(--muted-color); 
        font-weight: 500; 
    }}
    .ks {{ 
        font-size: 12px; 
        color: var(--muted-color); 
        margin-top: 4px; 
    }}

    /* Section header */
    .sh {{
        font-size: 18px; 
        font-weight: 700; 
        color: var(--main-text-color);
        letter-spacing: -0.01em; 
        padding-bottom: 12px; 
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }}

    /* Alert bar */
    .al {{
        background: rgba(253, 232, 232, 0.8); 
        border: none;
        border-radius: 16px; 
        padding: 16px 20px;
        font-size: 14px; 
        color: #922b21; 
        margin-bottom: 20px;
        font-weight: 500;
    }}

    /* Panel */
    .pr {{
        background: var(--card-bg); 
        border: 1px solid var(--border-color);
        border-radius: 20px; 
        padding: 24px 28px; 
        margin-top: 16px;
        box-shadow: var(--box-shadow);
    }}

    /* Streamlit tabs override */
    button[data-baseweb="tab"] {{
        background: transparent !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        color: var(--muted-color) !important;
        border-radius: 12px 12px 0 0 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--accent) !important;
        border-bottom-color: var(--accent) !important;
        font-weight: 700 !important;
    }}
    </style>
    """, unsafe_allow_html=True)
