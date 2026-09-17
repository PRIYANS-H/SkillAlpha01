from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Standard API Response wrapper
class APIResponse(BaseModel):
    data: Optional[Any] = None
    meta: Optional[Dict[str, Any]] = {}
    error: Optional[Dict[str, Any]] = None

# Auth & User Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ProfileUpdateRequest(BaseModel):
    goal: Optional[str] = None
    target_role: Optional[str] = None
    available_hours: Optional[int] = None
    duration_weeks: Optional[int] = None
    learning_preferences: Optional[List[str]] = None
    github_username: Optional[str] = None

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    goal: Optional[str] = None
    target_role: Optional[str] = None
    available_hours: int
    duration_weeks: int
    learning_preferences: Optional[List[str]] = None
    github_username: Optional[str] = None
    
    class Config:
        from_attributes = True

# Skill Schemas
class SkillBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    domain: str
    difficulty: str

class SkillResponse(SkillBase):
    id: str
    prerequisites: List[str] = []
    
    class Config:
        from_attributes = True

class UserSkillUpdate(BaseModel):
    skill_name: str
    self_reported_level: str # Beginner, Familiar, Intermediate, Advanced, Expert
    confidence_score: Optional[float] = 0.8

class UserSkillResponse(BaseModel):
    id: str
    skill_id: str
    skill_name: str
    skill_score: float
    confidence_score: float
    status: str # MASTERED, STRONG, NEEDS_REINFORCEMENT, MISSING, BLOCKED
    evidence_count: int
    last_assessed_at: datetime
    
    class Config:
        from_attributes = True

# Resource Schemas
class ResourceResponse(BaseModel):
    id: str
    title: str
    url: str
    provider: str
    resource_type: str
    description: Optional[str] = None
    duration_minutes: int
    difficulty: str
    quality_score: float
    relevance_score: float
    verified: bool
    match_score: Optional[int] = 92
    match_reason: Optional[str] = None
    skill_names: List[str] = []
    
    class Config:
        from_attributes = True

# Onboarding / Roadmap Creation Request
class OnboardingRequest(BaseModel):
    goal: str
    known_skills: List[UserSkillUpdate] = []
    available_hours: int = 10
    duration_weeks: int = 12
    learning_preferences: List[str] = ["VIDEO", "DOCUMENTATION", "PROJECT"]
    github_username: Optional[str] = None

class RoadmapTaskResourceResponse(BaseModel):
    resource_id: str
    title: str
    url: str
    provider: str
    resource_type: str
    duration_minutes: int
    recommendation_match_score: float
    recommendation_reason: Optional[str] = None

class RoadmapTaskResponse(BaseModel):
    id: str
    milestone_id: str
    skill_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    estimated_minutes: int
    sequence_order: int
    status: str # NOT_STARTED, IN_PROGRESS, COMPLETED, SKIPPED
    reason_why_next: Optional[str] = None
    resources: List[RoadmapTaskResourceResponse] = []
    
    class Config:
        from_attributes = True

class RoadmapMilestoneResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    week_number: int
    sequence_order: int
    is_completed: bool
    tasks: List[RoadmapTaskResponse] = []
    
    class Config:
        from_attributes = True

class RoadmapResponse(BaseModel):
    id: str
    user_id: str
    title: str
    goal: str
    duration_weeks: int
    hours_per_week: int
    total_tasks: int
    completed_tasks: int
    progress_percent: float
    route_reasoning: Optional[str] = None
    is_active: bool
    created_at: datetime
    milestones: List[RoadmapMilestoneResponse] = []
    
    class Config:
        from_attributes = True

# Today's Learning Response
class TodayLearningResponse(BaseModel):
    task: Optional[RoadmapTaskResponse] = None
    milestone_title: Optional[str] = None
    roadmap_id: Optional[str] = None
    total_due_today: int = 1
    reason_why_today: Optional[str] = None

# Task Completion / Progress Request
class TaskCompleteRequest(BaseModel):
    time_spent_minutes: int = 30
    self_evaluation: str = "GOT_IT" # GOT_IT, SHAKY, LOST
    notes: Optional[str] = None

# Assessment Schemas
class AssessmentQuestionResponse(BaseModel):
    id: str
    question_text: str
    options: List[str]
    explanation: Optional[str] = None

class AssessmentResponse(BaseModel):
    id: str
    skill_id: str
    title: str
    description: Optional[str] = None
    difficulty: str
    questions: List[AssessmentQuestionResponse] = []

class AssessmentAttemptRequest(BaseModel):
    answers: Dict[str, int] # question_id -> selected_option_index

class AssessmentAttemptResponse(BaseModel):
    id: str
    assessment_id: str
    score: float
    max_score: float
    passed: bool
    new_skill_score: float
    feedback: str

# Feedback Request
class ResourceFeedbackRequest(BaseModel):
    is_useful: bool
    rating_reason: Optional[str] = None # TOO_EASY, TOO_HARD, TOO_LONG, NOT_RELEVANT, HELPFUL

# Admin Metrics Response
class AdminMetricsResponse(BaseModel):
    active_users: int
    roadmaps_created: int
    resources_indexed: int
    recommendations_served: int
    save_rate_percent: float
    completion_rate_percent: float
    avg_feedback_score: float

# CMS Content Schema
class ContentResponse(BaseModel):
    key: str
    scope: str
    value: str
    updated_at: datetime

class ContentUpdateRequest(BaseModel):
    value: str
    scope: Optional[str] = "GLOBAL"
