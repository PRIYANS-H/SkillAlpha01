import json
import math
import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.models import (
    Roadmap, RoadmapMilestone, RoadmapTask, TaskResource, TaskProgress, UserSkill, Skill
)
from app.services.skill_service import get_target_skill_graph_for_goal, resolve_goal_family
from app.services.curriculum import build_day_plan
from app.services.problem_bank import problems_for_skill
from app.services.project_bank import projects_for_phases
from app.services.gap_engine import evaluate_skill_gaps, WEAK_STATUSES
from app.services.recommendation_engine import rank_resources_for_skill

REINFORCEMENT_MARKER = "Reinforcement Checkpoint"
MAX_REINFORCEMENTS_PER_SKILL = 2
PENDING_STATUSES = ("NOT_STARTED", "IN_PROGRESS")

# Study days inside each 7-day cycle (day 0 = the day the roadmap starts); the rest are rest days.
STUDY_PATTERNS = {
    1: [0], 2: [0, 3], 3: [0, 2, 4], 4: [0, 1, 3, 4],
    5: [0, 1, 2, 3, 4], 6: [0, 1, 2, 3, 4, 5], 7: [0, 1, 2, 3, 4, 5, 6],
}
PHASE_NAMES = {
    1: ["Core Skills"],
    2: ["Foundations", "Applied Practice"],
    3: ["Foundations", "Core Skills", "Applied Practice"],
    4: ["Foundations", "Core Skills", "Applied Practice", "Job-Ready Projects"],
}
MILESTONE_PASS_RATIO = 0.7
MAX_PROJECT_DAYS = 5
RESOURCES_PER_TASK = 4


def clamp_study_days(value: Optional[int]) -> int:
    return max(1, min(7, int(value or 5)))


def study_day_offset(index: int, per_week: int) -> int:
    """Calendar-day offset of the index-th study day (0-based) for a given number of study days a week."""
    week, position = divmod(index, per_week)
    return week * 7 + STUDY_PATTERNS[per_week][position]


def phase_count_for(skill_count: int) -> int:
    if skill_count <= 2:
        return 1
    if skill_count <= 5:
        return 2
    if skill_count <= 8:
        return 3
    return 4


def split_into_phases(items: List, count: int) -> List[List]:
    size = math.ceil(len(items) / float(count))
    return [items[i:i + size] for i in range(0, len(items), size)]


def task_plan(task: RoadmapTask) -> Dict:
    try:
        plan = json.loads(task.plan_json) if task.plan_json else {}
    except ValueError:
        plan = {}
    return plan if isinstance(plan, dict) else {}


def task_steps_done(task: RoadmapTask) -> List[int]:
    try:
        done = json.loads(task.steps_done) if task.steps_done else []
    except ValueError:
        done = []
    return sorted({int(i) for i in done if isinstance(i, int)}) if isinstance(done, list) else []


def task_day_count(task: RoadmapTask) -> int:
    plan = task_plan(task)
    if plan.get("days"):
        return len(plan["days"])
    return max(1, int(plan.get("day_count") or 1))


def pick_task_resources(db: Session, skill: Skill, score: float, preferred_types: List[str],
                        limit: int = RESOURCES_PER_TASK) -> List[Dict]:
    """
    Best-ranked resources for a skill, in the learner's preferred formats first and with at
    most two of any one format, so a task mixes something to watch, read and do.
    """
    ranked = rank_resources_for_skill(db=db, skill=skill, user_skill_score=score, preferred_types=preferred_types, limit=30)
    preferred = {t.upper() for t in (preferred_types or [])}
    ranked.sort(key=lambda item: (item["resource"].resource_type.upper() not in preferred, -item["match_score"]))
    chosen, per_type = [], {}
    for item in ranked:
        rtype = item["resource"].resource_type.upper()
        if per_type.get(rtype, 0) >= 2:
            continue
        per_type[rtype] = per_type.get(rtype, 0) + 1
        chosen.append(item)
        if len(chosen) >= limit:
            break
    return chosen


