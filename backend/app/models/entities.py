from __future__ import annotations

import enum
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


def uuid_str() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    SALES = "SALES"
    ADMIN = "ADMIN"


class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    QUALIFIED = "QUALIFIED"
    CONTACTED = "CONTACTED"
    QUOTATION_SENT = "QUOTATION_SENT"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"


class QuoteStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    SENT = "SENT"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(120), index=True)
    subcategory: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    use_cases: Mapped[list[str]] = mapped_column(JSON, default=list)
    industries: Mapped[list[str]] = mapped_column(JSON, default=list)
    environment: Mapped[str | None] = mapped_column(String(40), nullable=True)
    dimensions: Mapped[str | None] = mapped_column(String(120), nullable=True)
    material: Mapped[str | None] = mapped_column(String(120), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(120), nullable=True)
    specifications_json: Mapped[dict] = mapped_column(JSON, default=dict)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="AED")
    availability: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source: Mapped[str] = mapped_column(String(40), default="demo-seed")
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    customer_name: Mapped[str] = mapped_column(String(160))
    company: Mapped[str | None] = mapped_column(String(180), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(80), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    requirement: Mapped[str] = mapped_column(Text)
    requirement_json: Mapped[dict] = mapped_column(JSON, default=dict)
    recommended_products: Mapped[list[dict]] = mapped_column(JSON, default=list)
    solution_json: Mapped[dict] = mapped_column(JSON, default=dict)
    budget: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    timeline: Mapped[str | None] = mapped_column(String(120), nullable=True)
    quotation_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    lead_score: Mapped[int] = mapped_column(default=0)
    lead_temperature: Mapped[str] = mapped_column(String(20), default="Cold")
    lead_status: Mapped[LeadStatus] = mapped_column(Enum(LeadStatus), default=LeadStatus.NEW, index=True)
    source: Mapped[str] = mapped_column(String(80), default="AI Product Advisor")
    assigned_salesperson: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    quotes: Mapped[list["Quote"]] = relationship(back_populates="lead")


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    reference: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    lead_id: Mapped[str | None] = mapped_column(ForeignKey("leads.id"), nullable=True)
    customer: Mapped[str] = mapped_column(String(160))
    company: Mapped[str | None] = mapped_column(String(180), nullable=True)
    quote_date: Mapped[date] = mapped_column(Date, default=date.today)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    vat_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("5"))
    vat_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    grand_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    has_unconfirmed_pricing: Mapped[bool] = mapped_column(Boolean, default=False)
    terms: Mapped[str] = mapped_column(Text, default="Validity: 14 days. Delivery and installation subject to confirmation.")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[QuoteStatus] = mapped_column(Enum(QuoteStatus), default=QuoteStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    lead: Mapped[Lead | None] = relationship(back_populates="quotes")
    items: Mapped[list["QuoteItem"]] = relationship(back_populates="quote", cascade="all, delete-orphan")


class QuoteItem(Base):
    __tablename__ = "quote_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id"))
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    description: Mapped[str] = mapped_column(String(500))
    quantity: Mapped[int] = mapped_column(default=1)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    line_total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)

    quote: Mapped[Quote] = relationship(back_populates="items")
    product: Mapped[Product | None] = relationship()


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    campaign_name: Mapped[str] = mapped_column(String(200))
    business: Mapped[str] = mapped_column(String(120))
    offer: Mapped[str] = mapped_column(String(255))
    screen_format: Mapped[str] = mapped_column(String(40), default="portrait")
    resolution: Mapped[str] = mapped_column(String(40), default="1080 × 1920")
    audience: Mapped[str] = mapped_column(String(160))
    language: Mapped[str] = mapped_column(String(40), default="English")
    tone: Mapped[str] = mapped_column(String(40), default="Premium")
    content_json: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(40), default="DRAFT")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    metrics: Mapped[list["CampaignMetric"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class CampaignMetric(Base):
    __tablename__ = "campaign_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"))
    screen: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(120))
    hour: Mapped[int] = mapped_column()
    day: Mapped[str] = mapped_column(String(20))
    impressions: Mapped[int] = mapped_column(default=0)
    estimated_viewers: Mapped[int] = mapped_column(default=0)
    dwell_time: Mapped[float] = mapped_column(default=0)
    engagement: Mapped[float] = mapped_column(default=0)
    performance_score: Mapped[float] = mapped_column(default=0)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True)

    campaign: Mapped[Campaign] = relationship(back_populates="metrics")
