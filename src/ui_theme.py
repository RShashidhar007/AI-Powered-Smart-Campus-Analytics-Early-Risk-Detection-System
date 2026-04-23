"""
ui_theme.py - Centralised UI design tokens for the Smart Campus dashboard.

This module contains ONLY visual / styling constants and tiny HTML-helper
functions. It holds NO business logic, no data access, no model code.

Every page imports from here instead of carrying its own PAGE_CSS block.
"""

# Colour maps (used by Plotly charts)
GRADE_COL = {
    "A": "#81C784", "B": "#81A1C1", "C": "#E5C07B",
    "D": "#D19A66", "F": "#E06C75",
}
RISK_COL = {
    "Low": "#81C784", "Moderate": "#E5C07B",
    "High": "#D19A66", "Critical": "#E06C75",
}
DEPT_COL = {
    "CSE": "#81A1C1", "ECE": "#B48EAD", "ME": "#E5C07B",
    "CE": "#56B6C2", "ISE": "#E06C75",
}

# Plotly layout template
PL = dict(
    font=dict(family="Inter, sans-serif", color="var(--text-primary)"),
    title_font=dict(color="var(--text-primary)"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=12, r=12, t=40, b=12),
    xaxis=dict(
        gridcolor="rgba(128, 128, 128, 0.15)",
        zerolinecolor="rgba(128, 128, 128, 0.25)",
        tickfont=dict(color="var(--text-secondary)"),
        title=dict(font=dict(color="var(--text-secondary)")),
    ),
    yaxis=dict(
        gridcolor="rgba(128, 128, 128, 0.15)",
        zerolinecolor="rgba(128, 128, 128, 0.25)",
        tickfont=dict(color="var(--text-secondary)"),
        title=dict(font=dict(color="var(--text-secondary)")),
    ),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="var(--text-secondary)")),
)

THEME_TOKENS = {
    "Dark": {
        "bg": "#1E293B",
        "bg_secondary": "#334155",
        "card_bg": "#334155",
        "text_primary": "#F8FAFC",
        "text_secondary": "#E2E8F0",
        "text_muted": "#94A3B8",
        "accent": "#81A1C1",
        "accent_light": "#5E81AC",
        "accent_teal": "#8FBCBB",
        "accent_red": "#BF616A",
        "accent_amber": "#EBCB8B",
        "border": "#475569",
        "border_hover": "#64748B",
        "shadow": "0 4px 6px -1px rgba(0,0,0,0.5), 0 2px 4px -2px rgba(0,0,0,0.5)",
        "shadow_md": "0 10px 15px -3px rgba(0,0,0,0.5), 0 4px 6px -4px rgba(0,0,0,0.5)",
        "shadow_hover": "0 20px 25px -5px rgba(0,0,0,0.6), 0 8px 10px -6px rgba(0,0,0,0.6)",
        "collapse_icon_fill": "%23F8FAFC",
    },
    "Light": {
        "bg": "#F4F7FB",
        "bg_secondary": "#E8EEF6",
        "card_bg": "#FFFFFF",
        "text_primary": "#172033",
        "text_secondary": "#334155",
        "text_muted": "#64748B",
        "accent": "#2563EB",
        "accent_light": "#1D4ED8",
        "accent_teal": "#0F766E",
        "accent_red": "#DC2626",
        "accent_amber": "#B45309",
        "border": "#D7DEE8",
        "border_hover": "#A9B8CB",
        "shadow": "0 4px 12px rgba(15,23,42,0.08), 0 1px 3px rgba(15,23,42,0.06)",
        "shadow_md": "0 12px 24px rgba(15,23,42,0.10), 0 4px 10px rgba(15,23,42,0.08)",
        "shadow_hover": "0 18px 30px rgba(15,23,42,0.14), 0 8px 16px rgba(15,23,42,0.10)",
        "collapse_icon_fill": "%23172033",
    },
}


