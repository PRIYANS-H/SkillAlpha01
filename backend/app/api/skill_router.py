from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import Skill, UserSkill, User
from app.schemas.schemas import APIResponse, SkillResponse, UserSkillUpdate
from app.security.auth import get_current_user
from app.services.skill_service import get_or_create_skill

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("", response_model=APIResponse)
def get_all_skills(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    res = [
        {
            "id": s.id,
            "name": s.name,
            "slug": s.slug,
            "domain": s.domain,
            "difficulty": s.difficulty,
            "description": s.description
        }
        for s in skills
    ]
    return APIResponse(data=res)


@router.get("/{skill_id}", response_model=APIResponse)
def get_skill(skill_id: str, db: Session = Depends(get_db)):
    s = db.query(Skill).filter(Skill.id == skill_id).first()
    if not s:
        return APIResponse(error={"code": "NOT_FOUND", "message": "Skill not found"})
    return APIResponse(data={
        "id": s.id,
        "name": s.name,
        "slug": s.slug,
        "domain": s.domain,
        "difficulty": s.difficulty,
        "description": s.description
    })
