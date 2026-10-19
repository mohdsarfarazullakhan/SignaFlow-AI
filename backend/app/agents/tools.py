from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.entities import Lead, Product, Quote
from app.rag.knowledge_base import knowledge_base
from app.schemas.domain import CampaignCreate, CustomerRequirement, QuoteCreate
from app.services.analytics_service import campaign_analytics, sales_overview
from app.services.campaign_service import generate_campaign
from app.services.copilot_service import fallback_copilot
from app.services.lead_scoring import apply_score_to_lead
from app.services.quote_service import create_quote as create_quote_service
from app.services.recommendation_service import recommend_products


class ProductSearchInput(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)


class ProductIdInput(BaseModel):
    product_id: str = Field(min_length=36, max_length=36)


class ProductFilterInput(BaseModel):
    category: str | None = Field(default=None, max_length=120)
    environment: str | None = Field(default=None, pattern="^(indoor|outdoor|both)$")
    limit: int = Field(default=20, ge=1, le=100)


class CompareProductsInput(BaseModel):
    product_ids: list[str] = Field(min_length=2, max_length=4)


class LeadIdInput(BaseModel):
    lead_id: str = Field(min_length=36, max_length=36)


class CommunicationInput(LeadIdInput):
    channel: str = Field(pattern="^(email|whatsapp)$")


def search_products(db: Session, payload: ProductSearchInput) -> list[dict]:
    return [{"product_id": hit.product.id, "name": hit.product.name, "source": hit.product.source, "source_url": hit.product.source_url, "retrieval_score": round(hit.score, 4)} for hit in knowledge_base.semantic_search(db, payload.query, payload.limit)]


def get_product(db: Session, payload: ProductIdInput) -> Product | None:
    return db.get(Product, payload.product_id)


def filter_products(db: Session, payload: ProductFilterInput) -> list[Product]:
    query = db.query(Product)
    if payload.category:
        query = query.filter(Product.category == payload.category)
    if payload.environment:
        query = query.filter(Product.environment.in_([payload.environment, "both"]))
    return query.limit(payload.limit).all()


def compare_products(db: Session, payload: CompareProductsInput) -> list[dict]:
    products = db.query(Product).filter(Product.id.in_(payload.product_ids)).all()
    return [{"product_id": item.id, "name": item.name, "environment": item.environment, "dimensions": item.dimensions, "price": item.price, "currency": item.currency, "specifications": item.specifications_json, "source": item.source} for item in products]


def get_lead(db: Session, payload: LeadIdInput) -> Lead | None:
    return db.get(Lead, payload.lead_id)


def score_lead(db: Session, payload: LeadIdInput) -> dict | None:
    lead = get_lead(db, payload)
    if not lead:
        return None
    result = apply_score_to_lead(lead)
    db.commit()
    return {"score": result.score, "temperature": result.temperature, "reasons": result.reasons}


def create_quote(db: Session, payload: QuoteCreate) -> Quote:
    return create_quote_service(db, payload)


def draft_communication(db: Session, payload: CommunicationInput) -> str | None:
    lead = get_lead(db, payload)
    if not lead:
        return None
    prompt = "Draft a personalized WhatsApp follow-up" if payload.channel == "whatsapp" else "Draft an introductory sales email"
    return fallback_copilot(db, prompt, lead)[0]


def get_sales_metrics(db: Session) -> dict:
    return sales_overview(db)


def create_campaign(db: Session, payload: CampaignCreate):
    return generate_campaign(db, payload)


def get_campaign_metrics(db: Session) -> dict:
    return campaign_analytics(db)


def product_advisor(db: Session, requirement: CustomerRequirement):
    return recommend_products(db, requirement)
