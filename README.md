# SkillAlpha — Personalized Learning & Resource Discovery Platform

> **"Everything you need to learn. In the right order."**

SkillAlpha is a real, production-oriented startup MVP that understands a learner's goal, estimates their skill baseline, pinpoints exact skill gaps, bypasses what they already know, and curates a clear, daily learning sequence with evidence-based adaptive replanning.

---

## Key Features

- **Personalized Onboarding Wizard**: Goal selection, self-reported baseline skills, diagnostic calibration, weekly time constraints, and instant roadmap generation.
- **Skill Gap & Route Reasoning Engine**: Calculates skill gaps with prerequisite awareness and explains why specific modules were bypassed (*"Bypassed 34 basic lessons, saving ~18 hours"*).
- **Multi-Signal Recommendation Ranking**: Curates YouTube videos, Scikit-Learn docs, Jupyter practice labs, GitHub repos, and articles scored by relevance, difficulty fit, freshness, quality, and user feedback.
- **Today's Learning Workspace**: Actionable daily task queue with active learning session timer, curated resource stack, and reflection checkpoint.
- **Adaptive Replanning**: Re-calculates roadmap order and inserts reinforcement checkpoints when assessment scores or self-evaluations change.
- **Evidence-Based Progress Dashboard**: Displays verified skill score bars, confidence ratings, active habit streaks, and assessment logs.
- **Operational Admin Console**: System metrics (active users, roadmaps created, recommendation CTR), resource verification toggle, skill graph editor, CMS content editor, and audit logging.

---

## Tech Stack

- **Backend**: Python (FastAPI 3.12+), SQLAlchemy 2.0 ORM, SQLite / PostgreSQL, Alembic migrations, Pydantic v2 schemas, PyJWT authentication, Pytest test suite.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, React Query (TanStack Query), Axios, Recharts.
- **Design System**: Modern Learning Intelligence system (`#F6FBF5` base, `#0A4831` primary green, `#FF5B22` action orange, Plus Jakarta Sans typography).

---

## Quick Start (Local Setup)

### 1. Configure Environment Variables
Copy `.env.example` to `backend/.env` (or configure your keys):
```bash
cp .env.example backend/.env
```
* **YouTube Data API v3** (optional but recommended for dynamic videos): Set `YOUTUBE_DATA_API_KEY="AIza..."`
* **Groq API Key** (optional for dynamic AI diagnostic questions): Set `GROQ_API_KEY="gsk_..."`

### 2. Run Backend Server
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
- Backend API running at `http://localhost:8000`
- Interactive Swagger docs at `http://localhost:8000/docs`

### 3. Run Backend Tests
```bash
cd backend
python -m pytest tests/test_api.py
```

### 4. Run Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
- Frontend application running at `http://localhost:5173`

---

## Deployment (Vercel + Render)

### Backend on Render
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `JWT_SECRET`: your secret key
  - `DATABASE_URL`: `sqlite:///./skillalpha.db` (or PostgreSQL connection string)
  - `YOUTUBE_DATA_API_KEY`: your Google Cloud API key
  - `GROQ_API_KEY`: your Groq API key (optional)

### Frontend on Vercel
- **Root Directory**: `frontend`
- **Framework Preset**: `Vite`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**:
  - `VITE_API_URL`: your live Render backend URL (e.g. `https://skillalpha-api.onrender.com`)

---

## Pre-seeded Credentials

- **Learner User**: `learner@skillalpha.com` / `learner123`
- **Admin User**: `admin@skillalpha.com` / `admin123`

