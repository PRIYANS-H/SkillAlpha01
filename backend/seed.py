import os
import sys
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.db import Base, engine, SessionLocal
from app.models.models import (
    Skill, SkillRelationship, Resource, ResourceSkill
)
from app.services.skill_service import get_or_create_skill

def seed_database():
    print("--- Initializing Database Seed for SkillAlpha ---")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Skill Ontology
        skills_data = [
            ("Python Architecture", "Machine Learning", "BEGINNER", "Object-oriented patterns, data structures, and efficient Python code."),
            ("SQL & Analytical Queries", "Data Science", "BEGINNER", "Relational database queries, joins, aggregations, and window functions."),
            ("Applied Statistics", "Data Science", "INTERMEDIATE", "Probability distributions, hypothesis testing, and statistical confidence."),
            ("Pandas & Data Manipulation", "Machine Learning", "INTERMEDIATE", "DataFrames, data cleaning, vectorization, and feature transformations."),
            ("Machine Learning Foundations", "Machine Learning", "INTERMEDIATE", "Supervised vs unsupervised learning, bias-variance tradeoff, decision trees."),
            ("Model Validation & Split Hygiene", "Machine Learning", "INTERMEDIATE", "Cross-validation folds, avoiding target leakage, stratified splitting."),
            ("Feature Engineering & Selection", "Machine Learning", "ADVANCED", "Numerical scaling, categorical encoding, feature importance, dimensionality reduction."),
            ("Hyperparameter Optimization", "Machine Learning", "ADVANCED", "Grid search, random search, Bayesian optimization using Optuna."),
            ("Model Deployment & APIs", "MLOps", "ADVANCED", "Serving machine learning models using FastAPI, Docker, and REST endpoints."),
            ("Docker & Containerization", "DevOps", "INTERMEDIATE", "Containerizing application workloads, Dockerfiles, and compose configurations."),
            ("MLOps & Monitoring", "MLOps", "EXPERT", "Model monitoring, data drift detection, automated retraining pipelines.")
        ]

        skill_map = {}
        for name, domain, diff, desc in skills_data:
            s = get_or_create_skill(db, name, domain, diff)
            s.description = desc
            skill_map[name] = s
        db.commit()

        # 2. Resources
        raw_resources = [
            {
                "title": "Target Leakage & Split Hygiene in Time-Series Features",
                "url": "https://scikit-learn.org/stable/common_pitfalls.html#data-leakage",
                "provider": "Scikit-Learn Guide",
                "resource_type": "DOCUMENTATION",
                "description": "Official Scikit-Learn guide explaining train/validation leakage traps, pipeline isolation, and feature isolation.",
                "duration_minutes": 11,
                "difficulty": "INTERMEDIATE",
                "skill": "Model Validation & Split Hygiene"
            },
            {
                "title": "Interactive Lab: Building Leak-Free ML Pipelines",
                "url": "https://github.com/scikit-learn/scikit-learn/blob/main/examples/model_selection/plot_cv_predict.py",
                "provider": "Jupyter Executable",
                "resource_type": "PRACTICE",
                "description": "Practical notebook walking through Cross-Validation folds without pre-fit scaling leakage.",
                "duration_minutes": 15,
                "difficulty": "INTERMEDIATE",
                "skill": "Model Validation & Split Hygiene"
            },
            {
                "title": "Cross-Validation Explained Deep Dive",
                "url": "https://www.youtube.com/watch?v=fSytzGwwBVw",
                "provider": "StatQuest YouTube",
                "resource_type": "VIDEO",
                "description": "Visual intuition of k-fold, stratified, and leave-one-out cross-validation techniques.",
                "duration_minutes": 14,
                "difficulty": "INTERMEDIATE",
                "skill": "Model Validation & Split Hygiene"
            },
            {
                "title": "Feature Engineering for Machine Learning",
                "url": "https://github.com/dipanjanS/practical-machine-learning-with-python",
                "provider": "GitHub Repo",
                "resource_type": "GITHUB",
                "description": "Production Python scripts for one-hot encoding, target encoding, and automated feature selection.",
                "duration_minutes": 25,
                "difficulty": "ADVANCED",
                "skill": "Feature Engineering & Selection"
            },
            {
                "title": "Hyperparameter Search with Optuna",
                "url": "https://optuna.readthedocs.io/en/stable/tutorial/index.html",
                "provider": "Optuna Documentation",
                "resource_type": "DOCUMENTATION",
                "description": "Efficient Bayesian hyperparameter optimization tutorial with pruning algorithms.",
                "duration_minutes": 20,
                "difficulty": "ADVANCED",
                "skill": "Hyperparameter Optimization"
            },
            {
                "title": "Serving Scikit-Learn Models with FastAPI and Docker",
                "url": "https://fastapi.tiangolo.com/deployment/docker/",
                "provider": "FastAPI Docs",
                "resource_type": "DOCUMENTATION",
                "description": "Step-by-step guide to wrapping model prediction endpoints in FastAPI microservices.",
                "duration_minutes": 18,
                "difficulty": "ADVANCED",
                "skill": "Model Deployment & APIs"
            }
        ]

        for r_item in raw_resources:
            existing_res = db.query(Resource).filter(Resource.title == r_item["title"]).first()
            if not existing_res:
                r = Resource(
                    title=r_item["title"],
                    url=r_item["url"],
                    provider=r_item["provider"],
                    resource_type=r_item["resource_type"],
                    description=r_item["description"],
                    duration_minutes=r_item["duration_minutes"],
                    difficulty=r_item["difficulty"],
                    quality_score=0.94,
                    relevance_score=0.96,
                    freshness_score=0.95,
                    engagement_score=0.88,
                    verified=True
                )
                db.add(r)
                db.commit()
                db.refresh(r)

                s_obj = skill_map.get(r_item["skill"])
                if s_obj:
                    rs = ResourceSkill(resource_id=r.id, skill_id=s_obj.id)
                    db.add(rs)
        db.commit()

        db.commit()
        print("Database successfully seeded with skills ontology, relationships, and curated resources!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
