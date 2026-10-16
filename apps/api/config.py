import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "Verified Course Material Studio API"
    VERSION: str = "1.0.0"
    
    # LLM Settings
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    
    # Sandbox Settings
    SANDBOX_TIMEOUT_SEC: int = int(os.getenv("SANDBOX_TIMEOUT_SEC", "30"))
    SANDBOX_MEMORY_MB: int = int(os.getenv("SANDBOX_MEMORY_MB", "512"))
    MAX_FIX_ATTEMPTS: int = int(os.getenv("MAX_FIX_ATTEMPTS", "3"))
    
    # Storage Paths
    DATA_DIR: Path = BASE_DIR / os.getenv("DATA_DIR", "data")
    SCHEMA_FILE: Path = BASE_DIR / "schema" / "deck.schema.json"
    SAMPLES_DIR: Path = BASE_DIR / "samples"
    
    # Server Settings
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
