"""
pages/reports.py — Exploratory Data Analysis (EDA) page.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from config    import DATA_PATH, DEPARTMENTS, DEPT_FULL_NAMES, CURRENT_ACADEMIC_YEAR
from data_pro  import run_pipeline, run_pipeline_from_db, filter_dataframe
from ml_models import FEATURES
from language  import TEXTS

GRADE_COL = {"A": "#1e8449", "B": "#1a5276", "C": "#b7770d", "D": "#d35400", "F": "#c0392b"}
DEPT_COL  = {"CSE": "#5b5ef4", "ECE": "#e84855", "ME": "#f4a261", "CE": "#2ec4b6", "ISE": "#9b59b6"}
PL = dict(font_family="DM Sans,sans-serif", font_color="#8f9bba",
          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
          margin=dict(l=8, r=8, t=32, b=8))


@st.cache_data(show_spinner=False)
def _load_all():
    year = st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR)
    df = run_pipeline_from_db(year)
    if df.empty:
        df = run_pipeline(DATA_PATH)
    return df


def render_reports_page():
    T  = TEXTS[st.session_state.language]
    all_df = _load_all()

    sel_dept = st.session_state.get('selected_department', 'All')
    sel_sem  = st.session_state.get('selected_semester', 'All')
    df = filter_dataframe(all_df, sel_dept, sel_sem)

    st.markdown("## Exploratory Data Analysis")
    st.markdown(
        "<div style='color:var(--muted-color,#888);font-size:13px;margin-bottom:20px'>"
        "Distributions · Correlations · Box plots by grade · Department comparison</div>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Distributions", "🔥 Correlations", "📦 Box Plots", "🏫 Department Comparison"]
    )

    # ── Distributions ─────────────────────────────────────────────────────────
    with tab1:
        all_f = FEATURES + ['semester_marks']
        for i in range(0, len(all_f), 3):
            chunk = all_f[i:i+3]
            cols  = st.columns(3)
            for ci, feat in enumerate(chunk):
                with cols[ci]:
                    if len(df) > 0:
                        fig = px.histogram(df, x=feat, nbins=20,
                                           color_discrete_sequence=['#5b5ef4'],
                                           title=feat.replace('_', ' ').title())
                        fig.add_vline(x=df[feat].mean(), line_dash='dash', line_color='#c0392b',
                                      annotation_text=f"μ={df[feat].mean():.1f}",
                                      annotation_font_size=10, annotation_font_color='#c0392b')
                        fig.update_layout(**PL, height=210, title_font_size=12,
                                          xaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)'),
                                          yaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)'))
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── Correlations ──────────────────────────────────────────────────────────
    with tab2:
        if len(df) > 10:
            numeric = FEATURES + ['semester_marks']
            cm      = df[numeric].corr().round(3)
            fhm     = px.imshow(cm, color_continuous_scale='RdYlGn',
                                zmin=-0.3, zmax=0.8, text_auto=True, aspect='auto',
                                title="Correlation matrix")
            fhm.update_layout(**PL, height=420, title_font_size=13,
                              coloraxis_colorbar=dict(title="r", thickness=12))
            st.plotly_chart(fhm, use_container_width=True, config={'displayModeBar': False})

            st.markdown("#### Correlation with semester marks")
            cs2 = cm['semester_marks'].drop('semester_marks').sort_values(ascending=False)
            ca, cb = st.columns([1.2, 1])
            with ca:
                for feat, val in cs2.items():
                    col_c = "#1e8449" if val > 0.4 else ("#d35400" if val > 0.15 else "#888")
                    bw    = max(int(abs(val) * 120), 4)
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
                        f'<div style="width:140px;font-size:12px;color:#555">{feat.replace("_"," ").title()}</div>'
                        f'<div style="width:{bw}px;height:8px;background:{col_c};border-radius:4px"></div>'
                        f'<div style="font-size:12px;font-weight:600;color:{col_c}">{val:+.3f}</div></div>',
                        unsafe_allow_html=True,
                    )
            with cb:
                st.info("**Internal marks** — strongest predictor.\n\n"
                        "**Study hours** — almost zero correlation.\n\n"
                        "Focus interventions on internal assessment performance.")

    # ── Box Plots ─────────────────────────────────────────────────────────────
    with tab3:
        if len(df) > 0:
            fc = st.selectbox("Feature", options=FEATURES,
                              format_func=lambda x: x.replace('_', ' ').title())
            fb = px.box(df, x='grade_label', y=fc, color='grade_label',
                        color_discrete_map=GRADE_COL,
                        category_orders={'grade_label': ['A', 'B', 'C', 'D', 'F']},
                        points='outliers', title=f"{fc.replace('_',' ').title()} by Grade")
            fb.update_layout(**PL, height=380,
                             xaxis=dict(title='Grade', showgrid=False),
                             yaxis=dict(title=fc.replace('_', ' ').title(), gridcolor='rgba(143, 155, 186, 0.1)'),
                             title_font_size=13)
            st.plotly_chart(fb, use_container_width=True, config={'displayModeBar': False})

            gs = (df.groupby('grade_label')[fc]
                  .agg(['mean', 'median', 'std', 'min', 'max'])
                  .round(2).reindex(['A', 'B', 'C', 'D', 'F']))
            st.dataframe(gs.style.background_gradient(cmap='RdYlGn', axis=0)
                         .format("{:.2f}"), use_container_width=True)

    # ── Department Comparison ─────────────────────────────────────────────────
    with tab4:
        compare_df = all_df.copy()
        if sel_sem != 'All':
            compare_df = compare_df[compare_df['semester'] == int(sel_sem)]

        if len(compare_df) > 0:
            st.markdown("#### Department Performance Comparison")

            dept_agg = compare_df.groupby('department').agg(
                total=('usn', 'count'),
                avg_marks=('semester_marks', 'mean'),
                avg_attendance=('attendance', 'mean'),
                at_risk_pct=('is_at_risk', 'mean'),
                avg_internal=('internal_marks', 'mean'),
            ).round(2).reset_index()
            dept_agg['at_risk_pct'] = (dept_agg['at_risk_pct'] * 100).round(1)

            dc1, dc2 = st.columns(2)
            with dc1:
                fig1 = px.bar(dept_agg, x='department', y='avg_marks',
                              color='department', color_discrete_map=DEPT_COL,
                              text='avg_marks', title="Avg Semester Marks")
                fig1.update_traces(textposition='outside', texttemplate='%{text:.1f}')
                fig1.update_layout(**PL, height=300, xaxis_title='', yaxis_title='Marks')
                st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

            with dc2:
                fig2 = px.bar(dept_agg, x='department', y='at_risk_pct',
                              color='department', color_discrete_map=DEPT_COL,
                              text='at_risk_pct', title="At-Risk Percentage (%)")
                fig2.update_traces(textposition='outside', texttemplate='%{text:.1f}%')
                fig2.update_layout(**PL, height=300, xaxis_title='', yaxis_title='%')
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

            dc3, dc4 = st.columns(2)
            with dc3:
                fig3 = px.bar(dept_agg, x='department', y='avg_attendance',
                              color='department', color_discrete_map=DEPT_COL,
                              text='avg_attendance', title="Avg Attendance (%)")
                fig3.update_traces(textposition='outside', texttemplate='%{text:.1f}%')
                fig3.update_layout(**PL, height=300, xaxis_title='', yaxis_title='%')
                st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

            with dc4:
                # Semester-wise comparison across departments
                if sel_sem == 'All':
                    sem_dept = all_df.groupby(['department', 'semester']).agg(
                        avg_marks=('semester_marks', 'mean'),
                    ).round(1).reset_index()
                    sem_dept['semester'] = sem_dept['semester'].astype(str)
                    fig4 = px.line(sem_dept, x='semester', y='avg_marks',
                                  color='department', color_discrete_map=DEPT_COL,
                                  markers=True, title="Marks Trend by Semester")
                    fig4.update_layout(font_family="DM Sans,sans-serif", font_color="#8f9bba",
                                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                      margin=dict(l=8, r=8, t=32, b=8),
                                      height=300, showlegend=True,
                                      legend=dict(orientation='h', y=-0.25, font_size=10),
                                      xaxis_title='Semester', yaxis_title='Avg Marks')
                    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

            # Summary table
            st.markdown("#### Department Summary")
            dept_display = dept_agg.copy()
            dept_display.columns = ['Department', 'Total Students', 'Avg Marks', 'Avg Attendance %',
                                    'At-Risk %', 'Avg Internal']
            st.dataframe(dept_display.style.background_gradient(cmap='RdYlGn', subset=['Avg Marks', 'Avg Attendance %'])
                         .background_gradient(cmap='RdYlGn_r', subset=['At-Risk %'])
                         .format({'Avg Marks': '{:.1f}', 'Avg Attendance %': '{:.1f}',
                                  'At-Risk %': '{:.1f}', 'Avg Internal': '{:.1f}'}),
                         use_container_width=True)
