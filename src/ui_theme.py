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
def get_plotly_layout(theme_mode="Dark"):
    text_color = "#F8FAFC" if theme_mode == "Dark" else "#172033"
    grid_color = "rgba(255, 255, 255, 0.1)" if theme_mode == "Dark" else "rgba(0, 0, 0, 0.1)"
    return dict(
        font=dict(family="Inter, sans-serif", color=text_color),
        title_font=dict(color=text_color),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=12, r=12, t=40, b=12),
        xaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            tickfont=dict(color=text_color),
            title=dict(font=dict(color=text_color)),
        ),
        yaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            tickfont=dict(color=text_color),
            title=dict(font=dict(color=text_color)),
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=text_color)),
    )

PL = get_plotly_layout("Dark")

THEME_TOKENS = {
    "Dark": {
        "bg": "#020617",
        "bg_secondary": "#0F172A",
        "card_bg": "rgba(15, 23, 42, 0.6)",
        "text_primary": "#F8FAFC",
        "text_secondary": "#CBD5E1",
        "text_muted": "#64748B",
        "accent": "#6366F1",
        "accent_light": "#A855F7",
        "accent_teal": "#2DD4BF",
        "accent_red": "#F43F5E",
        "accent_amber": "#F59E0B",
        "border": "rgba(255, 255, 255, 0.1)",
        "border_hover": "rgba(255, 255, 255, 0.2)",
        "shadow": "0 4px 6px -1px rgba(0,0,0,0.5)",
        "shadow_md": "0 10px 15px -3px rgba(0,0,0,0.5)",
        "shadow_hover": "0 0 20px rgba(99, 102, 241, 0.3)",
        "collapse_icon_fill": "%23F8FAFC",
    }
}


def get_page_css(theme_mode="Dark"):
    """Return app CSS for the selected visual theme (always Dark)."""
    theme = THEME_TOKENS["Dark"]
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
    --radius:          10px;
    --radius-sm:       10px;
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
    background-color: #020617 !important;
    background-image: 
        radial-gradient(circle at 0% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 100% 100%, rgba(168, 85, 247, 0.1) 0%, transparent 40%),
        linear-gradient(to bottom, transparent, rgba(2, 6, 23, 0.8)),
        url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%239C92AC' fill-opacity='0.03' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 40V39L1 39V0H0V40z'/%3E%3C/g%3E%3C/svg%3E") !important;
    background-attachment: fixed !important;
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
    top: 22px !important;
    left: 20px !important;
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
    padding: 20px 40px !important;
    max-width: 1500px;
}

/* Sidebar */
[data-testid="stSidebar"], 
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebarNav"] {
    background: var(--card-bg) !important;
    border-right: none !important;
    overflow: hidden !important;
}
[data-testid="stSidebar"]::-webkit-scrollbar,
[data-testid="stSidebar"] *::-webkit-scrollbar {
    display: none !important;
    width: 0px !important;
    background: transparent !important;
}
[data-testid="stSidebar"] {
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
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin-bottom: 8px !important;
    font-family: 'Inter', sans-serif !important;
    cursor: pointer !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
}
div.stRadio > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}
div.stRadio > div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
    color: #FFFFFF !important;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    transform: translateX(4px) !important;
}
div.stRadio > div[role="radiogroup"] > label:hover:not(:has(input:checked)) {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: var(--accent) !important;
    color: var(--text-primary) !important;
    transform: translateX(2px) !important;
}

/* Sidebar-specific radio buttons (Menu) */
[data-testid="stSidebar"] div.stRadio > div[role="radiogroup"] > label {
    display: block !important;
    width: 100% !important;
    box-sizing: border-box !important;
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

/* Global Button Styling */
.stButton > button, 
.stFormSubmitButton > button,
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 22px !important;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.3) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: auto !important;
    min-height: 42px !important;
}

.stButton > button:hover, 
.stFormSubmitButton > button:hover,
[data-testid="baseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 25px rgba(168, 85, 247, 0.5) !important;
    filter: brightness(1.1) !important;
    color: white !important;
}

.stDownloadButton > button,
[data-testid="baseButton-secondary"] {
    background: rgba(15, 23, 42, 0.4) !important;
    backdrop-filter: blur(10px) !important;
    color: white !important;
    border: 1px solid #1F2937 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 10px 22px !important;
    transition: all 0.2s ease !important;
}

.stDownloadButton > button:hover,
[data-testid="baseButton-secondary"]:hover {
    background: rgba(31, 41, 55, 0.6) !important;
    border-color: #374151 !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active,
.stDownloadButton > button:active,
.stFormSubmitButton > button:active {
    transform: translateY(0px) !important;
    filter: brightness(0.9) !important;
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
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
}
.kpi:hover {
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    border-color: var(--accent);
    transform: translateY(-2px);
}
.kv {
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 8px;
    color: var(--text-primary);
}
.kl {
    font-size: 14px;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.ks {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 4px;
    opacity: 0.8;
}

/* Stat card (used in app.py) */
.stat-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}
.stat-card:hover {
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    border-color: var(--accent);
    transform: translateY(-2px);
}
.stat-title {
    font-size: 13px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    margin-bottom: 8px;
}
.stat-number {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
}

/* Section header */
.sh {
    font-size: 14px;
    font-weight: 600;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--accent);
    margin-bottom: 20px;
    display: inline-block;
}

/* Page title */
.page-title {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}
.page-subtitle {
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 32px;
    font-weight: 400;
}

/* Dashboard header */
.dashboard-header {
    margin-bottom: 32px;
    display: flex;
    align-items: center;
    gap: 20px;
}
.header-text-container {
    display: flex;
    flex-direction: column;
}
.header-title {
    font-size: 36px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}
.header-subtitle {
    font-size: 16px;
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