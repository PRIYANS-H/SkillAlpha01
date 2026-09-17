import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import RoadmapTask, RoadmapMilestone, Roadmap, LearningSession, User
from app.schemas.schemas import APIResponse
from app.security.auth import get_current_user

router = APIRouter(tags=["Learning & Recommendations"])

@router.get("/recommendations/today", response_model=APIResponse)
def get_today_learning(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    active_roadmap = db.query(Roadmap).filter(
        Roadmap.user_id == current_user.id,
        Roadmap.is_active == True
    ).order_by(Roadmap.created_at.desc()).first()

    if not active_roadmap:
        return APIResponse(data={
            "task": None,
            "milestone_title": None,
            "roadmap_id": None,
            "total_due_today": 0,
            "reason_why_today": "No active roadmap found. Complete onboarding to build your personalized plan."
        })

    next_task = None
    milestone_title = None

    for m in sorted(active_roadmap.milestones, key=lambda x: x.sequence_order):
        for t in sorted(m.tasks, key=lambda x: x.sequence_order):
            if t.status in ["NOT_STARTED", "IN_PROGRESS"]:
                next_task = t
                milestone_title = m.title
                break
        if next_task:
            break

    if not next_task:
        return APIResponse(data={
            "task": None,
            "milestone_title": "Roadmap Completed",
            "roadmap_id": active_roadmap.id,
            "total_due_today": 0,
            "reason_why_today": "Congratulations! You have completed all tasks in your roadmap."
        })

    resources_data = []
    for tr in sorted(next_task.task_resources, key=lambda x: x.sequence_order):
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

    task_data = {
        "id": next_task.id,
        "milestone_id": next_task.milestone_id,
        "skill_id": next_task.skill_id,
        "title": next_task.title,
        "description": next_task.description,
        "estimated_minutes": next_task.estimated_minutes,
        "sequence_order": next_task.sequence_order,
        "status": next_task.status,
        "reason_why_next": next_task.reason_why_next,
        "resources": resources_data
    }

    return APIResponse(data={
        "task": task_data,
        "milestone_title": milestone_title,
        "roadmap_id": active_roadmap.id,
        "total_due_today": 1,
        "reason_why_today": next_task.reason_why_next or "Primary recommended action to bridge your current skill gap."
    })


@router.post("/learning-sessions", response_model=APIResponse)
def start_learning_session(task_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Enforce task ownership: task -> milestone -> roadmap -> user_id
    task = db.query(RoadmapTask).join(RoadmapMilestone).join(Roadmap).filter(
        RoadmapTask.id == task_id,
        Roadmap.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied."
        )

    task.status = "IN_PROGRESS"
    
    session = LearningSession(
        user_id=current_user.id,
        task_id=task_id,
        status="IN_PROGRESS"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return APIResponse(data={"session_id": session.id, "status": "IN_PROGRESS"})


@router.patch("/learning-sessions/{session_id}", response_model=APIResponse)
def update_learning_session(
    session_id: str,
    duration_seconds: int = 0,
    notes: str = None,
    status: str = "COMPLETED",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found or access denied."
        )

    session.duration_seconds = duration_seconds
    if notes:
        session.notes = notes
    session.status = status
    if status == "COMPLETED":
        session.ended_at = datetime.datetime.utcnow()
        if session.task:
            session.task.status = "COMPLETED"

    db.commit()
    return APIResponse(data={"message": "Session updated successfully"})
