"""Central configuration. Everything comes from environment variables (.env)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Repo root: apps/api/config.py -> parents[2]. Same layout is mirrored inside the API container.
REPO_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(REPO_ROOT / ".env")

SCHEMA_PATH = Path(os.getenv("SCHEMA_PATH", REPO_ROOT / "schema" / "deck.schema.json"))
SAMPLES_DIR = REPO_ROOT / "samples"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "")

SANDBOX_TIMEOUT_SEC = int(os.getenv("SANDBOX_TIMEOUT_SEC", "60"))
SANDBOX_MEMORY_MB = int(os.getenv("SANDBOX_MEMORY_MB", "512"))
MAX_FIX_ATTEMPTS = int(os.getenv("MAX_FIX_ATTEMPTS", "3"))

_data_dir = Path(os.getenv("DATA_DIR", "./data"))
DATA_DIR = _data_dir if _data_dir.is_absolute() else (REPO_ROOT / _data_dir).resolve()

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
