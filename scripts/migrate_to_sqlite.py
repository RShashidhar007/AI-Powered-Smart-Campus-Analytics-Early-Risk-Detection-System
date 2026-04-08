"""
migrate_to_sqlite.py — Migrate CSV data to the unified SQLite students table.

Steps:
  1. Drop legacy tables (current_students, previous_students) if present.
  2. Create the new unified `students` table.
  3. Import all CSV rows as academic_year = '2025-26'.
  4. Generate synthetic previous-year data (2024-25) by adding noise.
  5. Print summary.
"""
import os
import sys
import sqlite3
import numpy as np
import pandas as pd

# Allow imports from src/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from database import DB_PATH, get_connection, init_db, upsert_students, get_available_years

CSV_PATH = os.path.join(BASE_DIR, 'data', 'student_data.csv')
CURRENT_YEAR  = '2025-26'
PREVIOUS_YEAR = '2024-25'


def _drop_legacy_tables(conn: sqlite3.Connection):
    """Drop the old tables from the prior partial migration attempt."""
    for table in ('current_students', 'previous_students', 'students'):
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    print("  [OK] Dropped legacy tables")


def _load_csv() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    print(f"  [OK] Loaded CSV: {len(df)} rows")
    return df


def _generate_previous_year(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Create synthetic previous-year data by applying gaussian noise.

    - Numeric academic fields get ±5-15% noise so there are visible but
      realistic differences between years.
    - Some students are randomly dropped (simulating different cohort sizes).
    """
    rng = np.random.default_rng(seed)
    prev = df.copy()

    # Add noise to numeric columns
    noise_cols = {
        'attendance':       {'mean': -2, 'std': 5,  'min': 0, 'max': 100},
        'internal_marks':   {'mean': -1, 'std': 4,  'min': 0, 'max': 50},
        'assignment_score': {'mean': -1, 'std': 3,  'min': 0, 'max': 50},
        'quiz_score':       {'mean':  0, 'std': 4,  'min': 0, 'max': 50},
        'lab_marks':        {'mean': -1, 'std': 3,  'min': 0, 'max': 50},
        'semester_marks':   {'mean': -5, 'std': 12, 'min': 0, 'max': 200},
        'study_hours':      {'mean':  0, 'std': 0.5,'min': 0, 'max': 10},
    }

    for col, cfg in noise_cols.items():
        if col in prev.columns:
            noise = rng.normal(cfg['mean'], cfg['std'], size=len(prev))
            prev[col] = np.clip(prev[col] + noise, cfg['min'], cfg['max']).round(2)

    # Drop ~5% of students randomly (different cohort size)
    keep_mask = rng.random(len(prev)) > 0.05
    prev = prev[keep_mask].reset_index(drop=True)

    print(f"  [OK] Generated previous-year data: {len(prev)} rows (with noise)")
    return prev


def main():
    print(f"\n{'='*60}")
    print("  Smart Campus Analytics — SQLite Migration")
    print(f"{'='*60}\n")

    print("[1/5] Connecting to database...")
    conn = get_connection(DB_PATH)

    print("[2/5] Dropping legacy tables...")
    _drop_legacy_tables(conn)
    conn.close()

    print("[3/5] Creating new schema...")
    init_db(DB_PATH)
    print("  [OK] Created unified `students` table")

    print("[4/5] Importing CSV as current year...")
    csv_df = _load_csv()
    upsert_students(csv_df, CURRENT_YEAR, DB_PATH)
    print(f"  [OK] Imported {len(csv_df)} students as {CURRENT_YEAR}")

    print("[5/5] Generating synthetic previous-year data...")
    prev_df = _generate_previous_year(csv_df)
    upsert_students(prev_df, PREVIOUS_YEAR, DB_PATH)
    print(f"  [OK] Imported {len(prev_df)} students as {PREVIOUS_YEAR}")

    # Summary
    years = get_available_years(DB_PATH)
    conn = get_connection(DB_PATH)
    cursor = conn.execute("SELECT academic_year, COUNT(*) FROM students GROUP BY academic_year")
    counts = cursor.fetchall()
    conn.close()

    print(f"\n{'='*60}")
    print("  Migration Complete!")
    print(f"{'='*60}")
    print(f"  Database: {DB_PATH}")
    print(f"  Years:    {years}")
    for year, count in counts:
        print(f"    {year}: {count} students")
    print()


if __name__ == '__main__':
    main()
