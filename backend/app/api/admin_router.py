from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import (
    User, Roadmap, Resource, TaskResource, ResourceFeedback, AuditLog, Skill
)
from app.schemas.schemas import APIResponse
from app.security.auth import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["Admin Portal"])

@router.get("/metrics", response_model=APIResponse)
def get_admin_metrics(admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    active_users = db.query(User).filter(User.is_active == True).count()
    roadmaps_created = db.query(Roadmap).count()
    resources_indexed = db.query(Resource).count()
    recommendations_served = db.query(TaskResource).count()
    
    feedbacks = db.query(ResourceFeedback).all()
    positive_fb = sum(1 for f in feedbacks if f.is_useful)
    save_rate = round((positive_fb / float(len(feedbacks))) * 100, 1) if feedbacks else 0.0

    completed_roadmaps = db.query(Roadmap).filter(Roadmap.progress_percent >= 100.0).count()
    completion_rate = round((completed_roadmaps / float(roadmaps_created)) * 100, 1) if roadmaps_created else 0.0

    avg_score = 0.0
    if feedbacks:
        # Assuming resource feedback usefulness is binary or has feedback scores
        avg_score = round(sum(1.0 if f.is_useful else 0.0 for f in feedbacks) / float(len(feedbacks)) * 5.0, 1)

    return APIResponse(data={
        "active_users": active_users,
        "roadmaps_created": roadmaps_created,
        "resources_indexed": resources_indexed,
        "recommendations_served": recommendations_served,
        "save_rate_percent": save_rate,
        "completion_rate_percent": completion_rate,
        "avg_feedback_score": avg_score
    })



@router.get("/resources", response_model=APIResponse)
def get_admin_resources(admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    resources = db.query(Resource).order_by(Resource.created_at.desc()).limit(100).all()
    res = [
        {
            "id": r.id,
            "title": r.title,
            "provider": r.provider,
            "resource_type": r.resource_type,
            "quality_score": r.quality_score,
            "verified": r.verified,
            "url": r.url
        }
        for r in resources
    ]
    return APIResponse(data=res)


@router.patch("/resources/{resource_id}", response_model=APIResponse)
def toggle_resource_verification(
    resource_id: str,
    verified: bool,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        return APIResponse(error={"code": "NOT_FOUND", "message": "Resource not found"})
    resource.verified = verified
    db.commit()
    return APIResponse(data={"message": f"Resource verification set to {verified}"})


@router.get("/skills", response_model=APIResponse)
def get_admin_skills(admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    res = [
        {
            "id": s.id,
            "name": s.name,
            "domain": s.domain,
            "difficulty": s.difficulty,
            "description": s.description
        }
        for s in skills
    ]
    return APIResponse(data=res)


@router.get("/audit", response_model=APIResponse)
def get_admin_audit_logs(admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(50).all()
    res = [
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "resource_type": l.resource_type,
            "details": l.details,
            "created_at": l.created_at.isoformat()
        }
        for l in logs
    ]
    return APIResponse(data=res)
