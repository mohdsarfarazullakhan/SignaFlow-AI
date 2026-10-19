from __future__ import annotations

import os
import random
import re
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.entities import Campaign, CampaignMetric, Lead, LeadStatus, Product, User, UserRole
from app.services.lead_scoring import apply_score_to_lead


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _product(
    name: str,
    category: str,
    description: str,
    use_cases: list[str],
    industries: list[str],
    environment: str,
    price: str | None,
    *,
    subcategory: str | None = None,
    dimensions: str | None = None,
    material: str | None = None,
    specs: dict | None = None,
) -> dict:
    return {
        "name": name,
        "slug": _slug(name),
        "category": category,
        "subcategory": subcategory,
        "description": description,
        "use_cases": use_cases,
        "industries": industries,
        "environment": environment,
        "dimensions": dimensions,
        "material": material,
        "brand": "Demo Catalogue",
        "specifications_json": specs or {},
        "price": Decimal(price) if price else None,
        "currency": "AED",
        "availability": "Demo availability — confirm with sales",
        "source": "demo-seed",
        "source_url": None,
        "image_url": None,
        "is_demo": True,
    }


PRODUCTS = [
    _product("43-inch Indoor Commercial Display", "Digital Signage", "Commercial-grade full-HD display for digital menus and promotional content.", ["digital menu boards", "retail promotions", "wayfinding"], ["restaurant", "café", "retail", "hotel"], "indoor", "3150", subcategory="Commercial Displays", dimensions="43-inch", specs={"resolution": "1920 × 1080", "orientation": "landscape or portrait"}),
    _product("55-inch Indoor Commercial Display", "Digital Signage", "Large-format commercial display suited to menus, promotions, and information screens.", ["restaurant menus", "corporate communication", "retail promotions"], ["restaurant", "retail", "corporate office", "hotel"], "indoor", "4250", subcategory="Commercial Displays", dimensions="55-inch", specs={"resolution": "3840 × 2160", "orientation": "landscape or portrait"}),
    _product("65-inch Indoor Commercial Display", "Digital Signage", "High-impact indoor screen for large hospitality, showroom, and corporate spaces.", ["large menu boards", "showroom advertising", "lobby information"], ["hotel", "automotive", "showroom", "corporate office"], "indoor", "6200", subcategory="Commercial Displays", dimensions="65-inch", specs={"resolution": "3840 × 2160"}),
    _product("55-inch High-Brightness Window Display", "Digital Signage", "High-brightness screen designed for storefront-facing promotions behind glass.", ["window advertising", "entrance promotions", "property listings"], ["retail", "real estate", "restaurant", "showroom"], "indoor", "7900", subcategory="High Brightness", dimensions="55-inch", specs={"brightness": "High brightness — exact rating to confirm"}),
    _product("55-inch Weatherproof Outdoor Display", "Digital Signage", "Outdoor-rated commercial advertising display for customer-facing promotions.", ["outdoor advertising", "restaurant promotions", "entrance messaging"], ["restaurant", "retail", "hotel", "automotive"], "outdoor", None, subcategory="Outdoor Displays", dimensions="55-inch", specs={"weather_rating": "Outdoor-rated — exact IP rating to confirm"}),
    _product("Outdoor LED Display Cabinet P4", "LED Displays", "Modular outdoor LED cabinet for high-impact advertising installations.", ["building advertising", "outdoor promotions", "event screens"], ["real estate", "mall", "events", "advertising agency"], "outdoor", "9500", subcategory="LED Cabinets", specs={"pixel_pitch": "P4", "configuration": "modular cabinet"}),
    _product("Indoor Fine-Pitch LED Panel P2.5", "LED Displays", "Fine-pitch modular LED panel for indoor video walls and presentation spaces.", ["video walls", "showroom displays", "event backdrops"], ["corporate office", "showroom", "events", "hotel"], "indoor", "6800", subcategory="LED Panels", specs={"pixel_pitch": "P2.5"}),
    _product("Android Digital Signage Media Player", "Digital Signage", "Compact player for scheduled content playback on commercial displays.", ["content playback", "menu scheduling", "campaign rotation"], ["restaurant", "retail", "hotel", "corporate office"], "indoor", "1150", subcategory="Media Players", specs={"connectivity": "Wi-Fi and Ethernet"}),
    _product("Cloud Signage CMS Annual Licence", "Digital Signage", "Demo annual software licence for remote content scheduling and screen management.", ["central content management", "campaign scheduling", "multi-screen control"], ["restaurant", "retail", "hotel", "corporate office"], "both", "720", subcategory="Software", specs={"term": "12 months"}),
    _product("Commercial Display Wall Mount", "Accessories", "Fixed wall mount for compatible commercial displays.", ["display installation", "menu board mounting"], ["restaurant", "retail", "hotel", "corporate office"], "indoor", "185", subcategory="Mounts", specs={"compatibility": "Confirm VESA and load rating"}),
    _product("Ceiling Display Mount", "Accessories", "Adjustable ceiling mount for suspended signage displays.", ["suspended menu boards", "wayfinding installation"], ["restaurant", "retail", "mall", "hotel"], "indoor", "340", subcategory="Mounts", specs={"compatibility": "Confirm screen weight and ceiling structure"}),
    _product("Outdoor Display Floor Stand", "Accessories", "Weighted floor-mount system for compatible outdoor display enclosures.", ["outdoor screen installation", "entrance advertising"], ["restaurant", "retail", "events"], "outdoor", None, subcategory="Mounts", specs={"installation": "Site survey required"}),
    _product("Large-Format Eco-Solvent Printer 1.6m", "Printing Machines", "Demo 1.6 metre printer configuration for banners, vinyl, and advertising graphics.", ["large-format advertising", "vinyl printing", "banner production"], ["signage company", "advertising agency", "printing business"], "indoor", None, subcategory="Eco-Solvent", dimensions="1.6m media width", specs={"print_width": "1.6 m"}),
    _product("UV Flatbed Printer 1.3 × 2.5m", "Printing Machines", "Demo flatbed configuration for direct printing onto rigid signage materials.", ["acrylic printing", "ACP printing", "display board production"], ["signage company", "advertising agency", "fit-out contractor"], "indoor", None, subcategory="UV Printers", dimensions="1.3 × 2.5m bed", specs={"media": "Rigid substrates"}),
    _product("Cold Laminator 1.6m", "Printing Machines", "Wide-format cold laminator for finishing printed signage media.", ["print finishing", "vinyl protection", "graphics production"], ["signage company", "advertising agency", "printing business"], "indoor", "7200", subcategory="Finishing", dimensions="1.6m working width"),
    _product("Gloss White Printable Vinyl Roll", "Vinyl", "General-purpose printable self-adhesive vinyl for promotional and branding graphics.", ["window graphics", "wall branding", "promotional stickers"], ["retail", "signage company", "advertising agency"], "both", "465", subcategory="Printable Vinyl", dimensions="1.27 × 50m", material="PVC vinyl"),
    _product("Grey-Back Printable Vinyl Roll", "Vinyl", "Opaque printable vinyl intended to reduce show-through on covered surfaces.", ["outdoor branding", "vehicle graphics", "retail promotions"], ["signage company", "advertising agency", "automotive"], "both", "545", subcategory="Printable Vinyl", dimensions="1.37 × 50m", material="PVC vinyl"),
    _product("One-Way Vision Window Film", "Vinyl", "Perforated printable film for window branding while retaining outward visibility.", ["storefront branding", "vehicle windows", "campaign graphics"], ["retail", "restaurant", "automotive", "real estate"], "both", "390", subcategory="Perforated Vinyl", dimensions="1.37 × 50m", material="Perforated PVC"),
    _product("Frosted Glass Effect Film", "Vinyl", "Translucent decorative film for privacy, branding, and interior glass treatments.", ["office privacy", "window branding", "decorative glass"], ["corporate office", "retail", "hotel", "hospital"], "indoor", "610", subcategory="Decorative Film", dimensions="1.22 × 50m", material="PVC film"),
    _product("Clear Cast Acrylic Sheet 5mm", "Acrylic", "Rigid clear acrylic sheet for fabricated displays and illuminated signs.", ["light boxes", "display fabrication", "protective panels"], ["signage company", "retail", "fit-out contractor"], "both", "285", dimensions="1.22 × 2.44m", material="Cast acrylic"),
    _product("Opal Acrylic Sheet 3mm", "Acrylic", "Light-diffusing acrylic sheet suitable for illuminated sign faces.", ["illuminated signage", "light boxes", "menu displays"], ["signage company", "restaurant", "retail"], "both", "220", dimensions="1.22 × 2.44m", material="Opal acrylic"),
    _product("Mirror Gold Acrylic Sheet", "Acrylic", "Decorative mirror-finish acrylic for premium interiors and lettering.", ["premium signage", "decorative letters", "retail displays"], ["hotel", "retail", "restaurant", "fit-out contractor"], "indoor", "360", dimensions="1.22 × 2.44m", material="Acrylic"),
    _product("Outdoor ACP Sheet 4mm", "ACP", "Aluminium composite panel for durable sign backing and cladding applications.", ["sign backing", "shopfront fascia", "outdoor cladding"], ["signage company", "fit-out contractor", "retail"], "outdoor", "145", dimensions="1.22 × 2.44m", material="Aluminium composite", specs={"thickness": "4 mm"}),
    _product("Brushed Silver ACP Sheet", "ACP", "Brushed-finish composite panel for premium interior and exterior signage.", ["corporate signs", "directional signage", "shopfront fascia"], ["corporate office", "retail", "hotel"], "both", "185", dimensions="1.22 × 2.44m", material="Aluminium composite"),
    _product("Clear Solid Polycarbonate Sheet 4mm", "Polycarbonate", "Impact-resistant transparent sheet for protective and outdoor signage applications.", ["protective glazing", "outdoor signs", "canopies"], ["signage company", "fit-out contractor", "industrial"], "outdoor", "410", dimensions="1.22 × 2.44m", material="Polycarbonate"),
    _product("Opal Polycarbonate Sheet 6mm", "Polycarbonate", "Durable light-diffusing sheet for illuminated exterior applications.", ["illuminated sign faces", "outdoor light boxes"], ["signage company", "retail", "restaurant"], "outdoor", "525", dimensions="1.22 × 2.44m", material="Polycarbonate"),
    _product("Waterproof LED Module 3-LED", "LED Modules", "Compact waterproof LED module for channel letters and light boxes.", ["channel letters", "light boxes", "illuminated signage"], ["signage company", "advertising agency", "fit-out contractor"], "outdoor", "4.50", subcategory="Sign Modules", specs={"input": "12V", "rating": "Waterproof — exact IP rating to confirm"}),
    _product("High-Brightness LED Module 2-LED", "LED Modules", "Efficient demo LED module for shallow channel letters and compact signs.", ["channel letters", "logo illumination", "retail signs"], ["signage company", "retail", "fit-out contractor"], "both", "3.25", subcategory="Sign Modules", specs={"input": "12V"}),
    _product("12V Rainproof Power Supply 200W", "Accessories", "Power supply for compatible low-voltage signage LED systems.", ["LED module power", "light box installation"], ["signage company", "fit-out contractor"], "outdoor", "92", subcategory="Power Supplies", specs={"output": "12V", "power": "200W"}),
    _product("Aluminium Channel Letter Coil", "Accessories", "Formable aluminium coil for fabricated channel letter returns.", ["channel letter fabrication", "illuminated logos"], ["signage company", "advertising agency"], "both", "175", subcategory="Fabrication", material="Aluminium"),
    _product("A1 Snap Frame Pavement Sign", "Accessories", "Portable double-sided pavement frame for printed promotion inserts.", ["entrance promotions", "restaurant offers", "retail wayfinding"], ["restaurant", "retail", "hotel", "events"], "outdoor", "165", subcategory="Display Stands", dimensions="A1"),
    _product("Interactive Self-Service Kiosk 32-inch", "Digital Signage", "Floor-standing interactive kiosk for directories, queueing, or self-service journeys.", ["self service", "wayfinding", "queue management"], ["hospital", "government", "hotel", "mall"], "indoor", None, subcategory="Kiosks", dimensions="32-inch", specs={"interaction": "touch-enabled demo configuration"}),
    _product("Digital Wayfinding Totem 49-inch", "Digital Signage", "Portrait totem display for directories and wayfinding in hospitality and public venues.", ["hotel wayfinding", "mall directory", "event navigation"], ["hotel", "mall", "hospital", "events"], "indoor", "8900", subcategory="Totems", dimensions="49-inch", specs={"orientation": "portrait"}),
]


