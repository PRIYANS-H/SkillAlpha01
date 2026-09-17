from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.models.models import Skill, SkillRelationship, UserSkill

def get_or_create_skill(db: Session, name: str, domain: str = "General", difficulty: str = "INTERMEDIATE") -> Skill:
    slug = name.lower().replace(" ", "-").replace("/", "-")
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        skill = Skill(
            name=name,
            slug=slug,
            domain=domain,
            difficulty=difficulty,
            description=f"Core concept and practical techniques for {name}"
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)
    return skill

def get_target_skill_graph_for_goal(db: Session, goal_name: str) -> List[Skill]:
    """
    Returns ordered skill node list for target goal graph.
    Supports Machine Learning Engineer, Data Scientist, Backend Developer, React Developer, Data Engineer.
    """
    goal_lower = goal_name.lower()
    
    if "machine learning" in goal_lower or "ml" in goal_lower:
        skill_names = [
            ("Python Architecture", "Machine Learning", "BEGINNER"),
            ("SQL & Analytical Queries", "Data Science", "BEGINNER"),
            ("Applied Statistics", "Data Science", "INTERMEDIATE"),
            ("Pandas & Data Manipulation", "Machine Learning", "INTERMEDIATE"),
            ("Machine Learning Foundations", "Machine Learning", "INTERMEDIATE"),
            ("Model Validation & Split Hygiene", "Machine Learning", "INTERMEDIATE"),
            ("Feature Engineering & Selection", "Machine Learning", "ADVANCED"),
            ("Hyperparameter Optimization", "Machine Learning", "ADVANCED"),
            ("Model Deployment & APIs", "MLOps", "ADVANCED"),
            ("Docker & Containerization", "DevOps", "INTERMEDIATE"),
            ("MLOps & Monitoring", "MLOps", "EXPERT")
        ]
    elif "data scientist" in goal_lower or "data science" in goal_lower:
        skill_names = [
            ("Python Architecture", "Data Science", "BEGINNER"),
            ("SQL & Analytical Queries", "Data Science", "BEGINNER"),
            ("Exploratory Data Analysis", "Data Science", "INTERMEDIATE"),
            ("Applied Statistics & Hypothesis Testing", "Data Science", "INTERMEDIATE"),
            ("Pandas & Data Manipulation", "Data Science", "INTERMEDIATE"),
            ("Machine Learning Foundations", "Data Science", "INTERMEDIATE"),
            ("Data Visualization & Storytelling", "Data Science", "INTERMEDIATE"),
            ("Model Validation & Split Hygiene", "Data Science", "ADVANCED")
        ]
    elif "backend" in goal_lower or "fastapi" in goal_lower or "python dev" in goal_lower:
        skill_names = [
            ("Python Architecture", "Backend", "BEGINNER"),
            ("SQL & Analytical Queries", "Backend", "INTERMEDIATE"),
            ("RESTful API Architecture", "Backend", "INTERMEDIATE"),
            ("Database Indexing & ORM Hygiene", "Backend", "ADVANCED"),
            ("Authentication & JWT Security", "Backend", "ADVANCED"),
            ("Docker & Containerization", "DevOps", "INTERMEDIATE"),
            ("Async Programming & Concurrency", "Backend", "EXPERT")
        ]
    elif "react" in goal_lower or "frontend" in goal_lower:
        skill_names = [
            ("JavaScript Fundamentals & ES6+", "Frontend", "BEGINNER"),
            ("React Component Architecture", "Frontend", "INTERMEDIATE"),
            ("TypeScript Integration", "Frontend", "INTERMEDIATE"),
            ("State Management & React Query", "Frontend", "ADVANCED"),
            ("Performance Optimization & Memoization", "Frontend", "EXPERT")
        ]
    else: # Default engineering path
        skill_names = [
            ("Python Architecture", "General", "BEGINNER"),
            ("SQL & Analytical Queries", "General", "BEGINNER"),
            ("Software Architecture", "General", "INTERMEDIATE"),
            ("API Integration & Web Security", "General", "INTERMEDIATE"),
            ("Deployment & CI/CD Pipelines", "DevOps", "ADVANCED")
        ]
        
    skills = []
    for name, domain, diff in skill_names:
        skills.append(get_or_create_skill(db, name, domain, diff))
    return skills
