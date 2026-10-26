import datetime
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.models import Skill, UserSkill

LEVEL_SCORES = {
    "BEGINNER": 0.25,
    "FAMILIAR": 0.45,
    "INTERMEDIATE": 0.65,
    "ADVANCED": 0.85,
    "EXPERT": 0.95
}

WEAK_STATUSES = ("NEEDS_REINFORCEMENT", "MISSING")

def classify_skill_status(skill_score: float) -> str:
    if skill_score >= 0.80:
        return "MASTERED"
    elif skill_score >= 0.65:
        return "STRONG"
    elif skill_score >= 0.40:
        return "NEEDS_REINFORCEMENT"
    else:
        return "MISSING"

def blend_assessment_score(old_score: float, correct_ratio: float) -> float:
    """Evidence-based score update (docs/architecture.md): 60% prior estimate, 40% quiz result."""
    return old_score * 0.6 + correct_ratio * 0.4

def record_skill_evidence(
    db: Session,
    user_id: str,
    skill_id: str,
    new_score: float,
    new_confidence: float,
    user_skill: Optional[UserSkill] = None
) -> UserSkill:
    """
    Single write path for skill evidence: status is always derived from the score,
    and every piece of evidence increments evidence_count.
    """
    if user_skill is None:
        user_skill = db.query(UserSkill).filter(
            UserSkill.user_id == user_id,
            UserSkill.skill_id == skill_id
        ).first()
    if user_skill is None:
        user_skill = UserSkill(user_id=user_id, skill_id=skill_id, evidence_count=0)
        db.add(user_skill)

    score = round(max(0.0, min(1.0, new_score)), 2)
    user_skill.skill_score = score
    user_skill.confidence_score = round(max(0.0, min(0.95, new_confidence)), 2)
    user_skill.status = classify_skill_status(score)
    user_skill.evidence_count = (user_skill.evidence_count or 0) + 1
    user_skill.last_assessed_at = datetime.datetime.now(datetime.timezone.utc)
    return user_skill

def evaluate_skill_gaps(
    db: Session,
    user_id: str,
    target_skills: List[Skill],
    self_reported_skills: Dict[str, str] = None,
    diagnostic_results: Dict[str, Tuple[int, int]] = None,
    goal: Optional[str] = None
) -> Tuple[List[Dict], str]:
    """
    Evaluates skill gaps between Target Skill Graph and User Baseline.
    diagnostic_results maps lowercase skill name -> (correct_answers, total_answers)
    and adjusts the self-reported / stored baseline as assessment evidence.
    Returns (evaluated_skill_list, route_reasoning_explanation)
    """
    if self_reported_skills is None:
        self_reported_skills = {}
    if diagnostic_results is None:
        diagnostic_results = {}

    # Query existing user skill DB records
    existing_user_skills = {
        us.skill.name.lower(): us
        for us in db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
        if us.skill
    }
    
    evaluated_skills = []
    skipped_skills = []
    focus_skills = []
    reinforce_skills = []
    calibrated_skills = []

    for skill in target_skills:
        skill_key = skill.name.lower()
        
        # Calculate baseline score from self-report or DB
        if skill_key in self_reported_skills:
            lvl = self_reported_skills[skill_key].upper()
            score = LEVEL_SCORES.get(lvl, 0.40)
            confidence = 0.85
        elif skill_key in existing_user_skills:
            score = existing_user_skills[skill_key].skill_score
            confidence = existing_user_skills[skill_key].confidence_score
        else:
            score = 0.10 # default baseline for unlearned target skill
            confidence = 0.50

        # Persist or update user skill record
        user_skill = existing_user_skills.get(skill_key)
        if skill_key in diagnostic_results:
            # Diagnostic answers are evidence: they calibrate the self-reported baseline
            correct, total = diagnostic_results[skill_key]
            baseline_status = classify_skill_status(score)
            user_skill = record_skill_evidence(
                db, user_id, skill.id,
                new_score=blend_assessment_score(score, correct / float(total)),
                new_confidence=confidence + 0.15,
                user_skill=user_skill
            )
            score = user_skill.skill_score
            confidence = user_skill.confidence_score
            if baseline_status in ["MASTERED", "STRONG"] and user_skill.status in WEAK_STATUSES:
                calibrated_skills.append(skill.name)
        elif not user_skill:
            user_skill = UserSkill(
                user_id=user_id,
                skill_id=skill.id,
                skill_score=score,
                confidence_score=confidence,
                status=classify_skill_status(score)
            )
            db.add(user_skill)
        else:
            user_skill.skill_score = score
            user_skill.confidence_score = confidence
            user_skill.status = classify_skill_status(score)

        status = user_skill.status
        db.commit()
        
        item = {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "domain": skill.domain,
            "score": score,
            "confidence": confidence,
            "status": status,
            "should_skip": status in ["MASTERED", "STRONG"]
        }
        evaluated_skills.append(item)
        
        if status in ["MASTERED", "STRONG"]:
            skipped_skills.append(skill.name)
        elif status == "NEEDS_REINFORCEMENT":
            reinforce_skills.append(skill.name)
        else:
            focus_skills.append(skill.name)
            
    # 1. Try Groq LLM generated route explanation if API key is present
    from app.services.llm_service import generate_llm_route_reasoning
    llm_explanation = generate_llm_route_reasoning(
        goal=goal or (target_skills[0].domain if target_skills else "Target Goal"),
        skipped=skipped_skills,
        focus=focus_skills,
        reinforce=reinforce_skills
    )
    if llm_explanation:
        return evaluated_skills, llm_explanation

    # 2. Fallback to transparent rule-based route explanation
    reason_parts = []
    if skipped_skills:
        skipped_str = ", ".join(skipped_skills[:3])
        reason_parts.append(f"You demonstrated solid background in {skipped_str}, so introductory modules were bypassed to save time.")
    if calibrated_skills:
        calibrated_str = ", ".join(calibrated_skills[:3])
        reason_parts.append(f"Your diagnostic answers showed gaps in {calibrated_str}, so they stay on your path despite your self-rating.")
    if reinforce_skills:
        reinforce_str = ", ".join(reinforce_skills[:2])
        reason_parts.append(f"{reinforce_str} needs active reinforcement to bridge your skill gap.")
    if focus_skills:
        focus_str = ", ".join(focus_skills[:3])
        reason_parts.append(f"Primary focus is allocated to {focus_str} in optimal dependency sequence.")
        
    route_explanation = " ".join(reason_parts) if reason_parts else "Curriculum tailored to your target milestone objectives."
    
    return evaluated_skills, route_explanation
