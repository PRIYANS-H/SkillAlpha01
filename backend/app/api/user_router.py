import json
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import User, Profile, UserSkill, TaskProgress, AssessmentAttempt
from app.schemas.schemas import ProfileUpdateRequest, APIResponse, ProfileResponse, UserSkillResponse
from app.security.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=APIResponse)
def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    prefs = json.loads(profile.learning_preferences) if profile.learning_preferences else ["VIDEO", "DOCUMENTATION", "PROJECT"]
    
    data = {
        "id": profile.id,
        "user_id": profile.user_id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "goal": profile.goal,
        "target_role": profile.target_role,
        "available_hours": profile.available_hours,
        "duration_weeks": profile.duration_weeks,
        "learning_preferences": prefs,
        "github_username": profile.github_username
    }
    return APIResponse(data=data)


@router.patch("/me", response_model=APIResponse)
def update_user_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    if req.goal is not None:
        profile.goal = req.goal
    if req.target_role is not None:
        profile.target_role = req.target_role
    if req.available_hours is not None:
        profile.available_hours = req.available_hours
    if req.duration_weeks is not None:
        profile.duration_weeks = req.duration_weeks
    if req.learning_preferences is not None:
        profile.learning_preferences = json.dumps(req.learning_preferences)
    if req.github_username is not None:
        profile.github_username = req.github_username

    db.commit()
    db.refresh(profile)
    return APIResponse(data={"message": "Profile updated successfully"})


@router.get("/me/skills", response_model=APIResponse)
def get_user_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    res = [
        {
            "id": us.id,
            "skill_id": us.skill_id,
            "skill_name": us.skill.name if us.skill else "Unknown Skill",
            "domain": us.skill.domain if us.skill else "",
            "skill_score": us.skill_score,
            "confidence_score": us.confidence_score,
            "status": us.status,
            "evidence_count": us.evidence_count,
            "last_assessed_at": us.last_assessed_at.isoformat() if us.last_assessed_at else None
        }
        for us in user_skills
    ]
    return APIResponse(data=res)


def _compute_streaks(active_days: set, today: datetime.date) -> tuple:
    """Returns (current_streak, longest_streak). The current streak survives until a full day is missed."""
    longest = run = 0
    previous = None
    for day in sorted(active_days):
        run = run + 1 if previous is not None and (day - previous).days == 1 else 1
        longest = max(longest, run)
        previous = day

    current = 0
    cursor = today if today in active_days else today - datetime.timedelta(days=1)
    while cursor in active_days:
        current += 1
        cursor -= datetime.timedelta(days=1)
    return current, longest


@router.get("/me/activity", response_model=APIResponse)
def get_user_activity(
    days: int = 28,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Real learning activity for the progress dashboard: study streak, totals, and a per-day
    series (minutes studied, tasks completed, quizzes taken) for the last `days` days (UTC).
    """
    days = max(7, min(days, 120))
    today = datetime.datetime.now(datetime.timezone.utc).date()

    progress = db.query(TaskProgress).filter(TaskProgress.user_id == current_user.id).all()
    attempts = db.query(AssessmentAttempt).filter(AssessmentAttempt.user_id == current_user.id).all()

    per_day = {}

    def bucket(moment) -> dict:
        return per_day.setdefault(moment.date(), {"minutes": 0, "tasks": 0, "quizzes": 0})

    for entry in progress:
        if entry.completed_at:
            b = bucket(entry.completed_at)
            b["tasks"] += 1
            b["minutes"] += entry.time_spent_minutes or 0
    for attempt in attempts:
        if attempt.completed_at:
            bucket(attempt.completed_at)["quizzes"] += 1

    current_streak, longest_streak = _compute_streaks(set(per_day), today)
    series = []
    for offset in range(days - 1, -1, -1):
        day = today - datetime.timedelta(days=offset)
        stats = per_day.get(day, {"minutes": 0, "tasks": 0, "quizzes": 0})
        series.append({"date": day.isoformat(), **stats})

    return APIResponse(data={
        "streak_days": current_streak,
        "longest_streak": longest_streak,
        "active_days": len(per_day),
        "total_minutes": sum(d["minutes"] for d in per_day.values()),
        "tasks_completed": sum(d["tasks"] for d in per_day.values()),
        "quizzes_taken": sum(d["quizzes"] for d in per_day.values()),
        "quizzes_passed": sum(1 for a in attempts if a.passed),
        "days": series,
    })
