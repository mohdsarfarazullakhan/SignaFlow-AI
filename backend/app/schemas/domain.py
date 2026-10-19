from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.entities import LeadStatus, QuoteStatus, UserRole


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
    demo_mode: bool
    llm: str
    database: str
    rag: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=200)


class UserOut(ORMModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProductOut(ORMModel):
    id: str
    name: str
    slug: str
    category: str
    subcategory: str | None
    description: str
    use_cases: list[str]
    industries: list[str]
    environment: str | None
    dimensions: str | None
    material: str | None
    brand: str | None
    specifications_json: dict[str, Any]
    price: Decimal | None
    currency: str
    availability: str | None
    source: str
    source_url: str | None
    image_url: str | None
    is_demo: bool


class ProductListResponse(BaseModel):
    items: list[ProductOut]
    total: int
    categories: list[str]


class ProductImportItem(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    category: str = Field(min_length=2, max_length=120)
    subcategory: str | None = Field(default=None, max_length=120)
    description: str = Field(min_length=3, max_length=4_000)
    use_cases: list[str] = Field(default_factory=list, max_length=30)
    industries: list[str] = Field(default_factory=list, max_length=30)
    environment: Literal["indoor", "outdoor", "both"] | None = None
    dimensions: str | None = Field(default=None, max_length=120)
    material: str | None = Field(default=None, max_length=120)
    brand: str | None = Field(default=None, max_length=120)
    specifications_json: dict[str, Any] = Field(default_factory=dict)
    price: Decimal | None = Field(default=None, ge=0)
    currency: str = Field(default="AED", min_length=3, max_length=8)
    availability: str | None = Field(default=None, max_length=80)
    source_url: str | None = Field(default=None, max_length=500)
    image_url: str | None = Field(default=None, max_length=500)


class ProductImportRequest(BaseModel):
    source_label: str = Field(default="admin-json-import", min_length=3, max_length=80)
    is_demo: bool = True
    products: list[ProductImportItem] = Field(min_length=1, max_length=100)


class ProductImportResponse(BaseModel):
    created: int
    updated: int
    is_demo: bool
    notice: str


class CustomerRequirement(BaseModel):
    industry: str | None = None
    business_type: str | None = None
    location: str | None = None
    use_case: str
    indoor_outdoor: Literal["indoor", "outdoor", "both", "unknown"] = "unknown"
    quantity: int | None = Field(default=None, ge=1, le=10_000)
    indoor_quantity: int | None = Field(default=None, ge=0, le=10_000)
    outdoor_quantity: int | None = Field(default=None, ge=0, le=10_000)
    dimensions: str | None = None
    screen_size: str | None = None
    budget: Decimal | None = Field(default=None, ge=0)
    timeline: str | None = None
    installation_requirement: str | None = None
    content_requirement: str | None = None
    preferred_product_type: str | None = None
    contact_intent: Literal["browsing", "interested", "quotation", "unknown"] = "unknown"
    source_text: str


class RequirementRequest(BaseModel):
    message: str = Field(min_length=3, max_length=4_000)
    previous: CustomerRequirement | None = None


class RequirementResponse(BaseModel):
    requirement: CustomerRequirement
    enough_information: bool
    clarification_question: str | None = None
    extraction_mode: Literal["groq", "fallback"]


class RecommendationRequest(BaseModel):
    requirement: CustomerRequirement
    limit: int = Field(default=3, ge=1, le=10)


class RecommendationOut(BaseModel):
    product: ProductOut
    confidence_score: int = Field(ge=0, le=100)
    retrieval_score: float = Field(ge=0, le=1)
    why_it_matches: str
    recommended_use: str
    matched_signals: list[str]
    missing_information: list[str]


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationOut]
    requirement: CustomerRequirement
    mode: str
    disclaimer: str


class SolutionRequest(BaseModel):
    requirement: CustomerRequirement
    recommendation_product_ids: list[str] = Field(default_factory=list, max_length=12)


class SolutionItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int = Field(ge=1, le=10_000)
    role: str
    rationale: str
    optional: bool = False
    unit_price: Decimal | None = None
    currency: str = "AED"


class SolutionOut(BaseModel):
    name: str
    summary: str
    items: list[SolutionItem]
    compatibility_notes: list[str]
    optional_upgrades: list[str]
    pricing_note: str


class LeadCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=160)
    company: str | None = Field(default=None, max_length=180)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=80)
    whatsapp: str | None = Field(default=None, max_length=80)
    industry: str | None = None
    location: str | None = None
    requirement: str = Field(min_length=3, max_length=4_000)
    requirement_json: dict[str, Any] = Field(default_factory=dict)
    recommended_products: list[dict[str, Any]] = Field(default_factory=list)
    solution_json: dict[str, Any] = Field(default_factory=dict)
    budget: Decimal | None = Field(default=None, ge=0)
    timeline: str | None = None
    quotation_requested: bool = False
    source: str = "AI Product Advisor"

    @field_validator("phone", "whatsapp")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value and len("".join(c for c in value if c.isdigit())) < 7:
            raise ValueError("Phone number must contain at least 7 digits")
        return value


