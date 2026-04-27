"""
pages/year_comparison.py - Year-over-Year comparison dashboard.

Compares current year data with a previous year, showing delta KPIs,
side-by-side charts, and student-level improvement tracking.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config   import CURRENT_ACADEMIC_YEAR, DEPARTMENTS, DEPT_FULL_NAMES
from data_pro import run_pipeline_from_db, filter_dataframe, get_summary_stats
from database import get_available_years
from language import TEXTS
from ui_theme import get_page_css, GRADE_COL, RISK_COL, DEPT_COL, PL as _PL, PL, kpi_card as _kpi, section_header as _sh

# Design system

# Colour maps & Plotly Theme


def _delta_kpi(col, label, curr_val, prev_val, suffix="", fmt=".1f",
               invert=False):
    """Render a KPI card with delta comparison.

    invert=True means a decrease is good (e.g., at-risk %).
    """
    if prev_val is not None and prev_val != 0:
        delta = curr_val - prev_val
        pct   = (delta / abs(prev_val)) * 100
        is_good = (delta < 0) if invert else (delta > 0)
        arrow = "up" if delta > 0 else "down" if delta < 0 else "-"
        color = "var(--accent-teal)" if is_good else "var(--accent-red)" if not is_good and delta != 0 else "#888"
        delta_str = f'<span style="color:{color};font-size:13px">{arrow} {abs(delta):{fmt}}{suffix} ({abs(pct):.1f}%)</span>'
    else:
        delta_str = '<span style="color:#888;font-size:12px">No prev. data</span>'

    col.markdown(
        f'<div class="kpi">'
        f'<div class="kv" style="color:#0075FF">{curr_val:{fmt}}{suffix}</div>'
        f'<div class="kl">{label}</div>'
        f'<div style="margin-top:4px">{delta_str}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def render_year_comparison_page():
    st.markdown(get_page_css(st.session_state.get('theme_mode', 'Dark')), unsafe_allow_html=True)
    
    T  = TEXTS[st.session_state.language]
    years = get_available_years()

    st.markdown(f'<div class="page-title">{T.get("yoy_title", "Year-over-Year Comparison")}</div>', unsafe_allow_html=True)
    st.markdown(
        f"<div class='page-subtitle'>"
        f"{T.get('yoy_subtitle', 'Compare academic performance across years - Identify trends - Track improvements')}</div>",
        unsafe_allow_html=True,
    )

    if len(years) < 2:
        st.warning("At least **two academic years** of data are needed for comparison. "
                    "Currently available: " + (", ".join(years) if years else "none"))
        st.info("Use the migration script or add data for another year to enable comparisons.")
        return

    # Year Selectors
    yc1, yc2, yc3 = st.columns([1, 1, 2])
    with yc1:
        curr_year = st.selectbox(T.get('curr_year', "Current Year"), years,
                                 index=years.index(CURRENT_ACADEMIC_YEAR)
                                 if CURRENT_ACADEMIC_YEAR in years else len(years) - 1)
    with yc2:
        prev_options = [y for y in years if y != curr_year]
        prev_year = st.selectbox(T.get('comp_year', "Compare With"), prev_options,
                                 index=0 if prev_options else 0)

    # Apply sidebar filters
    sel_dept = st.session_state.get('selected_department', 'All')
    sel_sem  = st.session_state.get('selected_semester', 'All')

    # Load data for both years
    @st.cache_data(show_spinner=False)
    def _load_year(year):
        return run_pipeline_from_db(year)

    curr_df_full = _load_year(curr_year)
    prev_df_full = _load_year(prev_year)

    if curr_df_full.empty or prev_df_full.empty:
        st.error("One or both years have no data. Cannot compare.")
        return

    curr_df = filter_dataframe(curr_df_full, sel_dept, sel_sem)
    prev_df = filter_dataframe(prev_df_full, sel_dept, sel_sem)

    curr_stats = get_summary_stats(curr_df) if len(curr_df) > 0 else {}
    prev_stats = get_summary_stats(prev_df) if len(prev_df) > 0 else {}

    # Filter label
    filter_parts = []
    if sel_dept != 'All':
        filter_parts.append(DEPT_FULL_NAMES.get(sel_dept, sel_dept))
    if sel_sem != 'All':
        filter_parts.append(f"Semester {sel_sem}")
    filter_str = " - ".join(filter_parts) if filter_parts else "All Departments - All Semesters"

    st.markdown(
        f"<div style='color:var(--muted-color,#A0AEC0);font-size:12px;margin-bottom:16px'>"
        f"{filter_str} - Comparing <b>{curr_year}</b> vs <b>{prev_year}</b></div>",
        unsafe_allow_html=True,
    )

    # Delta KPI Cards
    k1, k2, k3, k4, k5 = st.columns(5)

    c_total = curr_stats.get('total_students', 0)
    p_total = prev_stats.get('total_students', 0)
    _delta_kpi(k1, "Total Students", c_total, p_total, fmt="d")

    c_risk_pct = (curr_stats.get('at_risk_count', 0) / max(c_total, 1)) * 100
    p_risk_pct = (prev_stats.get('at_risk_count', 0) / max(p_total, 1)) * 100
    _delta_kpi(k2, "At-Risk %", c_risk_pct, p_risk_pct, suffix="%", invert=True)

    c_avg = curr_df['semester_marks'].mean() if len(curr_df) > 0 else 0
    p_avg = prev_df['semester_marks'].mean() if len(prev_df) > 0 else 0
    _delta_kpi(k3, "Avg Marks", c_avg, p_avg)

    c_att = curr_df['attendance'].mean() if len(curr_df) > 0 else 0
    p_att = prev_df['attendance'].mean() if len(prev_df) > 0 else 0
    _delta_kpi(k4, "Avg Attendance", c_att, p_att, suffix="%")

    c_pass = (curr_df['semester_marks'] >= 120).mean() * 100 if len(curr_df) > 0 else 0
    p_pass = (prev_df['semester_marks'] >= 120).mean() * 100 if len(prev_df) > 0 else 0
    _delta_kpi(k5, "Pass Rate", c_pass, p_pass, suffix="%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Side-by-Side Charts
    tab_grade, tab_risk, tab_dept, tab_students = st.tabs([
        T.get("tab_y_grade", "Grade Distribution"), 
        T.get("tab_y_risk", "Risk Tiers"),
        T.get("tab_y_dept", "Department Comparison"), 
        T.get("tab_y_student", "Student Tracking")
    ])

    # Grade Distribution
    with tab_grade:
        grades = ['A', 'B', 'C', 'D', 'F']
        c_gdist = curr_stats.get('grade_distribution', {})
        p_gdist = prev_stats.get('grade_distribution', {})

        grade_df = pd.DataFrame({
            'Grade': grades * 2,
            'Count': [c_gdist.get(g, 0) for g in grades] + [p_gdist.get(g, 0) for g in grades],
            'Year':  [curr_year] * 5 + [prev_year] * 5,
        })

        fig = px.bar(grade_df, x='Grade', y='Count', color='Year',
                     barmode='group', text='Count',
                     color_discrete_sequence=['var(--accent)', 'var(--accent-light)'],
                     title=f"Grade Distribution - {curr_year} vs {prev_year}")
        fig.update_traces(textposition='outside', marker_line_width=0)
        fig.update_layout(**_PL)
        fig.update_layout(height=340, showlegend=True,
                          legend=dict(orientation='h', y=-0.15, font_size=11),
                          xaxis=dict(showgrid=False),
                          yaxis=dict(showgrid=True))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, theme=None)

        # Insight text
        curr_a = c_gdist.get('A', 0)
        prev_a = p_gdist.get('A', 0)
        if curr_a > prev_a:
            st.success(f"Grade A students increased from **{prev_a}** to **{curr_a}** (+{curr_a - prev_a})")
        elif curr_a < prev_a:
            st.warning(f"Grade A students decreased from **{prev_a}** to **{curr_a}** ({curr_a - prev_a})")

    # Risk Tier Comparison
    with tab_risk:
        tiers = ['Low', 'Moderate', 'High', 'Critical']
        c_rdist = curr_stats.get('risk_distribution', {})
        p_rdist = prev_stats.get('risk_distribution', {})

        risk_df = pd.DataFrame({
            'Tier':  tiers * 2,
            'Count': [c_rdist.get(t, 0) for t in tiers] + [p_rdist.get(t, 0) for t in tiers],
            'Year':  [curr_year] * 4 + [prev_year] * 4,
        })

        fig2 = px.bar(risk_df, x='Tier', y='Count', color='Year',
                      barmode='group', text='Count',
                      color_discrete_sequence=['var(--accent-red)', 'var(--accent-amber)'],
                      title=f"Risk Tier Distribution - {curr_year} vs {prev_year}")
        fig2.update_traces(textposition='outside', marker_line_width=0)
        fig2.update_layout(**_PL)
        fig2.update_layout(height=340, showlegend=True,
                           legend=dict(orientation='h', y=-0.15, font_size=11),
                           xaxis=dict(showgrid=False,
                                      categoryorder='array',
                                      categoryarray=tiers),
                           yaxis=dict(showgrid=True))
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False}, theme=None)

        c_crit = c_rdist.get('Critical', 0)
        p_crit = p_rdist.get('Critical', 0)
        if c_crit < p_crit:
            st.success(f"Critical-risk students decreased from **{p_crit}** to **{c_crit}**")
        elif c_crit > p_crit:
            st.error(f"Critical-risk students increased from **{p_crit}** to **{c_crit}**")

    # Department Comparison
    with tab_dept:
        if sel_dept == 'All':
            dept_curr = curr_df.groupby('department').agg(
                avg_marks=('semester_marks', 'mean'),
                avg_attendance=('attendance', 'mean'),
                at_risk_pct=('is_at_risk', 'mean'),
            ).round(2).reset_index()
            dept_curr['at_risk_pct'] = (dept_curr['at_risk_pct'] * 100).round(1)
            dept_curr['Year'] = curr_year

            dept_prev = prev_df.groupby('department').agg(
                avg_marks=('semester_marks', 'mean'),
                avg_attendance=('attendance', 'mean'),
                at_risk_pct=('is_at_risk', 'mean'),
            ).round(2).reset_index()
            dept_prev['at_risk_pct'] = (dept_prev['at_risk_pct'] * 100).round(1)
            dept_prev['Year'] = prev_year

            dept_combined = pd.concat([dept_curr, dept_prev], ignore_index=True)

            dc1, dc2 = st.columns(2)
            with dc1:
                fig3 = px.bar(dept_combined, x='department', y='avg_marks',
                              color='Year', barmode='group', text='avg_marks',
                              color_discrete_sequence=['var(--accent)', 'var(--accent-light)'],
                              title="Avg Marks by Department")
                fig3.update_traces(textposition='outside', texttemplate='%{text:.1f}')
                fig3.update_layout(**_PL)
                fig3.update_layout(height=320, showlegend=True,
                                   legend=dict(orientation='h', y=-0.2, font_size=10),
                                   xaxis=dict(showgrid=False, title=''),
                                   yaxis=dict(showgrid=True, title='Avg Marks'))
                st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False}, theme=None)

            with dc2:
                fig4 = px.bar(dept_combined, x='department', y='at_risk_pct',
                              color='Year', barmode='group', text='at_risk_pct',
                              color_discrete_sequence=['var(--accent-red)', 'var(--accent-amber)'],
                              title="At-Risk % by Department")
                fig4.update_traces(textposition='outside', texttemplate='%{text:.1f}%')
                fig4.update_layout(**_PL)
                fig4.update_layout(height=320, showlegend=True,
                                   legend=dict(orientation='h', y=-0.2, font_size=10),
                                   xaxis=dict(showgrid=False, title=''),
                                   yaxis=dict(showgrid=True, title='At-Risk %'))
                st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False}, theme=None)

            # Summary Table
            st.markdown("#### Department Trend Summary")
            trend_data = []
            for dept in DEPARTMENTS:
                c_row = dept_curr[dept_curr['department'] == dept]
                p_row = dept_prev[dept_prev['department'] == dept]
                c_marks = c_row['avg_marks'].values[0] if len(c_row) else 0
                p_marks = p_row['avg_marks'].values[0] if len(p_row) else 0
                c_risk  = c_row['at_risk_pct'].values[0] if len(c_row) else 0
                p_risk  = p_row['at_risk_pct'].values[0] if len(p_row) else 0
                trend_data.append({
                    'Department': dept,
                    f'Avg Marks ({prev_year})': round(p_marks, 1),
                    f'Avg Marks ({curr_year})': round(c_marks, 1),
                    'Marks Delta': round(c_marks - p_marks, 1),
                    f'At-Risk% ({prev_year})': round(p_risk, 1),
                    f'At-Risk% ({curr_year})': round(c_risk, 1),
                    'Risk Delta': round(c_risk - p_risk, 1),
                })
            trend_df = pd.DataFrame(trend_data)
            st.dataframe(
                trend_df.style
                    .background_gradient(cmap='RdYlGn', subset=['Marks Delta'])
                    .background_gradient(cmap='RdYlGn_r', subset=['Risk Delta'])
                    .format({col: '{:.1f}' for col in trend_df.columns if col != 'Department'}),
                use_container_width=True,
            )
        else:
            st.info(f"Showing comparison for **{DEPT_FULL_NAMES.get(sel_dept, sel_dept)}** only. "
                    "Select 'All Departments' in the sidebar to see cross-department charts.")

            # Single dept comparison
            metrics = ['attendance', 'internal_marks', 'assignment_score',
                       'quiz_score', 'lab_marks', 'semester_marks']
            c_means = curr_df[metrics].mean().round(2)
            p_means = prev_df[metrics].mean().round(2) if len(prev_df) > 0 else pd.Series(dtype=float)

            compare_data = []
            for m in metrics:
                cv = c_means.get(m, 0)
                pv = p_means.get(m, 0) if len(p_means) > 0 else 0
                compare_data.append({
                    'Metric': m.replace('_', ' ').title(),
                    prev_year: round(pv, 1),
                    curr_year: round(cv, 1),
                    'Change': round(cv - pv, 1),
                })
            cdf = pd.DataFrame(compare_data)
            st.dataframe(
                cdf.style.background_gradient(cmap='RdYlGn', subset=['Change'])
                    .format({prev_year: '{:.1f}', curr_year: '{:.1f}', 'Change': '{:+.1f}'}),
                use_container_width=True,
            )

    # Student-Level Tracking
    with tab_students:
        st.markdown(f"#### {T.get('student_imp', 'Student Improvement Tracking')}")
        st.markdown(
            f"<div style='color:var(--muted-color,#A0AEC0);font-size:13px;margin-bottom:12px'>"
            f"{T.get('student_imp_sub', 'Students present in both years - who improved the most and who declined')}</div>",
            unsafe_allow_html=True,
        )

        # Find common students
        if 'usn' in curr_df.columns and 'usn' in prev_df.columns:
            common_usns = set(curr_df['usn'].values) & set(prev_df['usn'].values)

            if len(common_usns) > 0:
                c_common = curr_df[curr_df['usn'].isin(common_usns)][
                    ['usn', 'name', 'department', 'semester_marks', 'attendance', 'risk_score']
                ].set_index('usn')
                p_common = prev_df[prev_df['usn'].isin(common_usns)][
                    ['usn', 'semester_marks', 'attendance', 'risk_score']
                ].set_index('usn')

                merged = c_common.join(p_common, lsuffix='_curr', rsuffix='_prev')
                merged['marks_change'] = merged['semester_marks_curr'] - merged['semester_marks_prev']
                merged['attendance_change'] = merged['attendance_curr'] - merged['attendance_prev']
                merged['risk_change'] = merged['risk_score_curr'] - merged['risk_score_prev']
                merged = merged.reset_index()

                st.metric("Students tracked across both years", len(common_usns))

                # Top improvers and decliners
                imp_col, dec_col = st.columns(2)

                with imp_col:
                    st.markdown('<div class="sh"> Top 10 Improvers (by marks)</div>',
                                unsafe_allow_html=True)
                    top_imp = merged.nlargest(10, 'marks_change')[
                        ['usn', 'name', 'department', 'semester_marks_prev',
                         'semester_marks_curr', 'marks_change']
                    ].copy()
                    top_imp.columns = ['USN', 'Name', 'Dept',
                                       f'Marks ({prev_year})', f'Marks ({curr_year})', 'Delta']
                    styled_imp = top_imp.style.background_gradient(
                        cmap='Greens', subset=['Delta']
                    ).format({f'Marks ({prev_year})': '{:.1f}',
                              f'Marks ({curr_year})': '{:.1f}', 'Delta': '{:+.1f}'})
                    st.dataframe(styled_imp, use_container_width=True, height=380)

                with dec_col:
                    st.markdown('<div class="sh"> Top 10 Decliners (by marks)</div>',
                                unsafe_allow_html=True)
                    top_dec = merged.nsmallest(10, 'marks_change')[
                        ['usn', 'name', 'department', 'semester_marks_prev',
                         'semester_marks_curr', 'marks_change']
                    ].copy()
                    top_dec.columns = ['USN', 'Name', 'Dept',
                                       f'Marks ({prev_year})', f'Marks ({curr_year})', 'Delta']
                    styled_dec = top_dec.style.background_gradient(
                        cmap='Reds', subset=['Delta']
                    ).format({f'Marks ({prev_year})': '{:.1f}',
                              f'Marks ({curr_year})': '{:.1f}', 'Delta': '{:+.1f}'})
                    st.dataframe(styled_dec, use_container_width=True, height=380)

                # Summary insight
                improved = (merged['marks_change'] > 0).sum()
                declined = (merged['marks_change'] < 0).sum()
                no_change = (merged['marks_change'] == 0).sum()
                
                # Distribution of changes (Simplified to Bar Chart)
                st.markdown('<div class="sh">Overall Student Progress</div>',
                            unsafe_allow_html=True)
                            
                progress_df = pd.DataFrame({
                    'Status': ['Improved', 'Unchanged', 'Declined'],
                    'Students': [improved, no_change, declined]
                })
                
                fig_prog = px.bar(
                    progress_df, x='Status', y='Students', 
                    color='Status', color_discrete_map={'Improved':'#81C784', 'Unchanged':'#90A4AE', 'Declined':'#E57373'},
                    text='Students'
                )
                fig_prog.update_traces(textposition='outside')
                fig_prog.update_layout(**_PL)
                fig_prog.update_layout(height=280, showlegend=False, xaxis_title="", yaxis_title="Number of Students")
                st.plotly_chart(fig_prog, use_container_width=True, config={'displayModeBar': False}, theme=None)

                st.markdown(
                    f"**Summary**: Out of **{len(common_usns)}** tracked students, "
                    f"**{improved}** improved, **{declined}** declined, and "
                    f"**{no_change}** saw no change in their marks."
                )
            else:
                st.info("No common students found between the two years.")
        else:
            st.warning("USN column not found in data - cannot track individual students.")
