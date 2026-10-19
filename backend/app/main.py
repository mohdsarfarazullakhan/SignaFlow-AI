from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.database.seed import seed_database
from app.database.session import Base, SessionLocal, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("signaflow")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(
    title="SignaFlow AI API",
    description="Requirement-to-revenue AI platform for intelligent signage sales and campaign analytics.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def observability(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_id=%s path=%s status=error", request_id, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "The service could not complete this request. Demo fallback remains available; please try again."}, headers={"x-request-id": request_id})
    response.headers["x-request-id"] = request_id
    logger.info("request_id=%s method=%s path=%s status=%s latency_ms=%d", request_id, request.method, request.url.path, response.status_code, (time.perf_counter() - started) * 1000)
    return response


app.include_router(api_router)


@app.get("/")
def root() -> dict:
    return {"name": settings.app_name, "tagline": "From Requirement to Revenue — Powered by AI", "docs": "/api/docs"}
