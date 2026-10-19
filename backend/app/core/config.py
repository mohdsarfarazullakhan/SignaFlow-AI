from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = "SignaFlow AI"
    app_env: str = os.getenv("APP_ENV", "development")
    demo_mode: bool = _as_bool(os.getenv("DEMO_MODE"), True)
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{(PROJECT_ROOT / 'backend' / 'signaflow.db').as_posix()}")
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", str(PROJECT_ROOT / "data" / "vector_db"))
    jwt_secret: str = os.getenv("JWT_SECRET", "development-only-change-me")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    groq_api_key: str | None = os.getenv("GROQ_API_KEY") or None
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    groq_fast_model: str = os.getenv("GROQ_FAST_MODEL", "llama-3.1-8b-instant")
    groq_reasoning_model: str = os.getenv("GROQ_REASONING_MODEL", "llama-3.3-70b-versatile")
    catalog_allowed_hosts: tuple[str, ...] = tuple(
        value.strip().lower()
        for value in os.getenv("CATALOG_ALLOWED_HOSTS", "").split(",")
        if value.strip()
    )
    n8n_webhook_url: str | None = os.getenv("N8N_WEBHOOK_URL") or None
    cors_origins: tuple[str, ...] = tuple(
        value.strip()
        for value in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
        if value.strip()
    )

    @property
    def vector_path(self) -> Path:
        return Path(self.vector_db_path).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
