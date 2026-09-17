from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.db import get_db
from app.models.models import Content, User
from app.schemas.schemas import APIResponse, ContentUpdateRequest
from app.security.auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/content", tags=["Content CMS"])

@router.get("", response_model=APIResponse)
def get_all_content(db: Session = Depends(get_db)):
    content_list = db.query(Content).all()
    res = [
        {
            "id": c.id,
            "key": c.key,
            "scope": c.scope,
            "value": c.value,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None
        }
        for c in content_list
    ]
    return APIResponse(data=res)


@router.patch("/{key}", response_model=APIResponse)
def update_content(
    key: str,
    req: ContentUpdateRequest,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    item = db.query(Content).filter(Content.key == key).first()
    if not item:
        item = Content(key=key, scope=req.scope or "GLOBAL", value=req.value, updated_by=admin.email)
        db.add(item)
    else:
        item.value = req.value
        item.updated_by = admin.email

    db.commit()
    return APIResponse(data={"message": f"CMS key '{key}' updated successfully."})
