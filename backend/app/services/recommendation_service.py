from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.entities import Product
from app.rag.knowledge_base import RetrievalHit, knowledge_base
from app.schemas.domain import CustomerRequirement, ProductOut, RecommendationOut, RecommendationResponse, SolutionItem, SolutionOut


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def _contains_overlap(requirement: str, values: list[str]) -> bool:
    query = _tokens(requirement)
    return any(query & _tokens(value) for value in values)


@dataclass(frozen=True)
class RankedProduct:
    product: Product
    score: float
    retrieval: float
    signals: list[str]


def _rank_hit(hit: RetrievalHit, requirement: CustomerRequirement) -> RankedProduct:
    product = hit.product
    signals: list[str] = []
    score = hit.score * 35
    if requirement.industry and requirement.industry.lower() in [i.lower() for i in product.industries]:
        score += 15
        signals.append("industry match")
    env = requirement.indoor_outdoor
    if env == "both" and product.environment in {"indoor", "outdoor", "both"}:
        score += 15
        signals.append(f"{product.environment} environment")
    elif env != "unknown" and product.environment in {env, "both"}:
        score += 20
        signals.append("environment match")
    if _contains_overlap(requirement.use_case, product.use_cases + [product.description, product.category, product.subcategory or ""]):
        score += 20
        signals.append("use-case match")
    if requirement.screen_size and product.dimensions and requirement.screen_size.lower() in product.dimensions.lower():
        score += 5
        signals.append("size match")
    if requirement.budget is not None and product.price is not None and product.price <= requirement.budget:
        score += 3
        signals.append("within stated budget")
    if product.availability:
        score += 2
        signals.append("availability recorded")
    return RankedProduct(product, min(100.0, score), hit.score, signals)


def recommend_products(db: Session, requirement: CustomerRequirement, limit: int = 3) -> RecommendationResponse:
    query = " ".join(filter(None, [requirement.industry, requirement.use_case, requirement.indoor_outdoor, requirement.preferred_product_type, requirement.screen_size]))
    ranked = sorted((_rank_hit(hit, requirement) for hit in knowledge_base.semantic_search(db, query, 20)), key=lambda item: item.score, reverse=True)
    selected: list[RankedProduct] = []
    if requirement.indoor_outdoor == "both":
        for environment in ("indoor", "outdoor"):
            candidate = next((item for item in ranked if item.product.environment in {environment, "both"} and item.product.category in {"Digital Signage", "LED Displays"}), None)
            if candidate and candidate not in selected:
                selected.append(candidate)
    for item in ranked:
        if item not in selected:
            selected.append(item)
        if len(selected) >= limit:
            break
    recommendations = []
    for item in selected[:limit]:
        missing = []
        for label, value in (("dimensions", item.product.dimensions), ("price", item.product.price), ("availability", item.product.availability)):
            if value is None:
                missing.append(f"{label.capitalize()} not available — please confirm with the sales team.")
        why = f"Matches {', '.join(item.signals[:3])}." if item.signals else "Relevant to the stated use case based on local semantic retrieval."
        recommendations.append(RecommendationOut(product=ProductOut.model_validate(item.product), confidence_score=max(35, round(item.score)), retrieval_score=round(item.retrieval, 4), why_it_matches=why, recommended_use=(item.product.use_cases or [requirement.use_case])[0], matched_signals=item.signals, missing_information=missing))
    return RecommendationResponse(recommendations=recommendations, requirement=requirement, mode=f"deterministic + {knowledge_base.backend}", disclaimer="Recommendations use catalogue records only. Demo Products are illustrative; confirm final specifications, compatibility, availability, and pricing with the sales team.")


def _find_product(db: Session, *, contains: str, environment: str | None = None) -> Product | None:
    products = db.query(Product).all()
    return next((p for p in products if contains.lower() in f"{p.name} {p.category} {p.subcategory}".lower() and (not environment or p.environment in {environment, "both"})), None)


def build_solution(db: Session, requirement: CustomerRequirement, product_ids: list[str]) -> SolutionOut:
    selected_rows = db.query(Product).filter(Product.id.in_(product_ids)).all() if product_ids else []
    selected_by_id = {product.id: product for product in selected_rows}
    # SQL does not preserve the order of an IN clause. Rebuild the list in
    # recommendation order so solution roles use the best-ranked product first.
    selected = [selected_by_id[product_id] for product_id in product_ids if product_id in selected_by_id]
    items: list[SolutionItem] = []

    def add(product: Product | None, quantity: int, role: str, rationale: str, optional: bool = False) -> None:
        if product and quantity > 0 and not any(item.product_id == product.id and item.role == role for item in items):
            items.append(SolutionItem(product_id=product.id, product_name=product.name, quantity=quantity, role=role, rationale=rationale, optional=optional, unit_price=product.price, currency=product.currency))

    indoor_qty = requirement.indoor_quantity or (requirement.quantity if requirement.indoor_outdoor == "indoor" else 0) or 0
    outdoor_qty = requirement.outdoor_quantity or (requirement.quantity if requirement.indoor_outdoor == "outdoor" else 0) or 0
    indoor = next((p for p in selected if p.environment in {"indoor", "both"} and p.category == "Digital Signage"), None) or _find_product(db, contains="Indoor Commercial Display", environment="indoor")
    outdoor = next((p for p in selected if p.environment == "outdoor" and p.category in {"Digital Signage", "LED Displays"}), None) or _find_product(db, contains="Weatherproof Outdoor Display", environment="outdoor")
    if indoor_qty:
        add(indoor, indoor_qty, "Primary indoor display", "Commercial screens for menu, promotion, or information content.")
    if outdoor_qty:
        add(outdoor, outdoor_qty, "Primary outdoor display", "Outdoor-rated screen option aligned to the exterior advertising requirement.")
    if not items and selected:
        add(selected[0], requirement.quantity or 1, "Primary product", "Best-ranked catalogue match for the stated requirement.")
    display_count = indoor_qty + outdoor_qty or requirement.quantity or 1
    add(_find_product(db, contains="Media Player"), display_count, "Content playback", "Provides managed content playback for each display; final integration compatibility must be confirmed.")
    add(_find_product(db, contains="CMS Annual"), 1, "Content management", "Enables centralized scheduling and updates across the screen network.")
    if indoor_qty:
        add(_find_product(db, contains="Wall Mount"), indoor_qty, "Indoor mounting", "Secure mounting provision; wall structure and VESA compatibility require survey confirmation.")
    if outdoor_qty:
        add(_find_product(db, contains="Outdoor Display Floor Stand"), outdoor_qty, "Outdoor mounting", "Illustrative mounting option; final installation requires a site survey.")
    add(_find_product(db, contains="High-Brightness Window Display"), 1, "Optional upgrade", "Higher-impact storefront visibility where the screen faces daylight.", optional=True)
    industry_label = (requirement.industry or "Business").title()
    return SolutionOut(
        name=f"{industry_label} Intelligent Signage Package",
        summary=f"A connected solution for {requirement.use_case}, covering displays, content playback, management, and mounting provisions.",
        items=items,
        compatibility_notes=["Confirm display-to-mount compatibility before approval.", "Outdoor equipment and installation require a site survey.", "Network connectivity and power points should be validated on site."],
        optional_upgrades=["Content design and bilingual campaign setup", "High-brightness storefront display", "Extended support and maintenance plan — terms to be confirmed"],
        pricing_note="All values come from catalogue records. Any item without a recorded price is marked for sales confirmation; no LLM-generated pricing is used.",
    )
