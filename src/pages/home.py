"""
pages/home.py — Campus Overview dashboard page.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from config      import DATA_PATH, DEPARTMENTS, DEPT_FULL_NAMES, CURRENT_ACADEMIC_YEAR
from data_pro    import run_pipeline, run_pipeline_from_db, get_summary_stats, get_at_risk_students, filter_dataframe
from ml_models   import FEATURES
from language    import TEXTS

# ── Cached loader ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _load_all():
    year = st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR)
    df = run_pipeline_from_db(year)
    if df.empty:
        df = run_pipeline(DATA_PATH)
    return df

# ── Colour maps ───────────────────────────────────────────────────────────────
GRADE_COL = {"A": "#27AE60", "B": "#2980B9", "C": "#F39C12", "D": "#E67E22", "F": "#E74C3C"}
RISK_COL  = {"Low": "#27AE60", "Moderate": "#F39C12", "High": "#E67E22", "Critical": "#E74C3C"}
DEPT_COL  = {"CSE": "#0075FF", "ECE": "#E74C3C", "ME": "#F39C12", "CE": "#2CD9FF", "ISE": "#7C3AED"}

# Base plotly layout — matches the glassmorphic UI
_PL = dict(
    font_family="Plus Jakarta Sans, Inter, sans-serif",
    font_color="#A0AEC0",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)


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

    # =====================================================================
    # CHARTS ROW 1 — Gradient Bars + Treemap + Area Chart
    # =====================================================================
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown('<div class="sh">Grade Distribution</div>', unsafe_allow_html=True)
        grades = ['A', 'B', 'C', 'D', 'F']
        counts = [stats['grade_distribution'].get(g, 0) for g in grades]
        colors = [GRADE_COL[g] for g in grades]

        # Clean vertical bars with text
        fig_grade = go.Figure()
        fig_grade.add_trace(go.Bar(
            x=grades, y=counts,
            marker_color=colors,
            marker_line_width=0,
            opacity=0.9,
            text=counts,
            textposition='outside',
            textfont=dict(color='#A0AEC0', size=13, family='Plus Jakarta Sans'),
            hovertemplate="Grade %{x}: %{y} students<extra></extra>",
        ))
        fig_grade.update_layout(
            **_PL, height=300, showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(color='#FFFFFF', size=14, family='Plus Jakarta Sans')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', zeroline=True, zerolinecolor='rgba(255,255,255,0.1)', tickfont=dict(color='#A0AEC0')),
            margin=dict(l=8, r=8, t=20, b=8)
        )
        st.plotly_chart(fig_grade, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown('<div class="sh">Risk Proportions</div>', unsafe_allow_html=True)
        tiers   = ['Low', 'Moderate', 'High', 'Critical']
        rcounts = [stats['risk_distribution'].get(t, 0) for t in tiers]
        
        # Treemap for clear proportion understanding
        fig_risk = go.Figure(go.Treemap(
            labels=tiers,
            parents=[''] * len(tiers),
            values=rcounts,
            textinfo='label+value+percent entry',
            marker_colors=[RISK_COL[t] for t in tiers],
            textfont=dict(size=13, family='Plus Jakarta Sans', color='white'),
            hovertemplate="%{label}: %{value} students<extra></extra>",
            pathbar_visible=False,
            tiling_pad=2,
        ))
        fig_risk.update_layout(**_PL, height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_risk, use_container_width=True, config={'displayModeBar': False})

    with col3:
        st.markdown('<div class="sh">Attendance Tiers</div>', unsafe_allow_html=True)
        att_order = ['Critical', 'Warning', 'Average', 'Good', 'Excellent']
        att_counts = df['attendance_tier'].value_counts().reindex(att_order).fillna(0)
        
        # Smooth area chart showing the distribution curve
        fig_att = go.Figure()
        fig_att.add_trace(go.Scatter(
            x=att_order, y=att_counts.values,
            fill='tozeroy',
            mode='lines+markers',
            line=dict(color='#0075FF', width=3, shape='spline'),
            marker=dict(size=8, color='#2CD9FF', line=dict(width=2, color='#0075FF')),
            fillcolor='rgba(0,117,255,0.15)',
            text=att_counts.values,
            textposition='top center',
            hovertemplate="%{x}: %{y} students<extra></extra>",
        ))
        fig_att.update_layout(
            **_PL, height=300, showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(color='#A0AEC0', size=11, family='Plus Jakarta Sans')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', tickfont=dict(color='#A0AEC0')),
            margin=dict(l=8, r=8, t=20, b=8)
        )
        st.plotly_chart(fig_att, use_container_width=True, config={'displayModeBar': False})


    # =====================================================================
    # CHARTS ROW 2 — Bar Graph
    # =====================================================================
    col4, col5 = st.columns([1, 1])

    with col4:
        st.markdown(f'<div class="sh">Avg Marks by Attendance Tier</div>', unsafe_allow_html=True)
        if len(df) > 0:
            att_order = ['Critical', 'Warning', 'Average', 'Good', 'Excellent']
            tier_marks = df.groupby('attendance_tier')['semester_marks'].mean().reindex(att_order).fillna(0)
            att_colors = ['#E74C3C', '#E67E22', '#F39C12', '#2ECC71', '#27AE60'] 

            fig_bar = go.Figure(go.Bar(
                x=att_order, y=tier_marks.values,
                marker_color=att_colors,
                text=[f"{v:.1f}" if v > 0 else "" for v in tier_marks.values],
                textposition='outside',
                textfont=dict(color='#FFFFFF', size=13, family='Plus Jakarta Sans'),
                hovertemplate="Tier: %{x}<br>Avg Marks: %{y:.1f}<extra></extra>"
            ))
            
            # Threshold line
            fig_bar.add_hline(y=120, line_dash='dash', line_color='rgba(39,174,96,0.8)', annotation_text='Pass (120) ', annotation_position='bottom left', annotation_font_color='#27AE60')

            fig_bar.update_layout(
                **_PL, height=300, showlegend=False,
                xaxis=dict(title='Attendance Tier', showgrid=False, tickfont=dict(color='#A0AEC0', size=12, family='Plus Jakarta Sans')),
                yaxis=dict(title='Average Semester Marks', gridcolor='rgba(255,255,255,0.04)', tickfont=dict(color='#A0AEC0')),
                margin=dict(l=8, r=8, t=20, b=8)
            )
            
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

    with col5:
        st.markdown('<div class="sh">Impact on Final Marks</div>', unsafe_allow_html=True)
        if len(df) > 10:
            corr = df[FEATURES].corrwith(df['semester_marks']).sort_values(ascending=True).round(3)
            labels = [f.replace('_', ' ').title() for f in corr.index]
            vals = corr.values

            # Clean horizontal bars
            fig_corr = go.Figure()
            fig_corr.add_trace(go.Bar(
                x=vals, y=labels,
                orientation='h',
                marker=dict(
                    color=vals,
                    colorscale=[[0, '#E74C3C'], [0.3, '#F39C12'], [0.7, '#2CD9FF'], [1, '#27AE60']],
                ),
                text=[f"{v:.2f}" for v in vals],
                textposition='inside', insidetextanchor='end',
                textfont=dict(color='white', size=11, family='Plus Jakarta Sans'),
                hovertemplate="%{y}: %{x}<extra></extra>",
            ))
            fig_corr.update_layout(
                **_PL, height=300, showlegend=False,
                xaxis=dict(showgrid=False, visible=False, range=[0, max(vals)*1.1]),
                yaxis=dict(showgrid=False, tickfont=dict(color='#FFFFFF', size=12, family='Plus Jakarta Sans')),
                margin=dict(l=8, r=8, t=10, b=8)
            )
            st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False})


    # =====================================================================
    # CHARTS ROW 3 — Department Comparisons (Grouped Bars + Clean Boxplot)
    # =====================================================================
    if sel_dept == 'All' and len(df) > 0:
        col6, col7 = st.columns([1, 1])

        with col6:
            st.markdown('<div class="sh">Department Averages</div>', unsafe_allow_html=True)

            dept_stats = df.groupby('department').agg(
                avg_attendance=('attendance', 'mean'),
                pass_rate=('semester_marks', lambda x: (x >= 120).mean() * 100),
            ).round(1)

            depts = dept_stats.index.tolist()
            
            # Grouped bar chart comparing metrics side by side
            fig_dept = go.Figure()
            fig_dept.add_trace(go.Bar(
                x=depts, y=dept_stats['avg_attendance'],
                name='Attendance %',
                marker_color='#0075FF', opacity=0.85,
            ))
            fig_dept.add_trace(go.Bar(
                x=depts, y=dept_stats['pass_rate'],
                name='Pass Rate %',
                marker_color='#2CD9FF', opacity=0.85,
            ))

            fig_dept.update_layout(
                **_PL, height=300, barmode='group',
                legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center', font=dict(color='#A0AEC0')),
                xaxis=dict(showgrid=False, tickfont=dict(color='#FFFFFF', size=13, family='Plus Jakarta Sans')),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', range=[0, 100], tickfont=dict(color='#A0AEC0')),
                margin=dict(l=8, r=8, t=10, b=40)
            )
            st.plotly_chart(fig_dept, use_container_width=True, config={'displayModeBar': False})

        with col7:
            st.markdown('<div class="sh">Marks Spread by Department</div>', unsafe_allow_html=True)

            # Boxplot for a clean statistical spread
            fig_box = go.Figure()
            for dept in DEPARTMENTS:
                dept_data = df[df['department'] == dept]['semester_marks']
                if len(dept_data) > 0:
                    fig_box.add_trace(go.Box(
                        y=dept_data, name=dept,
                        fillcolor=f"rgba({int(DEPT_COL.get(dept, '#0075FF')[1:3], 16)},{int(DEPT_COL.get(dept, '#0075FF')[3:5], 16)},{int(DEPT_COL.get(dept, '#0075FF')[5:7], 16)}, 0.2)",
                        line=dict(color=DEPT_COL.get(dept, '#0075FF'), width=2),
                        marker=dict(color=DEPT_COL.get(dept, '#0075FF'), size=4),
                        boxpoints='outliers'
                    ))

            fig_box.update_layout(
                **_PL, height=300, showlegend=False,
                xaxis=dict(showgrid=False, tickfont=dict(color='#FFFFFF', size=13, family='Plus Jakarta Sans')),
                yaxis=dict(
                    title='Semester Marks', gridcolor='rgba(255,255,255,0.04)',
                    tickfont=dict(color='#A0AEC0'),
                ),
                margin=dict(l=8, r=8, t=10, b=8)
            )
            st.plotly_chart(fig_box, use_container_width=True, config={'displayModeBar': False})
