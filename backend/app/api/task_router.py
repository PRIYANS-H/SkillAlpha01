import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import RoadmapTask, TaskProgress, Roadmap, RoadmapMilestone, User
from app.schemas.schemas import APIResponse, TaskCompleteRequest
from app.security.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/{task_id}/complete", response_model=APIResponse)
def complete_task(
    task_id: str,
    req: TaskCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Enforce strict user ownership verification: task -> milestone -> roadmap -> user_id
    task = db.query(RoadmapTask).join(RoadmapMilestone).join(Roadmap).filter(
        RoadmapTask.id == task_id,
        Roadmap.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied."
        )

    task.status = "COMPLETED"

    progress_entry = TaskProgress(
        task_id=task.id,
        user_id=current_user.id,
        completed_at=datetime.datetime.utcnow(),
        time_spent_minutes=req.time_spent_minutes,
        self_evaluation=req.self_evaluation
    )
    db.add(progress_entry)

    # Evidence-based learning loop: update UserSkill status if self-evaluation indicates reinforcement needed
    if req.self_evaluation in ["SHAKY", "LOST"] and task.skill_id:
        from app.models.models import UserSkill
        user_skill = db.query(UserSkill).filter(
            UserSkill.user_id == current_user.id,
            UserSkill.skill_id == task.skill_id
        ).first()
        if not user_skill:
            user_skill = UserSkill(
                user_id=current_user.id,
                skill_id=task.skill_id,
                skill_score=0.40,
                confidence_score=0.35,
                status="NEEDS_REINFORCEMENT",
                evidence_count=1
            )
            db.add(user_skill)
        else:
            user_skill.status = "NEEDS_REINFORCEMENT"
            user_skill.confidence_score = max(0.20, (user_skill.confidence_score or 0.5) - 0.15)
            user_skill.evidence_count = (user_skill.evidence_count or 0) + 1

    # Recalculate roadmap overall progress percentage
    milestone = task.milestone
    if milestone:
        roadmap = milestone.roadmap
        if roadmap:
            all_tasks = []
            for m in roadmap.milestones:
                all_tasks.extend(m.tasks)
            comp_count = sum(1 for t in all_tasks if t.status == "COMPLETED")
            roadmap.completed_tasks = comp_count
            roadmap.progress_percent = round((comp_count / float(len(all_tasks))) * 100, 1) if all_tasks else 0.0

    db.commit()
    return APIResponse(data={"message": "Task completed successfully", "status": "COMPLETED"})
