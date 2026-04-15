"""
pages — Dashboard page renderers.
"""
from pages.home              import render_home_page
from pages.predictions       import render_predictions_page
from pages.students          import render_students_page
from pages.reports           import render_reports_page
from pages.settings          import render_settings_page
from pages.year_comparison   import render_year_comparison_page
from pages.student_dashboard import render_student_dashboard

__all__ = [
    'render_home_page',
    'render_predictions_page',
    'render_students_page',
    'render_reports_page',
    'render_settings_page',
    'render_year_comparison_page',
    'render_student_dashboard',
]