def seed_users(db: Session) -> None:
    if db.query(User).count():
        return
    users = [
        ("SignaFlow Admin", "admin@signaflow.example.com", UserRole.ADMIN, os.getenv("DEMO_ADMIN_PASSWORD", "demo123")),
        ("Maya – Sales", "sales@signaflow.example.com", UserRole.SALES, os.getenv("DEMO_SALES_PASSWORD", "demo123")),
        ("Demo Customer", "customer@signaflow.example.com", UserRole.CUSTOMER, os.getenv("DEMO_CUSTOMER_PASSWORD", "demo123")),
    ]
    for name, email, role, password in users:
        db.add(User(name=name, email=email, role=role, password_hash=hash_password(password)))


def seed_products(db: Session) -> None:
    if db.query(Product).count():
        return
    db.add_all(Product(**row) for row in PRODUCTS)


def seed_leads(db: Session) -> None:
    if db.query(Lead).count():
        return
    rows = [
        {"customer_name": "Ahmed Mansoor", "company": "ABC Restaurant Group", "email": "ahmed@example.test", "phone": "+971 50 000 1001", "industry": "restaurant", "location": "Dubai", "requirement": "Three indoor digital menu screens and one outdoor advertising screen for a new restaurant.", "requirement_json": {"industry": "restaurant", "location": "Dubai", "use_case": "digital menus and outdoor advertising", "indoor_outdoor": "both", "quantity": 4, "indoor_quantity": 3, "outdoor_quantity": 1, "timeline": "2 weeks"}, "budget": Decimal("35000"), "timeline": "2 weeks", "quotation_requested": True, "lead_status": LeadStatus.QUALIFIED, "assigned_salesperson": "Maya"},
        {"customer_name": "Sara Ali", "company": "XYZ Retail", "email": "sara@example.test", "industry": "retail", "location": "Sharjah", "requirement": "A digital display near the shop entrance for rotating promotions.", "requirement_json": {"industry": "retail", "location": "Sharjah", "use_case": "entrance promotions", "indoor_outdoor": "indoor", "quantity": 1}, "timeline": "6 weeks", "quotation_requested": False, "lead_status": LeadStatus.NEW},
        {"customer_name": "Omar Khalid", "company": "Crescent Properties", "email": "omar@example.test", "phone": "+971 50 000 1003", "industry": "real estate", "location": "Abu Dhabi", "requirement": "Outdoor LED advertising for a new property launch.", "requirement_json": {"industry": "real estate", "location": "Abu Dhabi", "use_case": "outdoor LED advertising", "indoor_outdoor": "outdoor", "quantity": 2, "timeline": "21 days"}, "budget": Decimal("80000"), "timeline": "21 days", "quotation_requested": True, "lead_status": LeadStatus.QUALIFIED, "assigned_salesperson": "Maya"},
        {"customer_name": "Lina Joseph", "company": "Harbour Hotel", "email": "lina@example.test", "industry": "hotel", "location": "Dubai", "requirement": "Digital wayfinding screens for lobby and conference areas.", "requirement_json": {"industry": "hotel", "location": "Dubai", "use_case": "digital wayfinding", "indoor_outdoor": "indoor", "quantity": 5}, "timeline": "2 months", "quotation_requested": True, "lead_status": LeadStatus.CONTACTED},
        {"customer_name": "Faisal Noor", "company": "BrightLine Signage", "phone": "+971 50 000 1005", "industry": "signage company", "location": "Ajman", "requirement": "Materials for outdoor illuminated channel letters.", "requirement_json": {"industry": "signage company", "location": "Ajman", "use_case": "outdoor illuminated signage", "indoor_outdoor": "outdoor", "quantity": 1}, "quotation_requested": False, "lead_status": LeadStatus.NEW},
    ]
    for row in rows:
        lead = Lead(**row, source="Demo Data")
        apply_score_to_lead(lead)
        db.add(lead)