def get_page_css(theme_mode="Dark"):
    """Return app CSS for the selected visual theme."""
    theme = THEME_TOKENS.get(theme_mode, THEME_TOKENS["Dark"])
    css = PAGE_CSS_TEMPLATE
    for key, value in theme.items():
        css = css.replace("{" + key + "}", value)
    return css


# Shared PAGE_CSS template
PAGE_CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* Root design tokens */
:root {
    --bg:              {bg};
    --bg-secondary:    {bg_secondary};
    --card-bg:         {card_bg};
    --text-primary:    {text_primary};
    --text-secondary:  {text_secondary};
    --text-muted:      {text_muted};
    --accent:          {accent};
    --accent-light:    {accent_light};
    --accent-teal:     {accent_teal};
    --accent-red:      {accent_red};
    --accent-amber:    {accent_amber};
    --border:          {border};
    --border-hover:    {border_hover};
    --shadow:          {shadow};
    --shadow-md:       {shadow_md};
    --shadow-hover:    {shadow_hover};
    --radius:          16px;
    --radius-sm:       12px;
}

/* Global typography */
html, body, p, label, a, button, input, select, textarea {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-secondary);
}
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}
/* Ensure Material Icons font is never overridden */
.material-icons, .material-symbols-rounded, [class*="icon"] {
    font-family: 'Material Icons', 'Material Symbols Rounded', sans-serif !important;
}

/* Background */
.stApp {
    background: var(--bg) !important;
}

/* Hide default Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
header {
    visibility: visible !important;
    background: transparent !important;
    pointer-events: none;
}
button[kind="header"] { pointer-events: auto; }

/* Sidebar collapse/expand button */
/* Sidebar collapse/expand button */
[data-testid="collapsedControl"], 
[data-testid="stSidebarCollapsedControl"] {
    position: fixed !important;
    top: 16px !important;
    left: 16px !important;
    z-index: 99999 !important;
    display: block !important;
    
    /* Bulletproof text/icon hiding */
    text-indent: -9999px !important;
    overflow: hidden !important;
    white-space: nowrap !important;
    
    background: var(--card-bg) url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{collapse_icon_fill}"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>') no-repeat center center !important;
    background-size: 20px 20px !important;
    border: 1px solid var(--border) !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    padding: 0 !important;
    box-shadow: var(--shadow) !important;
    pointer-events: auto !important;
    transition: all 0.2s ease !important;
    color: transparent !important;
}
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover {
    box-shadow: var(--shadow-hover) !important;
    border-color: var(--border-hover) !important;
}
/* Hide text label from the close button inside sidebar */
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] p,
[data-testid="stSidebar"] [data-testid="baseButton-headerNoPadding"] p,
[data-testid="stSidebar"] button p {
    display: none !important;
}

/* Block container */
.block-container {
    padding: 2.5rem 3rem 2rem !important;
    max-width: 1500px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--card-bg) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-secondary) !important;
}
[data-testid="stSidebar"]::-webkit-scrollbar,
[data-testid="stSidebar"] *::-webkit-scrollbar,
[data-testid="stSidebarUserContent"]::-webkit-scrollbar {
    display: none !important;
    width: 0px !important;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] *,
[data-testid="stSidebarUserContent"] {
    -ms-overflow-style: none !important;
    scrollbar-width: none !important;
}

/* Input fields */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--text-muted) !important;
}

/* Radio navigation pills */
div.stRadio > div[role="radiogroup"] > label {
    background: transparent !important;
    border: none !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.2s ease !important;
    margin-bottom: 4px !important;
    font-family: 'Inter', sans-serif !important;
}
div.stRadio > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}
div.stRadio > div[role="radiogroup"] > label[data-checked="true"] {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25) !important;
}
div.stRadio > div[role="radiogroup"] > label:hover:not([data-checked="true"]) {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    background: transparent !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    font-size: 14px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 1px 3px rgba(37, 99, 235, 0.2) !important;
    transition: all 0.2s ease !important;
    padding: 0.5rem 1.25rem !important;
}
.stButton > button:hover {
    background: var(--accent-light) !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
    transform: translateY(-1px) !important;
}
.stDownloadButton > button {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
}
.stDownloadButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* Data tables */
.stDataFrame {
    border-radius: var(--radius) !important;
    overflow: hidden;
    border: 1px solid var(--border);
}

