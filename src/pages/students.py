"""
pages/students.py — At-Risk Students list and filters.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from config      import DATA_PATH
from data_pro    import run_pipeline, get_at_risk_students
from pdf_ingest  import extract_tables_from_pdf
from language    import TEXTS

GRADE_COL = {"A": "#1e8449", "B": "#1a5276", "C": "#b7770d", "D": "#d35400", "F": "#c0392b"}
RISK_COL  = {"Low": "#1e8449", "Moderate": "#b7770d", "High": "#d35400", "Critical": "#c0392b"}
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


@st.cache_data(show_spinner=False)
def _load():
    df      = run_pipeline(DATA_PATH)
    at_risk = get_at_risk_students(df)
    return df, at_risk


def render_students_page():
    T = TEXTS[st.session_state.language]
    df, at_risk = _load()

    st.markdown("## At-Risk Students")
    st.markdown(
        "<div style='color:var(--muted-color,#888);font-size:13px;margin-bottom:20px'>"
        "Early warning list · sorted by risk score</div>",
        unsafe_allow_html=True,
    )

    # Filters
    f1, f2, _ = st.columns([1, 1, 2])
    tf = f1.selectbox("Risk Tier", ["All", "Critical", "High", "Moderate", "Low"])
    gf = f2.selectbox("Grade",     ["All", "A", "B", "C", "D", "F"])

    flt = at_risk.copy()
    if tf != "All":
        flt = flt[flt['risk_tier'] == tf]
    if gf != "All":
        flt = flt[flt['grade_label'] == gf]

    # Summary KPIs
    s1, s2, s3, s4 = st.columns(4)
    _kpi(s1, len(flt),                                     "Students",       "", "#5b5ef4")
    _kpi(s2, int((flt['risk_tier'] == 'Critical').sum()),   "Critical",       "", "#c0392b")
    _kpi(s3, int((flt['risk_tier'] == 'High').sum()),       "High Risk",      "", "#d35400")
    _kpi(s4, f"{flt['attendance'].mean():.1f}%" if len(flt) else "—",
         "Avg Attendance", "", "#b7770d")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    ch1, ch2 = st.columns([1.8, 1])
    with ch1:
        st.markdown('<div class="sh">Risk score distribution</div>', unsafe_allow_html=True)
        fh = px.histogram(at_risk, x='risk_score', nbins=10,
                          color_discrete_sequence=['#5b5ef4'])
        fh.update_layout(**PL, height=200,
                         xaxis=dict(title='Risk Score', gridcolor='rgba(143, 155, 186, 0.1)'),
                         yaxis=dict(title='Students', gridcolor='rgba(143, 155, 186, 0.1)'))
        st.plotly_chart(fh, use_container_width=True, config={'displayModeBar': False})

    with ch2:
        st.markdown('<div class="sh">Grade breakdown (at-risk)</div>', unsafe_allow_html=True)
        ag = at_risk['grade_label'].value_counts().reindex(['A', 'B', 'C', 'D', 'F']).fillna(0)
        fa = px.bar(x=ag.index, y=ag.values, color=ag.index,
                    color_discrete_map=GRADE_COL, text=ag.values.astype(int))
        fa.update_traces(textposition='outside', marker_line_width=0)
        fa.update_layout(**PL, height=200,
                         xaxis=dict(showgrid=False), yaxis=dict(gridcolor='rgba(143, 155, 186, 0.1)'))
        st.plotly_chart(fa, use_container_width=True, config={'displayModeBar': False})

    # Data table
    st.markdown('<div class="sh">Student list</div>', unsafe_allow_html=True)

    def _tc(v):
        bg = {'Critical': '#fde8e8', 'High': '#fef0e0', 'Moderate': '#fef9e0', 'Low': '#e8f8f0'}
        fg = {'Critical': '#c0392b', 'High': '#d35400', 'Moderate': '#b7770d', 'Low': '#1e8449'}
        return f'background:{bg.get(v,"#fff")};color:{fg.get(v,"#333")};font-weight:600'

    def _gc(v):
        bg = {'A': '#e8f8f0', 'B': '#e8f2fc', 'C': '#fef9e0', 'D': '#fef0e0', 'F': '#fde8e8'}
        return f'background:{bg.get(v,"#fff")};color:{GRADE_COL.get(v,"#333")};font-weight:600'

    sc = ['usn', 'name', 'attendance', 'internal_marks', 'semester_marks',
          'study_hours', 'risk_score', 'risk_tier', 'grade_label', 'performance_index']
    disp = flt[sc].copy()
    disp.columns = ['USN', 'Name', 'Attend %', 'Internals', 'Sem Marks',
                    'Study Hrs', 'Risk Score', 'Tier', 'Grade', 'Perf Index']
    styled = (disp.style
              .applymap(_tc, subset=['Tier'])
              .applymap(_gc, subset=['Grade'])
              .format({'Attend %': '{:.1f}', 'Internals': '{:.1f}', 'Sem Marks': '{:.1f}',
                       'Study Hrs': '{:.1f}', 'Risk Score': '{:.0f}', 'Perf Index': '{:.1f}'})
              .bar(subset=['Risk Score'], color='#fde8e8', vmin=0, vmax=100)
              .set_properties(**{'font-size': '12px'}))
    st.dataframe(styled, use_container_width=True, height=420)
    st.download_button("⬇ Download CSV", flt.to_csv(index=False),
                       "at_risk_students.csv", "text/csv")

    # ── Add New Student ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sh">➕ Add New Student</div>', unsafe_allow_html=True)

    with st.form("add_student_form", clear_on_submit=True):
        fc1, fc2 = st.columns(2)
        with fc1:
            new_usn  = st.text_input("USN", placeholder="e.g. 1RV21CS501")
            new_name = st.text_input("Student Name", placeholder="e.g. Rahul Sharma")
        with fc2:
            new_attendance = st.number_input("Attendance %", 0.0, 100.0, 75.0, 0.5)
            new_internal   = st.number_input("Internal Marks (0-50)", 0.0, 50.0, 30.0, 0.5)

        fc3, fc4, fc5 = st.columns(3)
        with fc3:
            new_assignment = st.number_input("Assignment Score (0-50)", 0.0, 50.0, 35.0, 0.5)
            new_quiz       = st.number_input("Quiz Score (0-50)", 0.0, 50.0, 30.0, 0.5)
        with fc4:
            new_lab        = st.number_input("Lab Marks (0-50)", 0.0, 50.0, 35.0, 0.5)
            new_semester   = st.number_input("Semester Marks (0-200)", 0.0, 200.0, 140.0, 0.5)
        with fc5:
            new_study      = st.number_input("Study Hours/Day", 0.0, 10.0, 3.0, 0.1)

        submitted = st.form_submit_button("✅ Add Student", use_container_width=True, type="primary")

        if submitted:
            if not new_usn.strip() or not new_name.strip():
                st.error("❌ USN and Name are required.")
            else:
                import os
                new_row = pd.DataFrame([{
                    'usn':              new_usn.strip(),
                    'name':             new_name.strip(),
                    'attendance':       new_attendance,
                    'internal_marks':   new_internal,
                    'assignment_score': new_assignment,
                    'quiz_score':       new_quiz,
                    'lab_marks':        new_lab,
                    'semester_marks':   new_semester,
                    'study_hours':      new_study,
                }])
                # Append to CSV
                new_row.to_csv(DATA_PATH, mode='a', header=False, index=False)
                # Clear all cached data so every page picks up the new student
                st.cache_data.clear()
                st.success(f"✅ Student **{new_name.strip()}** ({new_usn.strip()}) added successfully!")
                st.rerun()

    # ── Upload PDF ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sh">📄 Upload Student Data (PDF)</div>', unsafe_allow_html=True)
    st.caption("Upload a PDF containing student details in table format. "
               "The system will auto-detect columns and fill defaults for any missing ones.")

    uploaded_pdf = st.file_uploader(
        "Choose a PDF file", type=["pdf"], key="pdf_uploader",
        help="The PDF should contain tables with columns like USN, Name, Attendance, etc."
    )

    if uploaded_pdf is not None:
        with st.spinner("Extracting tables from PDF…"):
            extracted_df, status_msg = extract_tables_from_pdf(uploaded_pdf.read())

        st.markdown(status_msg)

        if extracted_df is not None and len(extracted_df) > 0:
            st.markdown("**Preview of extracted data:**")
            st.dataframe(extracted_df, use_container_width=True, height=250)

            col_add, col_cancel = st.columns(2)
            with col_add:
                if st.button("✅ Add All to Dataset", use_container_width=True, type="primary",
                             key="pdf_add_btn"):
                    extracted_df.to_csv(DATA_PATH, mode='a', header=False, index=False)
                    st.cache_data.clear()
                    st.success(f"✅ **{len(extracted_df)} students** added to the dataset!")
                    st.rerun()
            with col_cancel:
                if st.button("❌ Cancel", use_container_width=True, key="pdf_cancel_btn"):
                    st.rerun()