def seed_campaigns(db: Session) -> None:
    if db.query(Campaign).count():
        return
    campaigns = [
        ("Breakfast Coffee Campaign", "Café", "Coffee + croissant breakfast combo", "portrait", "Early commuters"),
        ("Weekend Burger Offer", "Restaurant", "Buy 1 Get 1 Free", "landscape", "Families"),
        ("Retail Summer Sale", "Retail", "Up to 30% off selected lines", "led-banner", "Mall shoppers"),
        ("Luxury Property Campaign", "Real Estate", "Private waterfront residences", "portrait", "Investors"),
        ("Hotel Promotion", "Hotel", "Weekend staycation package", "landscape", "UAE residents"),
    ]
    random.seed(42)
    for index, (name, business, offer, screen_format, audience) in enumerate(campaigns):
        campaign = Campaign(
            campaign_name=name,
            business=business,
            offer=offer,
            screen_format=screen_format,
            resolution="1080 × 1920" if screen_format == "portrait" else "1920 × 1080",
            audience=audience,
            language="English + Arabic" if index % 2 else "English",
            tone="Premium",
            content_json={"headline": offer, "subheadline": f"Created for {audience}", "cta": "Discover more", "variants": ["Benefit-led", "Urgency-led", "Bilingual"]},
            status="DRAFT",
            is_demo=True,
        )
        db.add(campaign)
        db.flush()
        for hour in range(8, 22, 2):
            impressions = random.randint(90, 260)
            viewers = int(impressions * random.uniform(0.3, 0.65))
            engagement = round(viewers / impressions * 100, 1)
            campaign.metrics.append(CampaignMetric(campaign_id=campaign.id, screen=f"Screen {index + 1}", location=["Dubai Marina", "Al Quoz", "Business Bay", "JLT", "Deira"][index], hour=hour, day="Friday" if index % 2 else "Thursday", impressions=impressions, estimated_viewers=viewers, dwell_time=round(random.uniform(3.4, 9.8), 1), engagement=engagement, performance_score=round(engagement * 1.25, 1), is_simulated=True))


def seed_database(db: Session) -> None:
    if not settings.demo_mode:
        return
    seed_users(db)
    seed_products(db)
    seed_leads(db)
    seed_campaigns(db)
    db.commit()
