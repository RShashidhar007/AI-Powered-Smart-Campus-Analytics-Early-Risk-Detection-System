# AI-Powered Smart Campus Analytics: Early Risk Detection System

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-f3a536?style=for-the-badge&logo=groq&logoColor=white)

An advanced, comprehensive **Smart Campus Analytics** dashboard built with Streamlit. This platform leverages Machine Learning to predict student outcomes across **5 departments** and **4 semesters**, functioning as an **Early Risk Detection System**. 

The system features a dual-profile **Faculty and Student Portal**, a robust **SQLite database** architecture for historical data and persistent user authentication, **Year-over-Year comparative analytics**, and a stunning, natively integrated **Glassmorphic Dark Mode UI**.

---

## 🌟 Key Features

* **🎭 Dual-Role Access Portals:** Features distinct interfaces for Faculty (advanced predictive analytics) and Students (read-only profiles mapping their specific performance vs class averages using Radar and Bullet charts).
* **🤖 AI-Powered Early Risk Detection:** Employs Machine Learning models (`scikit-learn`) to classify student performance and predict individuals at risk of failing or dropping out.
* **🗄️ Robust SQLite Authentication & Persistence:** Powered by a unified SQLite database (`campus_analytics.db`) enforcing secure SHA-256 faculty registration/authentication and rapid historical student querying.
* **📅 Year-over-Year Comparison:** A dedicated dashboard to compare KPIs, grade distributions, and predictive risk tiers between current and previous academic years with interactive delta metrics.
* **🏫 Multi-Department Support:** Scales efficiently across **5 major departments** (CSE, ECE, ME, CE, ISE) containing **4 semesters** worth of integrated insights.
* **📊 Premium Interactive Visualizations:** Upgraded dynamic visualizations using `Plotly`, featuring correlation impact bars, Risk Treemaps, Attendance Area Splines, and Statistical Boxplots inside a perfectly constrained geometric Grid layout.
* **📂 Multi-Format Data Ingestion:** Process student data continuously via CSV, Excel, and PDF files directly into the database.
* **🌐 Enterprise Multilingual Support:** Comprehensive, dynamic localization mapping for **English, Hindi, and Kannada** available entirely offline across all pages and charts.
* **💬 AI Campus Assistant:** Integrated floating AI agent powered by **Groq (Llama 3)** for granular data interpretation context, acting as a personal data scientist.
* **🎨 Deep Space Premium Styling:** Bespoke Streamlit layout enforcing an unbreakable **Glassmorphic Dark Theme** with polished typography, glowing hover actions, seamless metric cards, and perfectly aligned UI elements.

---

## 🛠️ Technology Stack

* **Frontend Framework:** Streamlit
* **Database & Persistence:** SQLite (`campus_analytics.db`)
* **Security Layer:** `hashlib` (SHA-256 cryptographic hashes for authentication)
* **Data Processing Pipeline:** `pandas`, `numpy`
* **Machine Learning Engine:** `scikit-learn`, `joblib`
* **Data Visualization:** `plotly`
* **LLM Engine:** Groq API (Llama-3.3-70b-versatile or similar)
* **Document Processing:** `pdfplumber`, `openpyxl`

---

## 📂 Project Structure

```text
├── data/                   # SQLite Database (campus_analytics.db) and CSV backups
├── models/                 # Serialized Machine Learning models
├── scripts/                # Utility scripts
│   ├── migrate_to_sqlite.py # Script to migrate CSV data to SQLite and generate history
│   ├── update_lang.py       # Auto-generator script for missing translation variables
│   ├── inspect_db.py       # DB inspection utility
├── src/                    # Primary source code
│   ├── pages/              # Dashboards (Home, Predictions, Students, Reports, Year Comparison, Settings, Student Dashboard)
│   ├── styles.py           # Core Glassmorphic dark theme application CSS logic
│   ├── ai_agent.py         # Groq-powered contextual floating Assistant
│   ├── database.py         # SQLite authentication abstractions & student CRUD operations
│   ├── data_pro.py         # Data processing & feature pipelines
│   ├── login.py            # Custom UI logic for Faculty/Student login & Registration routing
│   ├── config.py           # App configuration limits (DB_PATH, ACADEMIC_YEAR)
│   ├── language.py         # i18n localization dictionary references
│   ├── ml_models.py        # ML architectures, hyperparameter training frameworks
├── app.py                  # Main Streamlit entrance application
└── requirements.txt        # System Dependencies
```

---

## 🚀 Getting Started

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

## 🔐 Credentials & Access Roles

### Faculty Portal
The main interface providing full predictive modeling and analytical capabilities.
- **Default Super-Admin Username:** `teacher`
- **Default Super-Admin Password:** `team07pro`
*(Faculty users can directly register new permanent accounts via the "Register" GUI tab).*

### Student Portal
A restricted read-only interface mapped exclusively to a student's `USN` performance metrics.
- **Login Mechanism:** Enter a valid dataset `USN` (e.g. `1RV21CSE1001`) in both the Username and Password fields.

---

## 🤝 Contributing
Contributions are highly encouraged! Feel free to fork the project and open a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
