from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.models import Resource, ResourceSkill, Skill

def rank_resources_for_skill(
    db: Session,
    skill: Skill,
    user_skill_score: float = 0.40,
    preferred_types: Optional[List[str]] = None,
    limit: int = 3
) -> List[Dict]:
    """
    Retrieves and ranks candidate resources for a target skill using a multi-signal scoring model.
    Fallback order: Exact skill tagged/matched -> Prerequisite/Related skills -> Category/Domain match -> None.
    """
    if preferred_types is None:
        preferred_types = ["VIDEO", "DOCUMENTATION", "PROJECT", "ARTICLE", "PRACTICE"]

    match_nature = "EXACT"

    # 1. Exact skill tagged resources or matching title/description
    resource_ids = [rs.resource_id for rs in db.query(ResourceSkill).filter(ResourceSkill.skill_id == skill.id).all()]
    query = db.query(Resource).filter(Resource.verified == True)
    
    if resource_ids:
        candidate_resources = query.filter(Resource.id.in_(resource_ids)).all()
    else:
        candidate_resources = query.filter(Resource.title.ilike(f"%{skill.name}%")).all()

    # 2. Fallback to related skills via SkillRelationship graph
    if not candidate_resources:
        from app.models.models import SkillRelationship
        related_rel = db.query(SkillRelationship).filter(
            (SkillRelationship.skill_id == skill.id) | (SkillRelationship.prerequisite_id == skill.id)
        ).all()
        related_skill_ids = set()
        for rel in related_rel:
            if rel.skill_id != skill.id:
                related_skill_ids.add(rel.skill_id)
            if rel.prerequisite_id != skill.id:
                related_skill_ids.add(rel.prerequisite_id)
        
        if related_skill_ids:
            rel_res_ids = [rs.resource_id for rs in db.query(ResourceSkill).filter(ResourceSkill.skill_id.in_(list(related_skill_ids))).all()]
            if rel_res_ids:
                candidate_resources = db.query(Resource).filter(Resource.verified == True, Resource.id.in_(rel_res_ids)).all()
                match_nature = "RELATED"

    # 3. Fallback to domain match in title or description
    if not candidate_resources and skill.domain:
        candidate_resources = db.query(Resource).filter(
            Resource.verified == True,
            (Resource.title.ilike(f"%{skill.domain}%") | Resource.description.ilike(f"%{skill.domain}%"))
        ).limit(5).all()
        if candidate_resources:
            match_nature = "DOMAIN"

    # If no relevant candidate resources exist in DB, return empty list rather than attaching arbitrary unrelated resources
    if not candidate_resources:
        return []

    ranked_results = []
    
    for r in candidate_resources:
        # Calculate individual scoring signals (0.0 - 1.0)
        if match_nature == "EXACT":
            topic_relevance = 0.95 if skill.name.lower() in r.title.lower() or (r.description and skill.name.lower() in r.description.lower()) else 0.85
        elif match_nature == "RELATED":
            topic_relevance = 0.70
        else:
            topic_relevance = 0.55
        
        # Skill-gap match: higher score if resource difficulty matches user's current need
        skill_gap_match = 0.90 if user_skill_score < 0.50 and r.difficulty.upper() in ["BEGINNER", "INTERMEDIATE"] else 0.85
        quality = r.quality_score or 0.85
        difficulty_fit = 0.95 if r.difficulty.upper() == skill.difficulty.upper() else 0.80
        freshness = r.freshness_score or 0.90
        engagement = r.engagement_score or 0.80
        format_diversity = 0.95 if r.resource_type.upper() in [t.upper() for t in preferred_types] else 0.70
        
        # Weighted formula
        final_score = (
            0.30 * topic_relevance +
            0.20 * skill_gap_match +
            0.15 * quality +
            0.10 * difficulty_fit +
            0.10 * freshness +
            0.10 * engagement +
            0.05 * format_diversity
        )
        
        match_percentage = int(final_score * 100)
        
        # Generate transparent, non-misleading rationale
        if match_nature == "EXACT":
            if r.resource_type.upper() == "DOCUMENTATION":
                reason = f"Top official reference ({match_percentage}% match) for mastering {skill.name} without tutorial fluff."
            elif r.resource_type.upper() == "PRACTICE":
                reason = f"Interactive lab ({match_percentage}% match) to apply {skill.name} concepts in code."
            else:
                reason = f"Curated resource ({match_percentage}% match) covering {skill.name} for your current milestone."
        elif match_nature == "RELATED":
            reason = f"Prerequisite resource ({match_percentage}% match) to build foundational context for {skill.name}."
        else:
            reason = f"Domain background reading ({match_percentage}% match) in {skill.domain}."

        ranked_results.append({
            "resource": r,
            "match_score": match_percentage,
            "match_reason": reason
        })

    # Sort descending by match score
    ranked_results.sort(key=lambda x: x["match_score"], reverse=True)
    return ranked_results[:limit]

