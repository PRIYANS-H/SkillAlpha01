# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

SkillAlpha is a personalized learning-roadmap platform: a FastAPI monolith in `backend/`, a React + Vite SPA in `frontend/`, and Supabase providing auth and PostgreSQL. Deployed as backend on Render and frontend on Vercel.

## Commands

Backend (run from `backend/`; imports assume `backend/` is the working directory):
```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000     # Swagger at /docs
python -m pytest tests                                  # all tests
python -m pytest tests/test_api.py::test_admin_role_gating   # single test
python -m pytest tests/test_learner_journey.py          # MVP acceptance test (full 8-step learner loop)
python seed.py                                          # seed skill ontology + resources manually
alembic revision --autogenerate -m "msg" && alembic upgrade head
```

Frontend (run from `frontend/`):
```bash
npm install
npm run dev        # http://localhost:5173, proxies /api -> localhost:8000
npm run build      # runs `tsc` then `vite build` (this is the only type check; no linter is configured)
```

`docker-compose.yml` references `backend/Dockerfile` and `frontend/Dockerfile`, which don't exist, so only its `postgres`/`redis` services are usable.

## Configuration

- Backend settings live in `app/config.py` (pydantic-settings). They're read from `.env` in the working directory or one level up, so either `backend/.env` or the repo-root `.env` works. Template: `.env.example`.
- `DATABASE_URL` defaults to `sqlite:///./skillalpha.db`. `postgres://` and `postgresql://` URLs are rewritten to `postgresql+psycopg2://` in both `app/models/db.py` and `alembic/env.py`, so keep the two in sync.
- Frontend env: `VITE_API_URL` (backend origin; `/api` is appended if it's missing), `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY`.

## Architecture

### Startup side effects
On import, `app/main.py` runs `Base.metadata.create_all()` and auto-seeds via `seed.seed_database()` when the `skills` table is empty. Tables are therefore created without Alembic. Migrations in `alembic/versions/` exist for Supabase/Postgres schema management.

### Auth (Supabase)
The backend issues no tokens. Login, registration, and Google OAuth all go through `supabase.auth` in the frontend. `app/security/auth.py::get_current_user` verifies the Supabase JWT in this order:
1. HS256 with `SUPABASE_JWT_SECRET`
2. The JWKS from `SUPABASE_URL`
3. Supabase's `/auth/v1/user` endpoint

There is no unverified fallback, so a deployed backend must set `SUPABASE_JWT_SECRET` or `SUPABASE_URL`; otherwise every request gets a 401.

It then finds the `users` row by `auth_id` (falling back to an email match to link legacy rows) and **auto-provisions** a `User` + `Profile` on first request. Admin access is `users.role == "admin"` (case-insensitive) via `get_current_admin_user`. Nothing assigns admin, so it has to be set directly in the DB. The `/register` endpoint and `hashed_password` column are legacy. The pre-seeded credentials listed in README.md are stale: `seed.py` creates no users.

`tests/conftest.py` sets environment variables before `app` is imported. They point the tests at a throwaway SQLite database, set a test `SUPABASE_JWT_SECRET` that tests sign tokens with, and blank out the Supabase, Groq and YouTube keys, so tests never touch a real database or external API.

### Response envelope
Every endpoint returns `APIResponse` (`{data, meta, error}`, defined in `app/schemas/schemas.py`). Some "not found" cases return HTTP 200 with `error` set rather than raising. The global exception handler also returns this envelope with a reference ID. In `frontend/src/api/client.ts`, the axios interceptor attaches the Supabase bearer token, **unwraps `data`**, and rejects when `error` is present. Frontend callers therefore receive the payload directly, not the envelope. All routers are mounted under `/api` (`settings.API_V1_STR`).

### Roadmap generation pipeline (`app/services/`)
`POST /api/roadmaps` (body: `OnboardingRequest`) → `roadmap_service.generate_roadmap_for_user`:
1. `skill_service.get_target_skill_graph_for_goal` maps the goal string (keyword match: ML engineer, data scientist, backend, React/frontend, data engineer, mobile) to a hardcoded, ordered skill list, creating `Skill` rows by slug as needed.
2. `gap_engine.evaluate_skill_gaps` scores each skill from `UserSkill` rows or self-reported levels and classifies it as MASTERED/STRONG (skipped), NEEDS_REINFORCEMENT, or MISSING. Onboarding diagnostic answers (`diagnostic_results`, each tagged with the `skill_name` it tests) are blended in as evidence, so a failed diagnostic can keep a self-rated "Advanced" skill on the path. It also builds `route_reasoning`, optionally LLM-written via `llm_service` (Groq; returns `None` when no key is set, so callers must fall back).
3. The user's previous active roadmap is deactivated. Skills are packed 2 per weekly `RoadmapMilestone` as `RoadmapTask`s, with day/date text baked into the titles.
4. `recommendation_engine.rank_resources_for_skill` attaches the top 3 `Resource`s per task as `TaskResource` rows, using the weighted score documented in `docs/architecture.md`.

**Skill evidence.** Every evidence write goes through `gap_engine.record_skill_evidence`, which derives `status` from the score via `classify_skill_status` and increments `evidence_count`. Don't set `UserSkill.status` by hand. Evidence comes from:
- onboarding diagnostics and skill quizzes, blended as `old*0.6 + ratio*0.4`
- task self-evaluations: GOT_IT gives at least STRONG; SHAKY/LOST put the skill in the 0.40–0.60 reinforcement band

Skill scores are stored as 0–1 floats, not percentages.

**Adaptation.** `roadmap_service.adapt_roadmap_to_evidence` runs automatically after `POST /tasks/{id}/complete` and `POST /assessments/{id}/attempt`. The manual `POST /roadmaps/{id}/repace` button runs it too.
- A skill that is still weak after the learner has a `TaskProgress` for it gets a "Reinforcement Checkpoint" task inserted as the next action. There is at most one pending per skill, and at most 2 per skill in total.
- A pending reinforcement is marked SKIPPED once evidence for its skill turns strong.
- Gaps from the onboarding baseline alone never trigger reinforcement.

Task completion is idempotent per (task, user). Progress counts SKIPPED tasks as resolved.

### Resource matching
`resource_matcher.resolve_resource_matches` (`GET /api/resources/{id}/matches`) resolves a stored resource into concrete links:
- YouTube Data API search, cached in a 7-day **in-process** dict cache (`clear_cache()` is used in tests)
- Scoped doc/practice-site search URLs
- Book guidance

Tests mock `app.services.resource_matcher.httpx.Client` and patch `app.config.settings.YOUTUBE_DATA_API_KEY`.

### Frontend
- `App.tsx` owns the auth state. It syncs the Supabase session to the backend by calling `/auth/me` and mirrors the access token into `localStorage['skillalpha_token']`, which `getSupabaseToken` falls back to.
- Routes are not guarded client-side; the backend enforces auth.
- Pages live in `src/pages/` and fetch through `apiClient`. Shared types are in `src/types/index.ts`.
- `vercel.json` (root and `frontend/`) rewrites all paths to `index.html` for SPA routing.

### Design system
Tailwind tokens in `frontend/tailwind.config.js` follow Material-style naming (`surface`, `on-surface-variant`, `primary-container`, `secondary-container` = action orange `#FF5B22`, etc.); use these rather than raw hex values. The design spec and reference mockups (HTML + screenshots) for each screen are in `stitch_skillalpha_learning_roadmap_frontend/`, with tokens in `modern_learning_intelligence/DESIGN.md`.
