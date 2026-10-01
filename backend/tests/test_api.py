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


def test_complete_core_loop_end_to_end():
    email = f"loop_learner_{uuid.uuid4().hex[:8]}@skillalpha.com"
    reg_resp = client.post("/api/auth/register", json={
        "email": email, "password": "password123", "full_name": "Core Loop Learner"
    })
    token = reg_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Onboarding diagnostic questions
    diag_res = client.get("/api/assessments/diagnostic-by-goal?goal=Become%20a%20Machine%20Learning%20Engineer")
    assert diag_res.status_code == 200
    assert len(diag_res.json()["data"]["questions"]) >= 2

    # 2. Roadmap creation
    onboard_res = client.post("/api/roadmaps", headers=headers, json={
        "goal": "Become a Machine Learning Engineer",
        "known_skills": [
            {"skill_name": "Python Architecture", "self_reported_level": "ADVANCED"}
        ],
        "available_hours": 15,
        "duration_weeks": 8,
        "learning_preferences": ["VIDEO", "DOCUMENTATION"]
    })
    assert onboard_res.status_code == 200
    rm_data = onboard_res.json()["data"]
    rm_id = rm_data["id"]

    # 3. Verify user profile was synced
    prof_res = client.get("/api/users/me", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["data"]["goal"] == "Become a Machine Learning Engineer"
    assert prof_res.json()["data"]["available_hours"] == 15

    # 4. Verify user skills baseline created
    skills_res = client.get("/api/users/me/skills", headers=headers)
    assert skills_res.status_code == 200
    user_skills = skills_res.json()["data"]
    assert len(user_skills) > 0

    # 5. Fetch roadmap dashboard
    rm_detail = client.get(f"/api/roadmaps/{rm_id}", headers=headers)
    assert rm_detail.status_code == 200
    first_task = rm_detail.json()["data"]["milestones"][0]["tasks"][0]

    # 6. Fetch today's queue
    today_res = client.get("/api/recommendations/today", headers=headers)
    assert today_res.status_code == 200
    assert today_res.json()["data"]["task"]["id"] == first_task["id"]

    # 7. Start session
    session_res = client.post(f"/api/learning-sessions?task_id={first_task['id']}", headers=headers)
    assert session_res.status_code == 200
    session_id = session_res.json()["data"]["session_id"]

    # 8. Update session with JSON body duration
    patch_res = client.patch(f"/api/learning-sessions/{session_id}", headers=headers, json={
        "duration_seconds": 180,
        "status": "COMPLETED"
    })
    assert patch_res.status_code == 200

    # 9. Complete task with GOT_IT self-evaluation
    complete_res = client.post(f"/api/tasks/{first_task['id']}/complete", headers=headers, json={
        "time_spent_minutes": 3,
        "self_evaluation": "GOT_IT"
    })
    assert complete_res.status_code == 200

    # 10. Check progress page skills updated
    skills_after = client.get("/api/users/me/skills", headers=headers).json()["data"]
    completed_skill = next((s for s in skills_after if s["skill_id"] == first_task["skill_id"]), None)
    if completed_skill:
        assert completed_skill["status"] in ["STRONG", "MASTERED"]
        assert completed_skill["evidence_count"] >= 1


from unittest.mock import patch, MagicMock

def test_resource_matches_youtube_mocked_success():
    mock_youtube_response = {
        "items": [
            {
                "id": {"videoId": "test_vid_123"},
                "snippet": {
                    "title": "FastAPI Full Course - Python Backend",
                    "thumbnails": {"medium": {"url": "https://img.youtube.com/vi/test_vid_123/hqdefault.jpg"}},
                    "channelTitle": "freeCodeCamp.org"
                }
            },
            {
                "id": {"videoId": "test_vid_456"},
                "snippet": {
                    "title": "Machine Learning in 100 Seconds",
                    "thumbnails": {"medium": {"url": "https://img.youtube.com/vi/test_vid_456/hqdefault.jpg"}},
                    "channelTitle": "Fireship"
                }
            }
        ]
    }
    
    with patch("app.services.resource_matcher.httpx.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value.__enter__.return_value = mock_instance
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_youtube_response
        mock_instance.get.return_value = mock_resp
        
        with patch("app.config.settings.YOUTUBE_DATA_API_KEY", "mock_key_abc"):
            from app.services.resource_matcher import clear_cache
            clear_cache()
            
            resp = client.get("/api/resources/r_yt_test/matches?name=FastAPI%20Architecture&type=youtube_channel")
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert data["type"] == "youtube"
            assert data["fallback"] is False
            assert len(data["matches"]) == 2
            assert data["matches"][0]["video_id"] == "test_vid_123"
            assert data["matches"][0]["title"] == "FastAPI Full Course - Python Backend"
            assert data["matches"][0]["thumbnail_url"] == "https://img.youtube.com/vi/test_vid_123/hqdefault.jpg"
            assert data["matches"][0]["channel_title"] == "freeCodeCamp.org"


def test_resource_matches_youtube_empty_results():
    with patch("app.services.resource_matcher.httpx.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value.__enter__.return_value = mock_instance
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"items": []}
        mock_instance.get.return_value = mock_resp
        
        with patch("app.config.settings.YOUTUBE_DATA_API_KEY", "mock_key_abc"):
            from app.services.resource_matcher import clear_cache
            clear_cache()
            
            resp = client.get("/api/resources/r_yt_empty/matches?name=SuperNicheTopic12345&type=youtube_channel")
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert data["fallback"] is True
            assert data["matches"] == []


def test_resource_matches_youtube_quota_exceeded_fallback():
    with patch("app.services.resource_matcher.httpx.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value.__enter__.return_value = mock_instance
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.json.return_value = {"error": {"message": "Quota exceeded"}}
        mock_instance.get.return_value = mock_resp
        
        with patch("app.config.settings.YOUTUBE_DATA_API_KEY", "mock_key_abc"):
            from app.services.resource_matcher import clear_cache
            clear_cache()
            
            resp = client.get("/api/resources/r_yt_err/matches?name=Python%20Intro&type=youtube_channel")
            assert resp.status_code == 200
            data = resp.json()["data"]
            assert data["fallback"] is True


def test_resource_matches_docs_and_books():
    # Test docs scoped Google search
    docs_resp = client.get("/api/resources/r_docs_test/matches?name=Dependency%20Injection&type=docs&search_hint=FastAPI%20Dependency%20Injection")
    assert docs_resp.status_code == 200
    docs_data = docs_resp.json()["data"]
    assert docs_data["type"] == "docs"
    assert "google.com/search?q=site" in docs_data["search_url"]
    assert "FastAPI" in docs_data["search_url"]
    
    # Test book structured metadata without illegal download links
    book_resp = client.get("/api/resources/r_book_test/matches?name=Designing%20Data-Intensive%20Applications&type=book")
    assert book_resp.status_code == 200
    book_data = book_resp.json()["data"]
    assert book_data["type"] == "book"
    assert len(book_data["topics"]) > 0
    assert "download_link" not in book_data

