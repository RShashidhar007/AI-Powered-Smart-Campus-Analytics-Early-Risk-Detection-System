# Smart Campus AI — Integration Summary

## What was added

### New Files
| File | Purpose |
|------|---------|
| `smart_campus/app.py` | FastAPI web server — all API routes + serves dashboard |
| `smart_campus/templates/dashboard.html` | Full web UI: dashboard, student table, AI chat widget |
| `smart_campus/requirements.txt` | All Python dependencies |
| `smart_campus/.env.example` | API key template |

### app.py — API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the dashboard HTML |
| `/api/health` | GET | Health check |
| `/api/summary` | GET | KPIs: totals, risk & grade distribution |
| `/api/students` | GET | List students (search + risk filter) |
| `/api/students/{usn}` | GET | Single student full details |
| `/api/at-risk` | GET | Top at-risk students sorted by risk score |
| `/api/chat` | POST | AI chat with history + student context |

All endpoints use the existing `data_pro.py` pipeline — no data logic was changed.

## How to run

### 1. Install dependencies
```bash
cd smart_campus
pip install -r requirements.txt
```

### 2. Set your API key
```bash
cp .env.example .env
# Edit .env and paste your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Start the server
```bash
uvicorn app:app --reload --port 8000
```

### 4. Open in browser
```
http://localhost:8000
```

## How the AI chat works

1. User opens the 🤖 chat bubble (bottom-right)
2. User clicks any student row → student data loads into context
3. User asks questions → AI responds using real student data
4. Risk banner (🔴🟡🟢) appears automatically based on response

## Chat API payload example
```json
POST /api/chat
{
  "message": "Why is this student at high risk?",
  "history": [...previous messages...],
  "student_context": {
    "Name": "Vivek Kulkarni",
    "Attendance": "46.38%",
    "Risk Tier": "Critical",
    "Risk Score": "85"
  }
}
```
