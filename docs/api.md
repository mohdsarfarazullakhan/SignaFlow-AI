# API guide

Base URL: `http://localhost:8000/api`

Interactive OpenAPI: `/api/docs`

Except for health and informational opportunity/KPI routes, endpoints require a Bearer token from `POST /auth/login`.

## Authentication

- `POST /auth/login` — email/password login
- `GET /auth/me` — current user profile

## Customer journey

- `POST /requirements/extract` — Pydantic requirement extraction and one progressive question
- `POST /recommend` — catalogue-only ranked recommendations
- `POST /solutions/build` — complete product/accessory solution
- `POST /chat` — connected LangGraph path through all three stages

Example request:

```json
{
  "message": "I am opening a restaurant in Dubai. I need three indoor menu screens and one outdoor advertising screen."
}
```

## Products

- `GET /products?search=&category=&environment=`
- `GET /products/{product_id}`

Product records expose `source`, `source_url`, and `is_demo`. Missing values remain missing; no endpoint synthesizes facts.

## Leads and scoring

- `GET /leads` — SALES/ADMIN
- `POST /leads` — authenticated users; auto-scores in Python
- `GET /leads/{lead_id}` — SALES/ADMIN
- `PATCH /leads/{lead_id}` — allowed fields only; SALES/ADMIN
- `POST /leads/{lead_id}/score` — recompute deterministic score

Scoring maximum: clear requirement 15, business 10, quantity 10, budget 15, ≤30-day timeline 20, quote intent 20, actionable contact 10.

## Quotations

- `POST /quotes` — SALES/ADMIN; creates DRAFT only
- `GET /quotes`
- `GET /quotes/{quote_id}`
- `POST /quotes/{quote_id}/pdf`

`product_id` selects price from the database. User-provided or LLM-provided unit prices are not accepted by the input schema. Unknown pricing is returned as null, flagged by `has_unconfirmed_pricing`, and excluded from the partial total.

## Copilot

- `POST /copilot/chat` — SALES/ADMIN

Optional `lead_id` grounds the response. `requires_human_approval` is always true for generated communication drafts.

## Campaigns

- `POST /campaigns/generate`
- `GET /campaigns`
- `GET /campaigns/{campaign_id}`

Campaigns remain DRAFT and support English, Arabic, or English + Arabic.

## Analytics and vision

- `GET /analytics/overview`
- `GET /analytics/sales`
- `GET /analytics/campaigns`
- `POST /vision/analyze`
- `POST /visual-advisor/analyze`

Demo analytics responses are labelled `Demo / Simulated Analytics`.

## Platform information

- `GET /health`
- `GET /integrations/n8n/status`
- `GET /opportunities`
- `GET /business-impact`

No endpoint returns API keys, password hashes, or environment secrets.

