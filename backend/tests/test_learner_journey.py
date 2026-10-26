"""
MVP acceptance test: the complete learner journey, driven through the public API.

01 register -> 02 calibrate -> 03 roadmap -> 04 next action -> 05 learn + assess
-> 06 skill evidence -> 07 adaptation -> 08 return in a new session
"""
import uuid
import jwt
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.models.db import SessionLocal
from app.models.models import AssessmentQuestion
from app.services.gap_engine import classify_skill_status

client = TestClient(app)

GOAL = "Become a Machine Learning Engineer"
WEAK_SKILL = "Model Validation & Split Hygiene"


def login(auth_id: str, email: str, name: str = "Journey Learner") -> dict:
    """Mints a fresh Supabase access token, as a new login would."""
    token = jwt.encode(
        {"sub": auth_id, "email": email, "user_metadata": {"full_name": name}, "aud": "authenticated"},
        settings.SUPABASE_JWT_SECRET,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def new_learner(name: str = "Journey Learner"):
    auth_id = str(uuid.uuid4())
    email = f"journey_{uuid.uuid4().hex[:8]}@skillalpha.test"
    return auth_id, email, login(auth_id, email, name)


def ok(resp) -> dict:
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("error") is None, body["error"]
    return body["data"]


def answers_for(assessment_id: str, correct: bool) -> dict:
    db = SessionLocal()
    try:
        questions = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == assessment_id).all()
        return {
            q.id: q.correct_option_index if correct else (q.correct_option_index + 1) % 4
            for q in questions
        }
    finally:
        db.close()


def skills_by_name(headers: dict) -> dict:
    return {s["skill_name"]: s for s in ok(client.get("/api/users/me/skills", headers=headers))}


def all_tasks(roadmap: dict) -> list:
    return [t for m in roadmap["milestones"] for t in m["tasks"]]


def create_calibrated_roadmap(headers: dict) -> dict:
    """Self-reports strong skills, but fails the diagnostic for WEAK_SKILL."""
    diagnostic = ok(client.get("/api/assessments/diagnostic-by-goal", params={"goal": GOAL}))
    weak_questions = [q for q in diagnostic["questions"] if q.get("skill_name") == WEAK_SKILL]
    assert weak_questions, "diagnostic questions must say which skill they calibrate"

    return ok(client.post("/api/roadmaps", headers=headers, json={
        "goal": GOAL,
        "known_skills": [
            {"skill_name": "Python Architecture", "self_reported_level": "Advanced"},
            {"skill_name": "SQL & Analytical Queries", "self_reported_level": "Intermediate"},
            {"skill_name": "Applied Statistics", "self_reported_level": "Advanced"},
            {"skill_name": "Pandas & Data Manipulation", "self_reported_level": "Advanced"},
            {"skill_name": "Machine Learning Foundations", "self_reported_level": "Advanced"},
            {"skill_name": WEAK_SKILL, "self_reported_level": "Advanced"},
        ],
        "diagnostic_results": [
            {"skill_name": q["skill_name"], "is_correct": False} for q in weak_questions
        ],
        "available_hours": 10,
        "duration_weeks": 12,
        "learning_preferences": ["VIDEO", "DOCUMENTATION", "PRACTICE"],
    }))