def generate_roadmap_for_user(
    db: Session,
    user_id: str,
    goal: str,
    hours_per_week: int = 10,
    duration_weeks: int = 12,
    self_reported_skills: Dict[str, str] = None,
    preferred_types: List[str] = None,
    diagnostic_results: Dict[str, Tuple[int, int]] = None,
    study_days_per_week: int = 5
) -> Roadmap:
    """
    Builds a personalized, dated plan:
    - skills the learner already has are skipped; the rest are grouped into phases;
    - every skill becomes a block of study days (learn, practice, build, review), shorter
      when the learner only needs reinforcement;
    - each phase ends with a project and a milestone check that must be passed;
    - study days follow the learner's days-per-week choice, leaving the others as rest days.
    """
    if self_reported_skills is None:
        self_reported_skills = {}
    if preferred_types is None:
        preferred_types = ["VIDEO", "DOCUMENTATION", "PROJECT", "PRACTICE"]
    study_days = clamp_study_days(study_days_per_week)
    minutes_per_day = max(20, int(round(hours_per_week * 60.0 / study_days)))

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

    roadmap = Roadmap(
        user_id=user_id,
        title=f"Learning Path: {goal}",
        goal=goal,
        duration_weeks=duration_weeks,
        hours_per_week=hours_per_week,
        study_days_per_week=study_days,
        route_reasoning=route_reasoning,
        is_active=True
    )
    db.add(roadmap)
    db.flush()

    # 4. Phases, with one project and one milestone check at the end of each
    phases = split_into_phases(active_skills, phase_count_for(len(active_skills)))
    phase_names = PHASE_NAMES[len(phases)]
    phase_projects = projects_for_phases(resolve_goal_family(goal), len(phases))

    start_date = datetime.date.today()
    milestones: Dict[int, RoadmapMilestone] = {}
    task_counts: Dict[int, int] = {}
    cursor = 0  # index of the next free study day
    total_tasks_created = 0

    def add_task(day_count: int, phase_index: int, plan: Dict, **fields) -> RoadmapTask:
        nonlocal cursor, total_tasks_created
        week = cursor // study_days + 1
        milestone = milestones.get(week)
        if milestone is None:
            milestone = RoadmapMilestone(
                roadmap_id=roadmap.id,
                title=f"Week {week:02d} • {phase_names[phase_index]}",
                description=(
                    f"Phase {phase_index + 1} of {len(phases)}: {phase_names[phase_index]} • "
                    f"{minutes_per_day} min a day on {study_days} study day{'s' if study_days != 1 else ''}, "
                    f"{7 - study_days} rest day{'s' if 7 - study_days != 1 else ''}."
                ),
                week_number=week,
                sequence_order=week
            )
            db.add(milestone)
            db.flush()
            milestones[week] = milestone
        task_counts[week] = task_counts.get(week, 0) + 1
        task = RoadmapTask(
            milestone_id=milestone.id,
            sequence_order=task_counts[week],
            status="NOT_STARTED",
            estimated_minutes=minutes_per_day * day_count,
            due_date=start_date + datetime.timedelta(days=study_day_offset(cursor, study_days)),
            plan_json=json.dumps(plan),
            **fields
        )
        db.add(task)
        db.flush()
        cursor += day_count
        total_tasks_created += 1
        return task

    for phase_index, phase_skills in enumerate(phases):
        phase_skill_names = []
        for skill_item in phase_skills:
            skill_obj = db.query(Skill).filter(Skill.id == skill_item["skill_id"]).first()
            if not skill_obj:
                continue
            phase_skill_names.append(skill_obj.name)

            resources = pick_task_resources(db, skill_obj, skill_item["score"], preferred_types)
            primary = resources[0]["resource"] if resources else None
            days = build_day_plan(
                skill_obj.name,
                skill_item["status"],
                primary_resource=f"{primary.title} ({primary.provider})" if primary else None,
                problem_count=sum(1 for p in problems_for_skill(skill_obj.name) if p["type"] != "EXTERNAL"),
            )
            base = study_day_offset(cursor, study_days)
            for i, day in enumerate(days):
                day["offset"] = study_day_offset(cursor + i, study_days) - base

            first_day, last_day = cursor + 1, cursor + len(days)
            if skill_item["status"] == "NEEDS_REINFORCEMENT":
                why = "You already know part of this, so the plan skips the lesson day and goes straight to practice."
            else:
                why = "This is a gap on your path, so the plan covers it fully: learn, practice, build, then review."
            task = add_task(
                len(days), phase_index, {"days": days},
                skill_id=skill_obj.id,
                kind="SKILL",
                title=f"Master {skill_obj.name}",
                description=skill_obj.description or f"Complete curated readings, code labs, and checkpoints for {skill_obj.name}.",
                reason_why_next=f"Study days {first_day}-{last_day} of your plan • {minutes_per_day} min a day. {why}",
            )
            for r_seq, item in enumerate(resources):
                db.add(TaskResource(
                    task_id=task.id,
                    resource_id=item["resource"].id,
                    recommendation_match_score=item["match_score"] / 100.0,
                    recommendation_reason=item["resource"].description or item["match_reason"],
                    sequence_order=r_seq + 1
                ))

        if not phase_skill_names:
            continue
        phase_name = phase_names[phase_index]

        project = phase_projects[phase_index]
        if project:
            project_days = max(2, min(MAX_PROJECT_DAYS, int(round(project["estimated_hours"] * 60.0 / minutes_per_day))))
            add_task(
                project_days, phase_index, {"day_count": project_days},
                kind="PROJECT",
                ref_id=project["id"],
                title=f"Project: {project['title']}",
                description=project["summary"],
                reason_why_next=(
                    f"Phase project for {phase_name}: put {', '.join(phase_skill_names[:3])} to work on something you can show. "
                    f"Submit a link and tick the checklist to finish."
                ),
            )

        add_task(
            1, phase_index,
            {"day_count": 1, "skills": phase_skill_names, "pass_ratio": MILESTONE_PASS_RATIO, "phase": phase_name},
            kind="MILESTONE_CHECK",
            ref_id=str(phase_index + 1),
            title=f"Milestone check: {phase_name}",
            description=f"A mixed quiz on {', '.join(phase_skill_names)}. Score {int(MILESTONE_PASS_RATIO * 100)}% or more to pass this phase.",
            reason_why_next=(
                f"You finish {phase_name} by proving it. Below {int(MILESTONE_PASS_RATIO * 100)}%, "
                f"review the skills you missed and take the check again."
            ),
        )

    roadmap.total_tasks = total_tasks_created
    db.commit()
    db.refresh(roadmap)
    return roadmap


