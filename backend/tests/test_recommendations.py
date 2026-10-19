from app.schemas.domain import CustomerRequirement
from app.services.recommendation_service import build_solution, recommend_products


def requirement() -> CustomerRequirement:
    return CustomerRequirement(industry="restaurant", business_type="restaurant", location="Dubai", use_case="digital menus + advertising and promotions", indoor_outdoor="both", quantity=4, indoor_quantity=3, outdoor_quantity=1, contact_intent="interested", source_text="restaurant requirement")


def test_search_returns_catalogue_products_only(db):
    result = recommend_products(db, requirement(), 3)
    assert len(result.recommendations) == 3
    assert all(item.product.id for item in result.recommendations)
    assert any(item.product.environment == "outdoor" for item in result.recommendations)
    assert any(item.product.environment in {"indoor", "both"} for item in result.recommendations)


def test_solution_contains_primary_and_compatible_support_items(db):
    result = recommend_products(db, requirement(), 3)
    solution = build_solution(db, requirement(), [item.product.id for item in result.recommendations])
    quantities = {item.role: item.quantity for item in solution.items}
    assert quantities["Primary indoor display"] == 3
    assert quantities["Primary outdoor display"] == 1
    assert quantities["Content playback"] == 4
    assert any("site survey" in note.lower() for note in solution.compatibility_notes)

