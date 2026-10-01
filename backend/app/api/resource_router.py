from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import Resource, SavedResource, User
from app.schemas.schemas import APIResponse
from app.security.auth import get_current_user
from app.services.resource_matcher import resolve_resource_matches

router = APIRouter(prefix="/resources", tags=["Resources"])

def serialize_resource(r: Resource, is_saved: bool = False) -> dict:
    return {
        "id": r.id,
        "title": r.title,
        "url": r.url,
        "provider": r.provider,
        "resource_type": r.resource_type,
        "description": r.description,
        "duration_minutes": r.duration_minutes,
        "difficulty": r.difficulty,
        "quality_score": r.quality_score,
        "relevance_score": r.relevance_score,
        "verified": r.verified,
        "is_saved": is_saved,
        "match_score": int((r.quality_score or 0.85) * 100),
        "match_reason": f"Top verified {r.provider} {r.resource_type.lower()} resource for targeted skill acquisition."
    }


@router.get("", response_model=APIResponse)
def get_resources(
    query: Optional[str] = None,
    resource_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Resource).filter(Resource.verified == True)
    if query:
        q = q.filter(Resource.title.ilike(f"%{query}%") | Resource.provider.ilike(f"%{query}%"))
    if resource_type:
        q = q.filter(Resource.resource_type.ilike(resource_type))
    if difficulty:
        q = q.filter(Resource.difficulty.ilike(difficulty))

    resources = q.limit(50).all()
    res = [serialize_resource(r) for r in resources]
    return APIResponse(data=res)


@router.get("/{resource_id}", response_model=APIResponse)
def get_resource_detail(resource_id: str, db: Session = Depends(get_db)):
    r = db.query(Resource).filter(Resource.id == resource_id).first()
    if not r:
        return APIResponse(error={"code": "NOT_FOUND", "message": "Resource not found"})
    return APIResponse(data=serialize_resource(r))


@router.get("/{resource_id}/matches", response_model=APIResponse)
def get_resource_matches(
    resource_id: str,
    search_hint: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    r = db.query(Resource).filter(Resource.id == resource_id).first()
    effective_type = type or resource_type or (r.resource_type if r else "VIDEO")
    effective_title = name or (r.title if r else search_hint or "Resource")
    effective_provider = r.provider if r else "Web"
    effective_url = r.url if r else ""
    effective_desc = r.description if r else ""

    result = resolve_resource_matches(
        resource_id=resource_id,
        title=effective_title,
        resource_type=effective_type,
        provider=effective_provider,
        url=effective_url,
        description=effective_desc,
        search_hint=search_hint
    )
    return APIResponse(data=result)


@router.post("/{resource_id}/save", response_model=APIResponse)
def save_resource(resource_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(SavedResource).filter(
        SavedResource.user_id == current_user.id,
        SavedResource.resource_id == resource_id
    ).first()
    if not existing:
        sr = SavedResource(user_id=current_user.id, resource_id=resource_id)
        db.add(sr)
        db.commit()
    return APIResponse(data={"message": "Resource saved successfully", "is_saved": True})


@router.delete("/{resource_id}/save", response_model=APIResponse)
def unsave_resource(resource_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(SavedResource).filter(
        SavedResource.user_id == current_user.id,
        SavedResource.resource_id == resource_id
    ).delete()
    db.commit()
    return APIResponse(data={"message": "Resource unsaved successfully", "is_saved": False})


@router.get("/user/saved", response_model=APIResponse)
def get_saved_resources(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.query(SavedResource).filter(SavedResource.user_id == current_user.id).all()
    res = [serialize_resource(s.resource, is_saved=True) for s in saved if s.resource]
    return APIResponse(data=res)
