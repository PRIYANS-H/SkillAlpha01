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

### 1. Run Backend Server
```bash
cd backend
python -m pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --port 8000
```
- Backend API running at `http://localhost:8000`
- Interactive Swagger docs at `http://localhost:8000/docs`

### 2. Run Backend Tests
```bash
cd backend
python -m pytest tests/test_api.py
```

### 3. Run Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
- Frontend application running at `http://localhost:5173`

---

## Production Credentials (Pre-seeded)

- **Learner User**: `learner@skillalpha.com` / `learner123`
- **Admin User**: `admin@skillalpha.com` / `admin123`
