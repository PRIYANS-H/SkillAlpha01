from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import ResourceFeedback, Resource, User
from app.schemas.schemas import APIResponse, ResourceFeedbackRequest
from app.security.auth import get_current_user

router = APIRouter(prefix="/resources", tags=["Feedback"])

@router.post("/{resource_id}/feedback", response_model=APIResponse)
def submit_resource_feedback(
    resource_id: str,
    req: ResourceFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        return APIResponse(error={"code": "NOT_FOUND", "message": "Resource not found"})

    fb = ResourceFeedback(
        resource_id=resource_id,
        user_id=current_user.id,
        is_useful=req.is_useful,
        rating_reason=req.rating_reason
    )
    db.add(fb)

    # Adjust resource quality score based on feedback signal
    if req.is_useful:
        resource.quality_score = min(1.0, round((resource.quality_score or 0.85) + 0.02, 2))
    else:
        resource.quality_score = max(0.4, round((resource.quality_score or 0.85) - 0.05, 2))

    db.commit()
    return APIResponse(data={"message": "Feedback submitted successfully. Ranking signals updated."})
