# AI-Powered Smart Campus Analytics: Early Risk Detection System

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-f3a536?style=for-the-badge&logo=groq&logoColor=white)

An advanced, comprehensive **Smart Campus Analytics** dashboard built with Streamlit. This platform leverages Machine Learning to predict student outcomes across **5 departments** and **4 semesters**, functioning as an **Early Risk Detection System**. It now features a robust **SQLite database** architecture for historical data tracking and **Year-over-Year comparative analytics**.

---

## 🌟 Key Features

* **🤖 AI-Powered Early Risk Detection:** Employs Machine Learning models (`scikit-learn`) to classify student performance and predict individuals at risk.
* **📅 Year-over-Year Comparison:** A dedicated dashboard to compare KPIs, grade distributions, and risk tiers between current and previous academic years with interactive delta tracking.
* **🗄️ Robust SQLite Persistence:** Transitioned from legacy CSV storage to a unified SQLite database for better data integrity, indexing, and historical student tracking.
* **👤 Student Progress Tracking:** Identify "Improvers" and "Decliners" by tracking individual student performance (via USN) across different years.
* **🏫 Multi-Department Support:** Tracks **5 departments** (CSE, ECE, ME, CE, ISE) across **4 semesters** with comprehensive filtering.
* **📊 Interactive Dashboards:** Dynamic visualizations using `Plotly`, including heatmaps, risk distributions, and correlation matrices.
* **📂 Multi-Format Data Ingestion:** Process student data from CSV, Excel, and PDF files directly into the database.
* **🌐 Multilingual Support:** Localization for **English, Hindi, and Kannada**.
* **💬 AI Campus Assistant:** Integrated floating AI agent powered by **Groq (Llama 3)** for contextual data analysis and general campus Q&A.
* **🎨 Premium Styling:** Modern UI with DM Sans typography, soft shadows, and a reactive design system.

---

## 🛠️ Technology Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Database:** SQLite (SQLAlchemy/sqlite3)
* **Data Processing:** `pandas`, `numpy`
* **Machine Learning:** `scikit-learn`
* **Visualizations:** `plotly`
* **LLM Engine:** Groq API (Llama-3.3-70b-versatile)
* **Document Processing:** `pdfplumber`, `openpyxl`

---

## 📂 Project Structure

```text
├── data/                   # SQLite Database (campus_analytics.db) and CSV backups
├── models/                 # Serialized Machine Learning models
├── scripts/                # Utility scripts
│   ├── migrate_to_sqlite.py # Script to migrate CSV data to SQLite and generate history
│   ├── inspect_db.py       # DB inspection utility
├── src/                    # Primary source code
│   ├── pages/              # Dashboards (Home, Predictions, Students, Reports, Year Comparison, Settings)
│   ├── ai_agent.py         # Groq-powered AI Assistant
│   ├── database.py         # SQLite abstraction layer & CRUD operations
│   ├── data_pro.py         # Data processing & SQLite integrated analytics
│   ├── config.py           # App configuration (DB_PATH, ACADEMIC_YEAR)
│   ├── language.py         # i18n localization dictionaries
│   ├── ml_models.py        # ML architectures and training
├── app.py                  # Main Streamlit application
└── requirements.txt        # Dependencies
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
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Database Migration
Populate the SQLite database from existing CSV data:
```bash
python scripts/migrate_to_sqlite.py
```

### 4. Configuration
Create a `.env` file (see `.env.example`):
```env
GROQ_API_KEY=your_key_here
ADMIN_PASSWORD=team07pro
```

### 5. Run
```bash
streamlit run app.py
```

---

## 🔐 Credentials
- **Default Username:** `teacher`
- **Default Password:** `team07pro`
- (Configure additional users in the built-in Registration tab)

---

## 🤝 Contributing
Feel free to fork the project and open a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

---

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
