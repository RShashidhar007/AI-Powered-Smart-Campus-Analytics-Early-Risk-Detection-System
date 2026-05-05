"""
pages/predictions.py - ML models display + single-student prediction.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config    import DATA_PATH, DEPARTMENTS, SEMESTERS, CURRENT_ACADEMIC_YEAR
from data_pro  import run_pipeline, run_pipeline_from_db, filter_dataframe
from ml_models import (
    FEATURES, train_regression_models, train_classification_models,
)
from language  import TEXTS
from ui_theme import get_page_css, GRADE_COL, RISK_COL, DEPT_COL, PL as _PL, PL, kpi_card as _kpi, section_header as _sh

# Design system

# Colour maps & Plotly Theme


# Cached loaders
@st.cache_data(show_spinner=False)
def _load_df():
    year = st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR)
    df = run_pipeline_from_db(year)
    if df.empty:
        df = run_pipeline(DATA_PATH)
    return df

@st.cache_resource(show_spinner=False)
def _train_reg(dept, sem):
    df = filter_dataframe(_load_df(), dept, sem)
    if len(df) < 20:
        df = _load_df()  # Fall back to full dataset if filtered is too small
    return train_regression_models(df)

@st.cache_resource(show_spinner=False)
def _train_clf(dept, sem):
    df = filter_dataframe(_load_df(), dept, sem)
    if len(df) < 20:
        df = _load_df()
    return train_classification_models(df)

def render_predictions_page():
    st.markdown(get_page_css(st.session_state.get('theme_mode', 'Dark')), unsafe_allow_html=True)
    
    T  = TEXTS[st.session_state.language]

    sel_dept = st.session_state.get('selected_department', 'All')
    sel_sem  = st.session_state.get('selected_semester', 'All')
    df = filter_dataframe(_load_df(), sel_dept, sel_sem)

    # Build filter label
    filter_label = []
    if sel_dept != 'All': filter_label.append(sel_dept)
    if sel_sem != 'All': filter_label.append(f"Sem {sel_sem}")
    filter_str = " - ".join(filter_label) if filter_label else "All Departments"

    st.markdown(f'<div class="page-title">{T.get("predictions_title", "Predictions & Insights")}</div>', unsafe_allow_html=True)
    st.markdown(
        f"<div class='page-subtitle'>"
        f"{T.get('predictions_subtitle', 'Marks Predictor - Grade Forecast - Key Factors - Single-student predictor')} - {filter_str}</div>",
        unsafe_allow_html=True,
    )

    with st.spinner("Training models (first load ~5 s)..."):
        reg = _train_reg(sel_dept, sel_sem)
        clf = _train_clf(sel_dept, sel_sem)

    tab_reg_name  = T.get('tab_reg', ' Marks Predictor')
    tab_clf_name  = T.get('tab_clf', ' Grade Forecast')
    tab_fi_name   = T.get('tab_fi', ' Key Factors')
    tab_pred_name = T.get('tab_pred', ' Predict Student')

    active_tab = st.radio("View", [tab_reg_name, tab_clf_name, tab_fi_name, tab_pred_name], horizontal=True, label_visibility="collapsed")

    # Regression — Marks Predictor
    if active_tab == tab_reg_name:
        results   = reg['results']
        best_name = reg['best_model']
        best_r2   = results[best_name]['R2']

        # ── Hero header ──
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:14px;margin-bottom:6px'>"
            f"<div style='font-size:22px;font-weight:700;color:var(--text-primary)'>Marks Predictor</div>"
            f"<div style='background:linear-gradient(135deg,#6366F1,#A855F7);padding:4px 14px;"
            f"border-radius:999px;font-size:12px;font-weight:700;color:white'>"
            f"Best: {best_name} · {best_r2*100:.1f}% Accurate</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='color:var(--text-muted);font-size:13px;margin-bottom:20px'>"
            f"Predicting semester marks (0–200) using {len(df)} students · {filter_str}</div>",
            unsafe_allow_html=True,
        )

        # ── Model comparison cards ──
        mcols = st.columns(len(results))
        for i, (name, m) in enumerate(results.items()):
            ib = name == best_name
            col_color = "var(--accent-light)" if ib else "var(--text-muted)"
            with mcols[i]:
                badge = "<span style='background:linear-gradient(135deg,#6366F1,#A855F7);padding:2px 8px;border-radius:999px;font-size:10px;color:white;margin-left:8px'>BEST</span>" if ib else ""
                st.markdown(
                    f"<div class='glass-card' style='padding:18px;{'border:1px solid var(--accent)' if ib else ''}'>"
                    f"<div style='font-size:14px;font-weight:700;color:var(--text-primary);margin-bottom:12px'>{name}{badge}</div>"
                    f"<div style='display:flex;justify-content:space-between;gap:8px'>"
                    f"<div style='text-align:center;flex:1'>"
                    f"<div style='font-size:20px;font-weight:700;color:{col_color}'>{m['R2']*100:.1f}%</div>"
                    f"<div style='font-size:10px;color:var(--text-muted)'>Accuracy</div>"
                    f"</div>"
                    f"<div style='text-align:center;flex:1'>"
                    f"<div style='font-size:20px;font-weight:700;color:var(--text-primary)'>{m['RMSE']}</div>"
                    f"<div style='font-size:10px;color:var(--text-muted)'>Avg Error</div>"
                    f"</div>"
                    f"<div style='text-align:center;flex:1'>"
                    f"<div style='font-size:20px;font-weight:700;color:var(--text-primary)'>{m['MAE']}</div>"
                    f"<div style='font-size:10px;color:var(--text-muted)'>Typical Mistake</div>"
                    f"</div>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # ── Scatter + Error distribution ──
        st.markdown("<div class='sh' style='margin-top:28px'>Accuracy Check</div>", unsafe_allow_html=True)
        best_model = reg['trained_models'][best_name]
        is_lin     = best_name == 'Linear Regression'
        X_all      = df[FEATURES]
        X_in       = reg['scaler'].transform(X_all) if is_lin else X_all
        preds      = best_model.predict(X_in)
        sdf        = df.copy()
        sdf['predicted'] = np.round(preds, 2)
        sdf['error'] = sdf['predicted'] - sdf['semester_marks']
        sample_n   = min(200, len(sdf))
        smp        = sdf.sample(sample_n, random_state=42) if len(sdf) >= sample_n else sdf

        scatter_col, error_col = st.columns([1.2, 0.8])

        with scatter_col:
            fap = px.scatter(
                smp, x='semester_marks', y='predicted',
                color='grade_label', color_discrete_map=GRADE_COL, opacity=0.75,
                labels={'semester_marks': 'Actual Marks', 'predicted': 'Predicted Marks'},
            )
            mn, mx = smp['semester_marks'].min(), smp['semester_marks'].max()
            fap.add_trace(go.Scatter(
                x=[mn, mx], y=[mn, mx], mode='lines',
                line=dict(color='rgba(168, 85, 247, 0.7)', dash='dash', width=2),
                name='Perfect Fit', showlegend=True,
            ))
            fap.update_traces(
                hovertemplate='<b>Actual:</b> %{x}<br><b>Predicted:</b> %{y}<extra></extra>',
                selector=dict(mode='markers'),
            )
            fap.update_layout(**_PL)
            fap.update_layout(
                height=380, showlegend=True,
                legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center', font_size=11),
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis=dict(showgrid=True, gridcolor='rgba(148,163,184,0.1)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(148,163,184,0.1)'),
            )
            st.plotly_chart(fap, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")
            st.caption("Points on the dashed line = perfect predictions. Color = actual grade.")

        with error_col:
            fig_err = go.Figure()
            fig_err.add_trace(go.Histogram(
                x=sdf['error'], nbinsx=30, name='Error',
                marker_color='rgba(99, 102, 241, 0.6)',
                marker_line_color='rgba(168, 85, 247, 0.8)', marker_line_width=1,
            ))
            fig_err.add_vline(x=0, line_dash='dash', line_color='rgba(168,85,247,0.7)', line_width=2)
            fig_err.update_layout(**_PL)
            fig_err.update_layout(
                height=380,
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis_title='Difference (marks)',
                yaxis_title='Count',
                xaxis=dict(showgrid=True, gridcolor='rgba(148,163,184,0.1)'),
            )
            st.plotly_chart(fig_err, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")
            avg_err = sdf['error'].mean()
            std_err = sdf['error'].std()
            st.caption(f"On average, predictions are off by {abs(avg_err):.1f} marks")

    # Classification — Grade Forecast
    elif active_tab == tab_clf_name:
        clf_results = clf['results']
        best_c      = clf['best_model']
        best_acc    = clf_results[best_c]['Accuracy']

        # ── Section 1: Hero header ──
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:14px;margin-bottom:6px'>"
            f"<div style='font-size:22px;font-weight:700;color:var(--text-primary)'>Grade Forecast</div>"
            f"<div style='background:linear-gradient(135deg,#6366F1,#A855F7);padding:4px 14px;"
            f"border-radius:999px;font-size:12px;font-weight:700;color:white'>"
            f"Best: {best_c} · {best_acc*100:.1f}%</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='color:var(--text-muted);font-size:13px;margin-bottom:20px'>"
            f"Predicting final grade (A–F) using {len(df)} students · {filter_str}</div>",
            unsafe_allow_html=True,
        )

        # ── Section 2: Model comparison KPIs ──
        cols2 = st.columns(len(clf_results))
        for i, (name, m) in enumerate(clf_results.items()):
            ib = name == best_c
            _kpi(cols2[i], f"{m['Accuracy']*100:.1f}%", name, "Top Pick" if ib else "Correct %",
                 "var(--accent-light)" if ib else "var(--text-muted)", ib)

        # ── Section 3: Per-grade accuracy breakdown ──
        st.markdown("<div class='sh' style='margin-top:28px'>Grade Accuracy</div>", unsafe_allow_html=True)
        best_report = clf_results[best_c]['Report']
        grade_labels = clf.get('grade_classes', ['A', 'B', 'C', 'D', 'F'])
        gcols = st.columns(len(grade_labels))
        for i, g in enumerate(grade_labels):
            g_data = best_report.get(g, {})
            precision = g_data.get('precision', 0) * 100
            recall    = g_data.get('recall', 0) * 100
            support   = int(g_data.get('support', 0))
            g_color   = GRADE_COL.get(g, 'var(--text-primary)')
            with gcols[i]:
                st.markdown(
                    f"<div class='glass-card' style='padding:16px;text-align:center'>"
                    f"<div style='font-size:28px;font-weight:700;color:{g_color}'>{g}</div>"
                    f"<div style='font-size:11px;color:var(--text-muted);margin:6px 0 10px;text-transform:uppercase;"
                    f"letter-spacing:0.06em'>Grade</div>"
                    f"<div style='display:flex;justify-content:space-around;gap:6px'>"
                    f"<div>"
                    f"<div style='font-size:16px;font-weight:700;color:var(--text-primary)'>{precision:.0f}%</div>"
                    f"<div style='font-size:10px;color:var(--text-muted)'>Correct</div>"
                    f"</div>"
                    f"<div>"
                    f"<div style='font-size:16px;font-weight:700;color:var(--text-primary)'>{recall:.0f}%</div>"
                    f"<div style='font-size:10px;color:var(--text-muted)'>Found</div>"
                    f"</div>"
                    f"</div>"
                    f"<div style='font-size:11px;color:var(--text-muted);margin-top:10px'>{support} students</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # ── Section 4: Confusion matrix + Predicted vs Actual distribution ──
        st.markdown("<div class='sh' style='margin-top:28px'>Deep Dive</div>", unsafe_allow_html=True)
        cm_col, dist_col = st.columns([1, 1])

        with cm_col:
            best_cm = np.array(clf_results[best_c]['Confusion'])
            classes = clf.get('grade_classes', ['A', 'B', 'C', 'D', 'F'])
            fcm = px.imshow(
                best_cm, x=classes, y=classes,
                color_continuous_scale=[[0, '#0F172A'], [0.5, '#6366F1'], [1, '#A855F7']],
                text_auto=True, aspect='auto',
                labels=dict(x="Predicted Grade", y="Actual Grade", color="Count"),
            )
            fcm.update_layout(**_PL)
            fcm.update_layout(
                height=360, coloraxis_showscale=False,
                xaxis_title="What the AI Predicted",
                yaxis_title="What the Student Actually Got",
                margin=dict(l=10, r=10, t=30, b=10),
            )
            st.plotly_chart(fcm, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")
            st.caption("Bright diagonal = AI got it right. Other cells = where the AI got confused.")

        with dist_col:
            # Predicted vs Actual grade distribution
            best_clf_m = clf['trained_models'][best_c]
            is_log     = best_c == 'Logistic Regression'
            X_all      = df[FEATURES]
            X_in       = clf['scaler'].transform(X_all) if is_log else X_all
            pred_labels = clf['label_encoder'].inverse_transform(best_clf_m.predict(X_in))

            actual_counts = df['grade_label'].value_counts().reindex(grade_labels).fillna(0)
            pred_counts   = pd.Series(pred_labels).value_counts().reindex(grade_labels).fillna(0)

            fig_dist = go.Figure()
            fig_dist.add_trace(go.Bar(
                x=grade_labels, y=actual_counts.values, name="Actual",
                marker_color=[GRADE_COL.get(g, '#6366F1') for g in grade_labels],
                marker_line_width=1, marker_line_color="rgba(255,255,255,0.12)",
                opacity=0.85,
            ))
            fig_dist.add_trace(go.Bar(
                x=grade_labels, y=pred_counts.values, name="AI Predicted",
                marker_color="rgba(168, 85, 247, 0.6)",
                marker_line_width=1, marker_line_color="rgba(255,255,255,0.2)",
                marker_pattern_shape="/",
            ))
            fig_dist.update_layout(**_PL)
            fig_dist.update_layout(
                height=360, barmode="group", bargap=0.2,
                legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center"),
                margin=dict(l=10, r=10, t=30, b=10),
                yaxis_title="Students",
            )
            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")
            st.caption("Compares the real grades with what the AI predicted for all students.")

    # Feature Importance — Key Factors
    elif active_tab == tab_fi_name:
        # ── Hero header ──
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:14px;margin-bottom:6px'>"
            f"<div style='font-size:22px;font-weight:700;color:var(--text-primary)'>Key Factors</div>"
            f"<div style='background:linear-gradient(135deg,#6366F1,#A855F7);padding:4px 14px;"
            f"border-radius:999px;font-size:12px;font-weight:700;color:white'>"
            f"AI Engine</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='color:var(--text-muted);font-size:13px;margin-bottom:20px'>"
            f"What matters most for academic performance · {filter_str}</div>",
            unsafe_allow_html=True,
        )

        # ── Per-feature insight cards ──
        reg_fi = reg['feature_importance']
        clf_fi = clf['feature_importance']
        sorted_features = sorted(reg_fi.keys(), key=lambda k: reg_fi[k], reverse=True)

        fcols = st.columns(len(sorted_features))
        for i, feat in enumerate(sorted_features):
            reg_imp = reg_fi[feat]
            clf_imp = clf_fi.get(feat, 0)
            avg_imp = (reg_imp + clf_imp) / 2
            rank = i + 1
            label = feat.replace('_', ' ').title()
            # Color intensity based on rank
            if rank == 1:
                card_border = "border:1px solid var(--accent)"
                rank_color = "var(--accent-light)"
            elif rank <= 3:
                card_border = ""
                rank_color = "var(--accent)"
            else:
                card_border = ""
                rank_color = "var(--text-muted)"

            with fcols[i]:
                st.markdown(
                    f"<div class='glass-card' style='padding:16px;text-align:center;{card_border}'>"
                    f"<div style='font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em'>Rank</div>"
                    f"<div style='font-size:28px;font-weight:700;color:{rank_color}'>#{rank}</div>"
                    f"<div style='font-size:13px;font-weight:600;color:var(--text-primary);margin:8px 0 10px'>{label}</div>"
                    f"<div style='display:flex;justify-content:space-around;gap:4px'>"
                    f"<div>"
                    f"<div style='font-size:14px;font-weight:700;color:var(--text-primary)'>{reg_imp*100:.1f}%</div>"
                    f"<div style='font-size:9px;color:var(--text-muted)'>Marks</div>"
                    f"</div>"
                    f"<div>"
                    f"<div style='font-size:14px;font-weight:700;color:var(--text-primary)'>{clf_imp*100:.1f}%</div>"
                    f"<div style='font-size:9px;color:var(--text-muted)'>Grade</div>"
                    f"</div>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # ── Side-by-side bar charts ──
        st.markdown("<div class='sh' style='margin-top:28px'>Factor Influence</div>", unsafe_allow_html=True)
        bar_left, bar_right = st.columns(2)

        for col_widget, fi_data, title, grad_colors in [
            (bar_left, reg_fi, 'Marks Predictor', [[0, '#0F172A'], [0.5, '#6366F1'], [1, '#A855F7']]),
            (bar_right, clf_fi, 'Grade Forecast', [[0, '#0F172A'], [0.5, '#2DD4BF'], [1, '#6366F1']]),
        ]:
            with col_widget:
                fidf = pd.DataFrame({
                    'Feature':    [k.replace('_', ' ').title() for k in fi_data],
                    'Importance': [v * 100 for v in fi_data.values()],
                }).sort_values('Importance', ascending=True)
                ffi = go.Figure(go.Bar(
                    x=fidf['Importance'], y=fidf['Feature'], orientation='h',
                    marker=dict(
                        color=fidf['Importance'],
                        colorscale=grad_colors,
                        line=dict(width=1, color='rgba(255,255,255,0.12)'),
                    ),
                    text=[f"{v:.1f}%" for v in fidf['Importance']],
                    textposition='inside', insidetextanchor='end',
                    hovertemplate='<b>%{y}</b><br>Importance: %{x:.1f}%<extra></extra>',
                ))
                ffi.update_layout(**_PL)
                ffi.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=30, b=10),
                    xaxis=dict(showgrid=True, gridcolor='rgba(148,163,184,0.1)', title='Influence (%)'),
                    yaxis=dict(showgrid=False),
                )
                st.plotly_chart(ffi, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")
                st.caption(f"{title} — How much each factor influences the result")

        # ── Dynamic top-factor callout ──
        top_feat = sorted_features[0].replace('_', ' ').title()
        top_pct = reg_fi[sorted_features[0]] * 100
        st.markdown(
            f"<div class='glass-card' style='padding:16px;margin-top:10px;display:flex;align-items:center;gap:16px'>"
            f"<div style='font-size:32px'>🎯</div>"
            f"<div>"
            f"<div style='font-size:15px;font-weight:700;color:var(--text-primary)'>"
            f"{top_feat} is the #1 driver of student performance</div>"
            f"<div style='font-size:13px;color:var(--text-muted);margin-top:4px'>"
            f"This factor has the biggest influence ({top_pct:.1f}%) on marks prediction. "
            f"Focus improvements here for best results.</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Predict single student
    elif active_tab == tab_pred_name:
        # ── Hero header ──
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:14px;margin-bottom:6px'>"
            f"<div style='font-size:22px;font-weight:700;color:var(--text-primary)'>Predict Student</div>"
            f"<div style='background:linear-gradient(135deg,#6366F1,#A855F7);padding:4px 14px;"
            f"border-radius:999px;font-size:12px;font-weight:700;color:white'>"
            f"Interactive Predictor</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='color:var(--text-muted);font-size:13px;margin-bottom:20px'>"
            "Enter a student's academic metrics to predict their semester marks and final grade</div>",
            unsafe_allow_html=True,
        )

        # ── Input cards ──
        st.markdown("<div class='sh'>Academic Metrics</div>", unsafe_allow_html=True)
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            attendance = st.slider("Attendance %", 0.0, 100.0, 72.0, 0.5)
        with rc2:
            internal_marks = st.slider("Internal Marks (0–50)", 0.0, 50.0, 35.0, 0.5)
        with rc3:
            assignment_score = st.slider("Assignment Score (0–50)", 0.0, 50.0, 38.0, 0.5)

        rc4, rc5, rc6 = st.columns(3)
        with rc4:
            quiz_score = st.slider("Quiz Score (0–50)", 0.0, 50.0, 34.0, 0.5)
        with rc5:
            lab_marks = st.slider("Lab Marks (0–50)", 0.0, 50.0, 36.0, 0.5)
        with rc6:
            study_hours = st.slider("Study Hours / Day", 0.0, 10.0, 3.5, 0.1)

        if st.button(T.get('run_prediction', 'Run Prediction'), use_container_width=True, type="primary"):
            row = pd.DataFrame([{
                'attendance': attendance, 'internal_marks': internal_marks,
                'assignment_score': assignment_score, 'quiz_score': quiz_score,
                'lab_marks': lab_marks, 'study_hours': study_hours,
            }])
            # Regression prediction
            best_reg = reg['trained_models'][reg['best_model']]
            is_lin   = reg['best_model'] == 'Linear Regression'
            X_in     = reg['scaler'].transform(row[FEATURES]) if is_lin else row[FEATURES]
            pred_marks = float(best_reg.predict(X_in)[0])

            # Classification prediction
            best_clf_m = clf['trained_models'][clf['best_model']]
            is_log     = clf['best_model'] == 'Logistic Regression'
            X_clf      = clf['scaler'].transform(row[FEATURES]) if is_log else row[FEATURES]
            pred_grade = clf['label_encoder'].inverse_transform(best_clf_m.predict(X_clf))[0]

            # ── Result cards ──
            st.markdown("<div class='sh' style='margin-top:20px'>Prediction Results</div>", unsafe_allow_html=True)
            res1, res2, res3 = st.columns(3)
            _kpi(res1, f"{pred_marks:.1f}", "Predicted Marks", "out of 200", "var(--accent)", True)
            _kpi(res2, pred_grade, "Predicted Grade", "A-F scale", GRADE_COL.get(pred_grade, "var(--text-primary)"))

            # Risk assessment
            if pred_marks < 80:
                risk_level, risk_color = "Critical", "var(--accent-red)"
            elif pred_marks < 120:
                risk_level, risk_color = "High", "var(--accent-amber)"
            elif pred_marks < 150:
                risk_level, risk_color = "Moderate", "var(--accent)"
            else:
                risk_level, risk_color = "Low", "var(--accent-teal)"
            _kpi(res3, risk_level, "Risk Level", f"Marks: {pred_marks:.0f}/200", risk_color)

            # ── Radar chart: Student vs Average ──
            st.markdown("<div class='sh' style='margin-top:20px'>Student Profile vs Cohort Average</div>", unsafe_allow_html=True)
            radar_col, rec_col = st.columns([1.2, 0.8])
            with radar_col:
                categories = ['Attendance', 'Internals', 'Assignments', 'Quiz', 'Lab', 'Study Hrs']
                student_vals = [
                    attendance / 100, internal_marks / 50, assignment_score / 50,
                    quiz_score / 50, lab_marks / 50, study_hours / 10,
                ]
                avg_vals = [
                    df['attendance'].mean() / 100, df['internal_marks'].mean() / 50,
                    df['assignment_score'].mean() / 50, df['quiz_score'].mean() / 50,
                    df['lab_marks'].mean() / 50, df['study_hours'].mean() / 10,
                ] if len(df) > 0 else [0.5] * 6

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=avg_vals + [avg_vals[0]], theta=categories + [categories[0]],
                    name='Cohort Average', fill='toself',
                    fillcolor='rgba(99,102,241,0.1)', line=dict(color='rgba(99,102,241,0.5)', width=2),
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=student_vals + [student_vals[0]], theta=categories + [categories[0]],
                    name='This Student', fill='toself',
                    fillcolor='rgba(168,85,247,0.15)', line=dict(color='#A855F7', width=2),
                ))
                fig_radar.update_layout(**_PL)
                fig_radar.update_layout(
                    height=350, showlegend=True,
                    legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center'),
                    polar=dict(
                        bgcolor='rgba(0,0,0,0)',
                        radialaxis=dict(visible=True, range=[0, 1], showticklabels=False, gridcolor='rgba(148,163,184,0.15)'),
                        angularaxis=dict(gridcolor='rgba(148,163,184,0.15)'),
                    ),
                    margin=dict(l=40, r=40, t=20, b=40),
                )
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

            with rec_col:
                # Recommendation card
                if pred_grade in ['D', 'F']:
                    rec_icon, rec_color = "🔴", "#fca5a5"
                    rec_text = "Immediate intervention required. Focus on improving internal marks and attendance as top priorities."
                elif pred_grade == 'C':
                    rec_icon, rec_color = "🟡", "#fde68a"
                    rec_text = "On the edge. A modest increase in study hours (+1 hr/day) could push performance to a B grade."
                elif pred_grade == 'B':
                    rec_icon, rec_color = "🟢", "#86efac"
                    rec_text = "Good performance. Consistent effort in lab work and assignments can push toward an A grade."
                else:
                    rec_icon, rec_color = "⭐", "#c4b5fd"
                    rec_text = "Excellent trajectory. Maintain current habits and consider advanced coursework or mentoring peers."

                st.markdown(
                    f"<div class='glass-card' style='padding:20px;min-height:300px'>"
                    f"<div style='font-size:32px;margin-bottom:12px'>{rec_icon}</div>"
                    f"<div style='font-size:15px;font-weight:700;color:var(--text-primary);margin-bottom:8px'>AI Recommendation</div>"
                    f"<div style='color:{rec_color};font-size:13px;line-height:1.7;margin-bottom:16px'>{rec_text}</div>"
                    f"<div style='border-top:1px solid rgba(148,163,184,0.15);padding-top:12px;margin-top:auto'>"
                    f"<div style='font-size:11px;color:var(--text-muted)'>Powered by</div>"
                    f"<div style='font-size:13px;font-weight:600;color:var(--text-primary)'>{reg['best_model']} + {clf['best_model']}</div>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            # Store in prediction history
            st.session_state.prediction_history.append({
                'marks': round(pred_marks, 1),
                'grade': pred_grade,
                'attendance': attendance,
            })

            # ── Prediction History ──
            if len(st.session_state.prediction_history) > 1:
                st.markdown("<div class='sh' style='margin-top:20px'>Prediction History</div>", unsafe_allow_html=True)
                hist_df = pd.DataFrame(st.session_state.prediction_history)
                hist_df.index = range(1, len(hist_df) + 1)
                hist_df.columns = ['Predicted Marks', 'Grade', 'Attendance %']
                st.dataframe(hist_df, use_container_width=True)