def test_complete_learner_journey():
    # 01 Register: first authenticated request provisions the learner
    auth_id, email, headers = new_learner()
    me = ok(client.get("/api/auth/me", headers=headers))
    assert me["email"] == email and me["role"] == "learner"

    # 02 Calibrate + 03 Generate roadmap
    roadmap = create_calibrated_roadmap(headers)
    roadmap_id = roadmap["id"]

    profile = ok(client.get("/api/users/me", headers=headers))
    assert profile["goal"] == GOAL

    skills = skills_by_name(headers)
    assert skills["Python Architecture"]["status"] == "MASTERED"
    # Failed diagnostic outweighs the ADVANCED self-report and is recorded as evidence
    weak = skills[WEAK_SKILL]
    assert weak["status"] == "NEEDS_REINFORCEMENT"
    assert weak["evidence_count"] == 1

    task_skills = [t["skill_id"] for t in all_tasks(roadmap)]
    assert skills["Python Architecture"]["skill_id"] not in task_skills
    assert skills["Machine Learning Foundations"]["skill_id"] not in task_skills
    assert weak["skill_id"] in task_skills
    assert "Python Architecture" in roadmap["route_reasoning"]
    assert WEAK_SKILL in roadmap["route_reasoning"]

    # 04 Next action: the first gap in dependency order, with resources for that skill
    today = ok(client.get("/api/recommendations/today", headers=headers))
    task = today["task"]
    assert task["skill_id"] == weak["skill_id"]
    assert today["roadmap_id"] == roadmap_id
    assert len(task["resources"]) > 0

    # 05 Learn: session lifecycle is owner-only
    session_id = ok(client.post("/api/learning-sessions", params={"task_id": task["id"]}, headers=headers))["session_id"]
    _, _, intruder = new_learner("Intruder")
    intrusion = client.patch(f"/api/learning-sessions/{session_id}", headers=intruder,
                             json={"duration_seconds": 1, "status": "COMPLETED"})
    assert intrusion.status_code == 404
    ok(client.patch(f"/api/learning-sessions/{session_id}", headers=headers,
                    json={"duration_seconds": 1500, "status": "COMPLETED"}))

    # 05 Assess: every question is graded; a failed quiz lowers the score
    assessment = ok(client.get(f"/api/assessments/by-skill/{weak['skill_id']}"))
    assert len(assessment["questions"]) >= 1
    attempt = ok(client.post(f"/api/assessments/{assessment['id']}/attempt", headers=headers,
                             json={"answers": answers_for(assessment["id"], correct=False)}))
    assert attempt["passed"] is False
    assert attempt["new_skill_score"] < weak["skill_score"]

    completion = ok(client.post(f"/api/tasks/{task['id']}/complete", headers=headers,
                                json={"time_spent_minutes": 25, "self_evaluation": "SHAKY"}))

    # 06 Skill evidence: recorded, and status always agrees with score
    skills = skills_by_name(headers)
    weak = skills[WEAK_SKILL]
    assert weak["status"] == "NEEDS_REINFORCEMENT"
    assert weak["evidence_count"] == 3
    for s in skills.values():
        assert s["status"] == classify_skill_status(s["skill_score"]), s

    # 07 Adapt: weak evidence inserts reinforcement as the very next action, without a manual replan
    assert completion["adaptation"]["reinforced_skills"] == [WEAK_SKILL]
    today = ok(client.get("/api/recommendations/today", headers=headers))
    reinforcement = today["task"]
    assert reinforcement["skill_id"] == weak["skill_id"]
    assert reinforcement["id"] != task["id"]
    assert "Reinforcement" in reinforcement["title"]

    roadmap = ok(client.get(f"/api/roadmaps/{roadmap_id}", headers=headers))
    assert "Route adapted" in roadmap["route_reasoning"]
    assert roadmap["completed_tasks"] == 1
    assert roadmap["progress_percent"] == round(100 / roadmap["total_tasks"], 1)

    # Re-submitting the same completion must not double-count evidence
    ok(client.post(f"/api/tasks/{task['id']}/complete", headers=headers,
                   json={"time_spent_minutes": 25, "self_evaluation": "SHAKY"}))
    assert skills_by_name(headers)[WEAK_SKILL]["evidence_count"] == 3

    # Strong result on the reinforcement lets the learner move on
    ok(client.post(f"/api/assessments/{assessment['id']}/attempt", headers=headers,
                   json={"answers": answers_for(assessment["id"], correct=True)}))
    completion = ok(client.post(f"/api/tasks/{reinforcement['id']}/complete", headers=headers,
                                json={"time_spent_minutes": 30, "self_evaluation": "GOT_IT"}))
    assert completion["adaptation"] is None
    assert skills_by_name(headers)[WEAK_SKILL]["status"] in ("STRONG", "MASTERED")

    next_task = ok(client.get("/api/recommendations/today", headers=headers))["task"]
    assert next_task["skill_id"] != weak["skill_id"]
    roadmap = ok(client.get(f"/api/roadmaps/{roadmap_id}", headers=headers))
    statuses = {t["id"]: t["status"] for t in all_tasks(roadmap)}

    # 08 Return: a new login sees the same learner, progress and next action
    headers = login(auth_id, email)
    assert ok(client.get("/api/auth/me", headers=headers))["id"] == me["id"]
    assert ok(client.get("/api/recommendations/today", headers=headers))["task"]["id"] == next_task["id"]
    returned = ok(client.get(f"/api/roadmaps/{roadmap_id}", headers=headers))
    assert {t["id"]: t["status"] for t in all_tasks(returned)} == statuses
    assert statuses[task["id"]] == "COMPLETED" and statuses[reinforcement["id"]] == "COMPLETED"
    assert skills_by_name(headers)[WEAK_SKILL]["status"] in ("STRONG", "MASTERED")


def test_strong_assessment_clears_pending_reinforcement():
    _, _, headers = new_learner()
    create_calibrated_roadmap(headers)
    task = ok(client.get("/api/recommendations/today", headers=headers))["task"]
    ok(client.post(f"/api/tasks/{task['id']}/complete", headers=headers,
                   json={"time_spent_minutes": 20, "self_evaluation": "LOST"}))
    reinforcement = ok(client.get("/api/recommendations/today", headers=headers))["task"]
    assert "Reinforcement" in reinforcement["title"]

    # Demonstrating mastery on the quiz makes the pending reinforcement unnecessary
    assessment = ok(client.get(f"/api/assessments/by-skill/{task['skill_id']}"))
    for _ in range(3):
        ok(client.post(f"/api/assessments/{assessment['id']}/attempt", headers=headers,
                       json={"answers": answers_for(assessment["id"], correct=True)}))

    next_task = ok(client.get("/api/recommendations/today", headers=headers))["task"]
    assert next_task["id"] != reinforcement["id"]
    assert next_task["skill_id"] != task["skill_id"]


def test_onboarding_baseline_alone_does_not_trigger_reinforcement():
    # A skill that is merely weak at onboarding already has a regular task; replanning
    # must not stack "reinforcement" on top before the learner has studied it.
    _, _, headers = new_learner()
    roadmap = create_calibrated_roadmap(headers)
    replanned = ok(client.post(f"/api/roadmaps/{roadmap['id']}/repace", headers=headers))
    assert replanned["total_tasks"] == roadmap["total_tasks"]
    assert not any("Reinforcement" in t["title"] for t in all_tasks(replanned))
