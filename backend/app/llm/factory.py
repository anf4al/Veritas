import logging
from backend.app.core.config import settings
from backend.app.llm.base import LLMProvider
from backend.app.llm.openai_provider import OpenAIProvider
from backend.app.llm.grok_provider import GrokProvider
from backend.app.llm.mock_provider import MockProvider

logger = logging.getLogger("veritas.llm")

def get_llm_provider(allow_mock_fallback: bool = True) -> LLMProvider:
    """Instantiate and return the configured LLMProvider based on AI_PROVIDER in settings.
    Validates configuration per Part 5 specifications without printing keys.
    """
    provider_type = settings.AI_PROVIDER.lower().strip()

    if provider_type == "openai":
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
            return OpenAIProvider()
        elif allow_mock_fallback:
            logger.info("OPENAI_API_KEY not found in .env; initializing local provider emulation for OpenAI.")
            return MockProvider(provider_name="openai", model_name=f"{settings.OPENAI_MODEL} (Local Emulation)")
        else:
            raise ValueError("OPENAI_API_KEY is not configured in .env.")

    elif provider_type == "grok":
        if settings.GROK_API_KEY and settings.GROK_API_KEY.strip():
            return GrokProvider()
        elif allow_mock_fallback:
            logger.info("GROK_API_KEY not found in .env; initializing local provider emulation for Grok.")
            return MockProvider(provider_name="grok", model_name=f"{settings.GROK_MODEL} (Local Emulation)")
        else:
            raise ValueError("GROK_API_KEY is not configured in .env.")

    else:
        raise ValueError(f"Unknown AI_PROVIDER: '{settings.AI_PROVIDER}'. Must be 'openai' or 'grok'.")
