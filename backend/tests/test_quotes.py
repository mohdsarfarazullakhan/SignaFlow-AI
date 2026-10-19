from decimal import Decimal

from app.services.quote_service import calculate_totals, render_quote_pdf


def test_quote_math_and_vat_are_python_calculated():
    subtotal, vat, total, unconfirmed = calculate_totals([(3, Decimal("100")), (1, Decimal("200"))], Decimal("5"))
    assert subtotal == Decimal("500.00")
    assert vat == Decimal("25.00")
    assert total == Decimal("525.00")
    assert unconfirmed is False


def test_unconfirmed_price_is_excluded_and_flagged():
    subtotal, vat, total, unconfirmed = calculate_totals([(1, None), (2, Decimal("50"))], Decimal("5"))
    assert subtotal == Decimal("100.00")
    assert total == Decimal("105.00")
    assert unconfirmed is True


def test_quote_api_and_pdf(client, sales_headers):
    products = client.get("/api/products", headers=sales_headers).json()["items"]
    priced = next(product for product in products if product["price"] is not None)
    response = client.post("/api/quotes", headers=sales_headers, json={"customer": "Test Customer", "company": "Test Company", "items": [{"product_id": priced["id"], "quantity": 2}], "vat_rate": 5})
    assert response.status_code == 201
    quote = response.json()
    assert quote["status"] == "DRAFT"
    pdf = client.post(f"/api/quotes/{quote['id']}/pdf", headers=sales_headers)
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")

