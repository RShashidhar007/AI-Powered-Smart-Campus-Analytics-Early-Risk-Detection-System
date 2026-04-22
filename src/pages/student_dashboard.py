"""
pages/student_dashboard.py — Student-specific portal.
Restricted view of just their own data + gauge charts + predicted future.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import CURRENT_ACADEMIC_YEAR
from data_pro import run_pipeline_from_db
from language import TEXTS
from ui_theme import PAGE_CSS, GRADE_COL, RISK_COL, DEPT_COL, PL as _PL, PL, kpi_card as _kpi, section_header as _sh
from ml_models import train_regression_models, train_classification_models

# ── Design system ─────────────────────────────────────────────────────────────

# ── Colour maps & Plotly Theme ────────────────────────────────────────────────


@st.cache_data(show_spinner=False)
def _load_all_data():
    year = st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR)
    return run_pipeline_from_db(year)

@st.cache_resource(show_spinner=False)
def _get_models():
    """Load fully trained models for accurate predictions."""
    df = _load_all_data()
    reg = train_regression_models(df)
    clf = train_classification_models(df)
    return reg, clf

def render_student_dashboard():
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    
    T = TEXTS[st.session_state.language]
    usn = st.session_state.get('student_usn')

    if not usn:
        st.error(" Not logged in as a student.")
        return

    df = _load_all_data()
    student_df = df[df['usn'] == usn]

    if student_df.empty:
        st.error(f" Could not find data for USN: {usn}")
        return

    student = student_df.iloc[0]

    # Generate Profile Sidebar
    st.sidebar.markdown(f"### 👤 {T.get('student_profile', 'Student Profile')}")
    st.sidebar.markdown(f"**Name:** {student['name']}")
    st.sidebar.markdown(f"**USN:** {student['usn']}")
    st.sidebar.markdown(f"**Department:** {student['department']}")
    st.sidebar.markdown(f"**Semester:** {student['semester']}")
    st.sidebar.markdown("---")

    # Safe get of predicted_marks and predicted_grade if the pipeline added them
    pred_marks = student.get('predicted_marks', None)
    pred_grade = student.get('predicted_grade', None)

    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown(f'<div class="page-title">{T.get("welcome", "Welcome")}, {student["name"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f"<div class='page-subtitle'>{T.get('student_portal_text', 'Student Dashboard')} — {student['usn']}</div>",
        unsafe_allow_html=True,
    )

    if student['is_at_risk']:
         st.markdown(
            f'<div class="al"> {T.get("at_risk_alert", "You are currently flagged as At-Risk. Please focus on improving attendance and internals.")}</div>',
            unsafe_allow_html=True,
         )
    elif student['grade_label'] in ['A', 'B']:
         st.markdown(
            f'<div class="al-success">Exploring excellence! Keep up the good work.</div>',
            unsafe_allow_html=True,
         )

    # ── KPI Row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    r_color = RISK_COL.get(student['risk_tier'], "var(--accent)")
    g_color = GRADE_COL.get(student['grade_label'], "var(--accent)")

    _kpi(c1, f"{student['attendance']:.1f}%", T.get('attendance', 'Attendance'), "Target: > 75%", "var(--accent-amber)" if student['attendance'] < 75 else "var(--accent-teal)")
    _kpi(c2, f"{student['semester_marks']:.0f}", T.get('total_marks', 'Semester Marks'), "/ 200", "var(--accent)")
    _kpi(c3, student['grade_label'], T.get('current_grade', 'Grade'), "", g_color)
    _kpi(c4, student['risk_tier'], T.get('risk_status', 'Risk Status'), "", r_color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main Charts Area ──────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.markdown(f'<div class="sh">{T.get("attendance", "Attendance")} & {T.get("risk_status", "Risk")}</div>', unsafe_allow_html=True)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=student['attendance'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Attendance %", 'font': {'size': 14, 'family': 'Inter'}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1},
                'bar': {'color': "var(--accent-teal)"},
                'bgcolor': 'rgba(128,128,128,0.1)',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 65], 'color': "rgba(224, 108, 117, 0.4)"},  # Muted pastel red
                    {'range': [65, 75], 'color': "rgba(229, 192, 123, 0.4)"}, # Muted pastel yellow
                    {'range': [75, 100], 'color': "rgba(129, 199, 132, 0.4)"}], # Muted pastel green
                'threshold': {
                    'line': {'color': "rgba(128,128,128,0.8)", 'width': 3},
                    'thickness': 0.75,
                    'value': 75}
            }))
        fig_gauge.update_layout(**_PL)
        fig_gauge.update_layout(height=220)
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

        st.caption("Required threshold is 75%. Minimum exam requirement is 65%.")

    with col2:
        st.markdown(f'<div class="sh">{T.get("performance_breakdown", "Performance Breakdown")}</div>', unsafe_allow_html=True)

        categories = ['Internal Marks', 'Assignment', 'Quiz', 'Lab Marks']
        values = [
            (student['internal_marks'] / 50) * 100,
            (student['assignment_score'] / 50) * 100,
            (student['quiz_score'] / 50) * 100,
            (student['lab_marks'] / 50) * 100
        ]

        # Close the radar loop
        categories.append(categories[0])
        values.append(values[0])

        fig_radar = go.Figure(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(129,161,193,0.3)', # Soft Nord Blue
            line=dict(color='var(--accent)', width=2)
        ))

        fig_radar.update_layout(**_PL)
        fig_radar.update_layout(
            height=260,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                angularaxis=dict(showline=False, gridcolor="rgba(128,128,128,0.2)"),
                radialaxis=dict(showline=False, gridcolor="rgba(128,128,128,0.2)", range=[0, 100])
            )
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

    # ── AI Predictions ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sh">🔮 {T.get("ai_predictions", "AI Performance Predictions")}</div>', unsafe_allow_html=True)

    if pd.isna(pred_marks) or pd.isna(pred_grade):
        try:
            reg, clf = _get_models()
            FEATURES = ['attendance', 'internal_marks', 'assignment_score', 'quiz_score', 'lab_marks', 'study_hours']
            row = student_df[FEATURES]

            best_reg = reg['trained_models'][reg['best_model']]
            is_lin   = reg['best_model'] == 'Linear Regression'
            X_in     = reg['scaler'].transform(row) if is_lin else row
            pred_marks = float(best_reg.predict(X_in)[0])

            best_clf_m = clf['trained_models'][clf['best_model']]
            is_log     = clf['best_model'] == 'Logistic Regression'
            X_clf      = clf['scaler'].transform(row) if is_log else row
            pred_grade = clf['label_encoder'].inverse_transform(best_clf_m.predict(X_clf))[0]
        except Exception as e:
            pred_marks = 0
            pred_grade = "N/A"

    pc1, pc2, pc3 = st.columns(3)
    _kpi(pc1, f"{pred_marks:.1f}", "Predicted Marks", "End of semester model estimate", "var(--accent-light)")
    _kpi(pc2, pred_grade, "Predicted Grade", "", GRADE_COL.get(pred_grade, "#FFFFFF"))

    # Construct recommendation text based on models
    with pc3:
        st.markdown('<div class="glass-card" style="padding: 16px;">', unsafe_allow_html=True)
        st.markdown("**Personalized Recommendation**", unsafe_allow_html=True)
        if pred_grade in ['D', 'F'] or student['is_at_risk']:
            st.markdown("<span style='color:#fca5a5;font-size:13px'>Focus immediately on improving internal marks. "
                        "Seek help from faculty for upcoming assignments. Your current trajectory indicates a significant risk of failing.</span>", unsafe_allow_html=True)
        elif pred_grade == 'C':
            st.markdown("<span style='color:#A0AEC0;font-size:13px'>You are on track to pass, but margins are thin. "
                        "A slight increase in study hours (try +1 hr/day) could confidently push you to a B.</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#86efac;font-size:13px'>Subject mastery is excellent. "
                        "Maintain current attendance and study habits. Consider participating in advanced labs.</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
