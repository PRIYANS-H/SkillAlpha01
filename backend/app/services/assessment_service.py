import json
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.models.models import Assessment, AssessmentQuestion, AssessmentAttempt, UserSkill, Skill

GOAL_DIAGNOSTIC_QUESTIONS = {
    "machine learning": [
        (
            "Data Leakage Prevention",
            "When scaling numerical features for cross-validation, where should the scaler be fit?",
            ["Fit strictly on each training fold inside the CV loop", "Fit on the full dataset before splitting into folds", "Fit on the test set first then apply to train", "Scaling is not needed for CV"],
            0,
            "Fitting scalers outside CV folds causes data leakage from validation folds into training features."
        ),
        (
            "Model Validation",
            "What is the main benefit of Stratified K-Fold cross-validation over standard K-Fold?",
            ["Preserves the original target class ratio across every validation fold", "Doubles training speed by skipping hyperparameter fitting", "Eliminates memory overhead during matrix inversion", "Removes outliers automatically"],
            0,
            "Stratified K-Fold ensures every fold retains the exact target class distribution, preventing imbalanced validation metrics."
        )
    ],
    "data science": [
        (
            "Exploratory Data Analysis",
            "Which pandas operation is most memory-efficient for filtering a multi-gigabyte DataFrame?",
            ["Vectorized boolean indexing with chunking or query()", "Iterating line-by-line with for row in df.iterrows()", "Converting to Python dicts first", "Repeated append() in a loop"],
            0,
            "Vectorized C-optimized query operations execute in columnar memory without Python loop overhead."
        ),
        (
            "Statistical Evaluation",
            "When evaluating an imbalanced classification model (99% negative class), which metric is most reliable?",
            ["Area Under ROC Curve (ROC-AUC) or PR-AUC", "Raw Accuracy Score", "Mean Squared Error", "R-squared Score"],
            0,
            "Raw accuracy is misleading on imbalanced data because predicting 100% negative yields 99% accuracy."
        )
    ],
    "backend": [
        (
            "API Architecture",
            "In RESTful HTTP design, which method MUST be idempotent according to HTTP spec?",
            ["GET, PUT, and DELETE", "POST only", "PATCH only", "None of the above"],
            0,
            "GET, PUT, and DELETE are idempotent; repeating the request multiple times produces the same server state."
        ),
        (
            "Database Indexing",
            "What is the primary trade-off when adding a B-Tree index to a database table?",
            ["Speeds up SELECT queries but slows down INSERT/UPDATE writes", "Slows down SELECT queries but speeds up WRITES", "Increases CPU usage without affecting disk space", "Disables transactions"],
            0,
            "Indexes speed up search lookups but require writing updated index trees on every INSERT or UPDATE."
        )
    ],
    "react": [
        (
            "State Management",
            "Why must React component state never be mutated directly (e.g. state.count = 5)?",
            ["Direct mutation bypasses React's virtual DOM re-render trigger", "It causes compiler errors in Vite", "TypeScript forbids object mutations", "It deletes local storage"],
            0,
            "React relies on reference inequality (shallow equality check) to know when to trigger re-renders."
        ),
        (
            "Effect Hook Dependencies",
            "What happens if an object created inside render is passed to useEffect dependency array without useMemo?",
            ["The effect fires on every single render due to new object reference", "React throws a runtime crash", "The effect only runs once", "It turns off hot reload"],
            0,
            "Objects declared inside component render get a fresh memory reference every render, causing infinite effect loops."
        )
    ],
    "general": [
        (
            "Software Architecture",
            "What is the primary goal of modular decoupling in software engineering?",
            ["Isolating changes so updating one component doesn't break others", "Reducing code file count to 1", "Eliminating database usage", "Making code run 10x faster"],
            0,
            "Decoupling reduces cognitive complexity and keeps regression scope localized."
        ),
        (
            "Version Control",
            "What is the key advantage of feature branch workflows in Git?",
            ["Allows independent development and review before merging to main", "Deletes previous commit history automatically", "Encrypts all source code files", "Bypasses CI/CD build checks"],
            0,
            "Feature branches isolate experimental code until passing code review and integration tests."
        )
    ]
}

