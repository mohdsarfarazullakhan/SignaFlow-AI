from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.entities import Lead, Product
from app.services.llm_service import llm_service


def _lead_context(lead: Lead | None) -> str:
    if not lead:
        return "No lead selected."
    return f"Lead {lead.customer_name} / {lead.company or 'individual'}, {lead.industry or 'industry not provided'}, {lead.location or 'location not provided'}, score {lead.lead_score}/100 ({lead.lead_temperature}), status {lead.lead_status.value}. Requirement: {lead.requirement}"


def fallback_copilot(db: Session, message: str, lead: Lead | None) -> tuple[str, list[str]]:
    lower = message.lower()
    context = _lead_context(lead)
    if "whatsapp" in lower or "follow-up" in lower or "follow up" in lower:
        name = lead.customer_name.split()[0] if lead else "there"
        requirement = lead.requirement if lead else "your signage requirement"
        answer = f"Hi {name}, thank you for sharing details about {requirement.rstrip('.')}. We have shortlisted a practical solution and can confirm final specifications, availability, and installation requirements with you. Would a quick call today or tomorrow be convenient?"
        return answer, ["Copy message", "Review product shortlist", "Choose a follow-up time"]
    if "email" in lower:
        company = lead.company if lead and lead.company else "your business"
        answer = f"Subject: Next steps for {company}'s signage requirement\n\nHello {lead.customer_name if lead else 'there'},\n\nThank you for the opportunity to support your project. Based on the requirement shared, we have prepared a catalogue-backed solution for review. Final pricing, availability, installation scope, and specifications will be confirmed by our sales team.\n\nKind regards,\nSignaFlow Demo Sales"
        return answer, ["Copy email", "Attach reviewed quotation", "Confirm recipient details"]
    if "which leads" in lower or "contact first" in lower:
        leads = db.query(Lead).order_by(Lead.lead_score.desc()).limit(3).all()
        lines = [f"{index + 1}. {item.company or item.customer_name} — {item.lead_temperature} {item.lead_score}/100 — {item.requirement}" for index, item in enumerate(leads)]
        return "Contact these leads first:\n" + "\n".join(lines), ["Open highest-scoring lead", "Draft a personalized follow-up", "Check quote readiness"]
    if "compare" in lower:
        products = db.query(Product).filter(Product.category.in_(["Digital Signage", "LED Displays"])).limit(3).all()
        lines = [f"• {p.name}: {p.environment or 'environment not specified'}; {p.dimensions or 'size not available'}; {'AED ' + format(p.price, ',.2f') if p.price is not None else 'price to be confirmed'}" for p in products]
        return "Catalogue comparison:\n" + "\n".join(lines), ["Confirm site environment", "Validate dimensions", "Prepare a reviewed quote"]
    if "upsell" in lower:
        return f"{context}\nRelevant cross-sell checks: mounting hardware, a compatible media player, centralized CMS, content design, and a maintenance plan. Confirm compatibility and commercial terms before proposing them.", ["Add compatible accessories", "Ask about content management", "Confirm installation scope"]
    if lead:
        return f"{context}\nRecommended next action: contact the lead with a requirement-specific response, confirm the missing site and timeline details, then prepare a draft quotation from database pricing.", ["Generate WhatsApp follow-up", "Build draft quotation", "Confirm site survey needs"]
    return "I can compare catalogue products, rank leads, summarize an opportunity, draft a WhatsApp or email follow-up, suggest upsells, and prepare a quotation workflow. Select a lead for a contextual answer.", ["Choose a lead", "Ask for priority leads", "Compare display options"]


def copilot_answer(db: Session, message: str, lead: Lead | None) -> tuple[str, list[str], str]:
    fallback, actions = fallback_copilot(db, message, lead)
    live = llm_service.generate("You are the internal SignaFlow AI Sales Copilot for a fictional demo signage business. Be factual, concise, and action-oriented. Never invent product facts, prices, availability, discounts, delivery dates, or warranty. Never send communications; drafts require approval.", f"{_lead_context(lead)}\nEmployee request: {message}", model_kind="reasoning")
    return (live or fallback), actions, ("groq" if live else "fallback")
