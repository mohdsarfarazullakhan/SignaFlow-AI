# SignaFlow AI

SignaFlow AI is a personal full-stack project I built to explore a practical question: what would an AI-assisted sales workflow look like for a signage and digital-display business?

Instead of making another chatbot, I connected the whole journey. A customer can describe what they need in normal language, get product recommendations, build a complete solution and request a quote. The same information then becomes a scored CRM lead that a salesperson can follow up from.

The project also includes campaign creation and anonymous signage analytics, so the workflow continues after the sale.

> This is an independent portfolio project. It is not affiliated with a real company. Products, customers, prices, campaigns and analytics included in the repository are fictional demo data.

## What the project does

The main flow is:

```text
Customer requirement
    -> structured requirement
    -> product recommendations
    -> complete signage solution
    -> quotation request
    -> scored CRM lead
    -> sales follow-up and draft quote
    -> campaign creation
    -> signage analytics
```

A useful demo prompt is:

> I am opening a restaurant in Dubai. I need three indoor digital menu screens and one outdoor advertising screen.

The advisor extracts the business type, location, quantities, environments and use cases. It then searches the demo catalogue and carries the result into the rest of the application.

## Features

- Natural-language requirement extraction with progressive clarification
- Catalogue-grounded product search and recommendations
- Complete solution builder with accessories and compatibility notes
- Customer, sales and admin workspaces
- Deterministic Hot, Warm and Cold lead scoring
- CRM dashboard, lead details and pipeline metrics
- Draft quotation generation with Python-calculated VAT and totals
- PDF quotations marked for sales review
- Sales Copilot for summaries, comparisons and follow-up drafts
- English and Arabic campaign copy with responsive screen previews
- Simulated campaign-performance analytics
- Privacy-focused Smart Signage demo using anonymous aggregate metrics
- CSV, JSON and allow-listed public catalogue imports
- Offline demo fallbacks for the important workflows

## Where AI is used

Groq is used on the backend for language understanding, explanations, sales summaries and campaign copy. The frontend never receives the Groq API key and never calls Groq directly.

I kept authoritative operations outside the model:

- product facts and prices come from the database;
- lead scores are calculated in Python;
- quotation totals and VAT are calculated in Python;
- permissions and database changes are enforced by application code;
- messages, quotations and campaigns require human approval.

If Groq is unavailable, the app falls back to deterministic demo logic instead of breaking the entire presentation.

## Tech stack

| Area | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Recharts, Lucide |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy, Alembic |
| AI | Groq SDK, LangGraph, structured outputs |
| Retrieval | local hashing embeddings; optional MiniLM and Chroma |
| Database | SQLite locally, PostgreSQL with Docker Compose |
| Documents | ReportLab quotation PDFs |
| Vision | deterministic demo engine with an OpenCV/YOLO integration boundary |
| Testing | pytest and a TypeScript production build |

More detail is available in [the architecture notes](docs/architecture.md).

## Run it locally

You will need Python 3.12+, Node.js 20+ and pnpm.

### 1. Create the environment file

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS or Linux:

```bash
cp .env.example .env
```

The application works without a Groq key when `DEMO_MODE=true`.

### 2. Set up the backend

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python scripts/setup_demo.py
cd backend
uvicorn app.main:app --reload --port 8000
```

For macOS or Linux, activate the environment with `source .venv/bin/activate`.

### 3. Start the frontend

Open another terminal:

```powershell
cd frontend
pnpm install
pnpm dev
```

Open `http://localhost:5173`. FastAPI documentation is available at `http://localhost:8000/api/docs`.

### Demo accounts

| Workspace | Email | Password |
|---|---|---|
| Sales | `sales@signaflow.example.com` | `demo123` |
| Admin | `admin@signaflow.example.com` | `demo123` |
| Customer | `customer@signaflow.example.com` | `demo123` |

These credentials are only for the local demo and can be changed through environment variables.

## Optional Groq setup

Add your key to the uncommitted `.env` file:

```dotenv
GROQ_API_KEY=your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_FAST_MODEL=llama-3.1-8b-instant
GROQ_REASONING_MODEL=llama-3.3-70b-versatile
DEMO_MODE=false
```

No OpenAI key is required.

## Docker

After creating `.env`, run:

```bash
docker compose up --build
```

This starts the frontend, backend and PostgreSQL services. The frontend is exposed on port `3000` and the API on port `8000`.

## Product data

The bundled catalogue contains fictional products marked with `is_demo=true`. It should not be presented as a real supplier catalogue.

Local imports:

```bash
python scripts/ingest_products.py --file path/to/products.json --demo
python scripts/ingest_products.py --file path/to/products.csv
```

Public-page ingestion is disabled until `CATALOG_ALLOWED_HOSTS` is explicitly configured. The importer checks the allow-list and robots rules, limits retries and request frequency, caches responses and prevents duplicates.

## Tests

Backend:

```bash
pytest backend/tests -q
```

Frontend production build:

```bash
cd frontend
pnpm run build
```

At the time of this README update, all 16 backend tests pass and the frontend production build completes successfully.

## Security and privacy decisions

- `.env` is ignored by Git; only `.env.example` is committed.
- API keys stay on the backend and are not logged or returned to the browser.
- Retrieved website and product text is treated as untrusted data.
- LLM responses cannot execute arbitrary Python or approve business actions.
- Smart Signage does not use facial recognition or identify individuals.
- Outbound messages and campaigns are drafts only.

## Current limitations

This is still a portfolio prototype, not a deployed business system. The catalogue and analytics are demo data, the vision module uses a deterministic fallback unless a separate YOLO/OpenCV worker is connected, and external CRM or messaging integrations are intentionally disabled.

The next useful step would be to connect a reviewed real catalogue, add SSO and audit logging, and evaluate recommendation quality with actual sales feedback.

## Documentation

- [Architecture](docs/architecture.md)
- [API guide](docs/api.md)
- [Demo walkthrough](docs/demo-script.md)
- [Business value and pilot metrics](docs/business-value.md)
