import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import User, Profile, UserSkill
from app.schemas.schemas import ProfileUpdateRequest, APIResponse, ProfileResponse, UserSkillResponse
from app.security.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=APIResponse)
def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    prefs = json.loads(profile.learning_preferences) if profile.learning_preferences else ["VIDEO", "DOCUMENTATION", "PROJECT"]
    
    data = {
        "id": profile.id,
        "user_id": profile.user_id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "goal": profile.goal,
        "target_role": profile.target_role,
        "available_hours": profile.available_hours,
        "duration_weeks": profile.duration_weeks,
        "learning_preferences": prefs,
        "github_username": profile.github_username
    }
    return APIResponse(data=data)


@router.patch("/me", response_model=APIResponse)
def update_user_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    if req.goal is not None:
        profile.goal = req.goal
    if req.target_role is not None:
        profile.target_role = req.target_role
    if req.available_hours is not None:
        profile.available_hours = req.available_hours
    if req.duration_weeks is not None:
        profile.duration_weeks = req.duration_weeks
    if req.learning_preferences is not None:
        profile.learning_preferences = json.dumps(req.learning_preferences)
    if req.github_username is not None:
        profile.github_username = req.github_username

    db.commit()
    db.refresh(profile)
    return APIResponse(data={"message": "Profile updated successfully"})
