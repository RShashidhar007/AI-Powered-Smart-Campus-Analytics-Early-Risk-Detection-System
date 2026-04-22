"""
pages/reports.py â€” Exploratory Data Analysis (EDA) page.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from config    import DATA_PATH, DEPARTMENTS, DEPT_FULL_NAMES, CURRENT_ACADEMIC_YEAR
from data_pro  import run_pipeline, run_pipeline_from_db, filter_dataframe
from ml_models import FEATURES
from language  import TEXTS
from ui_theme import PAGE_CSS, GRADE_COL, RISK_COL, DEPT_COL, PL as _PL, PL, kpi_card as _kpi, section_header as _sh

# â”€â”€ Design system â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# â”€â”€ Colour maps & Plotly Theme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@st.cache_data(show_spinner=False)
def _load_all():
    year = st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR)
    df = run_pipeline_from_db(year)
    if df.empty:
        df = run_pipeline(DATA_PATH)
    return df

def render_reports_page():
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    
    T  = TEXTS[st.session_state.language]
    all_df = _load_all()

    sel_dept = st.session_state.get('selected_department', 'All')
    sel_sem  = st.session_state.get('selected_semester', 'All')
    df = filter_dataframe(all_df, sel_dept, sel_sem)

    st.markdown('<div class="page-title">Exploratory Data Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>"
        "Distributions Correlations Box Plots by grade Department Comparison</div>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [" Distributions", " Correlations", "Box Plots", "Department Comparison"]
    )

    # Distributions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with tab1:
        all_f = FEATURES + ['semester_marks']
        for i in range(0, len(all_f), 3):
            chunk = all_f[i:i+3]
            cols  = st.columns(3)
            for ci, feat in enumerate(chunk):
                with cols[ci]:
                    if len(df) > 0:
                        fig = px.histogram(df, x=feat, nbins=20,
                                           color_discrete_sequence=['var(--accent)'],
                                           title=feat.replace('_', ' ').title())
                        fig.add_vline(x=df[feat].mean(), line_dash='dash', line_color='var(--accent-red)',
                                      annotation_text=f"Î¼={df[feat].mean():.1f}",
                                      annotation_font_size=10, annotation_font_color='var(--accent-red)')
                        fig.update_layout(**_PL)
                        fig.update_layout(height=210, title_font_size=12,
                                          xaxis=dict(showgrid=True),
                                          yaxis=dict(showgrid=True))
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

    # Correlations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with tab2:
        if len(df) > 10:
            numeric = FEATURES + ['semester_marks']
            cm      = df[numeric].corr().round(3)
            fhm     = px.imshow(cm, color_continuous_scale='RdYlGn',
                                zmin=-0.3, zmax=0.8, text_auto=True, aspect='auto',
                                title="Correlation matrix")
            fhm.update_layout(**_PL)
            fhm.update_layout(height=420, title_font_size=13,
                              coloraxis_colorbar=dict(title="r", thickness=12))
            st.plotly_chart(fhm, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

            st.markdown("#### Correlation with semester marks")
            cs2 = cm['semester_marks'].drop('semester_marks').sort_values(ascending=False)
            ca, cb = st.columns([1.2, 1])
            with ca:
                for feat, val in cs2.items():
                    col_c = "var(--accent-teal)" if val > 0.4 else ("var(--accent-amber)" if val > 0.15 else "#888")
                    bw    = max(int(abs(val) * 120), 4)
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
                        f'<div style="width:140px;font-size:12px;color:#A0AEC0">{feat.replace("_"," ").title()}</div>'
                        f'<div style="width:{bw}px;height:8px;background:{col_c};border-radius:4px"></div>'
                        f'<div style="font-size:12px;font-weight:600;color:{col_c}">{val:+.3f}</div></div>',
                        unsafe_allow_html=True,
                    )
            with cb:
                st.info("**Internal marks** â€” strongest predictor.\n\n"
                        "**Study hours** â€” almost zero correlation.\n\n"
                        "Focus interventions on internal assessment performance.")

    # Box Plots â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with tab3:
        if len(df) > 0:
            fc = st.selectbox("Feature", options=FEATURES,
                              format_func=lambda x: x.replace('_', ' ').title())
            fb = px.box(df, x='grade_label', y=fc, color='grade_label',
                        color_discrete_map=GRADE_COL,
                        category_orders={'grade_label': ['A', 'B', 'C', 'D', 'F']},
                        points='outliers', title=f"{fc.replace('_',' ').title()} by Grade")
            fb.update_layout(**_PL)
            fb.update_layout(height=380,
                             xaxis=dict(title='Grade', showgrid=False),
                             yaxis=dict(title=fc.replace('_', ' ').title(), showgrid=True),
                             title_font_size=13, showlegend=False)
            st.plotly_chart(fb, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

            gs = (df.groupby('grade_label')[fc]
                  .agg(['mean', 'median', 'std', 'min', 'max'])
                  .round(2).reindex(['A', 'B', 'C', 'D', 'F']))
            st.dataframe(gs.style.background_gradient(cmap='RdYlGn', axis=0)
                         .format("{:.2f}"), use_container_width=True)

    # Department Comparison â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
                fig1.update_traces(textposition='outside', texttemplate='%{text:.1f}', marker_line_width=1, marker_line_color='rgba(0,0,0,0.1)')
                fig1.update_layout(**_PL)
                fig1.update_layout(height=300, xaxis_title='', yaxis_title='Marks', showlegend=False)
                st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

            with dc2:
                fig2 = px.bar(dept_agg, x='department', y='at_risk_pct',
                              color='department', color_discrete_map=DEPT_COL,
                              text='at_risk_pct', title="At-Risk Percentage (%)")
                fig2.update_traces(textposition='outside', texttemplate='%{text:.1f}%', marker_line_width=1, marker_line_color='rgba(0,0,0,0.1)')
                fig2.update_layout(**_PL)
                fig2.update_layout(height=300, xaxis_title='', yaxis_title='%', showlegend=False)
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

            dc3, dc4 = st.columns(2)
            with dc3:
                fig3 = px.bar(dept_agg, x='department', y='avg_attendance',
                              color='department', color_discrete_map=DEPT_COL,
                              text='avg_attendance', title="Avg Attendance (%)")
                fig3.update_traces(textposition='outside', texttemplate='%{text:.1f}%', marker_line_width=1, marker_line_color='rgba(0,0,0,0.1)')
                fig3.update_layout(**_PL)
                fig3.update_layout(height=300, xaxis_title='', yaxis_title='%', showlegend=False)
                st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

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
                    fig4.update_traces(line=dict(shape='spline', width=3), marker=dict(size=8, opacity=0.8, line=dict(width=1, color='rgba(0,0,0,0.2)')))
                    fig4.update_layout(**_PL)
                    fig4.update_layout(
                                      height=300, showlegend=True,
                                      legend=dict(orientation='h', y=-0.25, font_size=10),
                                      xaxis_title='Semester', yaxis_title='Avg Marks')
                    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

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

