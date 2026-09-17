import math
import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.models import (
    Roadmap, RoadmapMilestone, RoadmapTask, TaskResource, UserSkill, Skill
)
from app.services.skill_service import get_target_skill_graph_for_goal
from app.services.gap_engine import evaluate_skill_gaps
from app.services.recommendation_engine import rank_resources_for_skill

def generate_roadmap_for_user(
    db: Session,
    user_id: str,
    goal: str,
    hours_per_week: int = 10,
    duration_weeks: int = 12,
    self_reported_skills: Dict[str, str] = None,
    preferred_types: List[str] = None
) -> Roadmap:
    """
    Generates a personalized learning roadmap with explicit day-wise, date-wise, hour-wise schedule and ranked resources.
    """
    if self_reported_skills is None:
        self_reported_skills = {}
    if preferred_types is None:
        preferred_types = ["VIDEO", "DOCUMENTATION", "PROJECT", "PRACTICE"]

    # 1. Target Skill Graph
    target_skills = get_target_skill_graph_for_goal(db, goal)
    
    # 2. Skill Gap Engine
    evaluated_skills, route_reasoning = evaluate_skill_gaps(db, user_id, target_skills, self_reported_skills)
    
    # De-activate previous roadmaps for user
    db.query(Roadmap).filter(Roadmap.user_id == user_id, Roadmap.is_active == True).update({"is_active": False})
    
    # 3. Filter skills that need learning (skip MASTERED and STRONG)
    active_skills = [item for item in evaluated_skills if not item["should_skip"]]
    if not active_skills:
        active_skills = evaluated_skills

    title = f"Learning Path: {goal}"
    
    roadmap = Roadmap(
        user_id=user_id,
        title=title,
        goal=goal,
        duration_weeks=duration_weeks,
        hours_per_week=hours_per_week,
        route_reasoning=route_reasoning,
        is_active=True
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    # 4. Day-wise, Date-wise, and Hour-wise Allocation
    start_date = datetime.date.today()
    daily_hours_target = round(hours_per_week / 5.0, 1) # 5 study days per week
    
    milestone_titles = [
        "Foundations & Baseline Setup",
        "Core Concepts & Architecture",
        "Applied Practice & Validation",
        "Advanced Optimization & Projects",
        "Production Readiness & MLOps"
    ]
    
    num_milestones = max(1, math.ceil(len(active_skills) / 2))
    task_idx = 0
    total_tasks_created = 0
    current_day = 1

    for m_idx in range(num_milestones):
        m_title = milestone_titles[m_idx % len(milestone_titles)]
        week_num = m_idx + 1
        
        # Calculate start and end date for milestone
        m_start_date = start_date + datetime.timedelta(days=(week_num - 1) * 7)
        m_end_date = m_start_date + datetime.timedelta(days=6)
        
        milestone = RoadmapMilestone(
            roadmap_id=roadmap.id,
            title=f"Week {week_num:02d} ({m_start_date.strftime('%b %d')} - {m_end_date.strftime('%b %d')}) • {m_title}",
            description=f"Schedule Target: {hours_per_week} hrs/week ({daily_hours_target} hrs/day) • Master key dependencies for Week {week_num}.",
            week_number=week_num,
            sequence_order=m_idx + 1
        )
        db.add(milestone)
        db.commit()
        db.refresh(milestone)

        m_skills = active_skills[task_idx : task_idx + 2]
        if not m_skills and task_idx < len(active_skills):
            m_skills = [active_skills[task_idx]]
        task_idx += len(m_skills)

        for t_seq, skill_item in enumerate(m_skills):
            skill_obj = db.query(Skill).filter(Skill.id == skill_item["skill_id"]).first()
            if not skill_obj:
                continue

            # Day-wise date computation
            task_date = m_start_date + datetime.timedelta(days=(t_seq * 2))
            date_str = task_date.strftime("%a, %b %d")

            reason_why = f"Day {current_day} ({date_str}) • Allocated {daily_hours_target} hrs. Required to bridge your {skill_item['skill_name']} gap."

            task = RoadmapTask(
                milestone_id=milestone.id,
                skill_id=skill_obj.id,
                title=f"Day {current_day} ({date_str}) • Master {skill_obj.name}",
                description=skill_obj.description or f"Complete curated readings, code labs, and checkpoints for {skill_obj.name}.",
                estimated_minutes=int(daily_hours_target * 60),
                sequence_order=t_seq + 1,
                status="NOT_STARTED",
                reason_why_next=reason_why
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            total_tasks_created += 1
            current_day += 2

            # Attach ranked resources to task
            ranked_res = rank_resources_for_skill(
                db=db,
                skill=skill_obj,
                user_skill_score=skill_item["score"],
                preferred_types=preferred_types,
                limit=3
            )

            for r_seq, item in enumerate(ranked_res):
                res_obj = item["resource"]
                tr = TaskResource(
                    task_id=task.id,
                    resource_id=res_obj.id,
                    recommendation_match_score=item["match_score"] / 100.0,
                    recommendation_reason=item["match_reason"],
                    sequence_order=r_seq + 1
                )
                db.add(tr)

    roadmap.total_tasks = total_tasks_created
    db.commit()
    db.refresh(roadmap)
    return roadmap


def adaptive_replan_roadmap(db: Session, roadmap_id: str, user_id: str) -> Roadmap:
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id).first()
    if not roadmap:
        return None

    shaky_user_skills = db.query(UserSkill).filter(
        UserSkill.user_id == user_id,
        UserSkill.status == "NEEDS_REINFORCEMENT"
    ).all()

    if shaky_user_skills:
        # Find active milestone (earliest milestone with incomplete tasks)
        active_milestone = None
        for m in sorted(roadmap.milestones, key=lambda x: x.sequence_order):
            if any(t.status in ["NOT_STARTED", "IN_PROGRESS"] for t in m.tasks):
                active_milestone = m
                break
        if not active_milestone and roadmap.milestones:
            active_milestone = sorted(roadmap.milestones, key=lambda x: x.sequence_order)[-1]

        added_skills = []
        if active_milestone:
            for us in shaky_user_skills:
                skill_obj = us.skill
                if not skill_obj:
                    continue

                # Check if a reinforcement task already exists for this skill
                existing_ref = db.query(RoadmapTask).join(RoadmapMilestone).filter(
                    RoadmapMilestone.roadmap_id == roadmap.id,
                    RoadmapTask.skill_id == skill_obj.id,
                    RoadmapTask.title.ilike("%Reinforcement Checkpoint%")
                ).first()

                if not existing_ref:
                    seq_order = len(active_milestone.tasks) + 1
                    ref_task = RoadmapTask(
                        milestone_id=active_milestone.id,
                        skill_id=skill_obj.id,
                        title=f"Reinforcement Checkpoint • Practice & Review: {skill_obj.name}",
                        description=f"Targeted review lab & practice session to solidify understanding of {skill_obj.name} after self-evaluating as SHAKY.",
                        estimated_minutes=30,
                        sequence_order=seq_order,
                        status="NOT_STARTED",
                        reason_why_next=f"Inserted via evidence-based adaptive loop to reinforce {skill_obj.name} before moving forward."
                    )
                    db.add(ref_task)
                    db.commit()
                    db.refresh(ref_task)

                    # Attach resources for reinforcement
                    ranked_res = rank_resources_for_skill(
                        db=db,
                        skill=skill_obj,
                        user_skill_score=us.skill_score or 0.40,
                        limit=2
                    )
                    for r_seq, item in enumerate(ranked_res):
                        res_obj = item["resource"]
                        tr = TaskResource(
                            task_id=ref_task.id,
                            resource_id=res_obj.id,
                            recommendation_match_score=item["match_score"] / 100.0,
                            recommendation_reason=f"Reinforcement resource: {item['match_reason']}",
                            sequence_order=r_seq + 1
                        )
                        db.add(tr)
                    added_skills.append(skill_obj.name)

        # Recalculate total tasks
        total_count = db.query(RoadmapTask).join(RoadmapMilestone).filter(
            RoadmapMilestone.roadmap_id == roadmap.id
        ).count()
        roadmap.total_tasks = total_count

        if added_skills:
            roadmap.route_reasoning = f"Route adapted: Inserted dedicated reinforcement tasks for {', '.join(added_skills)} into your active schedule."
        else:
            roadmap.route_reasoning = f"Route adapted: Reinforced learning focus for {shaky_user_skills[0].skill.name} based on recent self-evaluations."
    else:
        roadmap.route_reasoning = "Roadmap schedule synchronized with your current completion pace."

    db.commit()
    db.refresh(roadmap)
    return roadmap

