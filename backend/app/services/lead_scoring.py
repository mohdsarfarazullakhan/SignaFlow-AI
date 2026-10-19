from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.entities import Lead
from app.schemas.domain import LeadScoreResponse


@dataclass(frozen=True)
class ScoreResult:
    score: int
    temperature: str
    reasons: list[str]
    breakdown: dict[str, int]


def _short_timeline(timeline: str | None) -> bool:
    if not timeline:
        return False
    text = timeline.lower()
    if any(term in text for term in ("urgent", "asap", "immediately", "this month")):
        return True
    match = re.search(r"(\d+)\s*(day|week|month)", text)
    if not match:
        return False
    value, unit = int(match.group(1)), match.group(2)
    days = value if unit == "day" else value * 7 if unit == "week" else value * 30
    return days <= 30


def calculate_lead_score(lead: Lead) -> ScoreResult:
    requirement = lead.requirement_json or {}
    breakdown = {
        "clear_requirement": 15 if len(lead.requirement.strip()) >= 20 and requirement.get("use_case") else 0,
        "business_identified": 10 if lead.company or lead.industry else 0,
        "quantity_provided": 10 if requirement.get("quantity") or requirement.get("indoor_quantity") or requirement.get("outdoor_quantity") else 0,
        "budget_provided": 15 if lead.budget is not None else 0,
        "timeline_under_30_days": 20 if _short_timeline(lead.timeline or requirement.get("timeline")) else 0,
        "quotation_requested": 20 if lead.quotation_requested else 0,
        "contact_details_complete": 10 if lead.email and (lead.phone or lead.whatsapp) else 0,
    }
    score = min(100, sum(breakdown.values()))
    temperature = "Hot" if score >= 70 else "Warm" if score >= 40 else "Cold"
    labels = {
        "clear_requirement": "Clear requirement",
        "business_identified": "Business or industry identified",
        "quantity_provided": "Quantity known",
        "budget_provided": "Budget provided",
        "timeline_under_30_days": "Purchasing timeline is within 30 days",
        "quotation_requested": "Quotation requested",
        "contact_details_complete": "Contact details are actionable",
    }
    reasons = [labels[key] for key, points in breakdown.items() if points]
    return ScoreResult(score=score, temperature=temperature, reasons=reasons, breakdown=breakdown)


def apply_score_to_lead(lead: Lead) -> ScoreResult:
    result = calculate_lead_score(lead)
    lead.lead_score = result.score
    lead.lead_temperature = result.temperature
    return result


def as_response(result: ScoreResult) -> LeadScoreResponse:
    return LeadScoreResponse(score=result.score, temperature=result.temperature, reasons=result.reasons, breakdown=result.breakdown)

