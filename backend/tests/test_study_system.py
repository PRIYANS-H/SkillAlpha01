"""
Day-by-day plans, rest days and breaks, milestone checks, practice problems, projects and
the curated content library, driven through the public API.
"""
import datetime
import uuid

import jwt
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.models.db import SessionLocal
from app.models.models import Resource

client = TestClient(app)

QUANT_GOAL = "Become a Quant Researcher"


def new_learner():
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "email": f"study_{uuid.uuid4().hex[:8]}@skillalpha.test",
         "user_metadata": {"full_name": "Study Learner"}, "aud": "authenticated"},
        settings.SUPABASE_JWT_SECRET, algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def ok(resp) -> dict:
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("error") is None, body["error"]
    return body["data"]


def make_roadmap(headers, goal=QUANT_GOAL, **overrides):
    payload = {"goal": goal, "known_skills": [], "available_hours": 10, "duration_weeks": 16,
               "learning_preferences": ["VIDEO", "PRACTICE"], **overrides}
    return ok(client.post("/api/roadmaps", headers=headers, json=payload))


def all_tasks(roadmap):
    return [t for m in roadmap["milestones"] for t in m["tasks"]]


def test_quant_goal_builds_a_dated_day_by_day_plan():
    headers = new_learner()
    roadmap = make_roadmap(headers, study_days_per_week=5)
    assert roadmap["goal_family"] == "quant_finance"
    tasks = all_tasks(roadmap)
    kinds = [t["kind"] for t in tasks]
    assert kinds.count("SKILL") == 13 and kinds.count("MILESTONE_CHECK") == 4 and kinds.count("PROJECT") == 4
    assert kinds[-1] == "MILESTONE_CHECK"

    first = tasks[0]
    assert first["skill_name"] == "Python for Quant Finance"
    assert [d["kind"] for d in first["days"]] == ["LEARN", "PRACTICE", "BUILD", "REVIEW"]
    assert all(d["date"] and d["steps"] and d["done"] is False for d in first["days"])
    assert first["days"][0]["date"] == datetime.date.today().isoformat()
    assert first["estimated_minutes"] == 4 * 120

    # Every skill task says which resources it uses and why, and mixes formats
    for task in (t for t in tasks if t["kind"] == "SKILL"):
        types = [r["resource_type"] for r in task["resources"]]
        assert len(types) >= 3, task["title"]
        assert "VIDEO" in types, task["title"]
        assert all(r["recommendation_reason"] for r in task["resources"])

    due = [t["due_date"] for t in tasks]
    assert due == sorted(due)
    schedule = roadmap["schedule"]
    assert schedule["study_days_per_week"] == 5 and schedule["rest_days_per_week"] == 2
    assert schedule["minutes_per_day"] == 120
    assert schedule["total_study_days"] == sum(t["day_count"] for t in tasks)
    assert schedule["fits_target"] is (schedule["weeks_needed"] <= 16)
    assert str(schedule["weeks_needed"]) in schedule["note"]


def test_study_days_per_week_leaves_rest_days():
    headers = new_learner()
    roadmap = make_roadmap(headers, goal="Become a DevOps Engineer", study_days_per_week=3, available_hours=6)
    first = all_tasks(roadmap)[0]
    today = datetime.date.today()
    dates = [datetime.date.fromisoformat(d["date"]) for d in first["days"]]
    # Three study days a week: day 0, 2 and 4 of each 7-day cycle; the 4th day starts week two
    assert [(d - today).days for d in dates] == [0, 2, 4, 7]
    assert roadmap["schedule"]["rest_days_per_week"] == 4


def test_a_known_skill_gets_a_shorter_plan():
    headers = new_learner()
    roadmap = make_roadmap(headers, known_skills=[
        {"skill_name": "Python for Quant Finance", "self_reported_level": "Familiar"},
        {"skill_name": "Financial Markets & Instruments", "self_reported_level": "Expert"},
    ])
    by_skill = {t["skill_name"]: t for t in all_tasks(roadmap) if t["kind"] == "SKILL"}
    assert "Financial Markets & Instruments" not in by_skill
    assert [d["kind"] for d in by_skill["Python for Quant Finance"]["days"]] == ["PRACTICE", "BUILD", "REVIEW"]
    assert len(by_skill["Backtesting & Performance Metrics"]["days"]) == 4


