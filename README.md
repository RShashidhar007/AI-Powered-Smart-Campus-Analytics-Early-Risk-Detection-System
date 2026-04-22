# AI-Powered Smart Campus Analytics: Early Risk Detection System

An advanced **Smart Campus Analytics** dashboard built with Streamlit. The platform uses machine learning and academic performance data to identify students who may need early support across multiple departments and semesters.

The system includes separate **Faculty** and **Student** portals, SQLite-backed data storage, year-over-year analytics, multilingual UI support, professional dashboard visualizations, and a contextual AI assistant.

---

## Key Features

* **Dual-role access portals:** Faculty users can access predictive analytics, reports, student management, and settings. Students can view a restricted personal dashboard using their USN.
* **Early risk detection:** Uses attendance, internal marks, assignments, study hours, and semester marks to classify student risk levels.
* **SQLite persistence:** Stores student records, academic-year data, and registered faculty accounts in `campus_analytics.db`.
* **Professional home dashboard:** Provides KPI summaries, risk proportions, grade distribution, attendance insights, academic drivers, and department comparisons.
* **Year-over-year comparison:** Compares KPIs, grade distributions, and predictive risk tiers across academic years.
* **Multi-department support:** Supports CSE, ECE, ME, CE, and ISE across multiple semesters.
* **Interactive visualizations:** Uses Plotly charts for distributions, correlations, attendance tiers, marks spread, and department-level comparisons.
* **Multi-format ingestion:** Supports student data workflows from CSV, Excel, and PDF sources.
* **Multilingual interface:** Includes English, Hindi, and Kannada text mappings.
* **AI campus assistant:** Provides contextual analytics support using the configured LLM provider.
* **Clean dark UI:** Uses a centralized theme for consistent spacing, typography, cards, and charts without logo-heavy branding.

---

## Technology Stack

* **Frontend:** Streamlit
* **Database:** SQLite
* **Data processing:** pandas, numpy
* **Machine learning:** scikit-learn
* **Visualization:** Plotly
* **Documents:** pdfplumber, openpyxl
* **Environment variables:** python-dotenv
* **AI assistant:** OpenAI/Groq-compatible API configuration, depending on local setup

---

## Project Structure

```text
.
|-- app.py                         # Main Streamlit application entry point
|-- requirements.txt               # Python dependencies
|-- README.md                      # Project documentation
|-- data/
|   |-- campus_analytics.db         # SQLite database
|   |-- student_data.csv            # Main student dataset
|   `-- student_data_500.csv        # Sample dataset
|-- scripts/
|   |-- generate_data.py            # Synthetic data generator
|   |-- inspect_csv.py              # CSV inspection utility
|   |-- inspect_db.py               # Database inspection utility
|   `-- migrate_to_sqlite.py        # CSV-to-SQLite migration script
`-- src/
    |-- ai_agent.py                 # AI assistant logic
    |-- auth.py                     # Login renderer re-export
    |-- config.py                   # App configuration and constants
    |-- data_pro.py                 # Data cleaning and feature engineering
    |-- database.py                 # SQLite access layer
    |-- exel_repo.py                # Excel report generation
    |-- file_ingest.py              # File ingestion helpers
    |-- language.py                 # UI language mappings
    |-- login.py                    # Faculty and student login UI
    |-- ml_models.py                # ML training and prediction helpers
    |-- pdf_report.py               # PDF report generation
    |-- styles.py                   # CSS injection helpers
    |-- ui_theme.py                 # Centralized design tokens and UI helpers
    |-- visual.py                   # Static chart/report visualizations
    `-- pages/
        |-- home.py                 # Campus overview dashboard
        |-- predictions.py          # Prediction tools
        |-- reports.py              # Analytics reports
        |-- settings.py             # Settings page
        |-- student_dashboard.py    # Student-facing dashboard
        |-- students.py             # Student management
        `-- year_comparison.py      # Academic year comparison
```

---

## Getting Started

### 1. Prerequisites

Install **Python 3.10+**.

### 2. Installation

```bash
git clone https://github.com/RShashidhar007/AI-Powered-Smart-Campus-Analytics-Early-Risk-Detection-System.git
cd AI-Powered-Smart-Campus-Analytics-Early-Risk-Detection-System
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux, activate the environment with:

```bash
source venv/bin/activate
```

### 3. Database Migration

Populate or refresh the SQLite database from the dataset:

```bash
python scripts/migrate_to_sqlite.py
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_key_here
ADMIN_USERNAME=teacher
ADMIN_PASSWORD=team07pro
```

### 5. Run The App

```bash
streamlit run app.py
```

---

## Credentials And Access

### Faculty Portal

Faculty users can access the full dashboard, predictions, reports, student records, and settings.

* **Default username:** `teacher`
* **Default password:** `team07pro`

Faculty users can also register permanent accounts from the Register tab.

### Student Portal

Students log in with a valid dataset USN.

* **Username:** student USN, for example `1RV21CSE1001`
* **Default password:** same as the student USN

---

## Notes

* The app falls back to `data/student_data.csv` if database data is unavailable.
* Academic-year filtering uses `CURRENT_ACADEMIC_YEAR` from `src/config.py`.
* The UI is intentionally logo-free and uses text-first navigation.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
