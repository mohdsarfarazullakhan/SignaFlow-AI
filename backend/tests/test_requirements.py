from app.services.requirement_service import fallback_requirement_response


def test_restaurant_requirement_fallback_extracts_exact_demo():
    result = fallback_requirement_response("I am opening a restaurant in Dubai. I need three indoor menu screens and one outdoor advertising screen.")
    assert result.requirement.industry == "restaurant"
    assert result.requirement.location == "Dubai"
    assert result.requirement.indoor_outdoor == "both"
    assert result.requirement.indoor_quantity == 3
    assert result.requirement.outdoor_quantity == 1
    assert result.requirement.quantity == 4
    assert result.enough_information is True


def test_progressive_clarification_asks_one_useful_question():
    result = fallback_requirement_response("I need screens for my restaurant.")
    assert result.enough_information is False
    assert result.clarification_question == "Will the signage be used indoors, outdoors, or in both environments?"