def test_ticking_study_days_is_owner_only_and_does_not_complete_the_task():
    headers = new_learner()
    task = all_tasks(make_roadmap(headers))[0]
    updated = ok(client.post(f"/api/tasks/{task['id']}/steps", headers=headers, json={"index": 0, "done": True}))
    assert updated["days"][0]["done"] is True and updated["days"][1]["done"] is False
    assert updated["status"] == "IN_PROGRESS"
    undone = ok(client.post(f"/api/tasks/{task['id']}/steps", headers=headers, json={"index": 0, "done": False}))
    assert undone["days"][0]["done"] is False

    assert client.post(f"/api/tasks/{task['id']}/steps", headers=headers, json={"index": 9, "done": True}).status_code == 400
    assert client.post(f"/api/tasks/{task['id']}/steps", headers=new_learner(), json={"index": 0, "done": True}).status_code == 404
    assert ok(client.get("/api/recommendations/today", headers=headers))["task"]["id"] == task["id"]


def test_milestone_check_must_be_passed():
    from app.api.milestone_router import build_check_questions

    headers = new_learner()
    roadmap = make_roadmap(headers, goal="Become a Security Engineer")
    check = next(t for t in all_tasks(roadmap) if t["kind"] == "MILESTONE_CHECK")
    assert check["milestone_check"]["pass_percent"] == 70

    # It cannot be ticked off like an ordinary task
    assert client.post(f"/api/tasks/{check['id']}/complete", headers=headers,
                       json={"time_spent_minutes": 5, "self_evaluation": "GOT_IT"}).status_code == 400

    quiz = ok(client.get(f"/api/milestone-checks/{check['id']}", headers=headers))
    assert len(quiz["questions"]) == 2 * len(quiz["skills"])
    assert all("correct_option_index" not in q and "explanation" not in q for q in quiz["questions"])
    assert client.get(f"/api/milestone-checks/{check['id']}", headers=new_learner()).status_code == 404

    key = {q["id"]: q["correct_option_index"] for q in build_check_questions(quiz["skills"])}
    assert len(set(key.values())) > 1, "correct answers must not all sit in the same position"

    wrong = {qid: (idx + 1) % 4 for qid, idx in key.items()}
    failed = ok(client.post(f"/api/milestone-checks/{check['id']}/attempt", headers=headers, json={"answers": wrong}))
    assert failed["passed"] is False and failed["score"] == 0 and failed["weak_skills"]
    assert all(r["explanation"] for r in failed["review"])
    statuses = {t["id"]: t["status"] for t in all_tasks(ok(client.get(f"/api/roadmaps/{roadmap['id']}", headers=headers)))}
    assert statuses[check["id"]] == "NOT_STARTED"

    passed = ok(client.post(f"/api/milestone-checks/{check['id']}/attempt", headers=headers, json={"answers": key}))
    assert passed["passed"] is True and passed["percent"] == 100
    after = ok(client.get(f"/api/roadmaps/{roadmap['id']}", headers=headers))
    assert {t["id"]: t["status"] for t in all_tasks(after)}[check["id"]] == "COMPLETED"
    assert after["completed_tasks"] == 1


