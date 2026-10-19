from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database.session import get_db
from app.integrations.catalog_ingestion import CatalogueIngestionService, ProductCandidate
from app.models.entities import User, UserRole
from app.schemas.domain import ProductImportRequest, ProductImportResponse, UserOut

router = APIRouter(prefix="/admin", tags=["administration"])
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]


@router.get("/users", response_model=list[UserOut])
def users(_: AdminUser, db: Annotated[Session, Depends(get_db)]) -> list[UserOut]:
    return [UserOut.model_validate(user) for user in db.query(User).order_by(User.role, User.name).all()]


@router.post("/products/import", response_model=ProductImportResponse)
def import_products(payload: ProductImportRequest, _: AdminUser, db: Annotated[Session, Depends(get_db)]) -> ProductImportResponse:
    if not payload.is_demo and any(not item.source_url for item in payload.products):
        raise HTTPException(status_code=400, detail="Every non-demo imported product requires a reviewed source URL")
    candidates = [ProductCandidate(**item.model_dump()) for item in payload.products]
    created, updated = CatalogueIngestionService.upsert(db, candidates, source=payload.source_label, is_demo=payload.is_demo)
    return ProductImportResponse(created=created, updated=updated, is_demo=payload.is_demo, notice="Imported records remain subject to catalogue review. Non-demo records require a source URL.")
