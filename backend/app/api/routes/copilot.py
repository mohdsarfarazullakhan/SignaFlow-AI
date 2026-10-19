from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database.session import get_db
from app.models.entities import Lead, User, UserRole
from app.schemas.domain import CopilotRequest, CopilotResponse
from app.services.copilot_service import copilot_answer

router = APIRouter(prefix="/copilot", tags=["sales copilot"])


@router.post("/chat", response_model=CopilotResponse)
def chat(payload: CopilotRequest, _: Annotated[User, Depends(require_roles(UserRole.SALES, UserRole.ADMIN))], db: Annotated[Session, Depends(get_db)]) -> CopilotResponse:
    lead = db.get(Lead, payload.lead_id) if payload.lead_id else None
    if payload.lead_id and not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    answer, actions, mode = copilot_answer(db, payload.message, lead)
    return CopilotResponse(answer=answer, suggested_actions=actions, mode=mode)