def test_practice_problems_are_graded_on_the_server():
    headers = new_learner()
    # Without a roadmap every skill is offered
    everything = ok(client.get("/api/problems", headers=headers))
    assert everything["has_roadmap"] is False and len(everything["skills"]) > 50

    make_roadmap(headers)
    listing = ok(client.get("/api/problems", headers=headers))
    assert listing["scope"] == "roadmap" and len(listing["skills"]) == 13
    assert all("answer" not in p and "explanation" not in p for p in listing["problems"])
    assert {p["type"] for p in listing["problems"]} == {"MCQ", "NUMERIC", "EXTERNAL"}
    assert listing["stats"]["solved"] == 0 and listing["stats"]["total"] == len(listing["problems"])
    assert len(ok(client.get("/api/problems?difficulty=hard", headers=headers))["problems"]) == listing["stats"]["by_difficulty"]["HARD"]["total"]

    # Numeric: first try wrong hides the answer, second wrong reveals it, a later solve earns half points
    first = ok(client.post("/api/problems/qbt-2/submit", headers=headers, json={"answer": "40"}))
    assert first["correct"] is False and first["explanation"] is None and first["correct_answer"] is None
    second = ok(client.post("/api/problems/qbt-2/submit", headers=headers, json={"answer": 10}))
    assert second["correct"] is False and second["explanation"] and second["correct_answer"] == "33.33"
    third = ok(client.post("/api/problems/qbt-2/submit", headers=headers, json={"answer": "33.3%"}))
    assert third["correct"] is True and third["points_awarded"] == 10 and third["attempts"] == 3
    again = ok(client.post("/api/problems/qbt-2/submit", headers=headers, json={"answer": "33.3"}))
    assert again["points_awarded"] == 0 and again["attempts"] == 3

    # Multiple choice: the option text is the answer; a first-try solve earns full points
    mcq = next(p for p in listing["problems"] if p["id"] == "qts-1")
    assert mcq["options"][0] != "Daily returns of a stock" or len(set(mcq["options"])) == 4
    solved = ok(client.post("/api/problems/qts-1/submit", headers=headers, json={"answer": "Daily returns of a stock"}))
    assert solved["correct"] is True and solved["points_awarded"] == 10

    # Outside problems are self-reported, for half points, and cannot be "submitted"
    assert client.post("/api/problems/qpy-x2/submit", headers=headers, json={"answer": "x"}).status_code == 400
    assert client.post("/api/problems/qts-1/mark", headers=headers, json={"solved": True}).status_code == 400
    marked = ok(client.post("/api/problems/qpy-x2/mark", headers=headers, json={"solved": True}))
    assert marked["solved"] is True and marked["points_earned"] == 5
    assert client.post("/api/problems/nope/submit", headers=headers, json={"answer": 1}).status_code == 404

    stats = ok(client.get("/api/problems", headers=headers))["stats"]
    assert stats["solved"] == 3 and stats["points"] == 25 and stats["streak_days"] == 1
    assert ok(client.get("/api/problems", headers=new_learner()))["stats"]["solved"] == 0


def test_project_submission_completes_the_roadmap_project():
    headers = new_learner()
    roadmap = make_roadmap(headers)
    project_task = next(t for t in all_tasks(roadmap) if t["kind"] == "PROJECT")
    assert project_task["project"]["id"] == project_task["ref_id"] == "qf-ma-crossover"

    listing = ok(client.get("/api/projects", headers=headers))
    assert listing["family"] == "quant_finance" and len(listing["projects"]) == 5
    project = listing["projects"][0]
    assert project["rubric"] and project["brief"] and project["submission"] is None
    assert len(ok(client.get("/api/projects?family=all", headers=headers))["projects"]) > 25

    # Not finishable without a submission
    assert client.post(f"/api/tasks/{project_task['id']}/complete", headers=headers,
                       json={"time_spent_minutes": 5, "self_evaluation": "GOT_IT"}).status_code == 400
    assert client.post("/api/projects/qf-ma-crossover/submit", headers=headers,
                       json={"url": "not a link", "checklist": []}).status_code == 400

    weak = ok(client.post("/api/projects/qf-ma-crossover/submit", headers=headers,
                          json={"url": "https://github.com/me/ma-crossover", "checklist": [True, False, False, False, False]}))
    assert weak["passed"] is False and weak["task_completed"] is False and weak["items_needed"] == 3

    done = ok(client.post("/api/projects/qf-ma-crossover/submit", headers=headers,
                          json={"url": "https://github.com/me/ma-crossover", "notes": "v2", "checklist": [True, True, True, True, False]}))
    assert done["passed"] is True and done["task_completed"] is True and done["submission"]["score"] == 0.8
    after = ok(client.get(f"/api/roadmaps/{roadmap['id']}", headers=headers))
    assert {t["id"]: t["status"] for t in all_tasks(after)}[project_task["id"]] == "COMPLETED"
    assert ok(client.get("/api/projects", headers=headers))["completed"] == 1
    assert ok(client.get("/api/projects", headers=new_learner()))["completed"] == 0


