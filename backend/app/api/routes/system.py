from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.rag.knowledge_base import knowledge_base
from app.schemas.domain import HealthResponse
from app.services.llm_service import llm_service

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(db: Annotated[Session, Depends(get_db)]) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", app=settings.app_name, environment=settings.app_env, demo_mode=settings.demo_mode, llm=llm_service.health_check(), database="connected", rag=knowledge_base.backend)


@router.get("/integrations/n8n/status")
def n8n_status() -> dict:
    return {"ready": True, "configured": bool(settings.n8n_webhook_url), "outbound_actions_enabled": False, "events": ["lead.created", "lead.hot", "quote.created", "lead.followup_due"], "notice": "This prototype exposes event contracts but never sends external communications automatically."}


@router.get("/opportunities")
def opportunities() -> dict:
    return {"items": [
        {"strength": "Large, specialized catalogue", "opportunity": "Customers may not know the technical product name", "enhancement": "Natural-language semantic discovery", "benefit": "Faster product matching"},
        {"strength": "Established enquiry journey", "opportunity": "Enquiries can carry more sales context", "enhancement": "Progressive AI qualification", "benefit": "Better prioritization"},
        {"strength": "Broad solution capability", "opportunity": "Quotation preparation has repeatable steps", "enhancement": "Database-backed AI quotation drafting", "benefit": "Shorter response time"},
        {"strength": "Website, store, and signage expertise", "opportunity": "The digital journey spans multiple properties", "enhancement": "One intelligent requirement-to-revenue layer", "benefit": "A smoother customer journey"},
        {"strength": "Digital signage installed in real locations", "opportunity": "Performance can become measurable", "enhancement": "Privacy-preserving audience analytics", "benefit": "Evidence-led campaign optimization"},
    ]}


@router.get("/business-impact")
def business_impact() -> dict:
    return {"label": "Potential / future measurable KPIs", "items": [
        {"metric": "Lead response time", "baseline": "Establish during pilot", "target": "Respond to Hot leads within a defined SLA"},
        {"metric": "Lead-to-quote conversion", "baseline": "Measure from CRM", "target": "Improve through qualification and next-best action"},
        {"metric": "Quote turnaround", "baseline": "Measure manual workflow", "target": "Reduce drafting time while retaining approval"},
        {"metric": "Products per quotation", "baseline": "Calculate from historical quotes", "target": "Increase relevant, compatible cross-sell"},
        {"metric": "Product search time", "baseline": "Observe sales workflow", "target": "Find shortlist in under two minutes"},
        {"metric": "Campaign engagement", "baseline": "Establish with anonymous analytics", "target": "Optimize schedules through approved experiments"},
    ], "notice": "These are targets, not claimed results."}

