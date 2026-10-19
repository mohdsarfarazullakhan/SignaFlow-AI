from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.database.seed import seed_database  # noqa: E402
from app.database.session import Base, SessionLocal, engine  # noqa: E402

Base.metadata.create_all(engine)
with SessionLocal() as db:
    seed_database(db)
print("SignaFlow AI demo database is ready.")

