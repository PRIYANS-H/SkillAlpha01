from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import User, Profile
from app.schemas.schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse, APIResponse
)
from app.security.auth import (
    hash_password, verify_password, create_access_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=APIResponse)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        return APIResponse(error={"code": "EMAIL_EXISTS", "message": "An account with this email already exists."})
        
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name or req.email.split("@")[0],
        role="USER"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create default profile
    profile = Profile(user_id=user.id)
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    user_resp = UserResponse.from_orm(user)
    
    return APIResponse(data={"access_token": token, "token_type": "bearer", "user": user_resp.dict()})


@router.post("/login", response_model=APIResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        return APIResponse(error={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."})

    if not user.is_active:
        return APIResponse(error={"code": "INACTIVE_ACCOUNT", "message": "User account is inactive."})

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    user_resp = UserResponse.from_orm(user)
    
    return APIResponse(data={"access_token": token, "token_type": "bearer", "user": user_resp.dict()})


@router.get("/me", response_model=APIResponse)
def get_me(current_user: User = Depends(get_current_user)):
    user_resp = UserResponse.from_orm(current_user)
    return APIResponse(data=user_resp.dict())


@router.post("/logout", response_model=APIResponse)
def logout():
    return APIResponse(data={"message": "Logged out successfully"})