def schedule_summary(roadmap: Roadmap) -> Dict:
    """How the plan is paced and whether it fits the learner's target, in plain numbers."""
    study_days = clamp_study_days(roadmap.study_days_per_week)
    minutes_per_day = max(20, int(round((roadmap.hours_per_week or 10) * 60.0 / study_days)))
    tasks = [t for m in roadmap.milestones for t in m.tasks]
    total_days = sum(task_day_count(t) for t in tasks)
    pending_days = sum(task_day_count(t) for t in tasks if t.status in PENDING_STATUSES)
    weeks_needed = max(1, math.ceil(total_days / float(study_days))) if tasks else 0
    target_weeks = roadmap.duration_weeks or weeks_needed
    fits = weeks_needed <= target_weeks

    last_dates = [t.due_date + datetime.timedelta(days=_last_day_offset(t)) for t in tasks if t.due_date and t.status in PENDING_STATUSES]
    if fits:
        note = f"At {roadmap.hours_per_week} hours a week this plan takes about {weeks_needed} week{'s' if weeks_needed != 1 else ''}, inside your {target_weeks}-week target."
    else:
        needed_hours = int(math.ceil((roadmap.hours_per_week or 10) * weeks_needed / float(target_weeks)))
        note = (
            f"At {roadmap.hours_per_week} hours a week this plan takes about {weeks_needed} weeks, longer than your "
            f"{target_weeks}-week target. To finish on time you would need about {needed_hours} hours a week."
        )
    today = datetime.date.today()
    on_break = bool(roadmap.break_until and roadmap.break_until > today)
    return {
        "study_days_per_week": study_days,
        "rest_days_per_week": 7 - study_days,
        "minutes_per_day": minutes_per_day,
        "total_study_days": total_days,
        "study_days_left": pending_days,
        "weeks_needed": weeks_needed,
        "target_weeks": target_weeks,
        "fits_target": fits,
        "projected_finish": max(last_dates).isoformat() if last_dates else None,
        "break_until": roadmap.break_until.isoformat() if on_break else None,
        "note": note,
    }


