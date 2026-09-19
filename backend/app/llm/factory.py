import logging
from backend.app.core.config import settings
from backend.app.llm.base import LLMProvider
from backend.app.llm.openai_provider import OpenAIProvider
from backend.app.llm.groq_provider import GroqProvider
from backend.app.llm.mock_provider import MockProvider

logger = logging.getLogger("veritas.llm")

def get_llm_provider(allow_mock_fallback: bool = True) -> LLMProvider:
    """Instantiate and return the configured LLMProvider based on AI_PROVIDER in settings.
    Validates configuration per specifications without printing keys.
    Supported providers: 'groq', 'openai', 'mock'.
    """
    provider_type = settings.AI_PROVIDER.lower().strip()

    if provider_type == "groq":
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip():
            return GroqProvider()
        elif allow_mock_fallback:
            logger.info("GROQ_API_KEY not found in .env; initializing local provider emulation for Groq.")
            return MockProvider(provider_name="groq", model_name=f"{settings.GROQ_MODEL} (Local Emulation)")
        else:
            raise ValueError("GROQ_API_KEY is not configured in .env.")

    elif provider_type == "openai":
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
            return OpenAIProvider()
        elif allow_mock_fallback:
            logger.info("OPENAI_API_KEY not found in .env; initializing local provider emulation for OpenAI.")
            return MockProvider(provider_name="openai", model_name=f"{settings.OPENAI_MODEL} (Local Emulation)")
        else:
            raise ValueError("OPENAI_API_KEY is not configured in .env.")

    elif provider_type == "mock":
        return MockProvider(provider_name="mock", model_name="Mock Grounded Engine")

    elif provider_type == "grok":
        # Deprecated: graceful fallback to GrokProvider if configured or MockProvider
        try:
            from backend.app.llm.grok_provider import GrokProvider
            if settings.GROK_API_KEY and settings.GROK_API_KEY.strip():
                return GrokProvider()
        except ImportError:
            pass
        if allow_mock_fallback:
            logger.info("Deprecated grok provider unconfigured; using local MockProvider.")
            return MockProvider(provider_name="grok", model_name=f"{settings.GROK_MODEL} (Local Emulation)")
        else:
            raise ValueError("GROK_API_KEY is not configured in .env.")

    else:
        raise ValueError(f"Unknown AI_PROVIDER: '{settings.AI_PROVIDER}'. Must be 'groq', 'openai', or 'mock'.")
