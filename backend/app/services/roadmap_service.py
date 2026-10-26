import math
import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.models import (
    Roadmap, RoadmapMilestone, RoadmapTask, TaskResource, TaskProgress, UserSkill, Skill
)
from app.services.skill_service import get_target_skill_graph_for_goal
from app.services.gap_engine import evaluate_skill_gaps, WEAK_STATUSES
from app.services.recommendation_engine import rank_resources_for_skill

REINFORCEMENT_MARKER = "Reinforcement Checkpoint"
MAX_REINFORCEMENTS_PER_SKILL = 2
PENDING_STATUSES = ("NOT_STARTED", "IN_PROGRESS")

def generate_roadmap_for_user(
    db: Session,
    user_id: str,
    goal: str,
    hours_per_week: int = 10,
    duration_weeks: int = 12,
    self_reported_skills: Dict[str, str] = None,
    preferred_types: List[str] = None,
    diagnostic_results: Dict[str, Tuple[int, int]] = None
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
    evaluated_skills, route_reasoning = evaluate_skill_gaps(
        db, user_id, target_skills, self_reported_skills, diagnostic_results, goal=goal
    )
    
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


def recalculate_roadmap_progress(roadmap: Roadmap) -> None:
    tasks = [t for m in roadmap.milestones for t in m.tasks]
    completed = sum(1 for t in tasks if t.status == "COMPLETED")
    resolved = completed + sum(1 for t in tasks if t.status == "SKIPPED")
    roadmap.total_tasks = len(tasks)
    roadmap.completed_tasks = completed
    roadmap.progress_percent = round((resolved / float(len(tasks))) * 100, 1) if tasks else 0.0


def _insert_reinforcement_task(db: Session, roadmap_tasks: List[RoadmapTask], milestones: List[RoadmapMilestone], user_skill: UserSkill) -> RoadmapTask:
    """Places a reinforcement task immediately before the learner's next pending task."""
    skill_obj = user_skill.skill
    next_task = next((t for t in roadmap_tasks if t.status in PENDING_STATUSES), None)
    if next_task:
        milestone = next_task.milestone
        seq_order = next_task.sequence_order
        for t in milestone.tasks:
            if t.sequence_order >= seq_order:
                t.sequence_order += 1
    else:
        milestone = milestones[-1]
        seq_order = max((t.sequence_order for t in milestone.tasks), default=0) + 1

    ref_task = RoadmapTask(
        skill_id=skill_obj.id,
        title=f"{REINFORCEMENT_MARKER} • Practice & Review: {skill_obj.name}",
        description=f"Targeted review lab & practice session to solidify understanding of {skill_obj.name}.",
        estimated_minutes=30,
        sequence_order=seq_order,
        status="NOT_STARTED",
        reason_why_next=f"Inserted via evidence-based adaptive loop: your latest results show {skill_obj.name} needs reinforcement before moving forward."
    )
    milestone.tasks.append(ref_task)

    # Attach resources for reinforcement
    ranked_res = rank_resources_for_skill(
        db=db,
        skill=skill_obj,
        user_skill_score=user_skill.skill_score or 0.40,
        limit=2
    )
    for r_seq, item in enumerate(ranked_res):
        ref_task.task_resources.append(TaskResource(
            resource_id=item["resource"].id,
            recommendation_match_score=item["match_score"] / 100.0,
            recommendation_reason=f"Reinforcement resource: {item['match_reason']}",
            sequence_order=r_seq + 1
        ))

    insert_at = roadmap_tasks.index(next_task) if next_task else len(roadmap_tasks)
    roadmap_tasks.insert(insert_at, ref_task)
    return ref_task


def adapt_roadmap_to_evidence(db: Session, roadmap: Roadmap, user_id: str) -> Tuple[List[str], List[str]]:
    """
    Applies the learner's latest skill evidence to a roadmap:
    - a skill that is still weak after the learner completed a task for it gets a
      reinforcement task as the next action (at most one pending, capped per skill);
    - pending reinforcement for a skill whose evidence is now strong is skipped.
    Baseline-only gaps are left alone: they already have regular tasks.
    Returns (reinforced_skill_names, cleared_skill_names). Does not commit.
    """
    db.flush()
    user_skills = {
        us.skill_id: us
        for us in db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    }
    milestones = sorted(roadmap.milestones, key=lambda m: m.sequence_order)
    roadmap_tasks = [t for m in milestones for t in sorted(m.tasks, key=lambda t: t.sequence_order)]
    if not roadmap_tasks:
        return [], []

    cleared = []
    for t in roadmap_tasks:
        user_skill = user_skills.get(t.skill_id)
        if REINFORCEMENT_MARKER in t.title and t.status == "NOT_STARTED" and user_skill and user_skill.status not in WEAK_STATUSES:
            t.status = "SKIPPED"
            cleared.append(user_skill.skill.name)

    studied_task_ids = {
        tp.task_id for tp in db.query(TaskProgress).filter(
            TaskProgress.user_id == user_id,
            TaskProgress.task_id.in_([t.id for t in roadmap_tasks])
        ).all()
    }
    studied_skill_ids = []
    for t in roadmap_tasks:
        if t.id in studied_task_ids and t.skill_id and t.skill_id not in studied_skill_ids:
            studied_skill_ids.append(t.skill_id)

    reinforced = []
    for skill_id in studied_skill_ids:
        user_skill = user_skills.get(skill_id)
        if not user_skill or not user_skill.skill or user_skill.status not in WEAK_STATUSES:
            continue
        existing = [t for t in roadmap_tasks if t.skill_id == skill_id and REINFORCEMENT_MARKER in t.title]
        if len(existing) >= MAX_REINFORCEMENTS_PER_SKILL or any(t.status in PENDING_STATUSES for t in existing):
            continue
        _insert_reinforcement_task(db, roadmap_tasks, milestones, user_skill)
        reinforced.append(user_skill.skill.name)

    changes = []
    if reinforced:
        changes.append(f"Inserted dedicated reinforcement tasks for {', '.join(reinforced)} as your next step")
    if cleared:
        changes.append(f"skipped pending reinforcement for {', '.join(cleared)} after strong results")
    if changes:
        roadmap.route_reasoning = f"Route adapted: {'; '.join(changes)}."

    recalculate_roadmap_progress(roadmap)
    return reinforced, cleared


def adaptive_replan_roadmap(db: Session, roadmap_id: str, user_id: str) -> Roadmap:
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id).first()
    if not roadmap:
        return None

    adapt_roadmap_to_evidence(db, roadmap, user_id)
    db.commit()
    db.refresh(roadmap)
    return roadmap
