import json
import random
import hashlib
import datetime
from typing import List, Dict, Tuple, Optional

import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import Assessment, AssessmentQuestion, AssessmentAttempt, UserSkill, Skill
from app.services.gap_engine import record_skill_evidence, blend_assessment_score
from app.services.question_bank import get_bank_questions
from app.services.skill_service import get_goal_skill_specs

DIAGNOSTIC_QUESTION_COUNT = 4
DIAGNOSTIC_TOKEN_TTL_HOURS = 24
DIAGNOSTIC_TOKEN_AUDIENCE = "skillalpha-diagnostic"

# Question text of the old generic quiz template; assessments still holding it are rebuilt.
LEGACY_TEMPLATE_PREFIX = "What is the core principle of "


def shuffle_question_options(question: Dict) -> Dict:
    """
    Every template (and most LLM output) lists the correct answer first, so learners could
    pass by always picking "A". Shuffle the options deterministically per question text
    (stable across requests) and remap correct_option_index.
    """
    options = list(question.get("options") or [])
    correct = question.get("correct_option_index")
    if len(options) < 2 or not isinstance(correct, int) or not 0 <= correct < len(options):
        return question
    seed = int(hashlib.sha256(question.get("question_text", "").encode("utf-8")).hexdigest(), 16)
    order = list(range(len(options)))
    random.Random(seed).shuffle(order)
    shuffled = dict(question)
    shuffled["options"] = [options[i] for i in order]
    shuffled["correct_option_index"] = order.index(correct)
    return shuffled


# ---------------------------------------------------------------------------
# Onboarding diagnostic
# ---------------------------------------------------------------------------

def _bank_diagnostic_questions(goal_name: str) -> List[Dict]:
    """
    One curated question for each of the first few non-beginner skills on the goal's path:
    those are the skills learners most often over-rate in a self-report.
    """
    specs = get_goal_skill_specs(goal_name)
    candidates = [name for name, _, diff in specs if diff != "BEGINNER"] or [name for name, _, _ in specs]
    questions = []
    for skill_name in candidates:
        bank = get_bank_questions(skill_name)
        if not bank:
            continue
        text, opts, correct_i, expl = bank[0]
        questions.append({
            "id": f"diag_q_{len(questions) + 1}",
            "title": skill_name,
            "skill_name": skill_name,
            "question_text": text,
            "options": opts,
            "correct_option_index": correct_i,
            "explanation": expl,
        })
        if len(questions) >= DIAGNOSTIC_QUESTION_COUNT:
            break
    return questions


def get_diagnostic_questions_for_goal(goal_name: str) -> List[Dict]:
    """Full diagnostic questions, including answers. Never send these to the client as-is."""
    from app.services.llm_service import generate_llm_diagnostic_questions

    skill_names = [name for name, _, _ in get_goal_skill_specs(goal_name)]
    questions = generate_llm_diagnostic_questions(goal_name, skill_names, count=DIAGNOSTIC_QUESTION_COUNT)
    if not questions:
        questions = _bank_diagnostic_questions(goal_name)
    return [shuffle_question_options(q) for q in questions]


def build_public_diagnostic(goal_name: str) -> Dict:
    """
    Questions for the client without answers or explanations, plus a signed token holding
    the answer key so POST /roadmaps can grade the diagnostic on the server.
    """
    questions = get_diagnostic_questions_for_goal(goal_name)
    answer_key = {q["id"]: [q.get("skill_name"), q["correct_option_index"]] for q in questions}
    token = jwt.encode(
        {
            "aud": DIAGNOSTIC_TOKEN_AUDIENCE,
            "goal": goal_name,
            "key": answer_key,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=DIAGNOSTIC_TOKEN_TTL_HOURS),
        },
        settings.JWT_SECRET,
        algorithm="HS256",
    )
    public = [
        {k: v for k, v in q.items() if k not in ("correct_option_index", "explanation")}
        for q in questions
    ]
    return {"goal": goal_name, "questions": public, "diagnostic_token": token}


def grade_diagnostic(token: Optional[str], answers: Dict[str, int]) -> Dict[str, Tuple[int, int]]:
    """
    Grades onboarding answers against the signed answer key.
    Returns lowercase skill name -> (correct, answered). Invalid/expired tokens grade nothing.
    """
    if not token or not answers:
        return {}
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"], audience=DIAGNOSTIC_TOKEN_AUDIENCE)
    except jwt.PyJWTError:
        return {}
    results: Dict[str, Tuple[int, int]] = {}
    for qid, entry in (payload.get("key") or {}).items():
        if qid not in answers or not isinstance(entry, list) or len(entry) != 2:
            continue
        skill_name, correct_idx = entry
        if not skill_name:
            continue
        key = skill_name.lower()
        correct, total = results.get(key, (0, 0))
        results[key] = (correct + int(answers[qid] == correct_idx), total + 1)
    return results


