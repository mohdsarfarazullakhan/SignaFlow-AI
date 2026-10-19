from decimal import Decimal

from app.models.entities import Lead
from app.services.lead_scoring import calculate_lead_score


def test_hot_lead_score_is_deterministic():
    lead = Lead(customer_name="A Customer", company="ABC Restaurant", email="a@example.com", phone="+971500000000", industry="restaurant", location="Dubai", requirement="Three indoor menu displays and one outdoor advertising display.", requirement_json={"use_case": "digital menus", "quantity": 4}, budget=Decimal("35000"), timeline="2 weeks", quotation_requested=True)
    result = calculate_lead_score(lead)
    assert result.score == 100
    assert result.temperature == "Hot"
    assert result.breakdown["quotation_requested"] == 20


def test_score_thresholds_are_application_controlled():
    lead = Lead(customer_name="Browser", requirement="General enquiry", requirement_json={}, quotation_requested=False)
    result = calculate_lead_score(lead)
    assert result.score == 0
    assert result.temperature == "Cold"

