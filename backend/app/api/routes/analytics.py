from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database.session import get_db
from app.models.entities import User, UserRole
from app.services.analytics_service import campaign_analytics, sales_overview

router = APIRouter(prefix="/analytics", tags=["analytics"])
AnalyticsUser = Annotated[User, Depends(require_roles(UserRole.SALES, UserRole.ADMIN))]


@router.get("/overview")
def overview(_: AnalyticsUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    return sales_overview(db)


@router.get("/sales")
def sales(_: AnalyticsUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    return sales_overview(db)


@router.get("/campaigns")
def campaigns(_: AnalyticsUser, db: Annotated[Session, Depends(get_db)]) -> dict:
    return campaign_analytics(db)

