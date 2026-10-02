from fastapi import APIRouter, Depends
from app.models.models import User
from app.schemas.schemas import UserResponse, APIResponse
from app.security.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/me", response_model=APIResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the authenticated user profile resolved from the Supabase JWT.
    If this is the user's first authenticated request, auth.py auto-provisions
    their public.users and profiles rows.
    """
    user_resp = UserResponse.model_validate(current_user)
    return APIResponse(data=user_resp.model_dump())


@router.post("/logout", response_model=APIResponse)
def logout():
    """
    Stateless logout endpoint. Client-side Supabase session is cleared via supabase.auth.signOut().
    """
    return APIResponse(data={"message": "Logged out successfully"})
