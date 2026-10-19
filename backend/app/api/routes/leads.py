from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, require_roles
from app.database.session import get_db
from app.models.entities import Lead, User, UserRole
from app.schemas.domain import LeadCreate, LeadOut, LeadScoreResponse, LeadUpdate
from app.services.lead_scoring import apply_score_to_lead, as_response

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=list[LeadOut])
def list_leads(
    _: Annotated[User, Depends(require_roles(UserRole.SALES, UserRole.ADMIN))],
    db: Annotated[Session, Depends(get_db)],
    temperature: str | None = Query(default=None, pattern="^(Cold|Warm|Hot)$"),
) -> list[LeadOut]:
    query = db.query(Lead)
    if temperature:
        query = query.filter(Lead.lead_temperature == temperature)
    return [LeadOut.model_validate(item) for item in query.order_by(Lead.lead_score.desc(), Lead.created_at.desc()).all()]


@router.post("", response_model=LeadOut, status_code=201)
def create_lead(payload: LeadCreate, _: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> LeadOut:
    lead = Lead(**payload.model_dump())
    apply_score_to_lead(lead)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: str, _: Annotated[User, Depends(require_roles(UserRole.SALES, UserRole.ADMIN))], db: Annotated[Session, Depends(get_db)]) -> LeadOut:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadOut.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: str, payload: LeadUpdate, _: Annotated[User, Depends(require_roles(UserRole.SALES, UserRole.ADMIN))], db: Annotated[Session, Depends(get_db)]) -> LeadOut:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    apply_score_to_lead(lead)
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.post("/{lead_id}/score", response_model=LeadScoreResponse)
def score_lead(lead_id: str, _: Annotated[User, Depends(require_roles(UserRole.SALES, UserRole.ADMIN))], db: Annotated[Session, Depends(get_db)]) -> LeadScoreResponse:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    result = apply_score_to_lead(lead)
    db.commit()
    return as_response(result)

