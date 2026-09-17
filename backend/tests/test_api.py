import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "SkillAlpha" in data["service"]

def test_auth_and_onboarding_flow():
    unique_email = f"testlearner_{uuid.uuid4().hex[:8]}@skillalpha.com"
    # 1. Register new user
    reg_resp = client.post("/api/auth/register", json={
        "email": unique_email,
        "password": "password123",
        "full_name": "Test Learner"
    })
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["error"] is None
    token = reg_data["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get me
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["email"] == unique_email

    # 3. Onboarding / Create Roadmap
    onboard_resp = client.post("/api/roadmaps", headers=headers, json={
        "goal": "Become a Machine Learning Engineer",
        "known_skills": [
            {"skill_name": "Python Architecture", "self_reported_level": "ADVANCED"},
            {"skill_name": "SQL & Analytical Queries", "self_reported_level": "INTERMEDIATE"}
        ],
        "available_hours": 10,
        "duration_weeks": 12,
        "learning_preferences": ["VIDEO", "DOCUMENTATION"]
    })
    assert onboard_resp.status_code == 200
    rm_data = onboard_resp.json()["data"]
    assert rm_data["goal"] == "Become a Machine Learning Engineer"
    assert rm_data["route_reasoning"] is not None
    assert len(rm_data["milestones"]) > 0

    # 4. Fetch Today's Learning
    today_resp = client.get("/api/recommendations/today", headers=headers)
    assert today_resp.status_code == 200
    today_data = today_resp.json()["data"]
    assert today_data["task"] is not None
    assert "resources" in today_data["task"]

    # 5. Fetch Public Resources
    res_resp = client.get("/api/resources")
    assert res_resp.status_code == 200
    assert len(res_resp.json()["data"]) > 0

    # 6. Fetch Diagnostic Questions by Goal
    diag_resp = client.get("/api/assessments/diagnostic-by-goal?goal=React")
    assert diag_resp.status_code == 200
    assert len(diag_resp.json()["data"]["questions"]) > 0


def test_adaptive_replanning_and_ownership():
    # Setup User A
    user_a_email = f"user_a_{uuid.uuid4().hex[:8]}@skillalpha.com"
    token_a = client.post("/api/auth/register", json={
        "email": user_a_email, "password": "password123", "full_name": "User A"
    }).json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Setup User B
    user_b_email = f"user_b_{uuid.uuid4().hex[:8]}@skillalpha.com"
    token_b = client.post("/api/auth/register", json={
        "email": user_b_email, "password": "password123", "full_name": "User B"
    }).json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a roadmap
    rm_resp = client.post("/api/roadmaps", headers=headers_a, json={
        "goal": "Become a Data Scientist",
        "known_skills": [],
        "available_hours": 10,
        "duration_weeks": 12
    })
    rm_data = rm_resp.json()["data"]
    rm_id = rm_data["id"]
    initial_task_count = rm_data["total_tasks"]
    first_task_id = rm_data["milestones"][0]["tasks"][0]["id"]

    # Ownership check: User B tries to complete User A's task -> should be blocked (404/Denied)
    b_complete_resp = client.post(f"/api/tasks/{first_task_id}/complete", headers=headers_b, json={
        "time_spent_minutes": 25,
        "self_evaluation": "GOT_IT"
    })
    assert b_complete_resp.status_code == 404

    # User A completes task self-evaluating as SHAKY
    a_complete_resp = client.post(f"/api/tasks/{first_task_id}/complete", headers=headers_a, json={
        "time_spent_minutes": 30,
        "self_evaluation": "SHAKY"
    })
    assert a_complete_resp.status_code == 200

    # User A triggers adaptive replanning
    replan_resp = client.post(f"/api/roadmaps/{rm_id}/repace", headers=headers_a)
    assert replan_resp.status_code == 200
    replanned_data = replan_resp.json()["data"]

    # Verify that adaptive replanning added reinforcement task and updated route reasoning
    assert replanned_data["total_tasks"] > initial_task_count
    assert "Route adapted" in replanned_data["route_reasoning"]

