"""
pages/home.py - Campus Overview dashboard page.
"""
import streamlit as st
import plotly.graph_objects as go

from config import DATA_PATH, DEPARTMENTS, DEPT_FULL_NAMES, CURRENT_ACADEMIC_YEAR
from data_pro import (
    run_pipeline,
    run_pipeline_from_db,
    get_summary_stats,
    filter_dataframe,
)
from ml_models import FEATURES
from ui_theme import get_page_css, GRADE_COL, RISK_COL, DEPT_COL, PL as _PL, kpi_card as _kpi


HOME_CSS = """
<style>
.home-topline {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 18px;
}
.home-context {
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 8px 12px;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: rgba(51, 65, 85, 0.55);
    white-space: nowrap;
}
.home-section-title {
    color: var(--text-primary);
    font-size: 16px;
    font-weight: 800;
    margin: 24px 0 6px;
}
.home-section-subtitle {
    color: var(--text-muted);
    font-size: 13px;
    margin: 0 0 14px;
}
.home-alert {
    border-radius: 14px;
    padding: 14px 18px;
    margin: 2px 0 18px;
    font-size: 14px;
    font-weight: 600;
}
.home-alert-danger {
    color: #FCA5A5;
    background: rgba(191, 97, 106, 0.16);
    border: 1px solid rgba(191, 97, 106, 0.38);
}
.home-alert-ok {
    color: #BBF7D0;
    background: rgba(129, 199, 132, 0.12);
    border: 1px solid rgba(129, 199, 132, 0.32);
}
@media (max-width: 900px) {
    .home-topline {
        display: block;
    }
    .home-context {
        display: inline-block;
        margin-top: 10px;
        white-space: normal;
    }
}
</style>
"""


@st.cache_data(show_spinner=False)
def _load_all():
    year = st.session_state.get("selected_academic_year", CURRENT_ACADEMIC_YEAR)
    df = run_pipeline_from_db(year)
    if df.empty:
        df = run_pipeline(DATA_PATH)
    return df


def _chart_title(title: str):
    st.markdown(f'<div class="sh">{title}</div>', unsafe_allow_html=True)


def _section(title: str, subtitle: str):
    st.markdown(
        f'<div class="home-section-title">{title}</div>'
        f'<div class="home-section-subtitle">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def _standard_layout(fig: go.Figure, height: int = 320, legend: bool = False) -> go.Figure:
    fig.update_layout(**_PL)
    fig.update_layout(
        height=height,
        showlegend=legend,
        margin=dict(l=12, r=12, t=18, b=12),
        font=dict(size=12),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(148,163,184,0.24)")
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.14)",
        zeroline=True,
        zerolinecolor="rgba(148,163,184,0.2)",
    )
    return fig


def _attendance_colors(order: list[str]) -> list[str]:
    tier_to_risk = {
        "Excellent": "Low",
        "Good": "Low",
        "Average": "Moderate",
        "Warning": "High",
        "Critical": "Critical",
    }
    return [RISK_COL[tier_to_risk[tier]] for tier in order]


