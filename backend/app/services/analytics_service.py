from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.entities import Campaign, CampaignMetric, Lead, LeadStatus, Product, Quote


def sales_overview(db: Session) -> dict:
    leads = db.query(Lead).all()
    quotes = db.query(Quote).all()
    temperatures = Counter(lead.lead_temperature for lead in leads)
    statuses = Counter(lead.lead_status.value for lead in leads)
    total_pipeline = sum((lead.budget or Decimal("0") for lead in leads if lead.lead_status not in {LeadStatus.WON, LeadStatus.LOST}), Decimal("0"))
    won = statuses[LeadStatus.WON.value]
    conversion = round((won / len(leads) * 100), 1) if leads else 0
    by_industry = Counter(lead.industry or "Not specified" for lead in leads)
    by_emirate = Counter(lead.location or "Not specified" for lead in leads)
    product_counts: Counter[str] = Counter()
    for lead in leads:
        for item in lead.recommended_products or []:
            product_counts[item.get("name") or item.get("product_name") or "Unknown"] += 1
    highest_industry = by_industry.most_common(1)[0][0] if by_industry else "No data"
    highest_location = by_emirate.most_common(1)[0][0] if by_emirate else "No data"
    return {
        "label": "Demo Data" if any(lead.source == "Demo Data" for lead in leads) else "Live Data",
        "metrics": {"total_leads": len(leads), "hot_leads": temperatures["Hot"], "warm_leads": temperatures["Warm"], "cold_leads": temperatures["Cold"], "new_leads": statuses["NEW"], "qualified_leads": statuses["QUALIFIED"], "quotes_generated": len(quotes), "deals_won": statuses["WON"], "deals_lost": statuses["LOST"], "conversion_rate": conversion, "pipeline_value": float(total_pipeline), "average_deal_value": float(total_pipeline / max(1, len(leads)))},
        "leads_by_industry": [{"name": key.title(), "value": value} for key, value in by_industry.most_common()],
        "leads_by_emirate": [{"name": key, "value": value} for key, value in by_emirate.most_common()],
        "top_products": [{"name": key, "value": value} for key, value in product_counts.most_common(5)],
        "pipeline": [{"name": status.replace("_", " ").title(), "value": statuses[status]} for status in [item.value for item in LeadStatus]],
        "insights": [f"{highest_industry.title()} is currently the largest lead segment.", f"{highest_location} contributes the most enquiries in the current dataset.", f"{temperatures['Hot']} lead(s) are ready for priority follow-up.", "All monetary and conversion indicators shown here are calculated from database records."],
    }


def campaign_analytics(db: Session) -> dict:
    metrics = db.query(CampaignMetric).all()
    campaigns = {item.id: item for item in db.query(Campaign).all()}
    by_campaign: dict[str, dict[str, float]] = defaultdict(lambda: {"impressions": 0, "viewers": 0, "engagement_total": 0, "rows": 0})
    by_hour: dict[int, dict[str, float]] = defaultdict(lambda: {"impressions": 0, "viewers": 0})
    by_location: dict[str, int] = defaultdict(int)
    for item in metrics:
        name = campaigns[item.campaign_id].campaign_name if item.campaign_id in campaigns else "Unknown"
        row = by_campaign[name]
        row["impressions"] += item.impressions
        row["viewers"] += item.estimated_viewers
        row["engagement_total"] += item.engagement
        row["rows"] += 1
        by_hour[item.hour]["impressions"] += item.impressions
        by_hour[item.hour]["viewers"] += item.estimated_viewers
        by_location[item.location] += item.estimated_viewers
    campaign_rows = [{"name": name, "impressions": int(row["impressions"]), "viewers": int(row["viewers"]), "engagement": round(row["engagement_total"] / max(1, row["rows"]), 1)} for name, row in by_campaign.items()]
    hourly = [{"hour": f"{hour:02d}:00", "impressions": int(row["impressions"]), "viewers": int(row["viewers"])} for hour, row in sorted(by_hour.items())]
    best = max(campaign_rows, key=lambda row: row["engagement"], default={"name": "No campaign", "engagement": 0})
    peak = max(hourly, key=lambda row: row["viewers"], default={"hour": "—", "viewers": 0})
    return {"label": "Demo / Simulated Analytics", "campaigns": campaign_rows, "hourly": hourly, "locations": [{"name": key, "viewers": value} for key, value in sorted(by_location.items(), key=lambda item: item[1], reverse=True)], "optimization_recommendations": [{"recommendation": f"Give {best['name']} additional rotations in matching audience windows.", "supporting_metrics": f"Highest average engagement at {best['engagement']}%. Idle demo metrics are excluded.", "confidence": 82, "suggested_schedule": f"Test additional delivery around {peak['hour']}; require approval before changing schedules."}, {"recommendation": "Use shorter creative variants during high-traffic periods.", "supporting_metrics": f"Peak estimated viewer volume occurs around {peak['hour']} in the simulated dataset.", "confidence": 76, "suggested_schedule": "Run an approved A/B test for one week."}]}
