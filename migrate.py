"""
migrate.py — CSV → SQLite migration script
Reads data/student_data_500.csv and writes it into data/campus_analytics.db.
Safe to re-run: uses IF EXISTS / replace semantics so data is never duplicated.
"""

import os
import sqlite3
import pandas as pd

# ── paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "student_data_500.csv")
DB_PATH = os.path.join(BASE_DIR, "data", "campus_analytics.db")


def migrate():
    # 1. Read CSV
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: CSV file not found at {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)

    # 2. Normalise column names: strip whitespace, lowercase, spaces → underscores
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    # 3. Add new columns
    df["dept"] = "CSE"
    df["semester"] = 1

    # 4. Connect / create SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 5. Write current_students (replace if exists → idempotent)
    df.to_sql("current_students", conn, if_exists="replace", index=False)

    # 6. Create previous_students table (empty, only if it doesn't already exist)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS previous_students (
            usn              TEXT,
            name             TEXT,
            dept             TEXT,
            semester         INTEGER,
            attendance       REAL,
            internal_marks   REAL,
            assignment_score REAL,
            quiz_score       REAL,
            lab_marks        REAL,
            semester_marks   REAL,
            study_hours      REAL,
            academic_year    TEXT
        )
    """)

    conn.commit()

    # 7. Verify & report
    row_count = cursor.execute("SELECT COUNT(*) FROM current_students").fetchone()[0]
    conn.close()

    print("Migration complete!")
    print(f"   Rows migrated : {row_count}")
    print(f"   Database path : {DB_PATH}")


if __name__ == "__main__":
    migrate()
