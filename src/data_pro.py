import pandas as pd
import numpy as np

from database import load_students, upsert_students as db_upsert
from config import CURRENT_ACADEMIC_YEAR

GRADE_THRESHOLDS = {
    'A': (165, 200),
    'B': (150, 165),
    'C': (135, 150),
    'D': (120, 135),
    'F': (0,   120),
}
RISK_WEIGHTS = {
    'attendance':       {'threshold': 65,  'weight': 30},
    'internal_marks':   {'threshold': 25,  'weight': 25},
    'semester_marks':   {'threshold': 120, 'weight': 25},
    'study_hours':      {'threshold': 2.0, 'weight': 10},
    'assignment_score': {'threshold': 25,  'weight': 10},
}
RISK_TIERS = [
    (0,  20,  'Low',      '#27AE60'),
    (21, 45,  'Moderate', '#F39C12'),
    (46, 70,  'High',     '#E67E22'),
    (71, 100, 'Critical', '#E74C3C'),
]


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()
    numeric_cols = ['attendance', 'internal_marks', 'assignment_score',
                    'quiz_score', 'lab_marks', 'semester_marks', 'study_hours']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    # Ensure department and semester columns exist
    if 'department' not in df.columns:
        df['department'] = 'CSE'
    if 'semester' not in df.columns:
        df['semester'] = 1
    df['semester'] = pd.to_numeric(df['semester'], errors='coerce').fillna(1).astype(int)

    return df.reset_index(drop=True)


def assign_grade(marks: float) -> str:
    for grade, (lo, hi) in GRADE_THRESHOLDS.items():
        if lo <= marks < hi:
            return grade
    return 'F'


def assign_attendance_tier(att: float) -> str:
    if att >= 85:
        return 'Excellent'
    elif att >= 75:
        return 'Good'
    elif att >= 65:
        return 'Average'
    elif att >= 50:
        return 'Warning'
    return 'Critical'


def compute_risk_score(row: pd.Series) -> int:
    score = 0
    for col, cfg in RISK_WEIGHTS.items():
        if col in row and row[col] < cfg['threshold']:
            score += cfg['weight']
    return min(score, 100)


def assign_risk_tier(score: int) -> str:
    for lo, hi, tier, _ in RISK_TIERS:
        if lo <= score <= hi:
            return tier
    return 'Critical'


def compute_performance_index(row: pd.Series) -> float:
    """Composite index (0–100) from all academic features."""
    att_norm   = min(row['attendance'] / 100, 1.0) * 20
    int_norm   = min(row['internal_marks'] / 50, 1.0) * 20
    asgn_norm  = min(row['assignment_score'] / 50, 1.0) * 15
    quiz_norm  = min(row['quiz_score'] / 50, 1.0) * 15
    lab_norm   = min(row['lab_marks'] / 50, 1.0) * 15
    sem_norm   = min(row['semester_marks'] / 200, 1.0) * 15
    return round(att_norm + int_norm + asgn_norm + quiz_norm + lab_norm + sem_norm, 2)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['grade_label']        = df['semester_marks'].apply(assign_grade)
    df['attendance_tier']    = df['attendance'].apply(assign_attendance_tier)
    df['risk_score']         = df.apply(compute_risk_score, axis=1)
    df['risk_tier']          = df['risk_score'].apply(assign_risk_tier)
    df['performance_index']  = df.apply(compute_performance_index, axis=1)
    df['total_continuous']   = df['internal_marks'] + df['assignment_score'] + df['quiz_score'] + df['lab_marks']
    df['is_at_risk']         = (df['risk_tier'].isin(['High', 'Critical'])).astype(int)
    return df


def filter_dataframe(df: pd.DataFrame, department: str = 'All', semester: str = 'All') -> pd.DataFrame:
    """Filter dataframe by department and/or semester."""
    filtered = df.copy()
    if department != 'All':
        filtered = filtered[filtered['department'] == department]
    if semester != 'All':
        filtered = filtered[filtered['semester'] == int(semester)]
    return filtered.reset_index(drop=True)


def get_summary_stats(df: pd.DataFrame) -> dict:
    numeric = ['attendance', 'internal_marks', 'assignment_score',
               'quiz_score', 'lab_marks', 'semester_marks', 'study_hours']
    stats = df[numeric].describe().round(2).to_dict()
    stats['grade_distribution'] = df['grade_label'].value_counts().to_dict()
    stats['risk_distribution']  = df['risk_tier'].value_counts().to_dict()
    stats['at_risk_count']      = int(df['is_at_risk'].sum())
    stats['total_students']     = len(df)
    if 'department' in df.columns:
        stats['dept_distribution'] = df['department'].value_counts().to_dict()
    return stats


def get_at_risk_students(df: pd.DataFrame) -> pd.DataFrame:
    cols = ['usn', 'name', 'department', 'semester', 'attendance', 'internal_marks',
            'semester_marks', 'study_hours', 'risk_score', 'risk_tier',
            'grade_label', 'performance_index']
    available = [c for c in cols if c in df.columns]
    return (df[df['is_at_risk'] == 1][available]
            .sort_values('risk_score', ascending=False)
            .reset_index(drop=True))


def run_pipeline(csv_path: str) -> pd.DataFrame:
    df = load_data(csv_path)
    df = clean_data(df)
    df = engineer_features(df)
    return df


def run_pipeline_from_db(academic_year: str | None = None) -> pd.DataFrame:
    """Load student data from SQLite, clean, and engineer features.

    If academic_year is None, loads the current year from config.
    Pass academic_year='ALL' to load every year (useful for comparisons).
    """
    if academic_year == 'ALL':
        df = load_students(academic_year=None)
    else:
        year = academic_year or CURRENT_ACADEMIC_YEAR
        df = load_students(academic_year=year)

    if len(df) == 0:
        return pd.DataFrame()

    df = clean_data(df)
    df = engineer_features(df)
    return df


def upsert_student_data(new_df: pd.DataFrame, csv_path: str,
                        academic_year: str | None = None):
    """Upsert new student data into both CSV and SQLite.

    Drops any existing rows whose USN appears in new_df, then appends new_df.
    Also writes to the SQLite database for the given academic year.
    """
    import os

    existing_df = pd.read_csv(csv_path)
    existing_df.columns = [c.strip().lower().replace(' ', '_') for c in existing_df.columns]

    # Normalise the new data columns too
    new_df = new_df.copy()
    new_df.columns = [c.strip().lower().replace(' ', '_') for c in new_df.columns]

    # Ensure department and semester columns exist
    if 'department' not in new_df.columns:
        new_df['department'] = 'CSE'
    if 'semester' not in new_df.columns:
        new_df['semester'] = 1

    # Remove rows from existing that will be replaced by new_df
    incoming_usns = set(new_df['usn'].astype(str).str.strip())
    mask = ~existing_df['usn'].astype(str).str.strip().isin(incoming_usns)
    updated_df = pd.concat([existing_df[mask], new_df], ignore_index=True)

    # Drop any lingering duplicates (keep the last occurrence = the newest data)
    updated_df = updated_df.drop_duplicates(subset='usn', keep='last').reset_index(drop=True)

    updated_df.to_csv(csv_path, index=False)

    # Also persist to SQLite
    year = academic_year or CURRENT_ACADEMIC_YEAR
    try:
        db_upsert(new_df, year)
    except Exception as e:
        print(f"[WARN] SQLite upsert failed (CSV still updated): {e}")