def render_home_page():
    st.markdown(get_page_css(st.session_state.get('theme_mode', 'Dark')), unsafe_allow_html=True)
    st.markdown(HOME_CSS, unsafe_allow_html=True)

    all_df = _load_all()
    sel_dept = st.session_state.get("selected_department", "All")
    sel_sem = st.session_state.get("selected_semester", "All")
    df = filter_dataframe(all_df, sel_dept, sel_sem)
    stats = get_summary_stats(df)

    filter_parts = [
        DEPT_FULL_NAMES.get(sel_dept, sel_dept) if sel_dept != "All" else "All Departments",
        f"Semester {sel_sem}" if sel_sem != "All" else "All Semesters",
    ]

    total_students = stats["total_students"]
    at_risk_count = stats["at_risk_count"]
    crit_n = int((df["risk_tier"] == "Critical").sum()) if len(df) else 0
    avg_marks = df["semester_marks"].mean() if len(df) else 0
    avg_att = df["attendance"].mean() if len(df) else 0
    pass_rate = (df["semester_marks"] >= 120).mean() * 100 if len(df) else 0
    risk_share = at_risk_count / max(total_students, 1) * 100

    st.markdown(
        f"""
        <div class="home-topline">
            <div>
                <div class="page-title">Campus Overview</div>
                <div class="page-subtitle">Real-time academic risk analytics for {total_students} students</div>
            </div>
            <div class="home-context">{" | ".join(filter_parts)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if crit_n > 0:
        st.markdown(
            f'<div class="home-alert home-alert-danger"><b>{crit_n} critical-risk students</b> need immediate review. '
            f'{risk_share:.1f}% of the filtered cohort is currently high or critical risk.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="home-alert home-alert-ok">No critical-risk students in the current filtered view.</div>',
            unsafe_allow_html=True,
        )

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    _kpi(c1, total_students, "Students", f"{len(DEPARTMENTS)} departments", "var(--accent)")
    _kpi(c2, at_risk_count, "At Risk", f"{risk_share:.1f}% of cohort", "var(--accent-red)", highlight=True)
    _kpi(c3, crit_n, "Critical", "immediate review", "var(--accent-red)")
    _kpi(c4, f"{avg_marks:.1f}" if len(df) else "-", "Avg Marks", "out of 200", "var(--accent-teal)")
    _kpi(c5, f"{avg_att:.1f}%" if len(df) else "-", "Avg Attend", "threshold 65%", "var(--accent-amber)")
    _kpi(c6, f"{pass_rate:.1f}%" if len(df) else "-", "Pass Rate", "marks >= 120", "var(--accent-light)")

    _section("Risk And Performance", "A quick view of academic outcomes and intervention priority.")
    left, center = st.columns([1, 1])

    with left:
        _chart_title("Risk Proportions")
        risk_tiers = ["Low", "Moderate", "High", "Critical"]
        risk_counts = [stats["risk_distribution"].get(t, 0) for t in risk_tiers]
        fig_risk = go.Figure(go.Pie(
            labels=risk_tiers,
            values=risk_counts,
            hole=0.62,
            textinfo="label+percent",
            marker_colors=[RISK_COL[t] for t in risk_tiers],
            marker_line_width=2,
            marker_line_color="rgba(30,41,59,0.9)",
            hovertemplate="<b>%{label}</b><br>%{value} students<extra></extra>",
        ))
        _standard_layout(fig_risk, height=330)
        fig_risk.update_layout(margin=dict(l=0, r=0, t=4, b=0))
        st.plotly_chart(fig_risk, use_container_width=True, config={"displayModeBar": False}, theme=None)

    with center:
        _chart_title("Grade Distribution")
        grades = ["A", "B", "C", "D", "F"]
        grade_counts = [stats["grade_distribution"].get(g, 0) for g in grades]
        fig_grade = go.Figure(go.Bar(
            x=grades,
            y=grade_counts,
            marker_color=[GRADE_COL[g] for g in grades],
            marker_line_width=1,
            marker_line_color="rgba(255,255,255,0.12)",
            text=grade_counts,
            textposition="outside",
            hovertemplate="<b>Grade %{x}</b><br>%{y} students<extra></extra>",
        ))
        _standard_layout(fig_grade, height=330)
        fig_grade.update_yaxes(title_text="Students")
        st.plotly_chart(fig_grade, use_container_width=True, config={"displayModeBar": False}, theme=None)

    _section("Attendance Insights", "Attendance tiers connected with student count and mark outcomes.")
    att_left, att_right = st.columns([1, 1])

    with att_left:
        _chart_title("Attendance Tiers")
        att_order = ["Excellent", "Good", "Average", "Warning", "Critical"]
        att_counts = df["attendance_tier"].value_counts().reindex(att_order).fillna(0)
        fig_att = go.Figure(go.Bar(
            x=att_order,
            y=att_counts.values,
            marker_color=_attendance_colors(att_order),
            marker_line_width=1,
            marker_line_color="rgba(255,255,255,0.12)",
            text=att_counts.values,
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y} students<extra></extra>",
        ))
        _standard_layout(fig_att, height=320)
        fig_att.update_xaxes(title_text="Attendance Tier")
        fig_att.update_yaxes(title_text="Students")
        st.plotly_chart(fig_att, use_container_width=True, config={"displayModeBar": False}, theme=None)

    with att_right:
        _chart_title("Avg Marks By Attendance Tier")
        mark_order = ["Critical", "Warning", "Average", "Good", "Excellent"]
        fig_marks = go.Figure()
        if len(df):
            tier_marks = df.groupby("attendance_tier")["semester_marks"].mean().reindex(mark_order).fillna(0)
            fig_marks.add_trace(go.Bar(
                x=mark_order,
                y=tier_marks.values,
                marker_color=_attendance_colors(mark_order),
                marker_line_width=1,
                marker_line_color="rgba(255,255,255,0.12)",
                text=[f"{v:.1f}" if v > 0 else "" for v in tier_marks.values],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Avg marks: %{y:.1f}<extra></extra>",
            ))
            fig_marks.add_hline(
                y=120,
                line_dash="dash",
                line_color=RISK_COL["Low"],
                annotation_text="Pass line",
                annotation_position="bottom left",
                annotation_font_color=RISK_COL["Low"],
            )
        _standard_layout(fig_marks, height=320)
        fig_marks.update_xaxes(title_text="Attendance Tier")
        fig_marks.update_yaxes(title_text="Average Marks")
        st.plotly_chart(fig_marks, use_container_width=True, config={"displayModeBar": False}, theme=None)

    _section("Academic Drivers", "Feature correlation and department-level comparisons.")
    driver_left, driver_right = st.columns([1, 1])

    with driver_left:
        _chart_title("Impact On Final Marks")
        fig_corr = go.Figure()
        if len(df) > 10:
            # Convert correlation to a 0-100% "Impact Strength" scale for easier understanding
            corr = df[FEATURES].corrwith(df["semester_marks"]).sort_values(ascending=True)
            vals = (corr * 100).round(1).values
            labels = [f.replace("_", " ").title() for f in corr.index]
            
            fig_corr.add_trace(go.Bar(
                x=vals,
                y=labels,
                orientation="h",
                marker=dict(
                    color=vals,
                    colorscale=[
                        [0, RISK_COL["Critical"]],
                        [0.35, RISK_COL["High"]],
                        [0.65, RISK_COL["Moderate"]],
                        [1, RISK_COL["Low"]],
                    ],
                    line=dict(width=1, color="rgba(255,255,255,0.12)"),
                ),
                text=[f"{v:.1f}%" for v in vals],
                textposition="inside",
                insidetextanchor="end",
                hovertemplate="<b>%{y}</b><br>Impact Strength: %{x}%<extra></extra>",
            ))
            fig_corr.update_xaxes(range=[min(vals.min() * 1.15, -5), max(vals.max() * 1.15, 5)])
        _standard_layout(fig_corr, height=330)
        fig_corr.update_xaxes(title_text="Impact Strength (%)")
        fig_corr.update_yaxes(showgrid=False)
        st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False}, theme=None)

    with driver_right:
        _chart_title("Department Averages")
        fig_dept = go.Figure()
        if sel_dept == "All" and len(df):
            dept_stats = df.groupby("department").agg(
                avg_attendance=("attendance", "mean"),
                pass_rate=("semester_marks", lambda x: (x >= 120).mean() * 100),
            ).round(1)
            depts = dept_stats.index.tolist()
            fig_dept.add_trace(go.Bar(
                x=depts,
                y=dept_stats["avg_attendance"],
                name="Attendance %",
                marker_color=RISK_COL["Moderate"],
                marker_line_width=1,
                marker_line_color="rgba(255,255,255,0.12)",
            ))
            fig_dept.add_trace(go.Bar(
                x=depts,
                y=dept_stats["pass_rate"],
                name="Pass Rate %",
                marker_color=RISK_COL["Low"],
                marker_line_width=1,
                marker_line_color="rgba(255,255,255,0.12)",
            ))
        _standard_layout(fig_dept, height=330, legend=True)
        fig_dept.update_layout(
            barmode="group",
            bargap=0.18,
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        )
        fig_dept.update_yaxes(title_text="Percent", range=[0, 100])
        st.plotly_chart(fig_dept, use_container_width=True, config={"displayModeBar": False}, theme="streamlit")

    if sel_dept == "All" and len(df) > 0:
        _chart_title("Marks Spread By Department")
        fig_box = go.Figure()
        for dept in DEPARTMENTS:
            dept_data = df[df["department"] == dept]["semester_marks"]
            if len(dept_data) > 0:
                hex_col = DEPT_COL.get(dept, "#81A1C1").lstrip("#")
                r, g, b = tuple(int(hex_col[i:i + 2], 16) for i in (0, 2, 4))
                fig_box.add_trace(go.Box(
                    y=dept_data,
                    name=dept,
                    fillcolor=f"rgba({r},{g},{b},0.24)",
                    line=dict(color=f"rgba({r},{g},{b},1)", width=2),
                    marker=dict(color=f"rgba({r},{g},{b},1)", size=4),
                    boxpoints="outliers",
                    hovertemplate=f"<b>{dept}</b><br>Marks: %{{y}}<extra></extra>",
                ))
        _standard_layout(fig_box, height=320)
        fig_box.update_yaxes(title_text="Semester Marks")
        st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar": False}, theme="streamlit")
