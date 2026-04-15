"""
pages/student_dashboard.py — Read-only student portal.
Shows only the logged-in student's marks, attendance, and results.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from config   import DATA_PATH, CURRENT_ACADEMIC_YEAR
from data_pro import run_pipeline, run_pipeline_from_db
from language import TEXTS

# ── Plot defaults ────────────────────────────────────────────────────────────
PL = dict(
    font_family="Plus Jakarta Sans, DM Sans, sans-serif",
    font_color="#8f9bba",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=8, r=8, t=32, b=8),
    showlegend=False,
)


@st.cache_data(show_spinner=False)
def _load_all():
    year = st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR)
    df = run_pipeline_from_db(year)
    if df.empty:
        df = run_pipeline(DATA_PATH)
    return df


def _gauge(value, title, max_val, suffix="", color="#0075FF"):
    """Create a sleek gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix, "font": {"size": 32, "color": "#FFFFFF", "family": "Plus Jakarta Sans"}},
        title={"text": title, "font": {"size": 14, "color": "#A0AEC0", "family": "Plus Jakarta Sans"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#A0AEC0", "tickfont": {"color": "#A0AEC0"}},
            "bar": {"color": color, "thickness": 0.7},
            "bgcolor": "rgba(255,255,255,0.05)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, max_val * 0.5], "color": "rgba(255,255,255,0.02)"},
                {"range": [max_val * 0.5, max_val * 0.75], "color": "rgba(255,255,255,0.04)"},
                {"range": [max_val * 0.75, max_val], "color": "rgba(255,255,255,0.06)"},
            ],
        },
    ))
    fig.update_layout(height=200, **PL)
    return fig


