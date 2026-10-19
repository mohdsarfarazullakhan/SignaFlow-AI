def test_health_and_demo_mode(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["demo_mode"] is True


def test_customer_cannot_list_crm_leads(client, customer_headers):
    response = client.get("/api/leads", headers=customer_headers)
    assert response.status_code == 403


def test_customer_can_create_a_scored_lead(client, customer_headers):
    payload = {"customer_name": "Customer User", "company": "New Restaurant", "email": "customer@example.com", "phone": "+971500000001", "industry": "restaurant", "location": "Dubai", "requirement": "Three indoor screens for digital menus.", "requirement_json": {"use_case": "digital menus", "quantity": 3}, "budget": 15000, "timeline": "2 weeks", "quotation_requested": True}
    response = client.post("/api/leads", headers=customer_headers, json=payload)
    assert response.status_code == 201
    assert response.json()["lead_temperature"] == "Hot"


def test_campaign_fallback_works_without_groq(client, customer_headers):
    response = client.post("/api/campaigns/generate", headers=customer_headers, json={"business": "Restaurant", "campaign": "Weekend promotion", "offer": "Buy 1 Get 1 Free", "screen_format": "portrait", "resolution": "1080 × 1920", "audience": "Families", "language": "English + Arabic", "tone": "Premium"})
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "DRAFT"
    assert body["content_json"]["headline"]
    assert body["content_json"]["approval_notice"]


def test_admin_routes_enforce_role_and_source_provenance(client, sales_headers):
    assert client.get("/api/admin/users", headers=sales_headers).status_code == 403
    login = client.post("/api/auth/login", json={"email": "admin@signaflow.example.com", "password": "demo123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get("/api/admin/users", headers=headers).status_code == 200
    payload = {"source_label": "reviewed-public", "is_demo": False, "products": [{"name": "Unverified Item", "category": "Accessories", "description": "Missing the required public source URL."}]}
    response = client.post("/api/admin/products/import", headers=headers, json=payload)
    assert response.status_code == 400
