from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import CurrentUser
from app.database.session import get_db
from app.models.entities import Campaign
from app.schemas.domain import CampaignCreate, CampaignOut
from app.services.campaign_service import generate_campaign

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/generate", response_model=CampaignOut, status_code=201)
def create_campaign(payload: CampaignCreate, _: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> CampaignOut:
    return CampaignOut.model_validate(generate_campaign(db, payload))


@router.get("", response_model=list[CampaignOut])
def list_campaigns(_: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> list[CampaignOut]:
    return [CampaignOut.model_validate(item) for item in db.query(Campaign).order_by(Campaign.created_at.desc()).all()]


@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign(campaign_id: str, _: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> CampaignOut:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignOut.model_validate(campaign)

