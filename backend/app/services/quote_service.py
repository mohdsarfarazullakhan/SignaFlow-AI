from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.models.entities import Lead, Product, Quote, QuoteItem
from app.schemas.domain import QuoteCreate

MONEY = Decimal("0.01")


def quantize(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def calculate_totals(lines: list[tuple[int, Decimal | None]], vat_rate: Decimal) -> tuple[Decimal, Decimal, Decimal, bool]:
    subtotal = sum((Decimal(quantity) * price for quantity, price in lines if price is not None), Decimal("0"))
    subtotal = quantize(subtotal)
    vat = quantize(subtotal * vat_rate / Decimal("100"))
    return subtotal, vat, quantize(subtotal + vat), any(price is None for _, price in lines)


def create_quote(db: Session, payload: QuoteCreate) -> Quote:
    lead = db.get(Lead, payload.lead_id) if payload.lead_id else None
    customer = payload.customer or (lead.customer_name if lead else None)
    if not customer:
        raise ValueError("Customer is required when no lead is provided")
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_([item.product_id for item in payload.items if item.product_id])).all()}
    reference = f"DSAI-{date.today():%Y%m%d}-{db.query(Quote).count() + 1:04d}"
    quote = Quote(reference=reference, lead_id=lead.id if lead else None, customer=customer, company=payload.company or (lead.company if lead else None), vat_rate=payload.vat_rate, terms=payload.terms or "Validity: 14 days. Delivery and installation are subject to stock and site confirmation.", notes=payload.notes)
    line_data: list[tuple[int, Decimal | None]] = []
    for item in payload.items:
        product = products.get(item.product_id) if item.product_id else None
        if item.product_id and product is None:
            raise ValueError(f"Unknown product id: {item.product_id}")
        description = product.name if product else item.description
        if not description:
            raise ValueError("A description is required for non-product quote items")
        unit_price = product.price if product else None
        line_total = quantize(unit_price * item.quantity) if unit_price is not None else None
        quote.items.append(QuoteItem(product_id=product.id if product else None, description=description, quantity=item.quantity, unit_price=unit_price, line_total=line_total))
        line_data.append((item.quantity, unit_price))
    quote.subtotal, quote.vat_amount, quote.grand_total, quote.has_unconfirmed_pricing = calculate_totals(line_data, payload.vat_rate)
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


def render_quote_pdf(quote: Quote) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm)
    styles = getSampleStyleSheet()
    story = [Paragraph("<b>SIGNAFLOW AI</b>", styles["Title"]), Paragraph("Independent signage sales automation prototype", styles["Normal"]), Spacer(1, 8 * mm), Paragraph("<font color='#D94B55'><b>DRAFT QUOTATION — SALES REVIEW REQUIRED</b></font>", styles["Heading2"]), Spacer(1, 4 * mm)]
    details = [["Quotation reference", quote.reference], ["Customer", quote.customer], ["Company", quote.company or "—"], ["Date", quote.quote_date.isoformat()], ["Status", quote.status.value]]
    story.append(Table(details, colWidths=[45 * mm, 110 * mm], style=TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF1F4")), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CCD2D8")), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("PADDING", (0, 0), (-1, -1), 6)])))
    story.append(Spacer(1, 7 * mm))
    rows = [["Item", "Qty", "Unit price", "Total"]]
    for item in quote.items:
        rows.append([item.description, str(item.quantity), f"AED {item.unit_price:,.2f}" if item.unit_price is not None else "To be confirmed", f"AED {item.line_total:,.2f}" if item.line_total is not None else "To be confirmed"])
    rows.extend([["", "", "Subtotal", f"AED {quote.subtotal:,.2f}"], ["", "", f"VAT ({quote.vat_rate}%)", f"AED {quote.vat_amount:,.2f}"], ["", "", "Grand total*", f"AED {quote.grand_total:,.2f}"]])
    table = Table(rows, colWidths=[82 * mm, 16 * mm, 30 * mm, 32 * mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172333")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("ALIGN", (1, 1), (-1, -1), "RIGHT"), ("GRID", (0, 0), (-1, -4), 0.25, colors.HexColor("#CCD2D8")), ("LINEABOVE", (2, -3), (-1, -3), 0.8, colors.HexColor("#172333")), ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"), ("PADDING", (0, 0), (-1, -1), 6)]))
    story.extend([table, Spacer(1, 7 * mm)])
    if quote.has_unconfirmed_pricing:
        story.append(Paragraph("* Grand total excludes items whose price must be confirmed by the sales team.", styles["Italic"]))
    story.extend([Spacer(1, 4 * mm), Paragraph(f"<b>Terms</b><br/>{quote.terms}", styles["BodyText"]), Spacer(1, 3 * mm), Paragraph(f"<b>Notes</b><br/>{quote.notes or 'Final specifications, delivery, installation, availability, and compatibility require sales approval.'}", styles["BodyText"])])
    document.build(story)
    return buffer.getvalue()