def get_diagnostic_questions_for_goal(goal_name: str) -> List[Dict]:
    goal_lower = goal_name.lower()
    
    if "machine learning" in goal_lower or "ml" in goal_lower:
        raw_q = GOAL_DIAGNOSTIC_QUESTIONS["machine learning"]
    elif "data scientist" in goal_lower or "data science" in goal_lower:
        raw_q = GOAL_DIAGNOSTIC_QUESTIONS["data science"]
    elif "backend" in goal_lower or "fastapi" in goal_lower or "python dev" in goal_lower:
        raw_q = GOAL_DIAGNOSTIC_QUESTIONS["backend"]
    elif "react" in goal_lower or "frontend" in goal_lower or "javascript" in goal_lower:
        raw_q = GOAL_DIAGNOSTIC_QUESTIONS["react"]
    else:
        raw_q = GOAL_DIAGNOSTIC_QUESTIONS["general"]

    questions = []
    for idx, (title, text, opts, correct_i, expl) in enumerate(raw_q):
        questions.append({
            "id": f"diag_q_{idx+1}",
            "title": title,
            "question_text": text,
            "options": opts,
            "correct_option_index": correct_i,
            "explanation": expl
        })
    return questions


def get_or_create_assessment_for_skill(db: Session, skill: Skill) -> Assessment:
    assessment = db.query(Assessment).filter(Assessment.skill_id == skill.id).first()
    if not assessment:
        assessment = Assessment(
            skill_id=skill.id,
            title=f"Diagnostic Calibration: {skill.name}",
            description=f"Short 3-question diagnostic to benchmark your {skill.name} baseline.",
            difficulty=skill.difficulty
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        questions = [
            (
                f"What is the core principle of {skill.name} in a production environment?",
                ["Avoiding data/state leakage across pipeline steps", "Maximizing parameter memory allocation", "Disabling validation checks", "Relying on random defaults"],
                0,
                f"In {skill.name}, avoiding leakage and preserving clean boundaries is essential."
            ),
            (
                f"Which metric or diagnostic tool is most appropriate when evaluating {skill.name}?",
                ["System CPU frequency", "Cross-validation score stability", "Source code line count", "Unindexed database scan time"],
                1,
                "Cross-validation stability directly measures model generalization."
            ),
            (
                f"What is the recommended best practice when implementing {skill.name}?",
                ["Hardcoding hyperparameters in global state", "Encapsulating operations in reproducible, tested pipelines", "Skipping feature normalization", "Testing on training data only"],
                1,
                "Encapsulation in modular pipelines ensures testability."
            )
        ]

        for q_text, opts, correct_idx, expl in questions:
            q = AssessmentQuestion(
                assessment_id=assessment.id,
                question_text=q_text,
                options_json=json.dumps(opts),
                correct_option_index=correct_idx,
                explanation=expl
            )
            db.add(q)
        db.commit()
        db.refresh(assessment)

    return assessment


def evaluate_assessment_attempt(
    db: Session,
    user_id: str,
    assessment_id: str,
    answers: Dict[str, int]
) -> Tuple[AssessmentAttempt, float, str]:
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        return None, 0.0, "Assessment not found"

    questions = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == assessment_id).all()
    correct_count = 0
    total = len(questions)

    for q in questions:
        user_choice = answers.get(q.id)
        if user_choice is not None and user_choice == q.correct_option_index:
            correct_count += 1

    score_ratio = correct_count / float(total) if total > 0 else 0.0
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
    evidence = (user_skill.evidence_count if user_skill else 0) + 1
    new_score = round(old_score * 0.6 + score_ratio * 0.4, 2)
    new_confidence = min(0.95, round((user_skill.confidence_score if user_skill else 0.5) + 0.15, 2))

    if not user_skill:
        user_skill = UserSkill(
            user_id=user_id,
            skill_id=assessment.skill_id,
            skill_score=new_score,
            confidence_score=new_confidence,
            status="STRONG" if new_score >= 0.65 else ("NEEDS_REINFORCEMENT" if new_score >= 0.40 else "MISSING"),
            evidence_count=evidence
        )
        db.add(user_skill)
    else:
        user_skill.skill_score = new_score
        user_skill.confidence_score = new_confidence
        user_skill.evidence_count = evidence
        user_skill.status = "STRONG" if new_score >= 0.65 else ("NEEDS_REINFORCEMENT" if new_score >= 0.40 else "MISSING")

    db.commit()

    feedback = f"You answered {correct_count}/{total} correctly. Skill benchmark updated from {int(old_score*100)}% to {int(new_score*100)}% based on verified evidence."
    return attempt, new_score, feedback