class LeadUpdate(BaseModel):
    lead_status: LeadStatus | None = None
    assigned_salesperson: str | None = None
    notes: str | None = None
    budget: Decimal | None = Field(default=None, ge=0)
    timeline: str | None = None


class LeadOut(ORMModel):
    id: str
    customer_name: str
    company: str | None
    email: str | None
    phone: str | None
    whatsapp: str | None
    industry: str | None
    location: str | None
    requirement: str
    requirement_json: dict[str, Any]
    recommended_products: list[dict[str, Any]]
    solution_json: dict[str, Any]
    budget: Decimal | None
    timeline: str | None
    quotation_requested: bool
    lead_score: int
    lead_temperature: str
    lead_status: LeadStatus
    source: str
    assigned_salesperson: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class LeadScoreResponse(BaseModel):
    score: int
    temperature: Literal["Cold", "Warm", "Hot"]
    reasons: list[str]
    breakdown: dict[str, int]


class QuoteItemCreate(BaseModel):
    product_id: str | None = None
    description: str | None = Field(default=None, max_length=500)
    quantity: int = Field(ge=1, le=10_000)


class QuoteCreate(BaseModel):
    lead_id: str | None = None
    customer: str | None = None
    company: str | None = None
    items: list[QuoteItemCreate] = Field(min_length=1, max_length=100)
    vat_rate: Decimal = Field(default=Decimal("5"), ge=0, le=100)
    terms: str | None = None
    notes: str | None = None


class QuoteItemOut(ORMModel):
    id: str
    product_id: str | None
    description: str
    quantity: int
    unit_price: Decimal | None
    line_total: Decimal | None


class QuoteOut(ORMModel):
    id: str
    reference: str
    lead_id: str | None
    customer: str
    company: str | None
    quote_date: date
    subtotal: Decimal
    vat_rate: Decimal
    vat_amount: Decimal
    grand_total: Decimal
    has_unconfirmed_pricing: bool
    terms: str
    notes: str | None
    status: QuoteStatus
    items: list[QuoteItemOut]
    created_at: datetime


class CopilotRequest(BaseModel):
    message: str = Field(min_length=2, max_length=4_000)
    lead_id: str | None = None


class CopilotResponse(BaseModel):
    answer: str
    suggested_actions: list[str]
    mode: str
    requires_human_approval: bool = True


class CampaignCreate(BaseModel):
    business: str
    campaign: str
    offer: str
    screen_format: Literal["portrait", "landscape", "led-banner", "menu-board"] = "portrait"
    resolution: str = "1080 × 1920"
    audience: str
    language: Literal["English", "Arabic", "English + Arabic"] = "English"
    tone: Literal["Premium", "Luxury", "Fun", "Corporate", "Energetic"] = "Premium"


class CampaignOut(ORMModel):
    id: str
    campaign_name: str
    business: str
    offer: str
    screen_format: str
    resolution: str
    audience: str
    language: str
    tone: str
    content_json: dict[str, Any]
    status: str
    is_demo: bool
    created_at: datetime


class VisionRequest(BaseModel):
    filename: str | None = None
    location: str = "Demo Showroom Entrance"
    screen: str = "Entrance Display"
    roi: dict[str, float] = Field(default_factory=lambda: {"x": 0.55, "y": 0.2, "width": 0.35, "height": 0.65})
    duration_seconds: int = Field(default=60, ge=10, le=86_400)


class VisionResponse(BaseModel):
    people_passed: int
    people_inside_roi: int
    estimated_engagement: float
    average_dwell_seconds: float
    peak_interval: str
    timeline: list[dict[str, int | float | str]]
    mode: str
    privacy_notice: str


class VisualAdvisorRequest(BaseModel):
    filename: str | None = None
    scene_type: str | None = None


class VisualAdvisorResponse(BaseModel):
    observations: list[str]
    recommended_categories: list[str]
    suggested_positions: list[str]
    confidence: str
    measurement_notice: str
