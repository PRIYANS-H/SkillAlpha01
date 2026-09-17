import json
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import Assessment, Skill, User
from app.schemas.schemas import APIResponse, AssessmentAttemptRequest
from app.security.auth import get_current_user
from app.services.assessment_service import (
    get_or_create_assessment_for_skill, evaluate_assessment_attempt, get_diagnostic_questions_for_goal
)

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.get("/diagnostic-by-goal", response_model=APIResponse)
def get_diagnostic_by_goal(goal: str = Query("Become a Machine Learning Engineer")):
    questions = get_diagnostic_questions_for_goal(goal)
    return APIResponse(data={
        "goal": goal,
        "questions": questions
    })


@router.get("/by-skill/{skill_id}", response_model=APIResponse)
def get_assessment_for_skill(skill_id: str, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        return APIResponse(error={"code": "NOT_FOUND", "message": "Skill not found"})

    assessment = get_or_create_assessment_for_skill(db, skill)
    
    questions_data = [
        {
            "id": q.id,
            "question_text": q.question_text,
            "options": json.loads(q.options_json),
            "explanation": q.explanation
        }
        for q in assessment.questions
    ]

    return APIResponse(data={
        "id": assessment.id,
        "skill_id": assessment.skill_id,
        "skill_name": skill.name,
        "title": assessment.title,
        "description": assessment.description,
        "difficulty": assessment.difficulty,
        "questions": questions_data
    })


@router.post("/{assessment_id}/attempt", response_model=APIResponse)
def submit_assessment_attempt(
    assessment_id: str,
    req: AssessmentAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempt, new_score, feedback = evaluate_assessment_attempt(
        db=db,
        user_id=current_user.id,
        assessment_id=assessment_id,
        answers=req.answers
    )

    if not attempt:
        return APIResponse(error={"code": "NOT_FOUND", "message": "Assessment evaluation failed"})

    return APIResponse(data={
        "attempt_id": attempt.id,
        "score": attempt.score,
        "max_score": attempt.max_score,
        "passed": attempt.passed,
        "new_skill_score": new_score,
        "feedback": feedback
    })
