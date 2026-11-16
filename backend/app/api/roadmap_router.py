from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import Roadmap, RoadmapTask, User, Profile
from app.schemas.schemas import APIResponse, OnboardingRequest, BreakRequest
import json
import datetime
from app.security.auth import get_current_user
from app.services.roadmap_service import (
    generate_roadmap_for_user, adaptive_replan_roadmap, take_break, resume_from_break,
    schedule_summary, task_plan, task_steps_done, task_day_count
)
from app.services.project_bank import get_project
from app.services.skill_service import resolve_goal_family
from app.services.assessment_service import grade_diagnostic

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])

def serialize_task(t: RoadmapTask) -> dict:
    """One task as the client sees it, including its dated day-by-day plan."""
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

    kind = t.kind or "SKILL"
    plan = task_plan(t)
    done = task_steps_done(t)
    finished = t.status in ("COMPLETED", "SKIPPED")
    days = []
    for index, day in enumerate(plan.get("days") or []):
        date = t.due_date + datetime.timedelta(days=int(day.get("offset") or 0)) if t.due_date else None
        days.append({
            "index": index,
            "kind": day.get("kind"),
            "title": day.get("title"),
            "steps": day.get("steps") or [],
            "check": day.get("check"),
            "date": date.isoformat() if date else None,
            "done": finished or index in done,
        })

    data = {
        "id": t.id,
        "milestone_id": t.milestone_id,
        "skill_id": t.skill_id,
        "skill_name": t.skill.name if t.skill_id and t.skill else None,
        "title": t.title,
        "description": t.description,
        "estimated_minutes": t.estimated_minutes,
        "sequence_order": t.sequence_order,
        "status": t.status,
        "reason_why_next": t.reason_why_next,
        "due_date": t.due_date.isoformat() if t.due_date else None,
        "kind": kind,
        "ref_id": t.ref_id,
        "day_count": task_day_count(t),
        "days": days,
        "resources": resources_data
    }
    if kind == "PROJECT":
        project = get_project(t.ref_id or "")
        data["project"] = {
            "id": project["id"], "title": project["title"], "level": project["level"],
            "dataset": project["dataset"], "estimated_hours": project["estimated_hours"],
        } if project else None
    if kind == "MILESTONE_CHECK":
        data["milestone_check"] = {
            "phase": plan.get("phase"),
            "skills": plan.get("skills") or [],
            "pass_percent": int(round(float(plan.get("pass_ratio") or 0.7) * 100)),
        }
    return data


def serialize_roadmap(rm: Roadmap) -> dict:
    milestones_data = []
    for m in sorted(rm.milestones, key=lambda x: x.sequence_order):
        milestones_data.append({
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "week_number": m.week_number,
            "sequence_order": m.sequence_order,
            "is_completed": m.is_completed,
            "tasks": [serialize_task(t) for t in sorted(m.tasks, key=lambda x: x.sequence_order)]
        })

    return {
        "id": rm.id,
        "user_id": rm.user_id,
        "title": rm.title,
        "goal": rm.goal,
        "goal_family": resolve_goal_family(rm.goal),
        "duration_weeks": rm.duration_weeks,
        "hours_per_week": rm.hours_per_week,
        "total_tasks": rm.total_tasks,
        "completed_tasks": rm.completed_tasks,
        "progress_percent": rm.progress_percent,
        "route_reasoning": rm.route_reasoning,
        "is_active": rm.is_active,
        "created_at": rm.created_at.isoformat() if rm.created_at else None,
        "schedule": schedule_summary(rm),
        "milestones": milestones_data
    }


@router.post("", response_model=APIResponse)
def create_roadmap(req: OnboardingRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    self_reported = {
        item.skill_name.lower(): item.self_reported_level
        for item in req.known_skills
    }
    diagnostic = grade_diagnostic(req.diagnostic_token, req.diagnostic_answers)
    for result in req.diagnostic_results:
        correct, total = diagnostic.get(result.skill_name.lower(), (0, 0))
        diagnostic[result.skill_name.lower()] = (correct + int(result.is_correct), total + 1)
    roadmap = generate_roadmap_for_user(
        db=db,
        user_id=current_user.id,
        goal=req.goal,
        hours_per_week=req.available_hours,
        duration_weeks=req.duration_weeks,
        self_reported_skills=self_reported,
        preferred_types=req.learning_preferences,
        diagnostic_results=diagnostic,
        study_days_per_week=req.study_days_per_week
    )

    # Sync onboarding profile details
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
    profile.goal = req.goal
    profile.available_hours = req.available_hours
    profile.duration_weeks = req.duration_weeks
    profile.learning_preferences = json.dumps(req.learning_preferences)
    db.commit()

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


@router.post("/{roadmap_id}/break", response_model=APIResponse)
def take_roadmap_break(roadmap_id: str, req: BreakRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Pauses the plan for a number of days; pending work moves later and nothing counts as overdue."""
    rm = take_break(db, roadmap_id, current_user.id, req.days)
    if not rm:
        return APIResponse(error={"code": "NOT_FOUND", "message": "Roadmap not found"})
    return APIResponse(data=serialize_roadmap(rm))


@router.post("/{roadmap_id}/resume", response_model=APIResponse)
def resume_roadmap(roadmap_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Ends a break early: the next task becomes due today."""
    rm = resume_from_break(db, roadmap_id, current_user.id)
    if not rm:
        return APIResponse(error={"code": "NOT_FOUND", "message": "Roadmap not found"})
    return APIResponse(data=serialize_roadmap(rm))
