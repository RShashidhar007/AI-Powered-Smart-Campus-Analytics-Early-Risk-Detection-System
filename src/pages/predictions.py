"""
pages/predictions.py — ML models display + single-student prediction.
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

# ── Colour maps ───────────────────────────────────────────────────────────────
GRADE_COL = {"A": "#1e8449", "B": "#1a5276", "C": "#b7770d", "D": "#d35400", "F": "#c0392b"}
RISK_COL  = {"Low": "#1e8449", "Moderate": "#b7770d", "High": "#d35400", "Critical": "#c0392b"}
PL = dict(font_family="DM Sans,sans-serif", font_color="#8f9bba",
          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
          margin=dict(l=8, r=8, t=32, b=8))


def _kpi(col, val, label, sub="", color="#4318ff", highlight=False):
    style_str = "border-left: 6px solid #4318ff;" if highlight else ""
    col.markdown(
        f'<div class="kpi" style="{style_str}">'
        f'<div class="kv" style="color:{color}">{val}</div>'
        f'<div class="kl">{label}</div>'
        f'<div class="ks">{sub}</div></div>',
        unsafe_allow_html=True,
    )


# ── Cached loaders ────────────────────────────────────────────────────────────
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
    T  = TEXTS[st.session_state.language]

    sel_dept = st.session_state.get('selected_department', 'All')
    sel_sem  = st.session_state.get('selected_semester', 'All')
    df = filter_dataframe(_load_df(), sel_dept, sel_sem)

    # Build filter label
    filter_label = []
    if sel_dept != 'All': filter_label.append(sel_dept)
    if sel_sem != 'All': filter_label.append(f"Sem {sel_sem}")
    filter_str = " · ".join(filter_label) if filter_label else "All Departments"

    st.markdown("## Predictions & ML Models")
    st.markdown(
        f"<div style='color:var(--muted-color,#888);font-size:13px;margin-bottom:20px'>"
        f"Regression · Classification · Feature importance · Single-student predictor · {filter_str}</div>",
        unsafe_allow_html=True,
    )

    with st.spinner("Training models (first load ~5 s)…"):
        reg = _train_reg(sel_dept, sel_sem)
        clf = _train_clf(sel_dept, sel_sem)

    tab_reg, tab_clf, tab_fi, tab_pred = st.tabs(
        ["📉 Regression", "🏷 Classification", "⭐ Feature Importance", "🔮 Predict Student"]
    )

    # ── Regression ────────────────────────────────────────────────────────────
    with tab_reg:
        st.markdown("#### Predicting semester marks")
        results   = reg['results']
        best_name = reg['best_model']
        cols = st.columns(len(results))
        for i, (name, m) in enumerate(results.items()):
            ib = name == best_name
            _kpi(cols[i], m['R2'], name, f"RMSE {m['RMSE']} · MAE {m['MAE']}",
                 "#1e8449" if ib else "#333", ib)
        st.markdown("<br>", unsafe_allow_html=True)
        st.success(f"✅ Best: **{best_name}** — R² = **{results[best_name]['R2']}** "
                   f"(explains {results[best_name]['R2']*100:.1f}% of variance)")

        # Actual vs Predicted scatter
        best_model = reg['trained_models'][best_name]
        is_lin     = best_name == 'Linear Regression'
        X_all      = df[FEATURES]
        X_in       = reg['scaler'].transform(X_all) if is_lin else X_all
        preds      = best_model.predict(X_in)
        sdf        = df.copy(); sdf['predicted'] = np.round(preds, 2)
        sample_n   = min(150, len(sdf))
        smp        = sdf.sample(sample_n, random_state=42) if len(sdf) >= sample_n else sdf
        fap = px.scatter(smp, x='semester_marks', y='predicted',
                         color='grade_label', color_discrete_map=GRADE_COL, opacity=0.7,
                         labels={'semester_marks': 'Actual', 'predicted': 'Predicted'},
                         title="Actual vs Predicted")
        mn, mx = smp['semester_marks'].min(), smp['semester_marks'].max()
        fap.add_trace(go.Scatter(x=[mn, mx], y=[mn, mx], mode='lines',
                                 line=dict(color='#c0392b', dash='dash', width=1.5),
                                 name='Perfect fit', showlegend=True))
        fap.update_layout(font_family="DM Sans,sans-serif", font_color="#8f9bba",
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=8, r=8, t=32, b=8),
                          height=340, showlegend=True,
                          legend=dict(orientation='h', y=-0.2, font_size=11),
                          xaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)'), yaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)'),
                          title_font_size=13)
        st.plotly_chart(fap, use_container_width=True, config={'displayModeBar': False})

    # ── Classification ────────────────────────────────────────────────────────
    with tab_clf:
        st.markdown("#### Predicting grade A–F")
        clf_results = clf['results']
        best_c      = clf['best_model']
        cols2 = st.columns(len(clf_results))
        for i, (name, m) in enumerate(clf_results.items()):
            ib = name == best_c
            _kpi(cols2[i], f"{m['Accuracy']*100:.1f}%", name, "Accuracy",
                 "#1a5276" if ib else "#333", ib)
        st.markdown("<br>", unsafe_allow_html=True)

        best_cm = np.array(clf_results[best_c]['Confusion'])
        classes = clf.get('grade_classes', ['A', 'B', 'C', 'D', 'F'])
        fcm = px.imshow(best_cm, x=classes, y=classes,
                        color_continuous_scale='Blues',
                        text_auto=True, aspect='auto',
                        title=f"Confusion Matrix — {best_c}")
        fcm.update_layout(**PL, height=360, coloraxis_showscale=False,
                          xaxis_title="Predicted", yaxis_title="Actual",
                          title_font_size=13)
        st.plotly_chart(fcm, use_container_width=True, config={'displayModeBar': False})

    # ── Feature Importance ────────────────────────────────────────────────────
    with tab_fi:
        ca, cb = st.columns(2)
        for col_widget, fi_data, title, cscale in [
            (ca, reg['feature_importance'], 'Regression',     ['#e8f2fc', '#1a5276']),
            (cb, clf['feature_importance'], 'Classification', ['#e8f8f0', '#1e8449']),
        ]:
            with col_widget:
                st.markdown(f"**{title} (Random Forest)**")
                fidf = pd.DataFrame({
                    'Feature':    [k.replace('_', ' ').title() for k in fi_data],
                    'Importance': list(fi_data.values()),
                }).sort_values('Importance', ascending=True)
                ffi = px.bar(fidf, x='Importance', y='Feature', orientation='h',
                             color='Importance', color_continuous_scale=cscale)
                ffi.update_layout(**PL, height=280, coloraxis_showscale=False,
                                  xaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)'), yaxis=dict(showgrid=False))
                st.plotly_chart(ffi, use_container_width=True, config={'displayModeBar': False})
        st.success("🔑 **Internal marks** is the most important feature in both models.")

    # ── Predict single student ────────────────────────────────────────────────
    with tab_pred:
        st.markdown("#### Enter student details")
        rc1, rc2, rc3 = st.columns(3)
        attendance       = rc1.slider("Attendance %",       0.0, 100.0, 72.0, 0.5)
        internal_marks   = rc2.slider("Internal marks",     0.0,  50.0, 35.0, 0.5)
        assignment_score = rc3.slider("Assignment score",   0.0,  50.0, 38.0, 0.5)
        rc4, rc5, rc6 = st.columns(3)
        quiz_score  = rc4.slider("Quiz score",      0.0, 50.0, 34.0, 0.5)
        lab_marks   = rc5.slider("Lab marks",       0.0, 50.0, 36.0, 0.5)
        study_hours = rc6.slider("Study hours/day", 0.0, 10.0,  3.5, 0.1)

        if st.button("🔮  Run Prediction", use_container_width=True, type="primary"):
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

            c1, c2 = st.columns(2)
            _kpi(c1, f"{pred_marks:.1f}", "Predicted Marks", "out of 200", "#4318ff", True)
            _kpi(c2, pred_grade, "Predicted Grade", "", GRADE_COL.get(pred_grade, "#333"))

            # Store in prediction history
            st.session_state.prediction_history.append({
                'marks': round(pred_marks, 1),
                'grade': pred_grade,
                'attendance': attendance,
            })
