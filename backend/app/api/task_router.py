import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import RoadmapTask, TaskProgress, Roadmap, RoadmapMilestone, User, UserSkill
from app.schemas.schemas import APIResponse, TaskCompleteRequest, TaskStepRequest
from app.security.auth import get_current_user
from app.services.gap_engine import record_skill_evidence
from app.services.roadmap_service import adapt_roadmap_to_evidence, task_plan, task_steps_done

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

    # Milestone checks and projects are finished by passing the quiz / submitting the work
    kind = task.kind or "SKILL"
    if kind == "MILESTONE_CHECK" and task.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pass the milestone check quiz to complete this task."
        )
    if kind == "PROJECT" and task.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submit your project link and checklist to complete this task."
        )

    # Idempotent: a repeated submission must not count the same evidence twice
    already_recorded = db.query(TaskProgress).filter(
        TaskProgress.task_id == task.id,
        TaskProgress.user_id == current_user.id
    ).first()
    if already_recorded:
        return APIResponse(data={"message": "Task already completed", "status": "COMPLETED", "adaptation": None})

    task.status = "COMPLETED"

    progress_entry = TaskProgress(
        task_id=task.id,
        user_id=current_user.id,
        completed_at=datetime.datetime.now(datetime.timezone.utc),
        time_spent_minutes=req.time_spent_minutes,
        self_evaluation=req.self_evaluation
    )
    db.add(progress_entry)

    # Evidence-based learning loop: update UserSkill based on self-evaluation
    if task.skill_id and req.self_evaluation in ["GOT_IT", "SHAKY", "LOST"]:
        user_skill = db.query(UserSkill).filter(
            UserSkill.user_id == current_user.id,
            UserSkill.skill_id == task.skill_id
        ).first()
        old_score = user_skill.skill_score if user_skill else None
        old_confidence = user_skill.confidence_score if user_skill else None

        if req.self_evaluation == "GOT_IT":
            # Solid after studying: at least STRONG
            new_score = max(0.65, (old_score if old_score is not None else 0.60) + 0.15)
            new_confidence = (old_confidence or 0.70) + 0.10
        else:
            # Studied but not solid: lands in the reinforcement band
            new_score = min(max(old_score if old_score is not None else 0.40, 0.40), 0.60)
            new_confidence = max(0.20, (old_confidence or 0.5) - 0.15)

        record_skill_evidence(db, current_user.id, task.skill_id, new_score, new_confidence, user_skill)

    # Recalculate progress and adapt the route to the new evidence
    adaptation = None
    roadmap = task.milestone.roadmap if task.milestone else None
    if roadmap:
        reinforced, _ = adapt_roadmap_to_evidence(db, roadmap, current_user.id)
        if reinforced:
            adaptation = {"reinforced_skills": reinforced, "route_reasoning": roadmap.route_reasoning}

    db.commit()
    return APIResponse(data={"message": "Task completed successfully", "status": "COMPLETED", "adaptation": adaptation})


@router.post("/{task_id}/steps", response_model=APIResponse)
def set_task_step(
    task_id: str,
    req: TaskStepRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ticks one day of a task's day-by-day plan on or off. Does not complete the task."""
    from app.api.roadmap_router import serialize_task

    task = db.query(RoadmapTask).join(RoadmapMilestone).join(Roadmap).filter(
        RoadmapTask.id == task_id,
        Roadmap.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or access denied.")

    day_total = len(task_plan(task).get("days") or [])
    if req.index >= day_total:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This task has no such study day.")

    done = set(task_steps_done(task))
    if req.done:
        done.add(req.index)
    else:
        done.discard(req.index)
    task.steps_done = json.dumps(sorted(done))
    if task.status == "NOT_STARTED" and done:
        task.status = "IN_PROGRESS"
    db.commit()
    return APIResponse(data=serialize_task(task))
