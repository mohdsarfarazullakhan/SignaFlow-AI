from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import CurrentUser
from app.database.session import get_db
from app.models.entities import Product
from app.schemas.domain import ProductListResponse, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    _: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    search: str | None = Query(default=None, max_length=200),
    category: str | None = Query(default=None, max_length=120),
    environment: str | None = Query(default=None, pattern="^(indoor|outdoor|both)$"),
    limit: int = Query(default=100, ge=1, le=500),
) -> ProductListResponse:
    query = db.query(Product)
    if search:
        term = f"%{search}%"
        query = query.filter(or_(Product.name.ilike(term), Product.description.ilike(term), Product.category.ilike(term)))
    if category:
        query = query.filter(Product.category == category)
    if environment:
        query = query.filter(Product.environment.in_([environment, "both"]))
    items = query.order_by(Product.category, Product.name).limit(limit).all()
    categories = [row[0] for row in db.query(Product.category).distinct().order_by(Product.category).all()]
    return ProductListResponse(items=[ProductOut.model_validate(item) for item in items], total=query.count(), categories=categories)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, _: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> ProductOut:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut.model_validate(product)

