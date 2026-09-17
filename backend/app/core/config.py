import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Project root resolution:
# config.py is at backend/app/core/config.py -> 3 levels up is backend, 4 levels is Veritas root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    # Required .env settings per spec (Part 5)
    AI_PROVIDER: str = "openai"
    GROK_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Centralized Model names (Part 5)
    OPENAI_MODEL: str = "gpt-4o-mini"
    GROK_MODEL: str = "grok-2-latest"
    GROK_BASE_URL: str = "https://api.x.ai/v1"

    # Internal application settings
    APP_NAME: str = "Veritas Enterprise Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = "veritas-super-secret-jwt-key-demo-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours for demo session
    DATABASE_URL: str = f"sqlite:///{ROOT_DIR / 'veritas.db'}"
    SEED_DATA_DIR: Path = ROOT_DIR / "data" / "seed"
    UPLOADS_DIR: Path = ROOT_DIR / "data" / "uploads"

    # RAG defaults per spec (Part 4)
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    ANN_TOP_K: int = 40
    RERANK_TOP_K: int = 8
    SIMILARITY_THRESHOLD: float = 0.25

    # Agent Limits per spec (Part 6)
    MAX_TOOL_CALLS: int = 10
    MAX_AGENT_STEPS: int = 8

    model_config = {
        "env_file": str(ENV_FILE),
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()

def validate_provider_keys() -> dict:
    """Validate that the active AI_PROVIDER has an API key configured.
    Does NOT print or return the API key.
    """
    provider = settings.AI_PROVIDER.lower().strip()
    if provider == "openai":
        has_key = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())
        return {"provider": "openai", "configured": has_key, "model": settings.OPENAI_MODEL}
    elif provider == "grok":
        has_key = bool(settings.GROK_API_KEY and settings.GROK_API_KEY.strip())
        return {"provider": "grok", "configured": has_key, "model": settings.GROK_MODEL}
    else:
        return {"provider": provider, "configured": False, "error": f"Unsupported AI_PROVIDER: '{provider}'. Must be 'openai' or 'grok'."}