/* Sliders */
.stSlider > div > div > div > div {
    background: var(--accent) !important;
}

/* Card classes */
.glass-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 28px;
    box-shadow: var(--shadow);
    transition: all 0.2s ease;
    margin-bottom: 16px;
}
.glass-card:hover {
    box-shadow: var(--shadow-hover);
    border-color: var(--border-hover);
    transform: translateY(-2px);
}

/* KPI card */
.kpi {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: var(--shadow);
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.kpi:hover {
    box-shadow: var(--shadow-hover);
    border-color: var(--border-hover);
    transform: translateY(-2px);
}
.kv {
    font-size: 32px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 6px;
    letter-spacing: -0.03em;
    color: var(--text-primary);
}
.kl {
    font-size: 13px;
    color: var(--text-secondary);
    font-weight: 600;
    letter-spacing: 0.01em;
}
.ks {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
    font-weight: 400;
}

/* Stat card (used in app.py) */
.stat-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: var(--shadow);
    transition: all 0.2s ease;
    border-left: 4px solid var(--accent);
}
.stat-card:hover {
    box-shadow: var(--shadow-hover);
    border-color: var(--border-hover);
    border-left-color: var(--accent);
    transform: translateY(-2px);
}
.stat-title {
    font-size: 12px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}
.stat-number {
    font-size: 28px;
    font-weight: 800;
    color: var(--text-primary);
    margin-top: 6px;
    letter-spacing: -0.02em;
}

/* Section header */
.sh {
    font-size: 12px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}

/* Page title */
.page-title {
    font-size: 26px;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 24px;
    font-weight: 400;
}

/* Dashboard header */
.dashboard-header {
    margin-bottom: 20px;
}
.header-title {
    font-size: 32px;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    line-height: 1.2;
}
.header-subtitle {
    font-size: 14px;
    color: var(--text-muted);
    margin-top: 4px;
    font-weight: 400;
}

/* Alert bars */
.al {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: var(--radius);
    padding: 14px 20px;
    font-size: 14px;
    color: #FCA5A5;
    font-weight: 500;
    margin-bottom: 20px;
}
.al-success {
    background: rgba(34, 197, 94, 0.15);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: var(--radius);
    padding: 14px 20px;
    font-size: 14px;
    color: #86EFAC;
    font-weight: 500;
    margin-bottom: 20px;
}

/* Login box */
.login-box {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 30px;
    box-shadow: var(--shadow-md);
    margin-bottom: 16px;
}
.login-title {
    font-size: 30px;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 6px;
}
.login-subtitle {
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 20px;
}

/* Premium report card */
.pr {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 28px;
    margin-top: 16px;
    box-shadow: var(--shadow);
    transition: all 0.2s ease;
}
.pr:hover {
    box-shadow: var(--shadow-hover);
    border-color: var(--border-hover);
    transform: translateY(-2px);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: #64748B;
    border-radius: 6px;
}
::-webkit-scrollbar-thumb:hover {
    background: #94A3B8;
}

</style>
"""


# Backward-compatible default CSS.
PAGE_CSS = get_page_css("Dark")


def kpi_card(col, val, label, sub="", color="#2563EB", highlight=False):
    """Render a styled KPI card in the given Streamlit column.

    This is a PURE UI helper - it only produces HTML.
    """
    border_style = f"border-left: 4px solid {color};" if highlight else ""
    col.markdown(
        f'<div class="kpi" style="{border_style}">'
        f'<div class="kv" style="color:{color}">{val}</div>'
        f'<div class="kl">{label}</div>'
        f'<div class="ks">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def section_header(text):
    """Return HTML for a section header."""
    return f'<div class="sh">{text}</div>'
