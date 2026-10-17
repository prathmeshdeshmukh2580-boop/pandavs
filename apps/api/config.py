import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "Verified Course Material Studio API"
    VERSION: str = "1.0.0"

    # ── LLM Settings ────────────────────────────────────────────────────────────
    # Primary: Google Gemini (free tier, fast)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str   = os.getenv("GEMINI_MODEL", "models/gemini-3.8-flash")

    # Secondary fallback: Anthropic Claude
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str      = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    # ── Sandbox ──────────────────────────────────────────────────────────────────
    SANDBOX_TIMEOUT_SEC: int = int(os.getenv("SANDBOX_TIMEOUT_SEC", "30"))
    SANDBOX_MEMORY_MB: int   = int(os.getenv("SANDBOX_MEMORY_MB", "512"))
    MAX_FIX_ATTEMPTS: int    = int(os.getenv("MAX_FIX_ATTEMPTS", "3"))

    # ── Storage ───────────────────────────────────────────────────────────────────
    DATA_DIR: Path    = BASE_DIR / os.getenv("DATA_DIR", "data")
    SCHEMA_FILE: Path = BASE_DIR / "schema" / "deck.schema.json"
    SAMPLES_DIR: Path = BASE_DIR / "samples"

    # ── Server ────────────────────────────────────────────────────────────────────
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

# Module-level aliases kept for backward compatibility
SCHEMA_PATH  = settings.SCHEMA_FILE
SAMPLES_DIR  = settings.SAMPLES_DIR
DATA_DIR     = settings.DATA_DIR
