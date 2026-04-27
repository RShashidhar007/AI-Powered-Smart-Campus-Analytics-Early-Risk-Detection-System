"""
pages/students.py - At-Risk Students list and filters.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from config      import DATA_PATH, DEPARTMENTS, SEMESTERS, CURRENT_ACADEMIC_YEAR
from data_pro    import run_pipeline, run_pipeline_from_db, get_at_risk_students, upsert_student_data, filter_dataframe
from file_ingest import process_uploaded_file
from language    import TEXTS
from ui_theme import get_page_css, GRADE_COL, RISK_COL, DEPT_COL, PL as _PL, PL, kpi_card as _kpi, section_header as _sh

# Design system

# Colour maps & Plotly Theme



@st.cache_data(show_spinner=False)
def _load():
    year = st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR)
    df = run_pipeline_from_db(year)
    if df.empty:
        df = run_pipeline(DATA_PATH)
    return df

def render_students_page():
    st.markdown(get_page_css(st.session_state.get('theme_mode', 'Dark')), unsafe_allow_html=True)
    T = TEXTS[st.session_state.language]
    full_df = _load()

    # Apply global filters
    sel_dept = st.session_state.get('selected_department', 'All')
    sel_sem  = st.session_state.get('selected_semester', 'All')
    df = filter_dataframe(full_df, sel_dept, sel_sem)
    at_risk = get_at_risk_students(df)

    st.markdown('<div class="page-title">At-Risk Students</div>', unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>"
        "Early warning list - sorted by risk score</div>",
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
    _kpi(s1, len(flt),                                     "Students",       "", "var(--accent)")
    _kpi(s2, int((flt['risk_tier'] == 'Critical').sum()),   "Critical",       "", "var(--accent-red)")
    _kpi(s3, int((flt['risk_tier'] == 'High').sum()),       "High Risk",      "", "var(--accent-amber)")
    _kpi(s4, f"{flt['attendance'].mean():.1f}%" if len(flt) else "-",
         "Avg Attendance", "", "var(--accent-amber)")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    ch1, ch2 = st.columns([1.8, 1])
    with ch1:
        st.markdown('<div class="sh">Risk score distribution</div>', unsafe_allow_html=True)
        if len(at_risk) > 0:
            fh = px.histogram(at_risk, x='risk_score', nbins=10,
                              color_discrete_sequence=['var(--accent)'])
            fh.update_layout(**_PL)
            fh.update_layout(height=200,
                             xaxis=dict(title='Risk Score', showgrid=True),
                             yaxis=dict(title='Students', showgrid=True))
            st.plotly_chart(fh, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

    with ch2:
        st.markdown('<div class="sh">Grade breakdown (at-risk)</div>', unsafe_allow_html=True)
        if len(at_risk) > 0:
            ag = at_risk['grade_label'].value_counts().reindex(['A', 'B', 'C', 'D', 'F']).fillna(0)
            fa = px.bar(x=ag.index, y=ag.values, color=ag.index,
                        color_discrete_map=GRADE_COL, text=ag.values.astype(int))
            fa.update_traces(textposition='outside', marker_line_width=1, marker_line_color='rgba(0,0,0,0.1)')
            fa.update_layout(**_PL)
            fa.update_layout(height=200, xaxis=dict(showgrid=False))
            st.plotly_chart(fa, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")

    # Data table
    st.markdown('<div class="sh">Student list</div>', unsafe_allow_html=True)

    def _tc(v):
        bg = {'Critical': 'rgba(231,76,60,0.2)', 'High': 'rgba(230,126,34,0.2)', 'Moderate': 'rgba(243,156,18,0.2)', 'Low': 'rgba(39,174,96,0.2)'}
        return f'background:{bg.get(v,"transparent")};color:{RISK_COL.get(v,"var(--text-primary)")};font-weight:600;border:1px solid {RISK_COL.get(v,"var(--border)")}'

    def _gc(v):
        bg = {'A': 'rgba(39,174,96,0.2)', 'B': 'rgba(46,134,171,0.2)', 'C': 'rgba(244,162,97,0.2)', 'D': 'rgba(230,126,34,0.2)', 'F': 'rgba(231,76,60,0.2)'}
        return f'background:{bg.get(v,"transparent")};color:{GRADE_COL.get(v,"var(--text-primary)")};font-weight:600;border:1px solid {GRADE_COL.get(v,"var(--border)")}'

    sc = ['usn', 'name', 'department', 'semester', 'attendance', 'internal_marks', 'semester_marks',
          'study_hours', 'risk_score', 'risk_tier', 'grade_label', 'performance_index']
    available_sc = [c for c in sc if c in flt.columns]
    disp = flt[available_sc].copy()

    col_names = {
        'usn': 'USN', 'name': 'Name', 'department': 'Dept', 'semester': 'Sem',
        'attendance': 'Attend %', 'internal_marks': 'Internals',
        'semester_marks': 'Sem Marks', 'study_hours': 'Study Hrs',
        'risk_score': 'Risk Score', 'risk_tier': 'Tier',
        'grade_label': 'Grade', 'performance_index': 'Overall Score',
    }
    disp.columns = [col_names.get(c, c) for c in available_sc]

    fmt_dict = {}
    for c in disp.columns:
        if c in ('Attend %', 'Internals', 'Sem Marks', 'Study Hrs', 'Overall Score'):
            fmt_dict[c] = '{:.1f}'
        elif c == 'Risk Score':
            fmt_dict[c] = '{:.0f}'

    styled = disp.style
    
    # Handle pandas 2.1+ applymap deprecation safely by using .map if available, else .applymap
    map_func = styled.map if hasattr(styled, 'map') else styled.applymap
    
    if 'Tier' in disp.columns:
        styled = map_func(_tc, subset=['Tier'])
    if 'Grade' in disp.columns:
        styled = map_func(_gc, subset=['Grade'])
        
    styled = styled.format(fmt_dict)
    
    if 'Risk Score' in disp.columns:
        styled = styled.bar(subset=['Risk Score'], color='rgba(231,76,60,0.6)', vmin=0, vmax=100)
        
    styled = styled.set_properties(**{'font-size': '12px', 'background-color': 'transparent', 'color': 'var(--text-primary)'})
              
    st.dataframe(styled, use_container_width=True, height=420)
    st.download_button("Download CSV", flt.to_csv(index=False),
                       "at_risk_students.csv", "text/csv")

    # Add New Student
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sh">Add New Student</div>', unsafe_allow_html=True)
    if 'student_added' in st.session_state:
        st.success(st.session_state['student_added'])
        del st.session_state['student_added']

    with st.form("add_student_form", clear_on_submit=True):
        fc1, fc2 = st.columns(2)
        with fc1:
            new_usn  = st.text_input("USN", placeholder="e.g. 1RV21CSE1001")
            new_name = st.text_input("Student Name", placeholder="e.g. Rahul Sharma")
            new_dept = st.selectbox("Department", DEPARTMENTS, index=0)
        with fc2:
            new_sem        = st.selectbox("Semester", SEMESTERS, index=0)
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

        submitted = st.form_submit_button("Add Student", use_container_width=True, type="primary")

        if submitted:
            if not new_usn.strip() or not new_name.strip():
                st.error(" USN and Name are required.")
            else:
                import os
                new_row = pd.DataFrame([{
                    'usn':              new_usn.strip(),
                    'name':             new_name.strip(),
                    'department':       new_dept,
                    'semester':         new_sem,
                    'attendance':       new_attendance,
                    'internal_marks':   new_internal,
                    'assignment_score': new_assignment,
                    'quiz_score':       new_quiz,
                    'lab_marks':        new_lab,
                    'semester_marks':   new_semester,
                    'study_hours':      new_study,
                }])
                # Upsert into CSV (Legacy fallback if needed, but db handled in upsert_student_data)
                upsert_student_data(new_row, DATA_PATH)
                # Clear all cached data so every page picks up the new student
                st.cache_data.clear()
                st.session_state['student_added'] = f" Student **{new_name.strip()}** ({new_usn.strip()}) added to {new_dept} Sem {new_sem}!"
                st.rerun()

    # Upload File
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sh"> Upload Student Data (PDF, CSV, Excel)</div>', unsafe_allow_html=True)
    st.caption("Upload a PDF, CSV, or Excel file containing student details in table format. "
               "The system will auto-detect columns and fill defaults for any missing ones.")

    uploaded_file = st.file_uploader(
        "Choose a file", type=["pdf", "csv", "xlsx", "xls"], key="file_uploader",
        help="The file should contain tables with columns like USN, Name, Department, Semester, Attendance, etc."
    )

    if uploaded_file is not None:
        with st.spinner("Processing file..."):
            extracted_df, status_msg = process_uploaded_file(uploaded_file.read(), uploaded_file.name)

        st.markdown(status_msg)

        if extracted_df is not None and len(extracted_df) > 0:
            st.markdown("**Preview of extracted data:**")
            st.dataframe(extracted_df, use_container_width=True, height=250)

            col_add, col_cancel = st.columns(2)
            with col_add:
                if st.button("Add All to Dataset", use_container_width=True, type="primary",
                             key="pdf_add_btn"):
                    upsert_student_data(extracted_df, DATA_PATH)
                    st.cache_data.clear()
                    st.success(f" **{len(extracted_df)} students** updated/added to the dataset!")
                    st.rerun()
            with col_cancel:
                if st.button("Cancel", use_container_width=True, key="pdf_cancel_btn"):
                    st.rerun()
