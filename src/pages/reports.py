"""
pages/reports.py — Exploratory Data Analysis (EDA) page.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from config    import DATA_PATH
from data_pro  import run_pipeline
from ml_models import FEATURES
from language  import TEXTS

GRADE_COL = {"A": "#1e8449", "B": "#1a5276", "C": "#b7770d", "D": "#d35400", "F": "#c0392b"}
PL = dict(font_family="DM Sans,sans-serif", font_color="#8f9bba",
          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
          margin=dict(l=8, r=8, t=32, b=8), showlegend=False)


@st.cache_data(show_spinner=False)
def _load():
    return run_pipeline(DATA_PATH)


def render_reports_page():
    T  = TEXTS[st.session_state.language]
    df = _load()

    st.markdown("## Exploratory Data Analysis")
    st.markdown(
        "<div style='color:var(--muted-color,#888);font-size:13px;margin-bottom:20px'>"
        "Distributions · Correlations · Box plots by grade</div>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["📊 Distributions", "🔥 Correlations", "📦 Box Plots"])

    # ── Distributions ─────────────────────────────────────────────────────────
    with tab1:
        all_f = FEATURES + ['semester_marks']
        for i in range(0, len(all_f), 3):
            chunk = all_f[i:i+3]
            cols  = st.columns(3)
            for ci, feat in enumerate(chunk):
                with cols[ci]:
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
        st.info("💡 Attendance is bimodal — clusters below 65 % and above 85 %. "
                "Semester marks are near-normal (mean 140.5). Study hours is flat — almost no predictive signal.")

    # ── Correlations ──────────────────────────────────────────────────────────
    with tab2:
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
            st.info("**Internal marks (0.609)** — strongest predictor.\n\n"
                    "**Study hours (0.017)** — almost zero correlation.\n\n"
                    "Focus interventions on internal assessment performance.")

    # ── Box Plots ─────────────────────────────────────────────────────────────
    with tab3:
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
