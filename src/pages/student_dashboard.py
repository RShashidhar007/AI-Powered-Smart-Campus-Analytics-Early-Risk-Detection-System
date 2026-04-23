"""
pages/student_dashboard.py - Student-specific portal.
Restricted view of just their own data + details + predicted future.
"""
from html import escape

import streamlit as st
import pandas as pd
from config import CURRENT_ACADEMIC_YEAR
from data_pro import run_pipeline_from_db
from language import TEXTS
from ui_theme import get_page_css, GRADE_COL, RISK_COL, kpi_card as _kpi
from ml_models import train_regression_models, train_classification_models

# Design system

# Colour maps & Plotly Theme


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


def _value(row, column, default="N/A"):
    if column not in row or pd.isna(row[column]):
        return default
    return row[column]


def _num(row, column, default=0.0):
    value = _value(row, column, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _detail_item(label, value, sub=""):
    return (
        "<div style='padding:10px 0;border-bottom:1px solid rgba(148,163,184,0.18)'>"
        f"<div style='font-size:12px;color:var(--text-muted);font-weight:700;text-transform:uppercase'>{escape(str(label))}</div>"
        f"<div style='font-size:16px;color:var(--text-primary);font-weight:700;margin-top:2px'>{escape(str(value))}</div>"
        f"<div style='font-size:12px;color:var(--text-muted);margin-top:2px'>{escape(str(sub))}</div>"
        "</div>"
    )


def _progress_item(label, value, total, color="var(--accent)"):
    pct = 0 if total == 0 else max(0, min(100, (float(value) / float(total)) * 100))
    return (
        "<div style='margin-bottom:14px'>"
        "<div style='display:flex;justify-content:space-between;gap:10px;margin-bottom:6px'>"
        f"<span style='font-size:13px;color:var(--text-secondary);font-weight:700'>{escape(str(label))}</span>"
        f"<span style='font-size:13px;color:var(--text-primary);font-weight:800'>{float(value):.1f}/{total}</span>"
        "</div>"
        "<div style='height:9px;background:rgba(148,163,184,0.22);border-radius:999px;overflow:hidden'>"
        f"<div style='width:{pct:.1f}%;height:100%;background:{color};border-radius:999px'></div>"
        "</div>"
        "</div>"
    )


def _risk_driver(label, current, threshold):
    current = float(current)
    threshold = float(threshold)
    needs_focus = current < threshold
    color = "var(--accent-red)" if needs_focus else "var(--accent-teal)"
    status = "Needs attention" if needs_focus else "On track"
    return (
        "<div style='display:flex;align-items:center;justify-content:space-between;gap:12px;"
        "padding:10px 0;border-bottom:1px solid rgba(148,163,184,0.18)'>"
        "<div>"
        f"<div style='font-size:13px;color:var(--text-primary);font-weight:700'>{escape(str(label))}</div>"
        f"<div style='font-size:12px;color:var(--text-muted)'>Current {current:.1f} | Target {threshold:.1f}</div>"
        "</div>"
        f"<div style='font-size:12px;color:{color};font-weight:800;text-align:right'>{status}</div>"
        "</div>"
    )


def render_student_dashboard():
    st.markdown(get_page_css(st.session_state.get('theme_mode', 'Dark')), unsafe_allow_html=True)
    
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
    peer_df = df[
        (df['department'] == student['department']) &
        (df['semester'] == student['semester'])
    ].copy()

    # Generate Profile Sidebar
    st.sidebar.markdown(f"###  {T.get('student_profile', 'Student Profile')}")
    st.sidebar.markdown("Your personal academic dashboard")
    st.sidebar.markdown("---")

    # Safe get of predicted_marks and predicted_grade if the pipeline added them
    pred_marks = student.get('predicted_marks', None)
    pred_grade = student.get('predicted_grade', None)

    # Page Header
    st.markdown(f'<div class="page-title">{T.get("welcome", "Welcome")}, {student["name"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f"<div class='page-subtitle'>{T.get('student_portal_text', 'Student Dashboard')} - {student['usn']}</div>",
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

    # KPI Row
    perf_rank = None
    if 'performance_index' in peer_df.columns and len(peer_df) > 0:
        ranked = peer_df['performance_index'].rank(method='min', ascending=False)
        perf_rank = int(ranked.loc[student.name])

    percentile = 0
    if 'performance_index' in df.columns and len(df) > 0:
        percentile = int(round((df['performance_index'] <= student['performance_index']).mean() * 100))

    risk_color = RISK_COL.get(student['risk_tier'], "var(--accent)")
    grade_color = GRADE_COL.get(student['grade_label'], "var(--accent)")

    st.markdown('<div class="sh">Student Information</div>', unsafe_allow_html=True)
    info_col, academic_col, risk_info_col = st.columns([1.05, 1.15, 1])

    with info_col:
        st.markdown(
            "<div class='glass-card'>"
            "<div style='font-size:13px;color:var(--text-muted);font-weight:800;text-transform:uppercase;margin-bottom:10px'>Profile</div>"
            + _detail_item("Name", student['name'])
            + _detail_item("USN", student['usn'])
            + _detail_item("Department", student['department'], f"Semester {student['semester']}")
            + _detail_item("Academic Year", st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR))
            + "</div>",
            unsafe_allow_html=True,
        )

    with academic_col:
        rank_text = f"Rank {perf_rank} of {len(peer_df)} in dept/semester" if perf_rank else "Rank unavailable"
        st.markdown(
            "<div class='glass-card'>"
            "<div style='font-size:13px;color:var(--text-muted);font-weight:800;text-transform:uppercase;margin-bottom:10px'>Academic Snapshot</div>"
            + _detail_item("Current Grade", student['grade_label'], "Based on semester marks")
            + _detail_item("Performance Index", f"{_num(student, 'performance_index'):.1f} / 100")
            + _detail_item("Class Rank", rank_text)
            + _detail_item("Overall Percentile", f"{percentile}th", "Based on performance index")
            + "</div>",
            unsafe_allow_html=True,
        )

    with risk_info_col:
        st.markdown(
            "<div class='glass-card'>"
            "<div style='font-size:13px;color:var(--text-muted);font-weight:800;text-transform:uppercase;margin-bottom:10px'>Risk Drivers</div>"
            + _detail_item("Risk Tier", student['risk_tier'], f"Risk score: {int(_num(student, 'risk_score'))}/100")
            + _risk_driver("Attendance", _num(student, 'attendance'), 75)
            + _risk_driver("Internal Marks", _num(student, 'internal_marks'), 25)
            + _risk_driver("Study Hours / Day", _num(student, 'study_hours'), 2)
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="sh">Marks Detail</div>', unsafe_allow_html=True)
    st.markdown(
        "<div class='glass-card'>"
        + _progress_item("Internal Marks", _num(student, 'internal_marks'), 50, "var(--accent)")
        + _progress_item("Assignment Score", _num(student, 'assignment_score'), 50, "var(--accent-teal)")
        + _progress_item("Quiz Score", _num(student, 'quiz_score'), 50, "var(--accent-amber)")
        + _progress_item("Lab Marks", _num(student, 'lab_marks'), 50, "var(--accent-light)")
        + _progress_item("Semester Marks", _num(student, 'semester_marks'), 200, grade_color)
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Charts Area
    # AI Predictions
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="sh"> {T.get("ai_predictions", "AI Performance Predictions")}</div>', unsafe_allow_html=True)

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
    _kpi(pc2, pred_grade, "Predicted Grade", "", GRADE_COL.get(pred_grade, "var(--text-primary)"))

    # Construct recommendation text based on models
    with pc3:
        if pred_grade in ['D', 'F'] or student['is_at_risk']:
            rec_color = "#fca5a5"
            rec_text = (
                "Focus immediately on improving internal marks. Seek help from faculty for upcoming assignments. "
                "Your current trajectory indicates a significant risk of failing."
            )
        elif pred_grade == 'C':
            rec_color = "#A0AEC0"
            rec_text = (
                "You are on track to pass, but margins are thin. A slight increase in study hours "
                "(try +1 hr/day) could confidently push you to a B."
            )
        else:
            rec_color = "#86efac"
            rec_text = (
                "Subject mastery is excellent. Maintain current attendance and study habits. "
                "Consider participating in advanced labs."
            )

        st.markdown(
            "<div class='glass-card' style='padding:16px;min-height:126px'>"
            "<div style='font-size:13px;color:var(--text-primary);font-weight:800;margin-bottom:8px'>"
            "Personalized Recommendation"
            "</div>"
            f"<div style='color:{rec_color};font-size:13px;line-height:1.55'>{escape(rec_text)}</div>"
            "</div>",
            unsafe_allow_html=True,
        )
