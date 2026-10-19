from __future__ import annotations

from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.models.entities import Campaign
from app.schemas.domain import CampaignCreate
from app.services.llm_service import llm_service


class CreativeVariant(BaseModel):
    name: str
    headline: str
    accent: str


class CampaignCopyDraft(BaseModel):
    headline: str
    subheadline: str
    cta: str
    short_promotional_copy: str
    layout_suggestion: str
    display_duration_seconds: int = Field(ge=4, le=20)
    schedule_recommendation: str
    creative_variants: list[CreativeVariant] = Field(min_length=3, max_length=3)


def _fallback_content(payload: CampaignCreate) -> dict:
    bilingual = payload.language == "English + Arabic"
    arabic_only = payload.language == "Arabic"
    english_headline = payload.offer.upper() if payload.tone in {"Energetic", "Fun"} else payload.offer
    arabic_headline = "عرض مميز لفترة محدودة"
    if arabic_only:
        headline, subheadline, cta = arabic_headline, f"مصمم خصيصاً لـ {payload.business}", "اكتشف المزيد"
    elif bilingual:
        headline, subheadline, cta = f"{english_headline}\n{arabic_headline}", f"Made for {payload.audience} • صُمم من أجلك", "Discover more • اكتشف المزيد"
    else:
        headline, subheadline, cta = english_headline, f"A {payload.tone.lower()} offer created for {payload.audience}", "Discover more"
    return {
        "headline": headline,
        "subheadline": subheadline,
        "cta": cta,
        "short_promotional_copy": f"Make this moment count with {payload.offer}. Available for a limited promotional period.",
        "layout_suggestion": "Use a strong offer block, one supporting visual zone, and a high-contrast CTA in the final third of the screen.",
        "display_duration_seconds": 8 if payload.screen_format != "led-banner" else 6,
        "schedule_recommendation": "Prioritize customer arrival and decision windows; validate against location analytics before publishing.",
        "creative_variants": [
            {"name": "Benefit-led", "headline": headline, "accent": "coral"},
            {"name": "Urgency-led", "headline": f"This weekend: {payload.offer}", "accent": "cyan"},
            {"name": "Minimal premium", "headline": payload.offer, "accent": "sand"},
        ],
        "approval_notice": "Draft only. A user must approve content before any future publishing integration.",
    }


def generate_campaign(db: Session, payload: CampaignCreate) -> Campaign:
    system = "You are the SignaFlow AI Campaign Agent. Generate concise screen-ready campaign copy. Do not promise publication or fabricate business facts."
    prompt = f"Business: {payload.business}\nCampaign: {payload.campaign}\nOffer: {payload.offer}\nAudience: {payload.audience}\nLanguage: {payload.language}\nTone: {payload.tone}\nReturn headline, subheadline, CTA, short copy, layout suggestion, display duration, schedule, and three variants as JSON."
    content = _fallback_content(payload)
    live = llm_service.generate_structured(system, prompt, CampaignCopyDraft, model_kind="default")
    if live:
        content = live.model_dump()
        content["approval_notice"] = "Draft only. A user must approve content before any future publishing integration."
    campaign = Campaign(campaign_name=payload.campaign, business=payload.business, offer=payload.offer, screen_format=payload.screen_format, resolution=payload.resolution, audience=payload.audience, language=payload.language, tone=payload.tone, content_json=content, status="DRAFT", is_demo=live is None)
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign
