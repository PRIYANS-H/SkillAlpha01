import datetime
import json
import math
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.models import ProjectSubmission, Roadmap, RoadmapMilestone, RoadmapTask, TaskProgress, User
from app.schemas.schemas import APIResponse, ProjectSubmitRequest
from app.security.auth import get_current_user
from app.services.project_bank import PROJECT_BANK, get_project, family_of, projects_for_family
from app.services.roadmap_service import recalculate_roadmap_progress
from app.services.skill_service import resolve_goal_family

router = APIRouter(prefix="/projects", tags=["Projects"])

PASS_RATIO = 0.6  # share of checklist items that must be met for a project to count as done

FAMILY_LABELS = {
    "quant_finance": "Quant Finance", "machine_learning": "Machine Learning", "data_science": "Data Science",
    "backend": "Backend", "frontend": "Frontend", "data_engineering": "Data Engineering", "devops": "DevOps",
    "security": "Security", "mobile": "Mobile", "general": "General Software",
}


def _active_roadmap(db: Session, user: User) -> Optional[Roadmap]:
    return db.query(Roadmap).filter(
        Roadmap.user_id == user.id, Roadmap.is_active == True
    ).order_by(Roadmap.created_at.desc()).first()


def _serialize_submission(s: Optional[ProjectSubmission], rubric_len: int) -> Optional[dict]:
    if not s:
        return None
    try:
        checklist = json.loads(s.checklist_json)
    except ValueError:
        checklist = []
    checklist = (list(checklist) + [False] * rubric_len)[:rubric_len]
    return {
        "url": s.url,
        "notes": s.notes,
        "checklist": checklist,
        "score": s.score,
        "passed": (s.score or 0) >= PASS_RATIO,
        "submitted_at": s.updated_at.isoformat() if s.updated_at else None,
    }


def _serialize_project(project: dict, family: str, submission: Optional[ProjectSubmission]) -> dict:
    return {
        **project,
        "family": family,
        "family_label": FAMILY_LABELS.get(family, family),
        "pass_items": math.ceil(len(project["rubric"]) * PASS_RATIO),
        "submission": _serialize_submission(submission, len(project["rubric"])),
    }


@router.get("", response_model=APIResponse)
def list_projects(
    family: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Projects for a goal family with the learner's submissions. Defaults to the family of
    their active roadmap; family=all lists every track.
    """
    roadmap = _active_roadmap(db, current_user)
    own_family = resolve_goal_family(roadmap.goal) if roadmap else None
    submissions: Dict[str, ProjectSubmission] = {
        s.project_id: s for s in db.query(ProjectSubmission).filter(ProjectSubmission.user_id == current_user.id).all()
    }

    if family == "all" or (not family and not own_family):
        families = list(PROJECT_BANK)
    else:
        chosen = family or own_family
        if chosen not in PROJECT_BANK:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown project track.")
        families = [chosen]

    projects = [
        _serialize_project(p, fam, submissions.get(p["id"]))
        for fam in families for p in projects_for_family(fam)
    ]
    return APIResponse(data={
        "family": families[0] if len(families) == 1 else "all",
        "own_family": own_family,
        "families": [{"key": k, "label": FAMILY_LABELS.get(k, k)} for k in PROJECT_BANK],
        "projects": projects,
        "completed": sum(1 for p in projects if p["submission"] and p["submission"]["passed"]),
    })


@router.post("/{project_id}/submit", response_model=APIResponse)
def submit_project(
    project_id: str,
    req: ProjectSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Saves a project link and self-graded checklist (resubmitting replaces the earlier one).
    When enough checklist items are met, the matching project task on the learner's active
    roadmap is completed.
    """
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    url = req.url.strip()
    if not (url.startswith("https://") or url.startswith("http://")) or " " in url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enter a full link starting with https://")

    rubric_len = len(project["rubric"])
    checklist = ([bool(v) for v in req.checklist] + [False] * rubric_len)[:rubric_len]
    score = round(sum(checklist) / float(rubric_len), 2) if rubric_len else 0.0

    submission = db.query(ProjectSubmission).filter(
        ProjectSubmission.user_id == current_user.id, ProjectSubmission.project_id == project_id
    ).first()
    if not submission:
        submission = ProjectSubmission(user_id=current_user.id, project_id=project_id, url=url, checklist_json="[]")
        db.add(submission)
    submission.url = url
    submission.notes = (req.notes or "").strip() or None
    submission.checklist_json = json.dumps(checklist)
    submission.score = score
    submission.updated_at = datetime.datetime.now(datetime.timezone.utc)

    task_completed = False
    passed = score >= PASS_RATIO
    roadmap = _active_roadmap(db, current_user)
    if passed and roadmap:
        task = db.query(RoadmapTask).join(RoadmapMilestone).filter(
            RoadmapMilestone.roadmap_id == roadmap.id,
            RoadmapTask.kind == "PROJECT",
            RoadmapTask.ref_id == project_id,
            RoadmapTask.status.in_(["NOT_STARTED", "IN_PROGRESS"])
        ).first()
        if task:
            task.status = "COMPLETED"
            db.add(TaskProgress(
                task_id=task.id,
                user_id=current_user.id,
                completed_at=datetime.datetime.now(datetime.timezone.utc),
                time_spent_minutes=0,
                self_evaluation=None
            ))
            db.flush()
            recalculate_roadmap_progress(roadmap)
            task_completed = True

    db.commit()
    db.refresh(submission)
    return APIResponse(data={
        "project_id": project_id,
        "family": family_of(project_id),
        "submission": _serialize_submission(submission, rubric_len),
        "passed": passed,
        "task_completed": task_completed,
        "items_needed": math.ceil(rubric_len * PASS_RATIO),
    })
