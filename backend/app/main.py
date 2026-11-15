import uuid
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text

from app.config import settings
from app.models.db import Base, engine
from app.api.auth_router import router as auth_router
from app.api.user_router import router as user_router
from app.api.skill_router import router as skill_router
from app.api.roadmap_router import router as roadmap_router
from app.api.task_router import router as task_router
from app.api.resource_router import router as resource_router
from app.api.learning_router import router as learning_router
from app.api.assessment_router import router as assessment_router
from app.api.feedback_router import router as feedback_router
from app.api.admin_router import router as admin_router
from app.api.content_router import router as content_router

from app.models.db import Base, engine, SessionLocal
from app.models.models import Skill
from seed import seed_database

logger = logging.getLogger("skillalpha")

# Initialize database tables (creates missing tables, never alters existing ones)
Base.metadata.create_all(bind=engine)


def ensure_schema_upgrades() -> None:
    """
    Adds columns introduced after a table was first created, for databases not managed by
    Alembic (local SQLite, or a Postgres deploy before `alembic upgrade head` ran).
    Mirrors alembic/versions/7c1e2a9b4f10_*.py.
    """
    inspector = inspect(engine)
    if "roadmap_tasks" in inspector.get_table_names():
        columns = {c["name"] for c in inspector.get_columns("roadmap_tasks")}
        if "due_date" not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE roadmap_tasks ADD COLUMN due_date DATE"))
            logger.info("Added roadmap_tasks.due_date column")


try:
    ensure_schema_upgrades()
except Exception as e:
    logger.error(f"Schema upgrade check failed: {e}")

# Auto-seed database on startup if empty
try:
    db = SessionLocal()
    if db.query(Skill).count() == 0:
        logger.info("Database is empty. Auto-seeding initial ontology & resources...")
        seed_database()
    db.close()
except Exception as e:
    logger.error(f"Auto-seed check failed: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS: localhost for development plus FRONTEND_ORIGINS in production. Auth uses a bearer
# header (not cookies), so credentials are never needed cross-origin.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
configured_origins = [o.strip().rstrip("/") for o in settings.FRONTEND_ORIGINS.split(",") if o.strip()]
origins.extend(configured_origins)
if not configured_origins:
    logger.warning("FRONTEND_ORIGINS is not set; allowing any https:// origin. Set it in production.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=None if configured_origins else r"https://.*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safe Global Exception Handler - No raw stack trace leakage
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    ref_id = str(uuid.uuid4())[:8]
    logger.error(f"[Ref: {ref_id}] Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "meta": {"reference_id": ref_id},
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": f"An unexpected error occurred. Reference ID: {ref_id}"
            }
        }
    )

# Include API Routers under /api
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(user_router, prefix=settings.API_V1_STR)
app.include_router(skill_router, prefix=settings.API_V1_STR)
app.include_router(roadmap_router, prefix=settings.API_V1_STR)
app.include_router(task_router, prefix=settings.API_V1_STR)
app.include_router(resource_router, prefix=settings.API_V1_STR)
app.include_router(learning_router, prefix=settings.API_V1_STR)
app.include_router(assessment_router, prefix=settings.API_V1_STR)
app.include_router(feedback_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(content_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
