from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, UserRole
from app.models.ngo_request import NGORequest
from app.schemas.ngo_request import NGORequestCreate, NGORequestOut

router = APIRouter(prefix="/ngo-requests", tags=["NGO Requests"])

@router.post("", response_model=NGORequestOut)
def create_ngo_request(
    req_in: NGORequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.NGO, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only NGOs can post requirement requests")

    request = NGORequest(
        ngo_id=current_user.id,
        food_type=req_in.food_type,
        quantity_needed_kg=req_in.quantity_needed_kg,
        urgency=req_in.urgency,
        active=True
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

@router.get("", response_model=List[NGORequestOut])
def list_ngo_requests(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(NGORequest)
    if active_only:
        query = query.filter(NGORequest.active == True)
    return query.order_by(NGORequest.created_at.desc()).all()
