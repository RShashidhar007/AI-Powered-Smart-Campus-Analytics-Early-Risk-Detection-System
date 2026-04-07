"""
Smart Campus Analytics - PDF Report Generator
Professional executive-ready PDF report using ReportLab.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable

# ── Colors ────────────────────────────────────────────────────────────────────
DARK_BLUE   = colors.HexColor('#1F4E79')
MID_BLUE    = colors.HexColor('#2E75B6')
LIGHT_BLUE  = colors.HexColor('#DEEAF1')
GREEN       = colors.HexColor('#27AE60')
LIGHT_GREEN = colors.HexColor('#D5F5E3')
RED         = colors.HexColor('#E74C3C')
LIGHT_RED   = colors.HexColor('#FADBD8')
ORANGE      = colors.HexColor('#E67E22')
LIGHT_ORANGE= colors.HexColor('#FDEBD0')
YELLOW      = colors.HexColor('#F4D03F')
LIGHT_YELLOW= colors.HexColor('#FEF9E7')
GRAY        = colors.HexColor('#7F8C8D')
LIGHT_GRAY  = colors.HexColor('#F8F9FA')
BLACK       = colors.black
WHITE       = colors.white

RISK_COLORS = {
    'Low':      (GREEN,  LIGHT_GREEN),
    'Moderate': (ORANGE, LIGHT_YELLOW),
    'High':     (ORANGE, LIGHT_ORANGE),
    'Critical': (RED,    LIGHT_RED),
}
GRADE_BG = {
    'A': LIGHT_GREEN, 'B': LIGHT_BLUE, 'C': LIGHT_YELLOW,
    'D': LIGHT_ORANGE, 'F': LIGHT_RED
}


def _get_styles():
    base = getSampleStyleSheet()
    custom = {
        'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=24,
                                textColor=WHITE, alignment=TA_CENTER, spaceAfter=4),
        'subtitle': ParagraphStyle('subtitle', fontName='Helvetica', fontSize=13,
                                   textColor=LIGHT_BLUE, alignment=TA_CENTER, spaceAfter=8),
        'h1': ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=15,
                             textColor=DARK_BLUE, spaceBefore=16, spaceAfter=8,
                             borderPad=4),
        'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=12,
                             textColor=MID_BLUE, spaceBefore=10, spaceAfter=5),
        'body': ParagraphStyle('body', fontName='Helvetica', fontSize=10,
                               textColor=colors.HexColor('#2C3E50'),
                               leading=15, spaceAfter=5),
        'small': ParagraphStyle('small', fontName='Helvetica', fontSize=8,
                                textColor=GRAY, spaceAfter=3),
        'bold_body': ParagraphStyle('bold_body', fontName='Helvetica-Bold', fontSize=10,
                                    textColor=BLACK, spaceAfter=4),
        'kpi_val': ParagraphStyle('kpi_val', fontName='Helvetica-Bold', fontSize=22,
                                  textColor=MID_BLUE, alignment=TA_CENTER),
        'kpi_label': ParagraphStyle('kpi_label', fontName='Helvetica', fontSize=8,
                                    textColor=GRAY, alignment=TA_CENTER),
        'footer': ParagraphStyle('footer', fontName='Helvetica', fontSize=8,
                                 textColor=GRAY, alignment=TA_CENTER),
        'table_header': ParagraphStyle('table_header', fontName='Helvetica-Bold',
                                       fontSize=9, textColor=WHITE, alignment=TA_CENTER),
        'table_cell': ParagraphStyle('table_cell', fontName='Helvetica',
                                     fontSize=9, alignment=TA_CENTER),
    }
    return custom


def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = letter
    # Header bar
    canvas.setFillColor(DARK_BLUE)
    canvas.rect(0, h - 0.55*inch, w, 0.55*inch, fill=1, stroke=0)
    canvas.setFont('Helvetica-Bold', 9)
    canvas.setFillColor(WHITE)
    canvas.drawString(0.5*inch, h - 0.35*inch, 'AI-Powered Smart Campus Analytics & Early Risk Detection System')
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(w - 0.5*inch, h - 0.35*inch, 'CONFIDENTIAL  |  Internal Use Only')
    # Footer
    canvas.setFillColor(LIGHT_GRAY)
    canvas.rect(0, 0, w, 0.45*inch, fill=1, stroke=0)
    canvas.setFillColor(MID_BLUE)
    canvas.rect(0, 0.43*inch, w, 0.02*inch, fill=1, stroke=0)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(GRAY)
    dept_label = getattr(doc, '_dept_label', 'All Departments')
    canvas.drawString(0.5*inch, 0.17*inch, f'Smart Campus Analytics System  |  {dept_label}')
    canvas.drawRightString(w - 0.5*inch, 0.17*inch, f'Page {doc.page}')
    canvas.restoreState()


def _section_title(title, styles):
    items = [
        HRFlowable(width='100%', thickness=3, color=MID_BLUE, spaceAfter=6),
        Paragraph(title, styles['h1']),
    ]
    return items


def _kpi_table(df, styles):
    total     = len(df)
    at_risk   = int(df['is_at_risk'].sum())
    critical  = int((df['risk_tier'] == 'Critical').sum())
    avg_marks = df['semester_marks'].mean()
    avg_att   = df['attendance'].mean()
    grade_a   = int((df['grade_label'] == 'A').sum())

    kpis = [
        (str(total),          'Total Students',      MID_BLUE),
        (str(at_risk),        'At-Risk Students',    RED),
        (str(critical),       'Critical Risk',       colors.HexColor('#C0392B')),
        (f'{avg_marks:.1f}',  'Avg Semester Marks',  GREEN),
        (f'{avg_att:.1f}%',   'Avg Attendance',      ORANGE),
        (str(grade_a),        'Grade A Students',    colors.HexColor('#8E44AD')),
    ]

    cells = []
    for val, label, color in kpis:
        cells.append([
            Paragraph(f'<font color="{color.hexval() if hasattr(color,"hexval") else "#2E75B6"}">{val}</font>',
                      styles['kpi_val']),
            Paragraph(label, styles['kpi_label']),
        ])

    # Split into 2 rows of 3
    row1 = [[cells[i][0], cells[i][1]] for i in range(3)]
    row2 = [[cells[i][0], cells[i][1]] for i in range(3, 6)]

    def _mini_row(row):
        tbl = Table([[c[0] for c in row], [c[1] for c in row]],
                    colWidths=[2.2*inch]*3)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY),
            ('BOX', (0,0), (-1,-1), 1, MID_BLUE),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_GRAY, WHITE]),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        return tbl

    return [_mini_row(row1), Spacer(1, 6), _mini_row(row2)]


def _risk_table(df, styles):
    data = [['Risk Tier', 'Count', 'Percentage', 'Required Action']]
    actions = {
        'Low':      'No action — monitor regularly',
        'Moderate': 'Faculty advisory recommended',
        'High':     'Mandatory counselling & attendance review',
        'Critical': 'IMMEDIATE intervention required',
    }
    for tier in ['Low', 'Moderate', 'High', 'Critical']:
        cnt = int((df['risk_tier'] == tier).sum())
        pct = cnt / len(df) * 100
        data.append([tier, str(cnt), f'{pct:.1f}%', actions[tier]])

    tbl = Table(data, colWidths=[1.2*inch, 0.8*inch, 1.0*inch, 3.8*inch])
    color_map = {'Low': LIGHT_GREEN, 'Moderate': LIGHT_YELLOW,
                 'High': LIGHT_ORANGE, 'Critical': LIGHT_RED}
    style = [
        ('BACKGROUND', (0,0), (-1,0), DARK_BLUE),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',      (3,1), (3,-1), 'LEFT'),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('ROWHEIGHT',  (0,0), (-1,-1), 20),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]
    for r, tier in enumerate(['Low', 'Moderate', 'High', 'Critical'], 1):
        style.append(('BACKGROUND', (0,r), (-1,r), color_map[tier]))
        fg, _ = RISK_COLORS[tier]
        style.append(('TEXTCOLOR', (0,r), (0,r), fg))
        style.append(('FONTNAME',  (0,r), (0,r), 'Helvetica-Bold'))
    tbl.setStyle(TableStyle(style))
    return tbl


def _grade_table(df, styles):
    ranges = {'A': '165–200', 'B': '150–165', 'C': '135–150', 'D': '120–135', 'F': '<120'}
    data = [['Grade', 'Count', 'Percentage', 'Marks Range']]
    for grade in ['A', 'B', 'C', 'D', 'F']:
        cnt = int((df['grade_label'] == grade).sum())
        pct = cnt / len(df) * 100
        data.append([grade, str(cnt), f'{pct:.1f}%', ranges[grade]])
    tbl = Table(data, colWidths=[1.0*inch, 1.0*inch, 1.2*inch, 1.5*inch])
    style = [
        ('BACKGROUND', (0,0), (-1,0), DARK_BLUE),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('ROWHEIGHT',  (0,0), (-1,-1), 20),
    ]
    bg_map = {'A': LIGHT_GREEN, 'B': LIGHT_BLUE, 'C': LIGHT_YELLOW, 'D': LIGHT_ORANGE, 'F': LIGHT_RED}
    for r, grade in enumerate(['A', 'B', 'C', 'D', 'F'], 1):
        style.append(('BACKGROUND', (0,r), (-1,r), bg_map[grade]))
        style.append(('FONTNAME',   (0,r), (0,r), 'Helvetica-Bold'))
    tbl.setStyle(TableStyle(style))
    return tbl


def _ml_table(reg_results, clf_results, styles):
    data = [['Model Type', 'Model Name', 'Key Metric', 'Score', 'Status']]
    for name, m in reg_results.items():
        status = 'Best' if m['R2'] == max(x['R2'] for x in reg_results.values()) else ''
        data.append(['Regression', name, 'R² Score', f"{m['R2']:.4f}", status])
    for name, m in clf_results.items():
        status = 'Best' if m['Accuracy'] == max(x['Accuracy'] for x in clf_results.values()) else ''
        data.append(['Classification', name, 'Accuracy', f"{m['Accuracy']*100:.1f}%", status])

    tbl = Table(data, colWidths=[1.3*inch, 1.8*inch, 1.1*inch, 1.0*inch, 0.8*inch])
    style = [
        ('BACKGROUND', (0,0), (-1,0), DARK_BLUE),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_GRAY, WHITE]),
        ('ROWHEIGHT',  (0,0), (-1,-1), 20),
    ]
    for i, row in enumerate(data[1:], 1):
        if row[4] == 'Best':
            style.append(('BACKGROUND', (0,i), (-1,i), LIGHT_GREEN))
            style.append(('FONTNAME', (0,i), (-1,i), 'Helvetica-Bold'))
    tbl.setStyle(TableStyle(style))
    return tbl


def _at_risk_table(df, styles):
    at_risk = df[df['is_at_risk'] == 1].sort_values('risk_score', ascending=False).head(20)
    data = [['USN', 'Name', 'Attend%', 'Internal', 'Sem.Marks', 'Risk Score', 'Tier', 'Grade']]
    for _, row in at_risk.iterrows():
        data.append([
            row['usn'], row['name'][:18],
            f"{row['attendance']:.1f}%", f"{row['internal_marks']:.1f}",
            f"{row['semester_marks']:.1f}", str(int(row['risk_score'])),
            row['risk_tier'], row['grade_label'],
        ])
    tbl = Table(data, colWidths=[1.0*inch, 1.5*inch, 0.7*inch, 0.7*inch, 0.85*inch, 0.8*inch, 0.75*inch, 0.6*inch])
    style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#8B0000')),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',      (1,1), (1,-1), 'LEFT'),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('ROWHEIGHT',  (0,0), (-1,-1), 18),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]
    tier_bg = {'Critical': LIGHT_RED, 'High': LIGHT_ORANGE}
    for i, (_, row) in enumerate(at_risk.iterrows(), 1):
        bg = tier_bg.get(row['risk_tier'], LIGHT_GRAY)
        style.append(('BACKGROUND', (0,i), (-1,i), bg))
    tbl.setStyle(TableStyle(style))
    return tbl


def generate_pdf_report(df, reg_results, clf_results, clustering_result,
                        chart_dir, output_path, **kwargs):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    styles = _get_styles()

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=0.6*inch, rightMargin=0.6*inch,
        topMargin=0.75*inch, bottomMargin=0.65*inch,
    )
    # Store dept_label on doc so the footer can access it
    doc._dept_label = kwargs.get('dept_label', 'All Departments')

    story = []

    # ── Cover Page ──
    story.append(Spacer(1, 0.8*inch))
    cover_data = [[Paragraph('AI-Powered Smart Campus Analytics', styles['title']),
                   Paragraph('& Early Risk Detection System', styles['title'])]]
    cover_bg = Table([[Paragraph('AI-Powered Smart Campus Analytics<br/>&amp; Early Risk Detection System',
                                  ParagraphStyle('ct', fontName='Helvetica-Bold', fontSize=22,
                                                 textColor=WHITE, alignment=TA_CENTER))]],
                     colWidths=[7.0*inch], rowHeights=[1.4*inch])
    cover_bg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_BLUE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        ('ROUNDEDCORNERS', [8]),
    ]))
    story.append(cover_bg)
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph('Executive Analytics Report', styles['subtitle']))

    # Dynamic department/semester info
    dept_label = kwargs.get('dept_label', 'All Departments')
    total_students = len(df)
    story.append(Paragraph(f'{dept_label}  |  {total_students} Students  |  2026',
                            ParagraphStyle('meta', fontName='Helvetica', fontSize=10,
                                           textColor=GRAY, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width='100%', thickness=2, color=MID_BLUE))
    story.append(Spacer(1, 0.2*inch))

    # ── Section 1: KPIs ──
    story += _section_title('1. Key Performance Indicators', styles)
    story += _kpi_table(df, styles)
    story.append(Spacer(1, 0.2*inch))

    # Charts
    def _add_chart(fname, caption, w=6.8, h=3.6):
        path = os.path.join(chart_dir, fname)
        if os.path.exists(path):
            img = Image(path, width=w*inch, height=h*inch)
            story.append(img)
            story.append(Paragraph(f'<i>{caption}</i>', styles['small']))
            story.append(Spacer(1, 0.12*inch))

    _add_chart('kpi_summary.png', 'Figure 1: KPI Summary Dashboard', h=2.2)

    # ── Section 2: Grade & Risk ──
    story += _section_title('2. Grade & Risk Distribution', styles)
    story.append(Paragraph('2.1 Grade Distribution', styles['h2']))
    story.append(_grade_table(df, styles))
    story.append(Spacer(1, 0.15*inch))
    _add_chart('grade_distribution.png', 'Figure 2: Student Grade Distribution', h=3.2)

    story.append(Paragraph('2.2 Risk Tier Distribution', styles['h2']))
    story.append(_risk_table(df, styles))
    story.append(Spacer(1, 0.15*inch))
    _add_chart('risk_distribution.png', 'Figure 3: Risk Tier Distribution', h=2.8)

    # ── Section 3: EDA ──
    story.append(PageBreak())
    story += _section_title('3. Exploratory Data Analysis', styles)
    _add_chart('distributions.png', 'Figure 4: Feature Distributions Across All Students', h=3.5)
    _add_chart('correlation_heatmap.png', 'Figure 5: Correlation Matrix — Academic Features', h=3.8)
    _add_chart('attendance_vs_marks.png', 'Figure 6: Attendance vs Semester Marks (colored by Risk Score)', h=3.2)
    _add_chart('study_hours_vs_marks.png', 'Figure 7: Study Hours vs Semester Marks by Grade', h=3.2)
    _add_chart('boxplots_by_grade.png', 'Figure 8: Feature Distribution by Grade Group', h=3.0)

    # ── Section 4: ML Results ──
    story.append(PageBreak())
    story += _section_title('4. Machine Learning Model Results', styles)
    story.append(Paragraph('4.1 Model Performance Summary', styles['h2']))
    story.append(_ml_table(reg_results, clf_results, styles))
    story.append(Spacer(1, 0.15*inch))
    _add_chart('model_comparison.png', 'Figure 9: Model Performance Comparison', h=3.0)
    _add_chart('regression_results.png', 'Figure 10: Regression Results — Actual vs Predicted', h=3.0)
    _add_chart('confusion_matrix.png', 'Figure 11: Classification Confusion Matrix (Best Model)', h=3.0)
    _add_chart('feature_importance_regression.png', 'Figure 12: Feature Importance — Regression', h=2.8)
    _add_chart('feature_importance_classification.png', 'Figure 13: Feature Importance — Classification', h=2.8)

    # ── Section 5: Clustering ──
    story.append(PageBreak())
    story += _section_title('5. Student Clustering & Personas', styles)
    story.append(Paragraph(
        f'K-Means clustering identified <b>{clustering_result["k"]} distinct student groups</b> '
        f'based on attendance, marks, study hours, and assignment performance.',
        styles['body']
    ))
    story.append(Spacer(1, 0.1*inch))
    _add_chart('clusters.png', 'Figure 14: Student Clustering Analysis', h=3.2)

    profile = clustering_result['cluster_profiles'].copy()
    profile = profile.loc[:, ~profile.columns.duplicated()]
    data = [['Cluster Name', 'Avg Attendance', 'Avg Semester Marks', 'Avg Study Hrs', 'Count']]
    sizes = clustering_result['cluster_sizes']
    for _, row in profile.iterrows():
        cnt = sizes.get(row['cluster_name'], 0)
        data.append([row['cluster_name'],
                     f"{float(row['attendance']):.1f}%", f"{float(row['semester_marks']):.1f}",
                     f"{float(row['study_hours']):.2f}h", str(cnt)])
    tbl = Table(data, colWidths=[2.0*inch, 1.3*inch, 1.6*inch, 1.2*inch, 0.8*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_BLUE),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_GRAY, WHITE]),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('ROWHEIGHT',  (0,0), (-1,-1), 20),
    ]))
    story.append(tbl)

    # ── Section 6: At-Risk Students ──
    story.append(PageBreak())
    story += _section_title('6. At-Risk Students — Early Warning List', styles)
    at_risk_count = int(df['is_at_risk'].sum())
    critical_count = int((df['risk_tier'] == 'Critical').sum())
    story.append(Paragraph(
        f'<b>{at_risk_count} students</b> are currently flagged as at-risk '
        f'(<b>{critical_count} Critical</b>). The table below shows the top 20 by risk score. '
        f'Full details are available in the Excel report.',
        styles['body']
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(_at_risk_table(df, styles))

    # ── Section 7: Recommendations ──
    story.append(PageBreak())
    story += _section_title('7. Recommendations & Action Plan', styles)
    recs = [
        ('Immediate Interventions', [
            f'Contact all {critical_count} Critical-risk students and their guardians immediately.',
            'Assign dedicated academic mentors to High and Critical risk students.',
            'Review attendance records for students below 65% — initiate attendance improvement plan.',
        ]),
        ('Faculty Actions', [
            'Conduct weekly attendance spot-checks for at-risk groups.',
            'Introduce supplementary tutorial sessions for students with internal marks below 25.',
            'Share personalized performance reports with students after mid-semester.',
        ]),
        ('System Improvements', [
            'Integrate this analytics system with the college ERP for real-time monitoring.',
            'Retrain ML models each semester with updated data for improved accuracy.',
            'Build a student-facing dashboard to allow self-monitoring of risk scores.',
        ]),
        ('Long-Term Strategy', [
            'Use clustering persona profiles to design targeted learning programs.',
            'Track intervention outcomes to measure the system\'s effectiveness.',
            'Expand dataset with library usage, hostel data, and attendance trends over time.',
        ]),
    ]
    for title, points in recs:
        story.append(Paragraph(title, styles['h2']))
        for p in points:
            story.append(Paragraph(f'• {p}', styles['body']))
        story.append(Spacer(1, 0.1*inch))

    # ── Footer note ──
    story.append(HRFlowable(width='100%', thickness=1, color=MID_BLUE))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        'This report was generated automatically by the Smart Campus Analytics System. '
        f'All ML models were trained and evaluated on {len(df)} student records across '
        f'5 departments and 4 semesters. For queries, contact the Analytics Team.',
        styles['footer']
    ))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return output_path
