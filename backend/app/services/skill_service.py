import re
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

# Ordered (name, domain, difficulty) skill graphs per goal family, prerequisites first.
GOAL_SKILL_GRAPHS: Dict[str, List[Tuple[str, str, str]]] = {
    "machine_learning": [
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
    ],
    "data_science": [
        ("Python Architecture", "Data Science", "BEGINNER"),
        ("SQL & Analytical Queries", "Data Science", "BEGINNER"),
        ("Exploratory Data Analysis", "Data Science", "INTERMEDIATE"),
        ("Applied Statistics & Hypothesis Testing", "Data Science", "INTERMEDIATE"),
        ("Pandas & Data Manipulation", "Data Science", "INTERMEDIATE"),
        ("Machine Learning Foundations", "Data Science", "INTERMEDIATE"),
        ("Data Visualization & Storytelling", "Data Science", "INTERMEDIATE"),
        ("Model Validation & Split Hygiene", "Data Science", "ADVANCED")
    ],
    "backend": [
        ("Python Architecture", "Backend", "BEGINNER"),
        ("SQL & Analytical Queries", "Backend", "INTERMEDIATE"),
        ("RESTful API Architecture", "Backend", "INTERMEDIATE"),
        ("Database Indexing & ORM Hygiene", "Backend", "ADVANCED"),
        ("Authentication & JWT Security", "Backend", "ADVANCED"),
        ("Docker & Containerization", "DevOps", "INTERMEDIATE"),
        ("Async Programming & Concurrency", "Backend", "EXPERT")
    ],
    "frontend": [
        ("JavaScript Fundamentals & ES6+", "Frontend", "BEGINNER"),
        ("React Component Architecture", "Frontend", "INTERMEDIATE"),
        ("TypeScript Integration", "Frontend", "INTERMEDIATE"),
        ("State Management & React Query", "Frontend", "ADVANCED"),
        ("Performance Optimization & Memoization", "Frontend", "EXPERT")
    ],
    "data_engineering": [
        ("SQL & Analytical Queries", "Data Engineering", "BEGINNER"),
        ("Python Architecture", "Data Engineering", "BEGINNER"),
        ("Data Modeling & Warehousing", "Data Engineering", "INTERMEDIATE"),
        ("Apache Spark & Distributed Computing", "Data Engineering", "ADVANCED"),
        ("Orchestration & Airflow", "Data Engineering", "ADVANCED"),
        ("Docker & Containerization", "DevOps", "INTERMEDIATE")
    ],
    "devops": [
        ("Linux Systems & Shell Scripting", "DevOps", "BEGINNER"),
        ("Docker & Containerization", "DevOps", "INTERMEDIATE"),
        ("Kubernetes Orchestration", "DevOps", "ADVANCED"),
        ("Infrastructure as Code & Terraform", "DevOps", "ADVANCED"),
        ("CI/CD Pipeline Automation", "DevOps", "INTERMEDIATE")
    ],
    "security": [
        ("Network Fundamentals & Security", "Security", "BEGINNER"),
        ("Web Security & OWASP Top 10", "Security", "INTERMEDIATE"),
        ("Cryptography & Identity Hygiene", "Security", "INTERMEDIATE"),
        ("Penetration Testing & Auditing", "Security", "ADVANCED")
    ],
    "mobile": [
        ("Mobile UI Architecture", "Mobile", "BEGINNER"),
        ("State Management & Reactivity", "Mobile", "INTERMEDIATE"),
        ("REST & GraphQL Integration", "Mobile", "INTERMEDIATE"),
        ("Native Device Access & Security", "Mobile", "ADVANCED")
    ],
    "quant_finance": [
        ("Python for Quant Finance", "Quant Finance", "BEGINNER"),
        ("Probability & Statistics for Trading", "Quant Finance", "BEGINNER"),
        ("Financial Markets & Instruments", "Quant Finance", "BEGINNER"),
        ("Backtesting & Performance Metrics", "Quant Finance", "INTERMEDIATE"),
        ("Time Series Analysis & Stationarity", "Quant Finance", "INTERMEDIATE"),
        ("Mean Reversion & Pairs Trading", "Quant Finance", "INTERMEDIATE"),
        ("Momentum & Technical Signals", "Quant Finance", "INTERMEDIATE"),
        ("Machine Learning for Trading", "Quant Finance", "ADVANCED"),
        ("Risk Management & Portfolio Construction", "Quant Finance", "ADVANCED"),
        ("Live Trading & Broker APIs", "Quant Finance", "ADVANCED"),
        ("Options Pricing & Greeks", "Quant Finance", "ADVANCED"),
        ("Alpha Research & Factor Models", "Quant Finance", "EXPERT"),
        ("Quant Interview Problem Solving", "Quant Finance", "EXPERT"),
    ],
    "general": [
        ("Python Architecture", "General", "BEGINNER"),
        ("SQL & Analytical Queries", "General", "BEGINNER"),
        ("Software Architecture", "General", "INTERMEDIATE"),
        ("API Integration & Web Security", "General", "INTERMEDIATE"),
        ("Deployment & CI/CD Pipelines", "DevOps", "ADVANCED")
    ],
}

# Goal keyword rules, checked in order. Terms are matched as whole words/phrases so that
# short terms like "ml" do not match inside "html".
GOAL_RULES: List[Tuple[str, Tuple[str, ...]]] = [
    # Checked first so "machine learning for trading" or "quant developer" land on the quant track
    ("quant_finance", ("quant", "quants", "quantitative", "algo trading", "algorithmic trading", "algo trader",
                       "trading", "trader", "hedge fund", "derivatives", "stock market")),
    ("machine_learning", ("machine learning", "ml", "mlops", "deep learning", "ai engineer")),
    ("data_science", ("data scientist", "data science", "data analyst", "analytics")),
    ("backend", ("backend", "back end", "back-end", "fastapi", "django", "python dev", "python developer", "api developer")),
    ("frontend", ("react", "frontend", "front end", "front-end", "javascript", "typescript", "web developer", "html", "css", "ui developer")),
    ("data_engineering", ("data engineer", "data engineering", "etl", "pipeline", "pipelines", "spark", "airflow")),
    ("devops", ("devops", "sre", "cloud", "aws", "azure", "gcp", "kubernetes", "platform engineer")),
    ("security", ("cybersecurity", "cyber security", "security", "pentest", "pentesting", "ethical hacking")),
    ("mobile", ("mobile", "android", "ios", "flutter", "react native", "kotlin", "swift")),
]


def goal_matches(goal: str, *terms: str) -> bool:
    text = (goal or "").lower()
    return any(re.search(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", text) for t in terms)


def resolve_goal_family(goal: str) -> str:
    # "React Native" is mobile even though it mentions React
    if goal_matches(goal, "react native"):
        return "mobile"
    for family, terms in GOAL_RULES:
        if goal_matches(goal, *terms):
            return family
    return "general"


def get_goal_skill_specs(goal: str) -> List[Tuple[str, str, str]]:
    """DB-free ordered (name, domain, difficulty) list for a goal."""
    return GOAL_SKILL_GRAPHS[resolve_goal_family(goal)]


def get_target_skill_graph_for_goal(db: Session, goal_name: str) -> List[Skill]:
    """Returns the ordered skill node list for the goal, creating Skill rows as needed."""
    skill_names = get_goal_skill_specs(goal_name)

    skills = []
    for name, domain, diff in skill_names:
        skills.append(get_or_create_skill(db, name, domain, diff))
    return skills
