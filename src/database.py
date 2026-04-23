"""
database.py - SQLite abstraction layer for Smart Campus Analytics.

Provides a unified `students` table with academic_year tracking,
replacing the old CSV-only data flow.
"""
import os
import sqlite3
import pandas as pd
import hashlib

# Path
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(_BASE_DIR, 'data', 'campus_analytics.db')

# Schema
_CREATE_STUDENTS = """
CREATE TABLE IF NOT EXISTS students (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    usn              TEXT    NOT NULL,
    name             TEXT,
    department       TEXT,
    semester         INTEGER,
    attendance       REAL,
    internal_marks   REAL,
    assignment_score REAL,
    quiz_score       REAL,
    lab_marks        REAL,
    semester_marks   REAL,
    study_hours      REAL,
    academic_year    TEXT    NOT NULL DEFAULT '2025-26',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usn, academic_year)
);
"""

_CREATE_FACULTY_USERS = """
CREATE TABLE IF NOT EXISTS faculty_users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    username         TEXT    NOT NULL UNIQUE,
    email            TEXT    NOT NULL,
    password_hash    TEXT    NOT NULL,
    department       TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

STUDENT_COLUMNS = [
    'usn', 'name', 'department', 'semester',
    'attendance', 'internal_marks', 'assignment_score',
    'quiz_score', 'lab_marks', 'semester_marks', 'study_hours',
    'academic_year',
]


def _hash_password(password: str) -> str:
    """Return a SHA-256 hash of the password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Return a connection to the campus analytics database."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(db_path: str = DB_PATH):
    """Create the required core database tables if they do not exist."""
    conn = get_connection(db_path)
    conn.execute(_CREATE_STUDENTS)
    conn.execute(_CREATE_FACULTY_USERS)
    conn.commit()
    conn.close()


def load_students(academic_year: str | None = None,
                  db_path: str = DB_PATH) -> pd.DataFrame:
    """Load students as a DataFrame, optionally filtered by academic year."""
    conn = get_connection(db_path)
    if academic_year:
        df = pd.read_sql_query(
            "SELECT * FROM students WHERE academic_year = ?",
            conn, params=(academic_year,),
        )
    else:
        df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()

    # Normalise columns to match rest of the codebase
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    # Drop the auto-increment id and created_at for downstream processing
    for drop_col in ('id', 'created_at'):
        if drop_col in df.columns:
            df = df.drop(columns=[drop_col])
    return df


def load_all_students(db_path: str = DB_PATH) -> pd.DataFrame:
    """Load every student row across all years."""
    return load_students(academic_year=None, db_path=db_path)


def upsert_students(df: pd.DataFrame, academic_year: str,
                    db_path: str = DB_PATH):
    """Insert or replace student records for the given academic year.

    Uses INSERT OR REPLACE keyed on (usn, academic_year).
    """
    conn = get_connection(db_path)
    df = df.copy()
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

    # Map 'dept' -> 'department' if needed
    if 'dept' in df.columns and 'department' not in df.columns:
        df = df.rename(columns={'dept': 'department'})

    # Ensure academic_year column
    df['academic_year'] = academic_year

    # Ensure required columns exist with defaults
    if 'department' not in df.columns:
        df['department'] = 'CSE'
    if 'semester' not in df.columns:
        df['semester'] = 1

    cols = [c for c in STUDENT_COLUMNS if c in df.columns]
    placeholders = ', '.join(['?'] * len(cols))
    col_names = ', '.join(cols)

    sql = f"INSERT OR REPLACE INTO students ({col_names}) VALUES ({placeholders})"

    rows = df[cols].values.tolist()
    conn.executemany(sql, rows)
    conn.commit()
    conn.close()


def get_available_years(db_path: str = DB_PATH) -> list[str]:
    """Return a sorted list of distinct academic years in the database."""
    conn = get_connection(db_path)
    cursor = conn.execute("SELECT DISTINCT academic_year FROM students ORDER BY academic_year")
    years = [row[0] for row in cursor.fetchall()]
    conn.close()
    return years


def get_year_student_count(academic_year: str,
                           db_path: str = DB_PATH) -> int:
    """Return the number of students for a given academic year."""
    conn = get_connection(db_path)
    cursor = conn.execute(
        "SELECT COUNT(*) FROM students WHERE academic_year = ?",
        (academic_year,),
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


def archive_year(from_year: str, to_year: str,
                 db_path: str = DB_PATH):
    """Copy all records from one academic year to another (for end-of-year archival)."""
    conn = get_connection(db_path)
    cols_no_id = ', '.join([c for c in STUDENT_COLUMNS if c != 'academic_year'])
    conn.execute(f"""
        INSERT OR REPLACE INTO students ({cols_no_id}, academic_year)
        SELECT {cols_no_id}, ? FROM students WHERE academic_year = ?
    """, (to_year, from_year))
    conn.commit()
    conn.close()


def delete_year(academic_year: str, db_path: str = DB_PATH):
    """Delete all records for a given academic year."""
    conn = get_connection(db_path)
    conn.execute("DELETE FROM students WHERE academic_year = ?", (academic_year,))
    conn.commit()
    conn.close()


def create_faculty_user(username: str, email: str, password: str, department: str, db_path: str = DB_PATH) -> bool:
    """Insert a new user into the database securely. Returns True if successful, False if username exists."""
    conn = get_connection(db_path)
    try:
        pw_hash = _hash_password(password)
        conn.execute(
            "INSERT INTO faculty_users (username, email, password_hash, department) VALUES (?, ?, ?, ?)",
            (username, email, pw_hash, department)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Catching IntegrityError handles the UNIQUE constraint on username naturally
        return False
    finally:
        conn.close()


def authenticate_faculty_user(username: str, password: str, db_path: str = DB_PATH) -> bool:
    """Verify the provided login credentials against the database securely."""
    conn = get_connection(db_path)
    cursor = conn.execute(
        "SELECT password_hash FROM faculty_users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        return False
        
    stored_hash = result[0]
    return stored_hash == _hash_password(password)
