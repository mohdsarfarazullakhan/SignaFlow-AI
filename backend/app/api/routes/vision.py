from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import require_roles
from app.models.entities import User, UserRole
from app.schemas.domain import VisualAdvisorRequest, VisualAdvisorResponse, VisionRequest, VisionResponse
from app.services.vision_service import analyze_demo_video, analyze_visual

router = APIRouter(tags=["vision"])


@router.post("/vision/analyze", response_model=VisionResponse)
def vision_analyze(payload: VisionRequest, _: Annotated[User, Depends(require_roles(UserRole.SALES, UserRole.ADMIN))]) -> VisionResponse:
    return analyze_demo_video(payload)


@router.post("/visual-advisor/analyze", response_model=VisualAdvisorResponse)
def visual_advisor(payload: VisualAdvisorRequest, _: Annotated[User, Depends(require_roles(UserRole.CUSTOMER, UserRole.SALES, UserRole.ADMIN))]) -> VisualAdvisorResponse:
    return analyze_visual(payload)

