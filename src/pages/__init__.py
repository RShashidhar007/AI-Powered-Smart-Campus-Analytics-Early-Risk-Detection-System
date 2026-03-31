"""
pages — Dashboard page renderers.
"""
from pages.home        import render_home_page
from pages.predictions import render_predictions_page
from pages.students    import render_students_page
from pages.reports     import render_reports_page
from pages.settings    import render_settings_page

__all__ = [
    'render_home_page',
    'render_predictions_page',
    'render_students_page',
    'render_reports_page',
    'render_settings_page',
]
