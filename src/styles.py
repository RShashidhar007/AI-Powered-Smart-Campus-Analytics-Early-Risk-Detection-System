"""
styles.py — CSS injection helpers for login and main dashboard.
"""
import streamlit as st


def set_login_styles():
    """Inject CSS specific to the login page."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    h1, h2, h3, h4, h5, h6, .login-title, .teacher-header {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding: 2rem 2rem 0rem 2rem !important;
        max-width: 1000px;
        margin: auto;
    }

    /* Login box with Vision UI Glassmorphism */
    .login-box {
        margin-top: 1rem;
        margin-bottom: 1rem;
        background: linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%);
        backdrop-filter: blur(120px);
        -webkit-backdrop-filter: blur(120px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px 30px;
        box-shadow: 0px 20px 40px rgba(0, 0, 0, 0.2);
        animation: float-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        opacity: 0;
        transform: translateY(20px);
    }
    
    @keyframes float-up {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .login-title {
        font-size: 38px;
        font-weight: 800;
        background: linear-gradient(135deg, #0075FF 0%, #2CD9FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .login-subtitle {
        font-size: 15px;
        color: #A0AEC0;
        margin-bottom: 24px;
        line-height: 1.5;
    }

    .teacher-header {
        font-size: 22px;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 20px;
        letter-spacing: -0.01em;
    }

    .footer {
        text-align: center;
        font-size: 13px;
        color: #A0AEC0;
        margin-top: 40px;
    }

    /* Dark sidebar for login */
    [data-testid="stSidebar"] { 
        background: linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%) !important;
        backdrop-filter: blur(120px);
        border-right: 1px solid rgba(255,255,255,0.1); 
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }

    /* Vision UI deep space background */
    .stApp {
        background: linear-gradient(159.02deg, #0f123b 14.25%, #090d2e 56.45%, #020515 86.14%);
        background-attachment: fixed;
    }
    </style>
    """, unsafe_allow_html=True)


