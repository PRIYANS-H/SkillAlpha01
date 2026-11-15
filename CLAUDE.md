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

`docker compose up --build` runs Postgres + the API (`backend/Dockerfile`) + the built SPA served by nginx (`frontend/Dockerfile`, port 5173). Supabase keys come from the shell or a root `.env`. CI (`.github/workflows/ci.yml`) runs `pytest` and `npm run build` on every push/PR.

## Configuration

- Backend settings live in `app/config.py` (pydantic-settings). They're read from `.env` in the working directory or one level up, so either `backend/.env` or the repo-root `.env` works. Template: `.env.example`.
- `DATABASE_URL` defaults to `sqlite:///./skillalpha.db`. `postgres://` and `postgresql://` URLs are rewritten to `postgresql+psycopg2://` in both `app/models/db.py` and `alembic/env.py`, so keep the two in sync.
- `FRONTEND_ORIGINS` (comma-separated) restricts CORS in production; when empty any `https://` origin is allowed. Credentials are never allowed cross-origin (auth is a bearer header).
- Frontend env: `VITE_API_URL` (backend origin; `/api` is appended if it's missing), `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY`.

## Architecture

### Startup side effects
On import, `app/main.py` runs `Base.metadata.create_all()`, then `ensure_schema_upgrades()` (adds columns introduced after a table existed, e.g. `roadmap_tasks.due_date`), and auto-seeds via `seed.seed_database()` when the `skills` table is empty. Tables are therefore created without Alembic. When you add a column to an existing model, add it to both `ensure_schema_upgrades()` and a new idempotent migration in `alembic/versions/` (see `7c1e2a9b4f10_*`). The initial migration assumes a pre-existing schema, so `alembic upgrade head` does not work on an empty database.

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
1. `skill_service.get_target_skill_graph_for_goal` maps the goal string to one of the ordered skill lists in `GOAL_SKILL_GRAPHS` via `resolve_goal_family` (whole-word keyword rules in `GOAL_RULES`, so "ml" doesn't match "html"; "React Native" is mobile), creating `Skill` rows by slug as needed. `get_goal_skill_specs` is the DB-free version.
2. `gap_engine.evaluate_skill_gaps` scores each skill from `UserSkill` rows or self-reported levels and classifies it as MASTERED/STRONG (skipped), NEEDS_REINFORCEMENT, or MISSING. Onboarding diagnostic answers (`diagnostic_results`, each tagged with the `skill_name` it tests) are blended in as evidence, so a failed diagnostic can keep a self-rated "Advanced" skill on the path. It also builds `route_reasoning`, optionally LLM-written via `llm_service` (Groq; returns `None` when no key is set, so callers must fall back).
3. The user's previous active roadmap is deactivated. Skills are packed 2 per weekly `RoadmapMilestone` as `RoadmapTask`s titled "Master <skill>". Each task's study day is stored in `RoadmapTask.due_date` (never baked into titles); the frontend formats it via `src/utils/dates.ts`.
4. `recommendation_engine.rank_resources_for_skill` attaches the top 3 `Resource`s per task as `TaskResource` rows, using the weighted score documented in `docs/architecture.md`.

**Skill evidence.** Every evidence write goes through `gap_engine.record_skill_evidence`, which derives `status` from the score via `classify_skill_status` and increments `evidence_count`. Don't set `UserSkill.status` by hand. Evidence comes from:
- onboarding diagnostics and skill quizzes, blended as `old*0.6 + ratio*0.4`
- task self-evaluations: GOT_IT gives at least STRONG; SHAKY/LOST put the skill in the 0.40–0.60 reinforcement band

Skill scores are stored as 0–1 floats, not percentages.

**Adaptation.** `roadmap_service.adapt_roadmap_to_evidence` runs automatically after `POST /tasks/{id}/complete` and `POST /assessments/{id}/attempt`. The manual `POST /roadmaps/{id}/repace` button runs it too, after `shift_overdue_schedule` moves all pending tasks forward (spacing preserved) so the earliest pending one is due today.
- A skill that is still weak after the learner has a `TaskProgress` for it gets a "Reinforcement Checkpoint" task inserted as the next action. There is at most one pending per skill, and at most 2 per skill in total.
- A pending reinforcement is marked SKIPPED once evidence for its skill turns strong.
- Gaps from the onboarding baseline alone never trigger reinforcement.

Task completion is idempotent per (task, user) and only happens through `POST /tasks/{id}/complete`; closing a learning session (`PATCH /learning-sessions/{id}`) never completes the task. Progress counts SKIPPED tasks as resolved.

### Assessments
- **Never send answers to the client.** `GET /assessments/diagnostic-by-goal` returns questions without `correct_option_index`/`explanation` plus a `diagnostic_token` (HS256 JWT signed with `JWT_SECRET`, audience `skillalpha-diagnostic`) holding the answer key. `POST /roadmaps` takes `diagnostic_token` + `diagnostic_answers` (`{question_id: option_index}`) and grades them in `assessment_service.grade_diagnostic`. The client-graded `diagnostic_results` field is legacy (tests still use it).
- Diagnostic questions: Groq (each tagged with a `skill_name` from the goal's graph) or else the first curated question for up to 4 non-beginner skills on the goal's path.
- Skill quizzes (`GET /assessments/by-skill/{id}`): 3 questions from `services/question_bank.py` (curated, keyed by exact skill name; every skill in `GOAL_SKILL_GRAPHS` must have an entry), else Groq, else none (the UI hides an empty quiz). Old generic-template quizzes are rebuilt on read. The attempt response includes a per-question `review` with the correct option and explanation.
- Options are shuffled deterministically per question text by `shuffle_question_options`; author bank questions with the correct answer first.

### Resource matching
`resource_matcher.resolve_resource_matches` (`GET /api/resources/{id}/matches`) resolves a stored resource into concrete links:
- YouTube Data API search, cached for 7 days in two tiers: an in-process dict in front of the `resource_match_cache` table (`clear_cache()` clears both and is used in tests)
- Scoped doc/practice-site search URLs
- Book guidance

Tests mock `app.services.resource_matcher.httpx.Client` and patch `app.config.settings.YOUTUBE_DATA_API_KEY`.

### Frontend
- `App.tsx` owns the auth state. It syncs the Supabase session to the backend by calling `/auth/me` and mirrors the access token into `localStorage['skillalpha_token']`, which `getSupabaseToken` falls back to.
- `RequireAuth` in `App.tsx` guards the roadmap/learn/progress/saved/profile/admin routes using the Supabase session and redirects to `/login` with a return path. `/create` stays public: a signed-out user's onboarding request is parked in `localStorage['skillalpha_pending_roadmap']` and submitted after sign-up/login (or by `PendingRoadmapSubmitter` after Google OAuth).
- Shared UI: `components/ui/Toast.tsx` (`useToast()` for success/error feedback; don't swallow errors with `console.error`), `components/ui/Skeleton.tsx` (`PageSkeleton` for loading states), `components/layout/MobileTabBar.tsx` (bottom nav on phones, signed-in app sections only).
- Progress page reads `GET /users/me/activity` (streak, totals, 28-day series computed from `TaskProgress` + `AssessmentAttempt`).
- Pages live in `src/pages/` and fetch through `apiClient`. Shared types are in `src/types/index.ts`.
- `vercel.json` (root and `frontend/`) rewrites all paths to `index.html` for SPA routing.

### Design system
Tailwind tokens in `frontend/tailwind.config.js` follow Material-style naming (`surface`, `on-surface-variant`, `primary-container`, `secondary-container` = action orange, etc.) and resolve to CSS variables defined for light and dark in `src/index.css` (`:root` / `:root.dark`). Always use the tokens, never raw hex or `bg-white`, or dark mode breaks. The theme is the `dark` class on `<html>`: `index.html` sets it before first paint from `localStorage['skillalpha_theme']` (falling back to the OS setting) and `hooks/useTheme.ts` toggles it. Note `on-primary` is white in light mode but dark in dark mode. The design spec and reference mockups (HTML + screenshots) for each screen are in `stitch_skillalpha_learning_roadmap_frontend/`, with tokens in `modern_learning_intelligence/DESIGN.md`.
