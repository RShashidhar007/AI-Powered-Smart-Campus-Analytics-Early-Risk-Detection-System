# AI-Powered Smart Campus Analytics: Early Risk Detection System

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-%23412991.svg?style=for-the-badge&logo=openai&logoColor=white)

An advanced, comprehensive **Smart Campus Analytics** dashboard built with Streamlit. This platform leverages Machine Learning to predict student outcomes, functioning as an **Early Risk Detection System**. It provides actionable insights, beautiful visualizations, and AI-assisted analysis for campus administration and teaching staff.

---

## 🌟 Key Features

* **🤖 AI-Powered Early Risk Detection:** Employs Machine Learning models (`scikit-learn`) to classify student performance and predict individuals at risk of falling behind.
* **📊 Interactive Dashboards:** Visually rich and dynamic data representations using `Plotly`. Heatmaps, risk distributions, and performance metrics are easy to explore.
* **📂 Multi-Format Data Ingestion:** Seamlessly upload and process student data from a variety of file formats, including CSV, Excel, and PDF files.
* **🌐 Multilingual Support:** Built-in localization for **English, Hindi, and Kannada**, ensuring accessibility across a broader user base.
* **📝 Automated Reporting:** Generate comprehensive student reports with ease. Exports are fully supported in both Excel and PDF formats.
* **💬 AI Chat Assistant:** An integrated, floating AI agent powered by Groq/OpenAI APIs that can contextually answer questions about student data and platform functionality.
* **🎨 Premium Styling:** A meticulously crafted user interface with modern typography (DM Sans), glassmorphism cards, dynamic theming, and smooth transitions.

---

## 🛠️ Technology Stack

* **Frontend / Web Framework:** [Streamlit](https://streamlit.io/)
* **Data Processing & Analytics:** `pandas`, `numpy`
* **Machine Learning:** `scikit-learn`
* **Visualizations:** `plotly`
* **GenAI / Assistant:** `openai` (Groq API compatible)
* **Document Processing:** `pdfplumber`, `openpyxl`

---

## 📂 Project Structure

```text
├── .streamlit/             # Streamlit configuration for themes and server
├── assets/                 # Images, logos, and UI graphics
├── data/                   # Sample datasets (e.g., student_data_500.csv)
├── models/                 # Serialized Machine Learning models
├── notebooks/              # Jupyter notebooks for data exploration & model training
├── outputs/                # System-generated outputs (reports, charts)
├── src/                    # Primary source code modules
│   ├── pages/              # Streamlit sub-pages (Home, Predictions, Students, Reports, Settings)
│   ├── ai_agent.py         # Floating AI Assistant integrations
│   ├── auth.py / login.py  # User authentication and login views
│   ├── config.py           # Core application configuration (Constants, State)
│   ├── data_pro.py         # Data processing and summary statistics pipelines
│   ├── file_ingest.py      # Logic for parsing CSV/Excel/PDF student data
│   ├── language.py         # Internationalization (i18n) dictionaries
│   ├── ml_models.py        # ML architectures and inference functions
│   ├── pdf_report.py       # PDF report generation system
│   ├── exel_repo.py        # Excel report generation system
│   ├── styles.py           # Custom CSS and dashboard aesthetics
│   └── visual.py           # Plotly charting wrappers
├── app.py                  # Main application entry point
├── main.py                 # Alternative/CLI entry point
└── requirements.txt        # Python dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites

Ensure you have **Python 3.9+** installed on your system.

### 2. Clone the Repository

```bash
git clone https://github.com/RShashidhar007/AI-Powered-Smart-Campus-Analytics-Early-Risk-Detection-System.git
cd AI-Powered-Smart-Campus-Analytics-Early-Risk-Detection-System
```

### 3. Install Dependencies

It is highly recommended to use a virtual environment:

```bash
python -m venv venv

# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Configuration

To utilize the AI Agent capabilities, you will need to set up your API keys. Wait for configuration prompts inside the Settings page of the app, or add your API keys in your environment or Streamlit secrets (`.streamlit/secrets.toml`).

### 5. Run the Application

Execute the standard Streamlit run command:

```bash
streamlit run app.py
```

The application will start, and you can view the dashboard by navigating to `http://localhost:8501` in your web browser.

---

## 🔐 Credentials

When presented with the login screen (if enabled by default), you can log in using the administrator credentials set in the database or `auth.py`. 

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you would like to contribute.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
