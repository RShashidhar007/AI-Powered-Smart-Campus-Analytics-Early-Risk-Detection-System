# AI-Powered Smart Campus Analytics: Early Risk Detection System

> A full-stack academic intelligence platform built with **Streamlit**, **SQLite**, and **Machine Learning** to proactively detect at-risk students and empower faculty with actionable insights — across departments, semesters, and academic years.

---

## Overview

The **Smart Campus Analytics** system transforms raw academic performance data into early warning signals. Using attendance records, internal marks, assignment completion, and study-hour patterns, the platform classifies each student into a risk tier and surfaces the data through a polished, role-aware dashboard.

Two separate portals serve different audiences:

| Role | Access |
|---|---|
| **Faculty / Admin** | Full dashboard — predictions, reports, student management, year comparison, settings, and AI assistant |
| **Student** | Read-only personal dashboard — own marks, attendance, risk level, and performance insights |

---

## Key Features

- **Dual-role authentication** — Faculty log in with username/password (SHA-256 hashed, persisted in SQLite). Students log in with their USN. Faculty can self-register permanent accounts.
- **Early risk detection** — Classifies students as *At Risk* or *On Track* using attendance, internal marks, assignments, study hours, and semester marks via a trained scikit-learn model (~92.4 % accuracy).
- **SQLite persistence** — All student records, academic-year data, and faculty accounts are stored in `data/campus_analytics.db`. CSV fallback is supported automatically.
- **Home dashboard KPIs** — Total students, at-risk count, on-track count, and model accuracy — all filtered by department and semester in real time.
- **Interactive Plotly visualisations** — Risk distribution, grade spread, attendance tiers, marks correlation, department comparisons, academic drivers — all using Streamlit's native dark/light theme engine.
- **Year-over-year comparison** — Compare KPIs, grade distributions, and risk tiers across any two academic years stored in the database.
- **Multi-department support** — CSE, ECE, ME, CE, and ISE across Semesters 1–4.
- **Multilingual UI** — English, Hindi (हिन्दी), and Kannada (ಕನ್ನಡ) text mappings via `src/language.py`.
- **Floating AI campus assistant** — Contextual analytics support on every page, powered by a Groq-compatible LLM API.
- **Report exports** — Download analytics as Excel workbooks (`openpyxl`) or formatted PDF reports (`pdfplumber`, `reportlab`).
- **Data ingestion** — Import student records from CSV, Excel, or PDF sources via `src/file_ingest.py`.
- **Premium dark UI** — Glassmorphism-inspired design system with CSS variables, Plotly theming, and consistent typography — no logos, no clutter.

---

## Technology Stack

