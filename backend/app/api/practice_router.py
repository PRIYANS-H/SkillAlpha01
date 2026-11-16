import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.models import ProblemAttempt, Roadmap, User
from app.schemas.schemas import APIResponse, ProblemSubmitRequest, ProblemMarkRequest
from app.security.auth import get_current_user
from app.services.problem_bank import (
    PROBLEM_BANK, POINTS, get_problem, skill_of, public_view, grade, correct_answer_text
)
from app.services.skill_service import get_goal_skill_specs

router = APIRouter(prefix="/problems", tags=["Practice"])

DIFFICULTIES = ("EASY", "MEDIUM", "HARD")
REVEAL_AFTER_ATTEMPTS = 2  # wrong tries before the answer and explanation are shown


def _roadmap_skill_names(db: Session, user: User) -> List[str]:
    """Skills on the learner's goal path, in path order; empty when they have no roadmap."""
    roadmap = db.query(Roadmap).filter(
        Roadmap.user_id == user.id, Roadmap.is_active == True
    ).order_by(Roadmap.created_at.desc()).first()
    if not roadmap:
        return []
    return [name for name, _, _ in get_goal_skill_specs(roadmap.goal)]


def _attempts_by_problem(db: Session, user: User) -> Dict[str, ProblemAttempt]:
    return {a.problem_id: a for a in db.query(ProblemAttempt).filter(ProblemAttempt.user_id == user.id).all()}


def _stats(attempts: Dict[str, ProblemAttempt], skill_names: List[str]) -> dict:
    by_difficulty = {d: {"solved": 0, "total": 0} for d in DIFFICULTIES}
    solved = total = 0
    for name in skill_names:
        for problem in PROBLEM_BANK.get(name, []):
            total += 1
            by_difficulty[problem["difficulty"]]["total"] += 1
            attempt = attempts.get(problem["id"])
            if attempt and attempt.solved:
                solved += 1
                by_difficulty[problem["difficulty"]]["solved"] += 1

    solved_days = {a.solved_at.date() for a in attempts.values() if a.solved and a.solved_at}
    today = datetime.datetime.now(datetime.timezone.utc).date()
    streak = 0
    cursor = today if today in solved_days else today - datetime.timedelta(days=1)
    while cursor in solved_days:
        streak += 1
        cursor -= datetime.timedelta(days=1)
    return {
        "solved": solved,
        "total": total,
        "points": sum(a.points or 0 for a in attempts.values()),
        "by_difficulty": by_difficulty,
        "streak_days": streak,
    }


@router.get("", response_model=APIResponse)
def list_problems(
    scope: str = Query("roadmap", pattern="^(roadmap|all)$"),
    skill: Optional[str] = None,
    difficulty: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Practice problems with the learner's status on each. scope=roadmap (default) limits the
    set to the skills on their goal path; scope=all shows every skill. Answers are never sent.
    """
    path_skills = _roadmap_skill_names(db, current_user)
    in_scope = [n for n in path_skills if n in PROBLEM_BANK] if scope == "roadmap" and path_skills else list(PROBLEM_BANK)
    attempts = _attempts_by_problem(db, current_user)

    problems = []
    for name in in_scope:
        if skill and name != skill:
            continue
        for problem in PROBLEM_BANK[name]:
            if difficulty and problem["difficulty"] != difficulty.upper():
                continue
            view = public_view(problem, name)
            attempt = attempts.get(problem["id"])
            view["solved"] = bool(attempt and attempt.solved)
            view["attempts"] = attempt.attempts if attempt else 0
            view["points_earned"] = attempt.points if attempt else 0
            problems.append(view)

    return APIResponse(data={
        "scope": scope if path_skills else "all",
        "has_roadmap": bool(path_skills),
        "skills": in_scope,
        "problems": problems,
        "stats": _stats(attempts, in_scope),
    })


def _load_problem(problem_id: str) -> dict:
    problem = get_problem(problem_id)
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found.")
    return problem


def _get_or_create_attempt(db: Session, user: User, problem_id: str) -> ProblemAttempt:
    attempt = db.query(ProblemAttempt).filter(
        ProblemAttempt.user_id == user.id, ProblemAttempt.problem_id == problem_id
    ).first()
    if not attempt:
        attempt = ProblemAttempt(user_id=user.id, problem_id=problem_id, attempts=0, solved=False, points=0)
        db.add(attempt)
    return attempt


@router.post("/{problem_id}/submit", response_model=APIResponse)
def submit_answer(
    problem_id: str,
    req: ProblemSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Grades an in-app problem on the server. Full points for a first-try solve, half after
    that. The explanation is returned once the problem is solved, or after two wrong tries.
    """
    problem = _load_problem(problem_id)
    if problem["type"] == "EXTERNAL":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This problem is solved on another site; mark it as solved instead.")

    attempt = _get_or_create_attempt(db, current_user, problem_id)
    already_solved = bool(attempt.solved)
    correct = grade(problem, req.answer)
    points_awarded = 0
    if not already_solved:
        attempt.attempts = (attempt.attempts or 0) + 1
        if correct:
            full = POINTS[problem["difficulty"]]
            points_awarded = full if attempt.attempts == 1 else full // 2
            attempt.solved = True
            attempt.points = points_awarded
            attempt.solved_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()

    reveal = correct or already_solved or (attempt.attempts or 0) >= REVEAL_AFTER_ATTEMPTS
    return APIResponse(data={
        "problem_id": problem_id,
        "skill_name": skill_of(problem_id),
        "correct": correct,
        "solved": bool(attempt.solved),
        "attempts": attempt.attempts,
        "points_awarded": points_awarded,
        "explanation": problem["explanation"] if reveal else None,
        "correct_answer": correct_answer_text(problem) if reveal else None,
        "tries_before_reveal": max(0, REVEAL_AFTER_ATTEMPTS - (attempt.attempts or 0)) if not reveal else 0,
    })


@router.post("/{problem_id}/mark", response_model=APIResponse)
def mark_external_problem(
    problem_id: str,
    req: ProblemMarkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Self-report for a problem solved on another site (LeetCode, Kaggle, ...). Worth half points."""
    problem = _load_problem(problem_id)
    if problem["type"] != "EXTERNAL":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This problem is graded here; submit an answer instead.")

    attempt = _get_or_create_attempt(db, current_user, problem_id)
    attempt.self_reported = True
    if req.solved and not attempt.solved:
        attempt.solved = True
        attempt.attempts = max(1, attempt.attempts or 0)
        attempt.points = POINTS[problem["difficulty"]] // 2
        attempt.solved_at = datetime.datetime.now(datetime.timezone.utc)
    elif not req.solved and attempt.solved:
        attempt.solved = False
        attempt.points = 0
        attempt.solved_at = None
    db.commit()
    return APIResponse(data={"problem_id": problem_id, "solved": bool(attempt.solved), "points_earned": attempt.points})
