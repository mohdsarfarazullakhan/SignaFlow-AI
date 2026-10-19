from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("JWT_SECRET", "test-secret-only")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app.database.seed import seed_database  # noqa: E402
from app.database.session import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def session_factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with factory() as db:
        seed_database(db)
    return factory


@pytest.fixture()
def db(session_factory):
    with session_factory() as session:
        yield session


@pytest.fixture()
def client(session_factory):
    def override_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as value:
        yield value
    app.dependency_overrides.clear()


@pytest.fixture()
def sales_headers(client):
    response = client.post("/api/auth/login", json={"email": "sales@signaflow.example.com", "password": "demo123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture()
def customer_headers(client):
    response = client.post("/api/auth/login", json={"email": "customer@signaflow.example.com", "password": "demo123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
