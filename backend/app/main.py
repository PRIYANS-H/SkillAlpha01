import uuid
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# Initialize database tables
Base.metadata.create_all(bind=engine)

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

# Explicit CORS configuration with Vercel & Render production support
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com",
    allow_credentials=True,
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
