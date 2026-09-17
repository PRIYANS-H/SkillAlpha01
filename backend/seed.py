import os
import sys
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.db import Base, engine, SessionLocal
from app.models.models import (
    User, Profile, Skill, SkillRelationship, UserSkill, Resource, ResourceSkill,
    Roadmap, RoadmapMilestone, RoadmapTask, TaskResource, Assessment, AssessmentQuestion
)
from app.security.auth import hash_password
from app.services.skill_service import get_or_create_skill
from app.services.recommendation_engine import rank_resources_for_skill

def seed_database():
    print("--- Initializing Database Seed for SkillAlpha ---")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Admin & Demo User
        admin_user = db.query(User).filter(User.email == "admin@skillalpha.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@skillalpha.com",
                hashed_password=hash_password("admin123"),
                full_name="SkillAlpha Lead Architect",
                role="ADMIN"
            )
            db.add(admin_user)

        demo_user = db.query(User).filter(User.email == "learner@skillalpha.com").first()
        if not demo_user:
            demo_user = User(
                email="learner@skillalpha.com",
                hashed_password=hash_password("learner123"),
                full_name="Alex Rivera",
                role="USER"
            )
            db.add(demo_user)
            db.commit()

            profile = Profile(
                user_id=demo_user.id,
                goal="Become a Machine Learning Engineer",
                target_role="Machine Learning Engineer",
                available_hours=12,
                duration_weeks=12,
                github_username="arivera-dev"
            )
            db.add(profile)

        db.commit()

        # 2. Skill Ontology
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

        # 3. User Baseline Skills
        user_skills_seed = [
            ("Python Architecture", 0.88, 0.90, "MASTERED", 4),
            ("SQL & Analytical Queries", 0.71, 0.85, "STRONG", 3),
            ("Applied Statistics", 0.63, 0.75, "NEEDS_REINFORCEMENT", 2),
            ("Machine Learning Foundations", 0.41, 0.60, "NEEDS_REINFORCEMENT", 1),
            ("Model Validation & Split Hygiene", 0.35, 0.50, "MISSING", 0)
        ]

        for s_name, score, conf, status, ev in user_skills_seed:
            s_obj = skill_map.get(s_name)
            if s_obj:
                us = db.query(UserSkill).filter(
                    UserSkill.user_id == demo_user.id,
                    UserSkill.skill_id == s_obj.id
                ).first()
                if not us:
                    us = UserSkill(
                        user_id=demo_user.id,
                        skill_id=s_obj.id,
                        skill_score=score,
                        confidence_score=conf,
                        status=status,
                        evidence_count=ev
                    )
                    db.add(us)
        db.commit()

        # 4. Resources
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

        # 5. Roadmap for Demo User
        existing_rm = db.query(Roadmap).filter(Roadmap.user_id == demo_user.id).first()
        if not existing_rm:
            rm = Roadmap(
                user_id=demo_user.id,
                title="Become a Machine Learning Engineer",
                goal="Become a Machine Learning Engineer",
                duration_weeks=12,
                hours_per_week=12,
                total_tasks=4,
                completed_tasks=1,
                progress_percent=25.0,
                route_reasoning="You demonstrated strong Python (88%) and SQL (71%) fundamentals, so introductory modules were bypassed to save ~18 hours. Model Validation is your current primary gap.",
                is_active=True
            )
            db.add(rm)
            db.commit()
            db.refresh(rm)

            m1 = RoadmapMilestone(
                roadmap_id=rm.id,
                title="Week 01 • Python & Data Handling Baseline",
                description="Verified background in Python data structures and SQL analytical queries.",
                week_number=1,
                sequence_order=1,
                is_completed=True
            )
            db.add(m1)
            db.commit()
            db.refresh(m1)

            t1 = RoadmapTask(
                milestone_id=m1.id,
                skill_id=skill_map["Python Architecture"].id,
                title="Master Python Data Architecture",
                description="Object-oriented programming principles and vectorized NumPy operations.",
                estimated_minutes=25,
                sequence_order=1,
                status="COMPLETED",
                reason_why_next="Bypassed based on 88% verified skill baseline score."
            )
            db.add(t1)

            m2 = RoadmapMilestone(
                roadmap_id=rm.id,
                title="Week 02 • Model Validation & Split Hygiene",
                description="Avoid data leakage across cross-validation folds. Essential prerequisite before gradient boosted trees.",
                week_number=2,
                sequence_order=2,
                is_completed=False
            )
            db.add(m2)
            db.commit()
            db.refresh(m2)

            val_skill = skill_map["Model Validation & Split Hygiene"]
            t2 = RoadmapTask(
                milestone_id=m2.id,
                skill_id=val_skill.id,
                title="Model Validation & Split Hygiene",
                description="Avoid data leakage across cross-validation folds. Essential prerequisite before starting gradient boosted trees.",
                estimated_minutes=32,
                sequence_order=1,
                status="NOT_STARTED",
                reason_why_next="Validation is currently one of your largest skill gaps."
            )
            db.add(t2)
            db.commit()
            db.refresh(t2)

            val_resources = rank_resources_for_skill(db, val_skill, 0.35, limit=3)
            for idx, item in enumerate(val_resources):
                tr = TaskResource(
                    task_id=t2.id,
                    resource_id=item["resource"].id,
                    recommendation_match_score=item["match_score"] / 100.0,
                    recommendation_reason=item["match_reason"],
                    sequence_order=idx + 1
                )
                db.add(tr)

            m3 = RoadmapMilestone(
                roadmap_id=rm.id,
                title="Week 03 • Feature Engineering & Selection",
                description="Transform categorical variables and scale numerical distributions.",
                week_number=3,
                sequence_order=3,
                is_completed=False
            )
            db.add(m3)
            db.commit()
            db.refresh(m3)

            fe_skill = skill_map["Feature Engineering & Selection"]
            t3 = RoadmapTask(
                milestone_id=m3.id,
                skill_id=fe_skill.id,
                title="Feature Engineering & Selection",
                description="Numerical scaling, categorical encoding, and feature importance analysis.",
                estimated_minutes=40,
                sequence_order=1,
                status="NOT_STARTED",
                reason_why_next="Queued following model validation hygiene."
            )
            db.add(t3)

        db.commit()
        print("Database successfully seeded with production demo data!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
