from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import Roadmap, User
from app.schemas.schemas import APIResponse, OnboardingRequest
from app.security.auth import get_current_user
from app.services.roadmap_service import generate_roadmap_for_user, adaptive_replan_roadmap

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])

def serialize_roadmap(rm: Roadmap) -> dict:
    milestones_data = []
    for m in sorted(rm.milestones, key=lambda x: x.sequence_order):
        tasks_data = []
        for t in sorted(m.tasks, key=lambda x: x.sequence_order):
            resources_data = []
            for tr in sorted(t.task_resources, key=lambda x: x.sequence_order):
                r = tr.resource
                if r:
                    resources_data.append({
                        "resource_id": r.id,
                        "title": r.title,
                        "url": r.url,
                        "provider": r.provider,
                        "resource_type": r.resource_type,
                        "duration_minutes": r.duration_minutes,
                        "recommendation_match_score": tr.recommendation_match_score,
                        "recommendation_reason": tr.recommendation_reason
                    })
            tasks_data.append({
                "id": t.id,
                "milestone_id": t.milestone_id,
                "skill_id": t.skill_id,
                "title": t.title,
                "description": t.description,
                "estimated_minutes": t.estimated_minutes,
                "sequence_order": t.sequence_order,
                "status": t.status,
                "reason_why_next": t.reason_why_next,
                "resources": resources_data
            })
        milestones_data.append({
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "week_number": m.week_number,
            "sequence_order": m.sequence_order,
            "is_completed": m.is_completed,
            "tasks": tasks_data
        })

    return {
        "id": rm.id,
        "user_id": rm.user_id,
        "title": rm.title,
        "goal": rm.goal,
        "duration_weeks": rm.duration_weeks,
        "hours_per_week": rm.hours_per_week,
        "total_tasks": rm.total_tasks,
        "completed_tasks": rm.completed_tasks,
        "progress_percent": rm.progress_percent,
        "route_reasoning": rm.route_reasoning,
        "is_active": rm.is_active,
        "created_at": rm.created_at.isoformat() if rm.created_at else None,
        "milestones": milestones_data
    }


@router.post("", response_model=APIResponse)
def create_roadmap(req: OnboardingRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    self_reported = {
        item.skill_name.lower(): item.self_reported_level
        for item in req.known_skills
    }
    roadmap = generate_roadmap_for_user(
        db=db,
        user_id=current_user.id,
        goal=req.goal,
        hours_per_week=req.available_hours,
        duration_weeks=req.duration_weeks,
        self_reported_skills=self_reported,
        preferred_types=req.learning_preferences
    )
    return APIResponse(data=serialize_roadmap(roadmap))


@router.get("", response_model=APIResponse)
def get_user_roadmaps(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    roadmaps = db.query(Roadmap).filter(Roadmap.user_id == current_user.id).order_by(Roadmap.created_at.desc()).all()
    res = [serialize_roadmap(r) for r in roadmaps]
    return APIResponse(data=res)


@router.get("/{roadmap_id}", response_model=APIResponse)
def get_roadmap_by_id(roadmap_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rm = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == current_user.id).first()
    if not rm:
        return APIResponse(error={"code": "NOT_FOUND", "message": "Roadmap not found"})
    return APIResponse(data=serialize_roadmap(rm))


@router.post("/{roadmap_id}/repace", response_model=APIResponse)
def repace_roadmap(roadmap_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rm = adaptive_replan_roadmap(db, roadmap_id, current_user.id)
    if not rm:
        return APIResponse(error={"code": "NOT_FOUND", "message": "Roadmap not found"})
    return APIResponse(data=serialize_roadmap(rm))
