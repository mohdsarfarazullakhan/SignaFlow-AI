from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / "scripts" / "seed_database.py")], check=True)
print("Demo setup complete. Start the API from backend with: uvicorn app.main:app --reload")