| Layer | Library / Tool |
|---|---|
| **Web framework** | [Streamlit](https://streamlit.io/) ≥ 1.32 |
| **Database** | SQLite (via Python `sqlite3`) |
| **Data processing** | pandas ≥ 2.1, numpy ≥ 1.26 |
| **Machine learning** | scikit-learn ≥ 1.4 |
| **Visualisation** | Plotly ≥ 5.18 |
| **PDF reports** | pdfplumber ≥ 0.10 |
| **Excel reports** | openpyxl ≥ 3.1 |
| **AI assistant** | openai ≥ 1.14, groq (Groq-compatible API) |
| **QR codes** | qrcode ≥ 7.4 |
| **Environment** | python-dotenv ≥ 1.0 |
| **HTTP** | requests ≥ 2.31 |

---

## Project Structure

```text
.
├── app.py                          # Streamlit entry point — routing, auth, layout
├── main.py                         # Standalone CLI / batch runner 
├── requirements.txt                # Python dependencies
├── .env.example                    # Template for environment variables
├── .gitignore
├── LICENSE
│
├── data/
│   ├── campus_analytics.db         # SQLite database 
│   └── student_data.csv            # Primary student dataset
│
├── scripts/
│   ├── generate_data.py            # Synthetic student data generator
│   ├── inspect_csv.py              # Quick CSV schema inspector
│   ├── inspect_db.py               # SQLite table/row inspector
│   └── migrate_to_sqlite.py        # One-time CSV → SQLite migration
│
├── models/                         # Saved ML model artefacts
├── notebooks/                      # Exploration and training notebooks
├── outputs/                        # Generated report files
├── reports/                        # Static report templates / assets
├── assets/                         # Static media assets
│
└── src/
    ├── ai_agent.py                 # Floating AI assistant (Groq LLM integration)
    ├── auth.py                     # Login page re-export shim
    ├── config.py                   # Global constants, paths, session-state init
    ├── data_pro.py                 # Data cleaning and feature engineering pipeline
    ├── database.py                 # SQLite CRUD and query helpers
    ├── exel_repo.py                # Excel report generation (openpyxl)
    ├── file_ingest.py              # CSV / Excel / PDF ingestion helpers
    ├── language.py                 # Multilingual UI text mappings
    ├── login.py                    # Faculty and student login/register UI
    ├── ml_models.py                # Model training, prediction, and risk scoring
    ├── pdf_report.py               # PDF report generation
    ├── styles.py                   # Global CSS injection helpers
    ├── ui_theme.py                 # Design tokens, card/chart helpers
    ├── visual.py                   # Reusable Plotly chart builders
    └── pages/
        ├── home.py                 # Campus overview dashboard
        ├── predictions.py          # Individual and bulk risk prediction
        ├── reports.py              # Analytics reports page
        ├── settings.py             # App and profile settings
        ├── student_dashboard.py    # Student-facing personal dashboard
        ├── students.py             # Student record management
        └── year_comparison.py      # Academic year comparison dashboard
```

---

## Getting Started

### Prerequisites

- **Python 3.10 or higher**
- A free [Groq API key](https://console.groq.com/) for the AI assistant (optional but recommended)

---

### 1. Clone the Repository

```bash
git clone https://github.com/RShashidhar007/AI-Powered-Smart-Campus-Analytics-Early-Risk-Detection-System.git
cd AI-Powered-Smart-Campus-Analytics-Early-Risk-Detection-System
```

### 2. Create and Activate a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# AI Assistant — get a free key at https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# Default faculty admin credentials
ADMIN_USERNAME=teacher
ADMIN_PASSWORD=team07pro
```

> **Note:** The AI assistant degrades gracefully if `GROQ_API_KEY` is missing — all other features remain fully functional.

### 5. Populate the Database

Run the migration script to seed the SQLite database from the bundled CSV dataset:

```bash
python scripts/migrate_to_sqlite.py
```

This creates `data/campus_analytics.db`. The app also falls back to `data/student_data.csv` automatically if the database is empty.

### 6. Launch the App

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

---

## Credentials and Access

### Faculty Portal

Access the full analytics dashboard, predictions, student management, reports, and settings.

| Field | Value |
|---|---|
| **Username** | `teacher` |
| **Password** | `team07pro` |

Faculty users can also create permanent accounts from the **Register** tab on the login screen. Registered accounts are stored in `campus_analytics.db` with SHA-256 hashed passwords.

> Department-scoped faculty accounts see only their assigned department's data.

### Student Portal

Students authenticate with their USN.

| Field | Value |
|---|---|
| **Username** | Student USN, e.g. `1RV21CSE1001` |
| **Password** | Same as the USN (default) |

Students see a read-only personal dashboard with their marks, attendance percentage, risk level, and semester trend.

---

## Navigation (Faculty View)

| Page | Description |
|---|---|
| **Home** | KPI cards, risk distribution, grade spread, attendance tiers, and department comparisons |
| **Predictions** | Run individual or bulk risk predictions with real-time feedback |
| **Students** | Browse, filter, and manage all student records |
| **Reports** | Download Excel and PDF analytics reports |
| **Year Comparison** | Side-by-side KPI and distribution comparison across academic years |
| **Settings** | Update profile, department assignment, and app preferences |

---

## Configuration Reference

Key constants in `src/config.py`:

| Constant | Default | Purpose |
|---|---|---|
| `CURRENT_ACADEMIC_YEAR` | `'2025-26'` | Default year used by the dashboard and data loaders |
| `PREDICTION_ACCURACY` | `0.924` | Displayed model accuracy KPI |
| `DEPARTMENTS` | CSE, ECE, ME, CE, ISE | Supported departments |
| `SEMESTERS` | 1, 2, 3, 4 | Supported semester numbers |

---

## Notes

- The app runs entirely in **dark mode** (forced at startup via `app.py`).
- Academic-year filtering is driven by `CURRENT_ACADEMIC_YEAR` in `src/config.py` — update this when the new year begins.
- Multilingual labels are toggled live from the language selector in the top-right corner — no page reload required.
- The floating AI assistant is available on every page and has access to the current filtered dataset context.

---

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