def set_styles():
    """Inject CSS for the main dashboard"""

    bg_color       = "#020515"
    card_bg        = "linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%)"
    card_bg_hover  = "linear-gradient(127.09deg, rgba(16, 21, 50, 0.94) 19.41%, rgba(20, 24, 45, 0.49) 76.65%)"
    text_color     = "#FFFFFF"
    text_accent    = "#FFFFFF"
    muted_color    = "#A0AEC0"
    border_color   = "rgba(255, 255, 255, 0.1)"
    border_glow    = "rgba(0, 117, 255, 0.5)"
    accent         = "linear-gradient(135deg, #0075FF 0%, #2CD9FF 100%)"
    accent_flat    = "#0075FF"
    sidebar_bg     = "linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%)"
    box_shadow     = "0px 20px 40px rgba(0, 0, 0, 0.2)"
    shadow_hover   = "0px 20px 40px rgba(0, 117, 255, 0.1)"
    gradient_bg    = "linear-gradient(159.02deg, #0f123b 14.25%, #090d2e 56.45%, #020515 86.14%)"
    alert_bg       = "linear-gradient(127.09deg, rgba(220, 38, 38, 0.3) 19.41%, rgba(220, 38, 38, 0.1) 76.65%)"
    alert_text     = "#fca5a5"
    alert_border   = "rgba(220, 38, 38, 0.3)"
    input_bg       = "rgba(15, 23, 42, 0.4)"

    bg_image = gradient_bg
    bg_size = "cover"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    :root {{
        --main-bg: {bg_color};
        --card-bg: {card_bg};
        --card-bg-hover: {card_bg_hover};
        --main-text-color: {text_color};
        --text-accent: {text_accent};
        --muted-color: {muted_color};
        --border-color: {border_color};
        --border-glow: {border_glow};
        --accent: {accent};
        --accent-flat: {accent_flat};
        --box-shadow: {box_shadow};
        --shadow-hover: {shadow_hover};
        --alert-bg: {alert_bg};
        --alert-text: {alert_text};
        --alert-border: {alert_border};
        --input-bg: {input_bg};
    }}

    html, body, [class*="css"], .stMarkdown, p, div, span, label {{ 
        color: var(--main-text-color);
        font-family: 'Plus Jakarta Sans', sans-serif; 
    }}
    
    /* Ensure Plotly chart text colors adapt generally where streamlits theme variables leak */
    .g-gtitle, .g-xtitle, .g-ytitle, .legendtext {{ fill: var(--muted-color) !important; }}
    
    /* Text overrides specifically for Light mode legibility against white */
    .stDataFrame, .stTable {{ color: var(--main-text-color) !important; }}

    h1, h2, h3, h4, h5, h6, .header-title, .stat-title, .kv, .sh {{ font-family: 'Plus Jakarta Sans', sans-serif; color: var(--main-text-color); }}
    
    #MainMenu, footer {{ visibility: hidden; }}

    /* Sidebar collapse/expand button */
    header {{ visibility: visible !important; background: transparent !important; pointer-events: none; }}
    button[kind="header"] {{ pointer-events: auto; }}
    
    [data-testid="collapsedControl"] {{
        display: flex !important;
        position: fixed;
        top: 16px;
        left: 16px;
        z-index: 99999;
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-color);
        border-radius: 50%;
        padding: 8px;
        box-shadow: var(--box-shadow);
        pointer-events: auto;
        transition: all 0.3s ease;
    }}
    [data-testid="collapsedControl"]:hover {{
        transform: scale(1.1);
        border-color: var(--border-glow);
    }}
    [data-testid="collapsedControl"] svg {{
        fill: var(--main-text-color) !important;
        width: 20px;
        height: 20px;
    }}

    .stApp {{
        background: {bg_image};
        background-size: {bg_size};
        background-attachment: fixed;
        color: var(--main-text-color);
    }}

    .block-container {{
        padding: 3rem 4rem 2rem;
        max-width: 1500px;
        animation: fade-in 0.6s ease-out;
    }}
    
    @keyframes fade-in {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Glassmorphic Sidebar */
    [data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        backdrop-filter: blur(120px);
        -webkit-backdrop-filter: blur(120px);
        border-right: 1px solid var(--border-color);
    }}
    [data-testid="stSidebar"] * {{ color: var(--main-text-color); }}
    
    /* Hide Sidebar Scrollbar robustly */
    [data-testid="stSidebar"]::-webkit-scrollbar,
    [data-testid="stSidebar"] *::-webkit-scrollbar,
    [data-testid="stSidebarUserContent"]::-webkit-scrollbar,
    [data-testid="stSidebarNav"]::-webkit-scrollbar {{
        display: none !important;
        width: 0px !important;
        height: 0px !important;
        background: transparent !important;
    }}
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebarUserContent"] {{
        -ms-overflow-style: none !important;  /* IE and Edge */
        scrollbar-width: none !important;  /* Firefox */
    }}
    
    /* Input Boxes (Selectbox & Text Input) */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{
        background-color: var(--input-bg) !important;
        color: var(--main-text-color) !important;
        border: 1px solid var(--border-color) !important;
    }}

    /* Dashboard header */
    .dashboard-header {{
        margin-bottom: 24px;
        animation: slide-right 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
    }}
    @keyframes slide-right {{
        from {{ opacity: 0; transform: translateX(-20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    .header-title {{
        font-size: 40px;
        font-weight: 800;
        background: var(--accent);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }}
    .header-subtitle {{
        font-size: 16px;
        color: var(--muted-color);
        margin-top: 6px;
        font-weight: 400;
    }}

    /* Main Navigation Pills */
    div.stRadio > div[role="radiogroup"] > label {{
        background: transparent !important;
        border: none !important;
        color: var(--muted-color) !important;
        font-weight: 600 !important;
        padding: 12px 20px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        margin-right: 0 !important;
        margin-bottom: 8px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}
    div.stRadio > div[role="radiogroup"] > label > div:first-child {{
        display: none !important; /* hide default radio indicator */
    }}
    div.stRadio > div[role="radiogroup"] > label[data-checked="true"] {{
        background: var(--accent) !important;
        color: white !important;
        border-color: transparent !important;
        box-shadow: 0 4px 15px var(--border-glow) !important;
        transform: translateY(0px) !important;
    }}
    div.stRadio > div[role="radiogroup"] > label:hover:not([data-checked="true"]) {{
        background: rgba(255, 255, 255, 0.05) !important;
        color: var(--main-text-color) !important;
    }}

    /* Stat cards & KPI cards with Glassmorphism */
    .stat-card, .kpi, .pr {{
        background: var(--card-bg);
        backdrop-filter: blur(120px);
        -webkit-backdrop-filter: blur(120px);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
        box-shadow: var(--box-shadow);
        position: relative;
        overflow: hidden;
    }}
    
    .stat-card {{
        padding: 20px 24px;
        margin-bottom: 16px;
        border-left: 4px solid var(--accent-flat);
    }}
    
    .kpi {{
        padding: 24px 28px;
    }}
    
    .pr {{
        padding: 24px 28px;
        margin-top: 16px;
    }}

    /* Hover effects */
    .stat-card:hover, .kpi:hover, .pr:hover {{
        transform: translateY(-6px) scale(1.01);
        box-shadow: var(--shadow-hover);
        background: var(--card-bg-hover);
        border-color: var(--border-glow);
    }}

    /* Subtle gradient overlay on cards */
    .stat-card::after, .kpi::after {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
    }}

    .stat-title {{
        font-size: 13px;
        color: var(--muted-color);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 700;
    }}
    .stat-number {{
        font-size: 36px;
        font-weight: 800;
        color: var(--main-text-color);
        margin-top: 8px;
        letter-spacing: -0.02em;
    }}

    .kv {{ 
        font-size: 38px; 
        font-weight: 800; 
        line-height: 1.1; 
        margin-bottom: 8px; 
        letter-spacing: -0.03em;
        color: var(--main-text-color);
    }}
    .kl {{ 
        font-size: 14px; 
        color: var(--main-text-color); 
        font-weight: 600; 
        letter-spacing: 0.02em;
    }}
    .ks {{ 
        font-size: 13px; 
        color: var(--muted-color); 
        margin-top: 4px; 
        font-weight: 400;
    }}

    /* Section header */
    .sh {{
        font-size: 18px; 
        font-weight: 700; 
        color: var(--text-accent);
        letter-spacing: -0.01em; 
        padding-bottom: 12px; 
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 24px;
        text-transform: uppercase;
        font-size: 14px;
        letter-spacing: 0.1em;
    }}

    /* Enhanced Alert bar */
    .al {{
        background: var(--alert-bg); 
        backdrop-filter: blur(8px);
        border: 1px solid var(--alert-border);
        border-radius: 16px; 
        padding: 16px 20px;
        font-size: 15px; 
        color: var(--alert-text); 
        margin-bottom: 24px;
        font-weight: 500;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 12px var(--alert-bg);
        animation: pulse-border 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}
    
    @keyframes pulse-border {{
        0%, 100% {{ border-color: var(--alert-border); opacity: 0.8; }}
        50% {{ border-color: var(--alert-border); opacity: 1; filter: brightness(1.2); }}
    }}

    /* Streamlit tabs override for Glass UI */
    button[data-baseweb="tab"] {{
        background: transparent !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        color: var(--muted-color) !important;
        border-radius: 12px 12px 0 0 !important;
        font-size: 16px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--main-text-color) !important;
        border-bottom-color: var(--main-text-color) !important;
        text-shadow: 0 0 12px var(--border-glow);
    }}
    
    /* Scrollbar styling for a cleaner look */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: rgba(0,0,0,0.1);
    }}
    ::-webkit-scrollbar-thumb {{
        background: rgba(100,100,100,0.3);
        border-radius: 8px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: rgba(100,100,100,0.5);
    }}
    
    </style>
    """, unsafe_allow_html=True)
