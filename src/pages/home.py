"""
pages/home.py — Campus Overview dashboard page.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from config      import DATA_PATH, DEPARTMENTS, DEPT_FULL_NAMES
from data_pro    import run_pipeline, get_summary_stats, get_at_risk_students, filter_dataframe
from ml_models   import FEATURES
from language    import TEXTS

# ── Cached loader ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _load_all():
    return run_pipeline(DATA_PATH)

# ── Colour maps ───────────────────────────────────────────────────────────────
GRADE_COL = {"A": "#1e8449", "B": "#1a5276", "C": "#b7770d", "D": "#d35400", "F": "#c0392b"}
RISK_COL  = {"Low": "#1e8449", "Moderate": "#b7770d", "High": "#d35400", "Critical": "#c0392b"}
DEPT_COL  = {"CSE": "#5b5ef4", "ECE": "#e84855", "ME": "#f4a261", "CE": "#2ec4b6", "ISE": "#9b59b6"}
PL = dict(font_family="DM Sans,sans-serif", font_color="#8f9bba",
          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
          margin=dict(l=8, r=8, t=32, b=8), showlegend=False)


def _kpi(col, val, label, sub="", color="#4318ff", highlight=False):
    style_str = "border-left: 6px solid #4318ff;" if highlight else ""
    col.markdown(
        f'<div class="kpi" style="{style_str}">'
        f'<div class="kv" style="color:{color}">{val}</div>'
        f'<div class="kl">{label}</div>'
        f'<div class="ks">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def render_home_page():
    T  = TEXTS[st.session_state.language]
    all_df = _load_all()

    # Apply global filters
    sel_dept = st.session_state.get('selected_department', 'All')
    sel_sem  = st.session_state.get('selected_semester', 'All')
    df = filter_dataframe(all_df, sel_dept, sel_sem)
    stats = get_summary_stats(df)

    # Build subtitle
    filter_parts = []
    if sel_dept != 'All':
        filter_parts.append(DEPT_FULL_NAMES.get(sel_dept, sel_dept))
    else:
        filter_parts.append("All Departments")
    if sel_sem != 'All':
        filter_parts.append(f"Semester {sel_sem}")
    else:
        filter_parts.append("All Semesters")

    st.markdown("## Campus Overview")
    st.markdown(
        f"<div style='color:var(--muted-color,#888);font-size:13px;margin-bottom:20px'>"
        f"Real-time analytics · {stats['total_students']} students · {' · '.join(filter_parts)}</div>",
        unsafe_allow_html=True,
    )

    # Critical alert
    crit_n = int((df['risk_tier'] == 'Critical').sum())
    if crit_n > 0:
        st.markdown(
            f'<div class="al">🚨 <b>{crit_n} students</b> are Critical risk — '
            f'immediate faculty intervention required.</div>',
            unsafe_allow_html=True,
        )

    # KPI row
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    _kpi(c1, stats['total_students'],                          "Total",      f"{len(DEPARTMENTS)} depts",  "#5b5ef4")
    _kpi(c2, stats['at_risk_count'],                           "At-Risk",    f"{stats['at_risk_count']/max(stats['total_students'],1)*100:.1f}%", "#c0392b")
    _kpi(c3, crit_n,                                           "Critical",   "immediate",          "#922b21")
    _kpi(c4, f"{df['semester_marks'].mean():.1f}" if len(df) else "—", "Avg Marks",  "out of 200",         "#1e8449")
    _kpi(c5, f"{df['attendance'].mean():.1f}%" if len(df) else "—",   "Avg Attend", "threshold 65%",      "#d35400")
    _kpi(c6, f"{(df['semester_marks']>=120).mean()*100:.1f}%" if len(df) else "—", "Pass Rate",  "marks ≥ 120",        "#1a5276")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row 1
    col1, col2, col3 = st.columns([1.3, 1, 1])

    with col1:
        st.markdown('<div class="sh">Grade distribution</div>', unsafe_allow_html=True)
        gd = pd.DataFrame({
            'Grade': ['A', 'B', 'C', 'D', 'F'],
            'Count': [stats['grade_distribution'].get(g, 0) for g in ['A', 'B', 'C', 'D', 'F']],
        })
        fig = px.bar(gd, x='Grade', y='Count', color='Grade',
                     color_discrete_map=GRADE_COL, text='Count')
        fig.update_traces(textposition='outside', marker_line_width=0)
        fig.update_layout(**PL, height=260,
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown('<div class="sh">Risk tier split</div>', unsafe_allow_html=True)
        rd = pd.DataFrame({
            'Tier':  ['Low', 'Moderate', 'High', 'Critical'],
            'Count': [stats['risk_distribution'].get(t, 0) for t in ['Low', 'Moderate', 'High', 'Critical']],
        })
        fig2 = px.pie(rd, names='Tier', values='Count', hole=0.55,
                       color='Tier', color_discrete_map=RISK_COL)
        fig2.update_traces(textposition='outside', textinfo='label+percent',
                           marker=dict(line=dict(color='white', width=2)))
        fig2.update_layout(**PL, height=260)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    with col3:
        st.markdown('<div class="sh">Attendance tiers</div>', unsafe_allow_html=True)
        am = df['attendance_tier'].value_counts().reindex(
            ['Excellent', 'Good', 'Average', 'Warning', 'Critical']).fillna(0)
        fig3 = px.bar(x=am.values, y=am.index, orientation='h',
                      color=am.values,
                      color_continuous_scale=['#c0392b', '#d35400', '#b7770d', '#1e8449'])
        fig3.update_layout(**PL, height=260, coloraxis_showscale=False,
                           xaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)'),
                           yaxis=dict(showgrid=False,
                                      categoryorder='array',
                                      categoryarray=['Critical', 'Warning', 'Average', 'Good', 'Excellent']))
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    # Charts row 2
    col4, col5 = st.columns([1.6, 1])

    with col4:
        sample_n = min(300, len(df))
        st.markdown(f'<div class="sh">Attendance vs semester marks ({sample_n} sample)</div>', unsafe_allow_html=True)
        if len(df) > 0:
            fig4 = px.scatter(df.sample(sample_n, random_state=1) if len(df) >= sample_n else df,
                              x='attendance', y='semester_marks',
                              color='grade_label', color_discrete_map=GRADE_COL,
                              opacity=0.65,
                              hover_data={'attendance': ':.1f', 'semester_marks': ':.1f', 'name': True})
            fig4.add_vline(x=65, line_dash='dash', line_color='#c0392b',
                           annotation_text='65%', annotation_font_size=10,
                           annotation_font_color='#c0392b')
            fig4.update_layout(font_family="DM Sans,sans-serif", font_color="#8f9bba",
                               plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               margin=dict(l=8, r=8, t=32, b=8),
                               height=280, showlegend=True,
                               legend=dict(title='Grade', orientation='h', y=-0.2, x=0, font_size=11),
                               xaxis=dict(title='Attendance %', gridcolor='rgba(143, 155, 186, 0.1)'),
                               yaxis=dict(title='Semester Marks', gridcolor='rgba(143, 155, 186, 0.1)'))
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

    with col5:
        st.markdown('<div class="sh">Correlation with marks</div>', unsafe_allow_html=True)
        if len(df) > 10:
            corr = df[FEATURES].corrwith(df['semester_marks']).sort_values(ascending=True).round(3)
            fig5 = px.bar(x=corr.values,
                          y=[f.replace('_', ' ').title() for f in corr.index],
                          orientation='h', color=corr.values,
                          color_continuous_scale=['#f5b7b1', '#fdebd0', '#1e8449'])
            fig5.update_layout(**PL, height=280, coloraxis_showscale=False,
                               xaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)', range=[0, 0.7]),
                               yaxis=dict(showgrid=False))
            st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})

    # ── Cross-Department Comparison ──────────────────────────────────────────
    if sel_dept == 'All' and len(all_df) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sh">📊 Cross-Department Comparison</div>', unsafe_allow_html=True)

        dept_sem_filter = all_df.copy()
        if sel_sem != 'All':
            dept_sem_filter = dept_sem_filter[dept_sem_filter['semester'] == int(sel_sem)]

        dept_stats = dept_sem_filter.groupby('department').agg(
            students=('usn', 'count'),
            avg_marks=('semester_marks', 'mean'),
            avg_attendance=('attendance', 'mean'),
            at_risk=('is_at_risk', 'sum'),
        ).round(1).reset_index()

        dc1, dc2 = st.columns(2)

        with dc1:
            fig_dept = px.bar(dept_stats, x='department', y='avg_marks',
                              color='department', color_discrete_map=DEPT_COL,
                              text='avg_marks', title="Avg Semester Marks by Department")
            fig_dept.update_traces(textposition='outside', marker_line_width=0)
            fig_dept.update_layout(**PL, height=280, showlegend=False,
                                   xaxis=dict(showgrid=False, title=''),
                                   yaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)', title='Avg Marks'))
            st.plotly_chart(fig_dept, use_container_width=True, config={'displayModeBar': False})

        with dc2:
            fig_risk = px.bar(dept_stats, x='department', y='at_risk',
                              color='department', color_discrete_map=DEPT_COL,
                              text='at_risk', title="At-Risk Students by Department")
            fig_risk.update_traces(textposition='outside', marker_line_width=0)
            fig_risk.update_layout(**PL, height=280, showlegend=False,
                                   xaxis=dict(showgrid=False, title=''),
                                   yaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)', title='At-Risk Count'))
            st.plotly_chart(fig_risk, use_container_width=True, config={'displayModeBar': False})
