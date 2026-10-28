# Multimodal Construction Intelligence Platform

Full-stack educational prototype inspired by your Skill Wallet brief.

**Stack:** React + Vite frontend, Python + FastAPI backend, SQLite history, optional Google Gemini multimodal integration.

## Features
- Site safety photo review
- Structural crack observation workflow
- Indicative real-estate valuation using user-provided rate assumptions
- Construction project phase planning
- Daily site assistant and weather-aware checklist (weather must be entered by user; no live forecast)
- SQLite report history and API docs at `/docs`

> Safety note: this is a prototype, not a certified engineering, safety, legal, or appraisal tool. Qualified professionals must verify site decisions. Demo-mode image reviews do not actually interpret image pixels.

## Run locally
Requires Python 3.10+ and Node.js 18+.

### Backend (terminal 1)
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# copy .env.example to .env (optional)
uvicorn app.main:app --reload
```
API: http://127.0.0.1:8000 — docs: http://127.0.0.1:8000/docs

### Frontend (terminal 2)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

### Optional Gemini
Add `GEMINI_API_KEY=your_key` to `backend/.env` and restart the backend. The key is never needed to run the demo. Never commit API keys.
