import datetime
import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.models.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="USER", nullable=False) # USER, ADMIN
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False)
    roadmaps = relationship("Roadmap", back_populates="user")
    user_skills = relationship("UserSkill", back_populates="user")
    learning_sessions = relationship("LearningSession", back_populates="user")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="user")
    saved_resources = relationship("SavedResource", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    goal = Column(String(255), nullable=True)
    target_role = Column(String(255), nullable=True)
    available_hours = Column(Integer, default=10)
    duration_weeks = Column(Integer, default=12)
    learning_preferences = Column(Text, nullable=True) # JSON list: ["VIDEO", "DOCUMENTATION"]
    github_username = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=False, index=True) # Machine Learning, Web Dev, Data, etc.
    difficulty = Column(String(50), default="INTERMEDIATE") # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_skills = relationship("UserSkill", back_populates="skill")
    resource_skills = relationship("ResourceSkill", back_populates="skill")


class SkillRelationship(Base):
    __tablename__ = "skill_relationships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    prerequisite_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    relationship_type = Column(String(50), default="PREREQUISITE") # PREREQUISITE, PARENT, RELATED


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    skill_score = Column(Float, default=0.0) # 0.0 to 1.0
    confidence_score = Column(Float, default=0.5) # 0.0 to 1.0
    status = Column(String(50), default="MISSING") # MASTERED, STRONG, NEEDS_REINFORCEMENT, MISSING, BLOCKED
    evidence_count = Column(Integer, default=0)
    last_assessed_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="user_skills")
    skill = relationship("Skill", back_populates="user_skills")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, index=True)
    url = Column(Text, nullable=False)
    provider = Column(String(100), nullable=False) # Scikit-Learn, YouTube, GitHub, FastAPI Docs, etc.
    resource_type = Column(String(50), nullable=False) # VIDEO, ARTICLE, DOCUMENTATION, COURSE, GITHUB, PRACTICE, TUTORIAL
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=15)
    difficulty = Column(String(50), default="INTERMEDIATE") # BEGINNER, INTERMEDIATE, ADVANCED
    quality_score = Column(Float, default=0.85) # 0.0 to 1.0
    relevance_score = Column(Float, default=0.90)
    freshness_score = Column(Float, default=0.95)
    engagement_score = Column(Float, default=0.80)
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    resource_skills = relationship("ResourceSkill", back_populates="resource")
    feedback = relationship("ResourceFeedback", back_populates="resource")


class ResourceSkill(Base):
    __tablename__ = "resource_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)

    resource = relationship("Resource", back_populates="resource_skills")
    skill = relationship("Skill", back_populates="resource_skills")


class ResourceFeedback(Base):
    __tablename__ = "resource_feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    is_useful = Column(Boolean, nullable=False)
    rating_reason = Column(String(255), nullable=True) # TOO_EASY, TOO_HARD, TOO_LONG, NOT_RELEVANT, HELPFUL
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resource = relationship("Resource", back_populates="feedback")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    goal = Column(String(255), nullable=False)
    duration_weeks = Column(Integer, default=12)
    hours_per_week = Column(Integer, default=10)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    progress_percent = Column(Float, default=0.0)
    route_reasoning = Column(Text, nullable=True) # "Why your route looks like this" explanation
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="roadmaps")
    milestones = relationship("RoadmapMilestone", back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapMilestone(Base):
    __tablename__ = "roadmap_milestones"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    roadmap_id = Column(String(36), ForeignKey("roadmaps.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    week_number = Column(Integer, nullable=False)
    sequence_order = Column(Integer, nullable=False)
    is_completed = Column(Boolean, default=False)

    roadmap = relationship("Roadmap", back_populates="milestones")
    tasks = relationship("RoadmapTask", back_populates="milestone", cascade="all, delete-orphan")


class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    milestone_id = Column(String(36), ForeignKey("roadmap_milestones.id"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    estimated_minutes = Column(Integer, default=30)
    sequence_order = Column(Integer, nullable=False)
    status = Column(String(50), default="NOT_STARTED") # NOT_STARTED, IN_PROGRESS, COMPLETED, SKIPPED
    reason_why_next = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    milestone = relationship("RoadmapMilestone", back_populates="tasks")
    task_resources = relationship("TaskResource", back_populates="task", cascade="all, delete-orphan")
    progress_entries = relationship("TaskProgress", back_populates="task")


class TaskResource(Base):
    __tablename__ = "task_resources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("roadmap_tasks.id"), nullable=False)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=False)
    recommendation_match_score = Column(Float, default=0.90) # 0.0 to 1.0
    recommendation_reason = Column(Text, nullable=True)
    sequence_order = Column(Integer, default=1)

    task = relationship("RoadmapTask", back_populates="task_resources")
    resource = relationship("Resource")


class TaskProgress(Base):
    __tablename__ = "task_progress"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("roadmap_tasks.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    time_spent_minutes = Column(Integer, default=0)
    self_evaluation = Column(String(50), nullable=True) # GOT_IT, SHAKY, LOST

    task = relationship("RoadmapTask", back_populates="progress_entries")


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("roadmap_tasks.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="IN_PROGRESS") # IN_PROGRESS, COMPLETED, PAUSED

    user = relationship("User", back_populates="learning_sessions")
    task = relationship("RoadmapTask")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(50), default="INTERMEDIATE")

    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False) # JSON list of string options
    correct_option_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)

    assessment = relationship("Assessment", back_populates="questions")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    passed = Column(Boolean, default=True)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="assessment_attempts")
    assessment = relationship("Assessment")


class SavedResource(Base):
    __tablename__ = "saved_resources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="saved_resources")
    resource = relationship("Resource")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class Content(Base):
    __tablename__ = "content"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    key = Column(String(255), unique=True, nullable=False, index=True)
    scope = Column(String(50), default="GLOBAL") # LANDING, ROADMAP, GLOBAL
    value = Column(Text, nullable=False)
    locale = Column(String(10), default="en")
    updated_by = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