def _last_day_offset(task: RoadmapTask) -> int:
    days = task_plan(task).get("days") or []
    return max((int(d.get("offset") or 0) for d in days), default=0)


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
        due_date=max(next_task.due_date, datetime.date.today()) if next_task and next_task.due_date else datetime.date.today(),
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


def shift_overdue_schedule(roadmap: Roadmap, today: Optional[datetime.date] = None, allow_earlier: bool = False) -> int:
    """
    If the learner has fallen behind, moves every pending task forward by the same number of
    days so the earliest pending task is due today; spacing between tasks (and so the rest
    days) is preserved. With allow_earlier, a plan that was pushed into the future (a break
    ended early) is pulled back to today as well.
    Returns the number of days shifted (0 when on schedule).
    """
    today = today or datetime.date.today()
    pending = [
        t for m in roadmap.milestones for t in m.tasks
        if t.status in PENDING_STATUSES and t.due_date is not None
    ]
    if not pending:
        return 0
    earliest = min(t.due_date for t in pending)
    if earliest == today or (earliest > today and not allow_earlier):
        return 0
    delta = today - earliest
    for t in pending:
        t.due_date = t.due_date + delta
    return delta.days


def take_break(db: Session, roadmap_id: str, user_id: str, days: int) -> Optional[Roadmap]:
    """
    Pauses the plan: everything still to do moves `days` later (after first catching up any
    overdue work to today), so a break never shows up as being behind.
    """
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id).first()
    if not roadmap:
        return None
    today = datetime.date.today()
    shift_overdue_schedule(roadmap, today)
    for m in roadmap.milestones:
        for t in m.tasks:
            if t.status in PENDING_STATUSES and t.due_date is not None:
                t.due_date = t.due_date + datetime.timedelta(days=days)
    roadmap.break_until = today + datetime.timedelta(days=days)
    roadmap.route_reasoning = (
        f"Break taken: your plan is paused for {days} day{'s' if days != 1 else ''} and resumes on "
        f"{roadmap.break_until.strftime('%d %b')}. Nothing was skipped and no progress was lost."
    )
    db.commit()
    db.refresh(roadmap)
    return roadmap


def resume_from_break(db: Session, roadmap_id: str, user_id: str) -> Optional[Roadmap]:
    """Ends a break early: the next pending task becomes due today."""
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id).first()
    if not roadmap:
        return None
    shift_overdue_schedule(roadmap, allow_earlier=True)
    roadmap.break_until = None
    roadmap.route_reasoning = "Welcome back: your plan resumes today, from the task you had reached."
    db.commit()
    db.refresh(roadmap)
    return roadmap


def adaptive_replan_roadmap(db: Session, roadmap_id: str, user_id: str) -> Roadmap:
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id).first()
    if not roadmap:
        return None

    shifted_days = shift_overdue_schedule(roadmap)
    if roadmap.break_until and roadmap.break_until <= datetime.date.today():
        roadmap.break_until = None
    adapt_roadmap_to_evidence(db, roadmap, user_id)
    if shifted_days:
        note = f"Schedule re-paced: pending tasks moved {shifted_days} day{'s' if shifted_days != 1 else ''} later so today's task is due today."
        roadmap.route_reasoning = f"{roadmap.route_reasoning} {note}" if roadmap.route_reasoning and roadmap.route_reasoning.startswith("Route adapted") else note
    db.commit()
    db.refresh(roadmap)
    return roadmap