def test_break_pauses_the_plan_and_resume_restarts_it():
    headers = new_learner()
    roadmap = make_roadmap(headers)
    before = {t["id"]: datetime.date.fromisoformat(t["due_date"]) for t in all_tasks(roadmap)}

    paused = ok(client.post(f"/api/roadmaps/{roadmap['id']}/break", headers=headers, json={"days": 3}))
    after = {t["id"]: datetime.date.fromisoformat(t["due_date"]) for t in all_tasks(paused)}
    assert all((after[i] - before[i]).days == 3 for i in before)
    assert paused["schedule"]["break_until"] == (datetime.date.today() + datetime.timedelta(days=3)).isoformat()
    assert "Break" in paused["route_reasoning"] and paused["total_tasks"] == roadmap["total_tasks"]
    assert client.post(f"/api/roadmaps/{roadmap['id']}/break", headers=headers, json={"days": 0}).status_code == 422
    intruder = client.post(f"/api/roadmaps/{roadmap['id']}/break", headers=new_learner(), json={"days": 2})
    assert intruder.json()["error"]["code"] == "NOT_FOUND"

    resumed = ok(client.post(f"/api/roadmaps/{roadmap['id']}/resume", headers=headers))
    assert min(t["due_date"] for t in all_tasks(resumed)) == datetime.date.today().isoformat()
    assert resumed["schedule"]["break_until"] is None


def test_every_skill_has_a_guide_resources_and_problems():
    from app.services.curriculum import SKILL_GUIDE
    from app.services.problem_bank import PROBLEM_BANK
    from app.services.project_bank import PROJECT_BANK
    from app.services.resource_library import RESOURCE_LIBRARY, all_skill_names, sync_resource_library
    from app.services.skill_service import GOAL_SKILL_GRAPHS, resolve_goal_family

    assert resolve_goal_family("Algo trading with Python") == "quant_finance"
    assert resolve_goal_family("Become a Quant Researcher") == "quant_finance"
    assert set(PROJECT_BANK) == set(GOAL_SKILL_GRAPHS)

    names = all_skill_names()
    tagged = {}
    for _, url, _, rtype, _, _, skills, why in RESOURCE_LIBRARY:
        assert url.startswith("https://") and why
        for skill in skills:
            assert skill in names, skill
            tagged.setdefault(skill, []).append(rtype)
    for name in names:
        assert name in SKILL_GUIDE, name
        assert len(tagged.get(name, [])) >= 3 and "VIDEO" in tagged[name], name
        problems = PROBLEM_BANK.get(name, [])
        assert sum(p["type"] != "EXTERNAL" for p in problems) >= 2, name
        assert any(p["type"] == "EXTERNAL" for p in problems), name

    # Syncing again adds nothing and never duplicates a URL
    db = SessionLocal()
    try:
        assert sync_resource_library(db) == 0
        urls = [r.url for r in db.query(Resource).all()]
        assert len(urls) == len(set(urls))
    finally:
        db.close()


def test_a_curated_video_plays_exactly_that_video():
    from app.services.resource_matcher import resolve_resource_matches, extract_youtube_video_id

    assert extract_youtube_video_id("https://www.youtube.com/watch?v=rfscVS0vtbw") == "rfscVS0vtbw"
    assert extract_youtube_video_id("https://www.youtube.com/playlist?list=PL2SOU6wwxB0uwwH80KTQ6ht66KWxbzTIo") is None
    assert extract_youtube_video_id("https://docs.python.org/3/tutorial/") is None

    video = resolve_resource_matches("r1", "Learn Python", "VIDEO", "freeCodeCamp", "https://www.youtube.com/watch?v=rfscVS0vtbw")
    assert video["type"] == "youtube" and [m["video_id"] for m in video["matches"]] == ["rfscVS0vtbw"]
    playlist = resolve_resource_matches("r2", "Stat 110", "VIDEO", "Harvard", "https://www.youtube.com/playlist?list=PL2SOU6wwxB0uwwH80KTQ6ht66KWxbzTIo")
    assert playlist["type"] == "fallback" and "playlist" in playlist["url"]