# ---------------------------------------------------------------------------
# Per-skill quizzes
# ---------------------------------------------------------------------------

def _quiz_questions_for_skill(skill: Skill) -> List[Dict]:
    bank = get_bank_questions(skill.name)
    if bank:
        return [
            {"question_text": t, "options": o, "correct_option_index": c, "explanation": e}
            for t, o, c, e in bank
        ]
    from app.services.llm_service import generate_llm_skill_questions
    return generate_llm_skill_questions(skill.name, skill.difficulty or "INTERMEDIATE") or []


def _fill_assessment_questions(db: Session, assessment: Assessment, skill: Skill) -> None:
    for q in _quiz_questions_for_skill(skill):
        q = shuffle_question_options(q)
        assessment.questions.append(AssessmentQuestion(
            question_text=q["question_text"],
            options_json=json.dumps(q["options"]),
            correct_option_index=q["correct_option_index"],
            explanation=q.get("explanation"),
        ))


def get_or_create_assessment_for_skill(db: Session, skill: Skill) -> Assessment:
    """
    Returns the skill's quiz. Questions come from the curated bank, then the LLM. If neither is
    available the assessment has no questions and the UI hides the quiz (no fake questions).
    Old generic-template quizzes and empty quizzes are rebuilt when better questions exist.
    """
    assessment = db.query(Assessment).filter(Assessment.skill_id == skill.id).first()
    if not assessment:
        assessment = Assessment(
            skill_id=skill.id,
            title=f"Skill Check: {skill.name}",
            description=f"Short quiz to verify your {skill.name} level.",
            difficulty=skill.difficulty
        )
        db.add(assessment)
        _fill_assessment_questions(db, assessment, skill)
        db.commit()
        db.refresh(assessment)
        return assessment

    is_legacy = any(q.question_text.startswith(LEGACY_TEMPLATE_PREFIX) for q in assessment.questions)
    if is_legacy or not assessment.questions:
        replacement = _quiz_questions_for_skill(skill)
        if replacement:
            assessment.questions.clear()
            assessment.title = f"Skill Check: {skill.name}"
            assessment.description = f"Short quiz to verify your {skill.name} level."
            _fill_assessment_questions(db, assessment, skill)
            db.commit()
            db.refresh(assessment)
    return assessment


def evaluate_assessment_attempt(
    db: Session,
    user_id: str,
    assessment_id: str,
    answers: Dict[str, int]
) -> Tuple[Optional[AssessmentAttempt], float, str, List[Dict]]:
    """
    Grades a quiz on the server and records the result as skill evidence.
    Returns (attempt, new_skill_score, feedback, review) where review lists, per question,
    the learner's choice, the correct option and the explanation.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        return None, 0.0, "Assessment not found", []

    questions = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == assessment_id).all()
    if not questions:
        return None, 0.0, "This quiz has no questions yet", []

    correct_count = 0
    review = []
    for q in questions:
        user_choice = answers.get(q.id)
        is_correct = user_choice is not None and user_choice == q.correct_option_index
        correct_count += int(is_correct)
        review.append({
            "question_id": q.id,
            "selected_option_index": user_choice,
            "correct_option_index": q.correct_option_index,
            "is_correct": is_correct,
            "explanation": q.explanation,
        })

    total = len(questions)
    score_ratio = correct_count / float(total)
    passed = score_ratio >= 0.60

    attempt = AssessmentAttempt(
        user_id=user_id,
        assessment_id=assessment_id,
        score=correct_count,
        max_score=total,
        passed=passed
    )
    db.add(attempt)

    user_skill = db.query(UserSkill).filter(
        UserSkill.user_id == user_id,
        UserSkill.skill_id == assessment.skill_id
    ).first()

    old_score = user_skill.skill_score if user_skill else 0.40
    user_skill = record_skill_evidence(
        db, user_id, assessment.skill_id,
        new_score=blend_assessment_score(old_score, score_ratio),
        new_confidence=(user_skill.confidence_score if user_skill else 0.5) + 0.15,
        user_skill=user_skill
    )
    new_score = user_skill.skill_score

    db.commit()

    feedback = f"You answered {correct_count}/{total} correctly. Skill benchmark updated from {int(old_score*100)}% to {int(new_score*100)}% based on verified evidence."
    return attempt, new_score, feedback, review
