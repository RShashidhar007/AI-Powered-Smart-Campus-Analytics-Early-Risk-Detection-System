"""
pages/reports.py - Exploratory Data Analysis (EDA) page.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config    import DATA_PATH, DEPARTMENTS, DEPT_FULL_NAMES, CURRENT_ACADEMIC_YEAR
from data_pro  import run_pipeline, run_pipeline_from_db, filter_dataframe
from ml_models import FEATURES
from language  import TEXTS
from ui_theme import get_page_css, GRADE_COL, RISK_COL, DEPT_COL, PL as _PL, PL, kpi_card as _kpi, section_header as _sh

# Design system

# Colour maps & Plotly Theme


@st.cache_data(show_spinner=False)
def _load_all():
    year = st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR)
    df = run_pipeline_from_db(year)
    if df.empty:
        df = run_pipeline(DATA_PATH)
    return df

def render_reports_page():
    st.markdown(get_page_css(st.session_state.get('theme_mode', 'Dark')), unsafe_allow_html=True)
    
    T  = TEXTS[st.session_state.language]
    all_df = _load_all()

    sel_dept = st.session_state.get('selected_department', 'All')
    sel_sem  = st.session_state.get('selected_semester', 'All')
    df = filter_dataframe(all_df, sel_dept, sel_sem)

    filter_parts = []
    if sel_dept != 'All': filter_parts.append(sel_dept)
    if sel_sem != 'All': filter_parts.append(f"Sem {sel_sem}")
    filter_str = " · ".join(filter_parts) if filter_parts else "All Departments"

    # Hero header
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:14px;margin-bottom:6px'>"
        f"<div style='font-size:22px;font-weight:700;color:var(--text-primary)'>Data Reports</div>"
        f"<div style='background:linear-gradient(135deg,#6366F1,#A855F7);padding:4px 14px;"
        f"border-radius:999px;font-size:12px;font-weight:700;color:white'>"
        f"{len(df)} students · {filter_str}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='color:var(--text-muted);font-size:13px;margin-bottom:20px'>"
        "Detailed data patterns, relationships, and department performance analysis</div>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Overview", "Relationships", "Grade Breakdown", "Department Comparison"]
    )

    # ── Tab 1: Distributions ──
    with tab1:
        st.markdown("<div class='sh'>Feature Distributions</div>", unsafe_allow_html=True)
        all_f = FEATURES + ['semester_marks']
        for i in range(0, len(all_f), 3):
            chunk = all_f[i:i+3]
            cols  = st.columns(3)
            for ci, feat in enumerate(chunk):
                with cols[ci]:
                    if len(df) > 0:
                        fig = go.Figure()
                        fig.add_trace(go.Histogram(
                            x=df[feat], nbinsx=20,
                            marker_color='rgba(99,102,241,0.6)',
                            marker_line_color='rgba(168,85,247,0.8)', marker_line_width=1,
                        ))
                        mean_val = df[feat].mean()
                        fig.add_vline(x=mean_val, line_dash='dash', line_color='#A855F7', line_width=2,
                                      annotation_text=f"μ={mean_val:.1f}",
                                      annotation_font_size=10, annotation_font_color='#A855F7')
                        fig.update_layout(**_PL)
                        fig.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10),
                                          xaxis=dict(title=feat.replace('_', ' ').title(), showgrid=True, gridcolor='rgba(148,163,184,0.1)'),
                                          yaxis=dict(title='Count', showgrid=True, gridcolor='rgba(148,163,184,0.1)'))
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

    # ── Tab 2: Relationships ──
    with tab2:
        if len(df) > 10:
            st.markdown("<div class='sh'>Impact on Final Marks</div>", unsafe_allow_html=True)
            numeric = FEATURES
            corr = df[numeric].corrwith(df['semester_marks']).abs().sort_values(ascending=True)
            vals = (corr * 100).round(1).values
            labels = [f.replace("_", " ").title() for f in corr.index]

            fig_corr = go.Figure(go.Bar(
                x=vals, y=labels, orientation="h",
                marker=dict(
                    color=vals,
                    colorscale=[[0, '#0F172A'], [0.5, '#6366F1'], [1, '#A855F7']],
                    line=dict(width=1, color="rgba(255,255,255,0.12)"),
                ),
                text=[f"{v:.1f}%" for v in vals],
                textposition="inside", insidetextanchor="end",
                hovertemplate="<b>%{y}</b><br>Impact: %{x:.1f}%<extra></extra>",
            ))
            fig_corr.update_layout(**_PL)
            fig_corr.update_layout(
                height=350, margin=dict(l=10, r=10, t=30, b=10),
                xaxis_title="Impact Strength (%)",
                xaxis=dict(showgrid=True, gridcolor='rgba(148,163,184,0.1)'),
            )
            fig_corr.update_yaxes(showgrid=False)
            st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

            top_feat = labels[-1]
            st.markdown(
                f"<div class='glass-card' style='padding:16px;display:flex;align-items:center;gap:16px'>"
                f"<div style='font-size:32px'>🎯</div>"
                f"<div>"
                f"<div style='font-size:15px;font-weight:700;color:var(--text-primary)'>"
                f"{top_feat} has the strongest impact on final marks</div>"
                f"<div style='font-size:13px;color:var(--text-muted);margin-top:4px'>"
                f"Focus interventions on this factor for maximum academic improvement.</div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

    # ── Tab 3: Box Plots ──
    with tab3:
        if len(df) > 0:
            st.markdown("<div class='sh'>Feature Distribution by Grade</div>", unsafe_allow_html=True)
            fc = st.selectbox("Feature", options=FEATURES,
                              format_func=lambda x: x.replace('_', ' ').title())
            fb = px.box(df, x='grade_label', y=fc, color='grade_label',
                        color_discrete_map=GRADE_COL,
                        category_orders={'grade_label': ['A', 'B', 'C', 'D', 'F']},
                        points='outliers')
            fb.update_layout(**_PL)
            fb.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10),
                             xaxis=dict(title='Grade', showgrid=False),
                             yaxis=dict(title=fc.replace('_', ' ').title(), showgrid=True, gridcolor='rgba(148,163,184,0.1)'),
                             showlegend=False)
            st.plotly_chart(fb, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

            st.markdown("<div class='sh' style='margin-top:20px'>Grade Statistics</div>", unsafe_allow_html=True)
            gs = (df.groupby('grade_label')[fc]
                  .agg(['mean', 'median', 'std', 'min', 'max'])
                  .round(2).reindex(['A', 'B', 'C', 'D', 'F']))
            st.dataframe(gs.style.background_gradient(cmap='RdYlGn', axis=0)
                         .format("{:.2f}"), use_container_width=True)

    # ── Tab 4: Department Comparison ──
    with tab4:
        compare_df = all_df.copy()
        if sel_sem != 'All':
            compare_df = compare_df[compare_df['semester'] == int(sel_sem)]

        if len(compare_df) > 0:
            st.markdown("<div class='sh'>Department Performance</div>", unsafe_allow_html=True)

            dept_agg = compare_df.groupby('department').agg(
                total=('usn', 'count'),
                avg_marks=('semester_marks', 'mean'),
                avg_attendance=('attendance', 'mean'),
                at_risk_pct=('is_at_risk', 'mean'),
                avg_internal=('internal_marks', 'mean'),
            ).round(2).reset_index()
            dept_agg['at_risk_pct'] = (dept_agg['at_risk_pct'] * 100).round(1)

            # KPI cards for departments
            dept_cols = st.columns(len(dept_agg))
            for i, row in dept_agg.iterrows():
                with dept_cols[i]:
                    d_color = DEPT_COL.get(row['department'], 'var(--accent)')
                    st.markdown(
                        f"<div class='glass-card' style='padding:16px;text-align:center'>"
                        f"<div style='font-size:20px;font-weight:700;color:{d_color}'>{row['department']}</div>"
                        f"<div style='font-size:11px;color:var(--text-muted);margin:4px 0 10px'>{int(row['total'])} students</div>"
                        f"<div style='display:flex;justify-content:space-around;gap:4px'>"
                        f"<div><div style='font-size:14px;font-weight:700;color:var(--text-primary)'>{row['avg_marks']:.0f}</div>"
                        f"<div style='font-size:9px;color:var(--text-muted)'>Avg Marks</div></div>"
                        f"<div><div style='font-size:14px;font-weight:700;color:var(--text-primary)'>{row['at_risk_pct']:.0f}%</div>"
                        f"<div style='font-size:9px;color:var(--text-muted)'>At-Risk</div></div>"
                        f"</div></div>",
                        unsafe_allow_html=True,
                    )

            dc1, dc2 = st.columns(2)
            with dc1:
                fig1 = px.bar(dept_agg, x='department', y='avg_marks',
                              color='department', color_discrete_map=DEPT_COL,
                              text='avg_marks')
                fig1.update_traces(textposition='outside', texttemplate='%{text:.1f}', marker_line_width=1, marker_line_color='rgba(255,255,255,0.12)')
                fig1.update_layout(**_PL)
                fig1.update_layout(height=300, xaxis_title='', yaxis_title='Marks', showlegend=False,
                                   margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")
                st.caption("Average Semester Marks")

            with dc2:
                fig2 = px.bar(dept_agg, x='department', y='at_risk_pct',
                              color='department', color_discrete_map=DEPT_COL,
                              text='at_risk_pct')
                fig2.update_traces(textposition='outside', texttemplate='%{text:.1f}%', marker_line_width=1, marker_line_color='rgba(255,255,255,0.12)')
                fig2.update_layout(**_PL)
                fig2.update_layout(height=300, xaxis_title='', yaxis_title='%', showlegend=False,
                                   margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")
                st.caption("At-Risk Percentage")

            dc3, dc4 = st.columns(2)
            with dc3:
                fig3 = px.bar(dept_agg, x='department', y='avg_attendance',
                              color='department', color_discrete_map=DEPT_COL,
                              text='avg_attendance')
                fig3.update_traces(textposition='outside', texttemplate='%{text:.1f}%', marker_line_width=1, marker_line_color='rgba(255,255,255,0.12)')
                fig3.update_layout(**_PL)
                fig3.update_layout(height=300, xaxis_title='', yaxis_title='%', showlegend=False,
                                   margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")
                st.caption("Average Attendance")

            with dc4:
                if sel_sem == 'All':
                    sem_dept = all_df.groupby(['department', 'semester']).agg(
                        avg_marks=('semester_marks', 'mean'),
                    ).round(1).reset_index()
                    sem_dept['semester'] = sem_dept['semester'].astype(str)
                    fig4 = px.line(sem_dept, x='semester', y='avg_marks',
                                  color='department', color_discrete_map=DEPT_COL,
                                  markers=True)
                    fig4.update_traces(line=dict(shape='spline', width=3), marker=dict(size=8, opacity=0.8))
                    fig4.update_layout(**_PL)
                    fig4.update_layout(height=300, showlegend=True,
                                      legend=dict(orientation='h', y=-0.25, font_size=10),
                                      xaxis_title='Semester', yaxis_title='Avg Marks',
                                      margin=dict(l=10, r=10, t=20, b=10))
                    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")
                    st.caption("Marks Trend by Semester")

            st.markdown("<div class='sh' style='margin-top:20px'>Department Summary</div>", unsafe_allow_html=True)
            dept_display = dept_agg.copy()
            dept_display.columns = ['Department', 'Total Students', 'Avg Marks', 'Avg Attendance %',
                                    'At-Risk %', 'Avg Internal']
            st.dataframe(dept_display.style.background_gradient(cmap='RdYlGn', subset=['Avg Marks', 'Avg Attendance %'])
                         .background_gradient(cmap='RdYlGn_r', subset=['At-Risk %'])
                         .format({'Avg Marks': '{:.1f}', 'Avg Attendance %': '{:.1f}',
                                  'At-Risk %': '{:.1f}', 'Avg Internal': '{:.1f}'}),
                         use_container_width=True)
