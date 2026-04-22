# AI-Powered Smart Campus Analytics: Early Risk Detection System

An advanced, comprehensive **Smart Campus Analytics** dashboard built with Streamlit. This platform leverages Machine Learning to predict student outcomes across **5 departments** and **4 semesters**, functioning as an **Early Risk Detection System**. 

The system features a dual-profile **Faculty and Student Portal**, a robust **SQLite database** architecture for historical data and persistent user authentication, **Year-over-Year comparative analytics**, and a stunning, natively integrated **Glassmorphic Dark Mode UI**.

---

## Key Features

* **Dual-Role Access Portals:** Features distinct interfaces for Faculty (advanced predictive analytics) and Students (read-only profiles mapping their specific performance vs class averages using Radar and Bullet charts).
* **AI-Powered Early Risk Detection:** Employs Machine Learning models (`scikit-learn`) to classify student performance and predict individuals at risk of failing or dropping out.
* **Robust SQLite Authentication & Persistence:** Powered by a unified SQLite database (`campus_analytics.db`) enforcing secure SHA-256 faculty registration/authentication and rapid historical student querying.
* **Year-over-Year Comparison:** A dedicated dashboard to compare KPIs, grade distributions, and predictive risk tiers between current and previous academic years with interactive delta metrics.
* **Multi-Department Support:** Scales efficiently across **5 major departments** (CSE, ECE, ME, CE, ISE) containing **4 semesters** worth of integrated insights.
* **Premium Interactive Visualizations:** Upgraded dynamic visualizations using `Plotly`, featuring correlation impact bars, Risk Treemaps, Attendance Area Splines, and Statistical Boxplots inside a perfectly constrained geometric Grid layout.
* **Multi-Format Data Ingestion:** Process student data continuously via CSV, Excel, and PDF files directly into the database.
* **Enterprise Multilingual Support:** Comprehensive, dynamic localization mapping for **English, Hindi, and Kannada** available entirely offline across all pages and charts.
* **AI Campus Assistant:** Integrated floating AI agent powered by **Groq (Llama 3)** for granular data interpretation context, acting as a personal data scientist.
* **Deep Space Premium Styling:** Bespoke Streamlit layout enforcing an unbreakable **Glassmorphic Dark Theme** with polished typography, glowing hover actions, seamless metric cards, and perfectly aligned UI elements.

---

## Technology Stack

* **Frontend Framework:** Streamlit
* **Database & Persistence:** SQLite (`campus_analytics.db`)
* **Security Layer:** `hashlib` (SHA-256 cryptographic hashes for authentication)
* **Data Processing Pipeline:** `pandas`, `numpy`
* **Machine Learning Engine:** `scikit-learn`, `joblib`
* **Data Visualization:** `plotly`
* **LLM Engine:** Groq API (Llama-3.3-70b-versatile or similar)
* **Document Processing:** `pdfplumber`, `openpyxl`

---

## ðŸ“‚ Project Structure

```text
â”œâ”€â”€ data/                   # SQLite Database (campus_analytics.db) and CSV backups
â”œâ”€â”€ models/                 # Serialized Machine Learning models
â”œâ”€â”€ scripts/                # Utility scripts
â”‚   â”œâ”€â”€ migrate_to_sqlite.py # Script to migrate CSV data to SQLite and generate history
â”‚   â”œâ”€â”€ update_lang.py       # Auto-generator script for missing translation variables
â”‚   â”œâ”€â”€ inspect_db.py       # DB inspection utility
â”œâ”€â”€ src/                    # Primary source code
â”‚   â”œâ”€â”€ pages/              # Dashboards (Home, Predictions, Students, Reports, Year Comparison, Settings, Student Dashboard)
â”‚   â”œâ”€â”€ styles.py           # Core Glassmorphic dark theme application CSS logic
â”‚   â”œâ”€â”€ ai_agent.py         # Groq-powered contextual floating Assistant
â”‚   â”œâ”€â”€ database.py         # SQLite authentication abstractions & student CRUD operations
â”‚   â”œâ”€â”€ data_pro.py         # Data processing & feature pipelines
â”‚   â”œâ”€â”€ login.py            # Custom UI logic for Faculty/Student login & Registration routing
â”‚   â”œâ”€â”€ config.py           # App configuration limits (DB_PATH, ACADEMIC_YEAR)
â”‚   â”œâ”€â”€ language.py         # i18n localization dictionary references
â”‚   â”œâ”€â”€ ml_models.py        # ML architectures, hyperparameter training frameworks
â”œâ”€â”€ app.py                  # Main Streamlit entrance application
â””â”€â”€ requirements.txt        # System Dependencies
```

---

## ðŸš€ Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Installation
```bash
git clone https://github.com/RShashidhar007/AI-Powered-Smart-Campus-Analytics-Early-Risk-Detection-System.git
cd AI-Powered-Smart-Campus-Analytics-Early-Risk-Detection-System
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 3. Database Initial Migration
To populate the SQLite database schema and extract any residual CSV sample data:
```bash
python scripts/migrate_to_sqlite.py
```

### 4. Configuration Requirements
Create a `.env` file within the system root directory (An `.env.example` is provided):
```env
# Optional but required for floating chat AI
GROQ_API_KEY=your_key_here

# Required for super-admin login dashboard interface
ADMIN_PASSWORD=team07pro
```

### 5. Launch the Application
```bash
streamlit run app.py
```

---

## ðŸ” Credentials & Access Roles

### Faculty Portal
The main interface providing full predictive modeling and analytical capabilities.
- **Default Super-Admin Username:** `teacher`
- **Default Super-Admin Password:** `team07pro`
*(Faculty users can directly register new permanent accounts via the "Register" GUI tab).*

### Student Portal
A restricted read-only interface mapped exclusively to a student's `USN` performance metrics.
- **Login Mechanism:** Enter a valid dataset `USN` (e.g. `1RV21CSE1001`) in both the Username and Password fields.

---

## ðŸ¤ Contributing
Contributions are highly encouraged! Feel free to fork the project and open a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ðŸ“ License
Distributed under the MIT License. See `LICENSE` for more information.

