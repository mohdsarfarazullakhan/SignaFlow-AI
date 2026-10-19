from __future__ import annotations

import re
from decimal import Decimal

from app.schemas.domain import CustomerRequirement, RequirementResponse

NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}
INDUSTRIES = [
    "restaurant", "café", "cafe", "retail", "supermarket", "hotel", "hospitality",
    "real estate", "corporate office", "mall", "exhibition", "events", "signage company",
    "advertising agency", "fit-out contractor", "school", "hospital", "automotive",
    "showroom", "government",
]
LOCATIONS = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"]


def _number(token: str) -> int | None:
    token = token.lower().strip()
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def _extract_quantity_before(text: str, marker: str) -> int | None:
    pattern = rf"\b(a|an|one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:[\w-]+\s+){{0,3}}{marker}\b"
    match = re.search(pattern, text, re.IGNORECASE)
    return _number(match.group(1)) if match else None


def _infer_use_case(text: str) -> str:
    lower = text.lower()
    uses: list[str] = []
    rules = [
        (("menu", "restaurant screen"), "digital menus"),
        (("advert", "promotion", "campaign"), "advertising and promotions"),
        (("wayfinding", "directory"), "digital wayfinding"),
        (("illuminated", "channel letter", "light box"), "illuminated signage"),
        (("large-format", "large format", "printer", "printing"), "large-format advertising printing"),
        (("window", "storefront"), "window branding"),
        (("queue", "self-service", "self service"), "self-service and queue management"),
    ]
    for terms, label in rules:
        if any(term in lower for term in terms):
            uses.append(label)
    if not uses and any(term in lower for term in ("screen", "display", "signage", "led")):
        uses.append("digital signage")
    return " + ".join(dict.fromkeys(uses)) or text.strip()[:240]


def fallback_extract(message: str) -> CustomerRequirement:
    lower = message.lower()
    industry = next((item for item in INDUSTRIES if item in lower), None)
    if industry == "cafe":
        industry = "café"
    location = next((item for item in LOCATIONS if item.lower() in lower), None)
    indoor_qty = _extract_quantity_before(message, "indoor")
    outdoor_qty = _extract_quantity_before(message, "outdoor")
    generic_qty = None
    quantity_match = re.search(r"\b(a|an|one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:screens?|displays?|kiosks?|printers?)\b", lower)
    if quantity_match:
        generic_qty = _number(quantity_match.group(1))
    quantity = (indoor_qty or 0) + (outdoor_qty or 0) or generic_qty
    if "indoor" in lower and "outdoor" in lower:
        environment = "both"
    elif "outdoor" in lower or "outside" in lower or "shopfront" in lower:
        environment = "outdoor"
    elif "indoor" in lower or "inside" in lower:
        environment = "indoor"
    else:
        environment = "unknown"
    screen_size_match = re.search(r"(\d{2,3})\s*(?:inch|\")", lower)
    money_match = re.search(r"(?:aed|dhs?)\s*([\d,]+)", lower)
    budget = Decimal(money_match.group(1).replace(",", "")) if money_match else None
    timeline_match = re.search(r"(?:in|within|by)\s+((?:\d+|one|two|three|four)\s+(?:days?|weeks?|months?))", lower)
    contact_intent = "quotation" if any(term in lower for term in ("quote", "quotation", "price proposal")) else "interested" if any(term in lower for term in ("need", "want", "opening", "looking for")) else "browsing"
    preferred = None
    for term in ("led display", "digital menu", "kiosk", "printer", "vinyl", "acrylic", "polycarbonate", "acp", "led module"):
        if term in lower:
            preferred = term
            break
    return CustomerRequirement(
        industry=industry,
        business_type=industry,
        location=location,
        use_case=_infer_use_case(message),
        indoor_outdoor=environment,
        quantity=quantity,
        indoor_quantity=indoor_qty,
        outdoor_quantity=outdoor_qty,
        screen_size=f"{screen_size_match.group(1)}-inch" if screen_size_match else None,
        budget=budget,
        timeline=timeline_match.group(1) if timeline_match else None,
        installation_requirement="required" if "install" in lower else None,
        content_requirement="required" if any(term in lower for term in ("content", "design", "campaign")) else None,
        preferred_product_type=preferred,
        contact_intent=contact_intent,
        source_text=message,
    )


def clarification_for(requirement: CustomerRequirement) -> str | None:
    if requirement.indoor_outdoor == "unknown" and any(term in requirement.source_text.lower() for term in ("screen", "display", "sign")):
        return "Will the signage be used indoors, outdoors, or in both environments?"
    if requirement.quantity is None and requirement.preferred_product_type not in {"printer", "vinyl", "acrylic", "polycarbonate", "acp", "led module"}:
        return "Approximately how many screens or signage positions do you need?"
    if not requirement.location and requirement.indoor_outdoor in {"outdoor", "both"}:
        return "Which emirate is the installation in? This helps us account for the site environment."
    return None


def fallback_requirement_response(message: str) -> RequirementResponse:
    requirement = fallback_extract(message)
    question = clarification_for(requirement)
    return RequirementResponse(requirement=requirement, enough_information=question is None, clarification_question=question, extraction_mode="fallback")

