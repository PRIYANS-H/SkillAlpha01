import datetime
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.models import Roadmap, RoadmapMilestone, RoadmapTask, Skill, TaskProgress, User, UserSkill
from app.schemas.schemas import APIResponse, MilestoneAttemptRequest
from app.security.auth import get_current_user
from app.services.assessment_service import shuffle_question_options
from app.services.gap_engine import record_skill_evidence, blend_assessment_score
from app.services.question_bank import get_bank_questions
from app.services.roadmap_service import adapt_roadmap_to_evidence, task_plan

router = APIRouter(prefix="/milestone-checks", tags=["Milestone Checks"])

MAX_QUESTIONS = 10


def _check_task(db: Session, task_id: str, user: User) -> RoadmapTask:
    task = db.query(RoadmapTask).join(RoadmapMilestone).join(Roadmap).filter(
        RoadmapTask.id == task_id,
        Roadmap.user_id == user.id
    ).first()
    if not task or (task.kind or "SKILL") != "MILESTONE_CHECK":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone check not found or access denied.")
    return task


def build_check_questions(skill_names: List[str]) -> List[Dict]:
    """
    A mixed quiz for a phase, drawn from the curated bank. Deterministic for a given skill
    list, so the server can rebuild it to grade an attempt without storing it. Uses each
    skill's later questions first: the onboarding diagnostic already used the first one.
    """
    per_skill = 2 if len(skill_names) <= MAX_QUESTIONS // 2 else 1
    questions = []
    for skill_index, name in enumerate(skill_names):
        bank = get_bank_questions(name)
        picks = list(range(len(bank)))[::-1][:per_skill]
        for question_index in sorted(picks):
            text, options, correct_index, explanation = bank[question_index]
            shuffled = shuffle_question_options({
                "question_text": text, "options": options,
                "correct_option_index": correct_index, "explanation": explanation,
            })
            questions.append({"id": f"{skill_index}-{question_index}", "skill_name": name, **shuffled})
    return questions[:MAX_QUESTIONS]


@router.get("/{task_id}", response_model=APIResponse)
def get_milestone_check(task_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = _check_task(db, task_id, current_user)
    plan = task_plan(task)
    questions = build_check_questions(plan.get("skills") or [])
    return APIResponse(data={
        "task_id": task.id,
        "title": task.title,
        "phase": plan.get("phase"),
        "skills": plan.get("skills") or [],
        "pass_percent": int(round(float(plan.get("pass_ratio") or 0.7) * 100)),
        "status": task.status,
        # Answers and explanations stay on the server until the attempt is graded
        "questions": [
            {"id": q["id"], "skill_name": q["skill_name"], "question_text": q["question_text"], "options": q["options"]}
            for q in questions
        ],
    })


@router.post("/{task_id}/attempt", response_model=APIResponse)
def attempt_milestone_check(
    task_id: str,
    req: MilestoneAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Grades the phase quiz. Every skill's result is recorded as evidence. A pass completes the
    task; a fail leaves it open, and skills that came out weak get a reinforcement task first.
    """
    task = _check_task(db, task_id, current_user)
    plan = task_plan(task)
    pass_ratio = float(plan.get("pass_ratio") or 0.7)
    questions = build_check_questions(plan.get("skills") or [])
    if not questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This milestone check has no questions.")

    review = []
    per_skill: Dict[str, List[int]] = {}
    correct_total = 0
    for q in questions:
        choice = req.answers.get(q["id"])
        is_correct = choice is not None and choice == q["correct_option_index"]
        correct_total += int(is_correct)
        tally = per_skill.setdefault(q["skill_name"], [0, 0])
        tally[0] += int(is_correct)
        tally[1] += 1
        review.append({
            "question_id": q["id"],
            "skill_name": q["skill_name"],
            "selected_option_index": choice,
            "correct_option_index": q["correct_option_index"],
            "is_correct": is_correct,
            "explanation": q.get("explanation"),
        })

    weak_skills = []
    for name, (correct, total) in per_skill.items():
        skill = db.query(Skill).filter(Skill.name == name).first()
        if not skill:
            continue
        user_skill = db.query(UserSkill).filter(
            UserSkill.user_id == current_user.id, UserSkill.skill_id == skill.id
        ).first()
        old_score = user_skill.skill_score if user_skill else 0.40
        record_skill_evidence(
            db, current_user.id, skill.id,
            new_score=blend_assessment_score(old_score, correct / float(total)),
            new_confidence=(user_skill.confidence_score if user_skill else 0.5) + 0.10,
            user_skill=user_skill
        )
        if correct < total:
            weak_skills.append(name)

    ratio = correct_total / float(len(questions))
    passed = ratio >= pass_ratio
    if passed and task.status != "COMPLETED":
        task.status = "COMPLETED"
        db.add(TaskProgress(
            task_id=task.id,
            user_id=current_user.id,
            completed_at=datetime.datetime.now(datetime.timezone.utc),
            time_spent_minutes=max(0, req.time_spent_minutes),
            self_evaluation=None
        ))

    adaptation = None
    roadmap = task.milestone.roadmap if task.milestone else None
    if roadmap:
        reinforced, cleared = adapt_roadmap_to_evidence(db, roadmap, current_user.id)
        if reinforced or cleared:
            adaptation = {"reinforced_skills": reinforced, "cleared_skills": cleared, "route_reasoning": roadmap.route_reasoning}
    db.commit()

    percent = int(round(ratio * 100))
    if passed:
        feedback = f"You scored {percent}% and passed this phase. Your skill scores were updated from each answer."
    else:
        feedback = (
            f"You scored {percent}%; the pass mark is {int(round(pass_ratio * 100))}%. "
            f"Review {', '.join(weak_skills[:3]) or 'the explanations'} and take the check again."
        )
    return APIResponse(data={
        "task_id": task.id,
        "score": correct_total,
        "max_score": len(questions),
        "percent": percent,
        "passed": passed,
        "pass_percent": int(round(pass_ratio * 100)),
        "weak_skills": weak_skills,
        "feedback": feedback,
        "review": review,
        "adaptation": adaptation,
    })