def render_student_dashboard():
    """Render the student-only dashboard."""
    T = TEXTS[st.session_state.language]
    usn = st.session_state.get("student_usn")

    if not usn:
        st.error("No student USN found. Please log in again.")
        return

    full_df = _load_all()

    # Find this student's row
    student_rows = full_df[full_df['usn'].astype(str).str.strip().str.upper() == usn.strip().upper()]

    if student_rows.empty:
        st.error(f"No data found for USN: **{usn}**")
        return

    s = student_rows.iloc[0]  # student record

    # ─── Inject CSS for hover effects (Streamlit strips JS event handlers) ────
    st.markdown("""
    <style>
        @keyframes student-float-up {
            to { opacity: 1; transform: translateY(0); }
        }
        .student-welcome {
            background: linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%);
            backdrop-filter: blur(120px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 28px 32px;
            margin-bottom: 24px;
            box-shadow: 0px 20px 40px rgba(0, 0, 0, 0.2);
            animation: student-float-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
            opacity: 0;
            transform: translateY(20px);
        }
        .student-kpi {
            background: linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%);
            backdrop-filter: blur(120px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 22px 24px;
            box-shadow: 0px 20px 40px rgba(0, 0, 0, 0.2);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        .student-kpi:hover {
            transform: translateY(-6px) scale(1.01);
            border-color: rgba(0, 117, 255, 0.5);
        }
        .student-profile {
            background: linear-gradient(127.09deg, rgba(6, 11, 40, 0.94) 19.41%, rgba(10, 14, 35, 0.49) 76.65%);
            backdrop-filter: blur(120px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0px 20px 40px rgba(0, 0, 0, 0.2);
        }
        .student-profile-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            transition: background 0.2s;
        }
        .student-profile-row:hover {
            background: rgba(255, 255, 255, 0.03);
        }
        .student-profile-row:last-child {
            border-bottom: none;
        }
        .profile-label {
            color: #A0AEC0;
            font-size: 14px;
            font-weight: 500;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .profile-value {
            color: #FFFFFF;
            font-size: 15px;
            font-weight: 700;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
    </style>
    """, unsafe_allow_html=True)

    # ─── Welcome Header ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="student-welcome">
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="
                width: 64px; height: 64px;
                background: linear-gradient(135deg, #0075FF 0%, #2CD9FF 100%);
                border-radius: 16px;
                display: flex; align-items: center; justify-content: center;
                font-size: 28px; flex-shrink: 0;
            ">🎓</div>
            <div>
                <div style="
                    font-size: 28px; font-weight: 800; color: #FFFFFF;
                    font-family: 'Plus Jakarta Sans', sans-serif;
                    letter-spacing: -0.02em;
                ">{T.get('welcome_student', 'Welcome')}, {s['name']}</div>
                <div style="
                    font-size: 14px; color: #A0AEC0; margin-top: 4px;
                    font-family: 'Plus Jakarta Sans', sans-serif;
                ">USN: {s['usn']}  ·  {s.get('department', 'N/A')}  ·  Semester {s.get('semester', 'N/A')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── KPI Cards Row ────────────────────────────────────────────────────────
    att_val = round(s['attendance'], 1)
    int_val = round(s['internal_marks'], 1)
    sem_val = round(s['semester_marks'], 1)
    perf_val = round(s.get('performance_index', 0), 1)

    # Attendance tier coloring
    if att_val >= 85:
        att_color, att_tier = "#27AE60", "Excellent"
    elif att_val >= 75:
        att_color, att_tier = "#2ECC71", "Good"
    elif att_val >= 65:
        att_color, att_tier = "#F39C12", "Average"
    elif att_val >= 50:
        att_color, att_tier = "#E67E22", "Warning"
    else:
        att_color, att_tier = "#E74C3C", "Critical"

    # Grade and Risk
    grade = s.get('grade_label', 'N/A')
    risk_tier = s.get('risk_tier', 'N/A')
    risk_score = int(s.get('risk_score', 0))

    grade_colors = {"A": "#27AE60", "B": "#2980B9", "C": "#F39C12", "D": "#E67E22", "F": "#E74C3C"}
    risk_colors = {"Low": "#27AE60", "Moderate": "#F39C12", "High": "#E67E22", "Critical": "#E74C3C"}

    def _kpi_card(icon, value, label, sub, color, border_color):
        return f"""
        <div class="student-kpi" style="border-left: 5px solid {border_color};">
            <div style="font-size: 22px; margin-bottom: 8px;">{icon}</div>
            <div style="font-size: 32px; font-weight: 800; color: {color};
                        font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.02em;">{value}</div>
            <div style="font-size: 13px; color: #A0AEC0; text-transform: uppercase; letter-spacing: 0.1em;
                        font-weight: 700; margin-top: 6px; font-family: 'Plus Jakarta Sans', sans-serif;">{label}</div>
            <div style="font-size: 12px; color: #718096; margin-top: 4px;
                        font-family: 'Plus Jakarta Sans', sans-serif;">{sub}</div>
        </div>"""

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_kpi_card("📊", f"{att_val}%", T.get("your_attendance", "Attendance"), att_tier, att_color, att_color), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi_card("📝", f"{int_val}/50", T.get("your_internals", "Internal Marks"), "Out of 50", "#FFFFFF", "#0075FF"), unsafe_allow_html=True)
    with c3:
        st.markdown(_kpi_card("🏆", f"{sem_val}/200", T.get("your_semester_marks", "Semester Marks"), f"Grade: {grade}", grade_colors.get(grade, "#FFF"), grade_colors.get(grade, "#0075FF")), unsafe_allow_html=True)
    with c4:
        st.markdown(_kpi_card("⚡", f"{perf_val}", T.get("your_performance", "Performance Index"), f"Risk: {risk_tier}", risk_colors.get(risk_tier, "#FFF"), risk_colors.get(risk_tier, "#0075FF")), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Charts Row ───────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        st.markdown('<div class="sh">📊 ' + T.get("marks_breakdown", "Marks Breakdown") + '</div>', unsafe_allow_html=True)

        categories = ["Internal\nMarks", "Assignment\nScore", "Quiz\nScore", "Lab\nMarks"]
        values = [
            round(s['internal_marks'], 1),
            round(s['assignment_score'], 1),
            round(s['quiz_score'], 1),
            round(s['lab_marks'], 1),
        ]
        max_val = 50

        colors = []
        for v in values:
            pct = v / max_val
            if pct >= 0.7:
                colors.append("#27AE60")
            elif pct >= 0.5:
                colors.append("#F39C12")
            else:
                colors.append("#E74C3C")

        fig_marks = go.Figure()
        fig_marks.add_trace(go.Bar(
            x=categories, y=values,
            marker_color=colors,
            marker_line_width=0,
            text=[f"{v:.1f}" for v in values],
            textposition='outside',
            textfont=dict(color='#A0AEC0', size=13, family='Plus Jakarta Sans'),
        ))
        # Add max line
        fig_marks.add_hline(y=max_val, line_dash="dash", line_color="rgba(255,255,255,0.2)", annotation_text="Max: 50")
        fig_marks.update_layout(
            **PL, height=320,
            xaxis=dict(showgrid=False, tickfont=dict(color="#A0AEC0", size=11)),
            yaxis=dict(range=[0, max_val + 10], gridcolor="rgba(143, 155, 186, 0.1)", tickfont=dict(color="#A0AEC0")),
        )
        st.plotly_chart(fig_marks, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.markdown('<div class="sh">📈 ' + T.get("your_attendance", "Attendance") + ' & ' + T.get("your_results", "Results") + '</div>', unsafe_allow_html=True)
        fig_gauge = _gauge(att_val, T.get("your_attendance", "Attendance"), 100, "%", att_color)
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

    # ─── Semester Marks Gauge ─────────────────────────────────────────────────
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_sem = _gauge(sem_val, T.get("your_semester_marks", "Semester Marks"), 200, "", grade_colors.get(grade, "#0075FF"))
        st.plotly_chart(fig_sem, use_container_width=True, config={"displayModeBar": False})
    with col_g2:
        fig_perf = _gauge(perf_val, T.get("your_performance", "Performance Index"), 100, "", risk_colors.get(risk_tier, "#0075FF"))
        st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})

    # ─── Academic Profile Card ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sh">🎓 ' + T.get("academic_profile", "Academic Profile") + '</div>', unsafe_allow_html=True)

    study_hrs = round(s.get('study_hours', 0), 1)
    assignment_val = round(s['assignment_score'], 1)
    quiz_val = round(s['quiz_score'], 1)
    lab_val = round(s['lab_marks'], 1)
    total_cont = round(s.get('total_continuous', 0), 1)

    # Build profile data as a table — Streamlit handles <table> reliably
    profile_rows = [
        ("🆔", T.get("usn_label", "USN"), str(s['usn'])),
        ("👤", T.get("name_label", "Name"), str(s['name'])),
        ("🏢", T.get("department_label", "Department"), str(s.get('department', 'N/A'))),
        ("📚", T.get("semester_label", "Semester"), str(s.get('semester', 'N/A'))),
        ("📊", T.get("your_attendance", "Attendance"), f"{att_val}% ({att_tier})"),
        ("📝", T.get("your_internals", "Internal Marks"), f"{int_val} / 50"),
        ("📋", "Assignment Score", f"{assignment_val} / 50"),
        ("❓", "Quiz Score", f"{quiz_val} / 50"),
        ("🔬", "Lab Marks", f"{lab_val} / 50"),
        ("🏆", T.get("your_semester_marks", "Semester Marks"), f"{sem_val} / 200"),
        ("📐", "Total Continuous Assessment", f"{total_cont} / 200"),
        ("⏰", "Study Hours / Day", f"{study_hrs} hrs"),
        ("🅰️", "Grade", str(grade)),
        ("⚠️", "Risk Level", str(risk_tier)),
        ("⚡", T.get("your_performance", "Performance Index"), f"{perf_val} / 100"),
    ]

    table_rows_html = ""
    for icon, label, value in profile_rows:
        table_rows_html += f"""<tr>
            <td style="padding:14px 20px; border-bottom: 1px solid rgba(255,255,255,0.06); color:#A0AEC0; font-size:14px; font-weight:500;">{icon} {label}</td>
            <td style="padding:14px 20px; border-bottom: 1px solid rgba(255,255,255,0.06); color:#FFFFFF; font-size:15px; font-weight:700; text-align:right;">{value}</td>
        </tr>"""

    profile_table = f"""<table style="
        width: 100%;
        border-collapse: collapse;
        background: linear-gradient(127.09deg, rgba(6,11,40,0.94) 19.41%, rgba(10,14,35,0.49) 76.65%);
        backdrop-filter: blur(120px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0px 20px 40px rgba(0,0,0,0.2);
        font-family: 'Plus Jakarta Sans', sans-serif;
    ">{table_rows_html}</table>"""

    st.markdown(profile_table, unsafe_allow_html=True)
