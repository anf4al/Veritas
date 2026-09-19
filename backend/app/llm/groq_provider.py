import asyncio
import re
from typing import Optional, AsyncIterator, List, Dict
import httpx
from openai import AsyncOpenAI, APIError, APITimeoutError, AuthenticationError, RateLimitError, NotFoundError
from backend.app.core.config import settings
from backend.app.llm.base import LLMProvider

def sanitize_error_message(msg: str, key: Optional[str] = None) -> str:
    """Strip any accidental credential or key substring from error messages."""
    if not msg:
        return "Unknown error"
    if key and len(key) > 6:
        msg = msg.replace(key, "[REDACTED_API_KEY]")
    # Redact common key prefixes
    msg = re.sub(r"gsk_[A-Za-z0-9_\-]+", "[REDACTED_API_KEY]", msg)
    msg = re.sub(r"xai-[A-Za-z0-9_\-]+", "[REDACTED_API_KEY]", msg)
    msg = re.sub(r"sk-[A-Za-z0-9_\-]+", "[REDACTED_API_KEY]", msg)
    return msg

class GroqProvider(LLMProvider):
    """Production provider for Groq ultra-low latency inference using OpenAI-compatible client."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self._api_key = api_key or settings.GROQ_API_KEY
        self._model = model or settings.GROQ_MODEL
        self._base_url = base_url or settings.GROQ_BASE_URL
        if self._api_key:
            self._client = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=30.0
            )
        else:
            self._client = None

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return self._model

    def _ensure_client(self):
        if not self._client or not self._api_key or not self._api_key.strip():
            raise RuntimeError("Groq API key is missing or not configured in .env (GROQ_API_KEY).")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> str:
        self._ensure_client()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return await self.generate_chat(messages, max_tokens=max_tokens, temperature=temperature)

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> str:
        self._ensure_client()
        retries = 2
        for attempt in range(retries + 1):
            try:
                response = await self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content or ""
            except AuthenticationError as e:
                clean_msg = sanitize_error_message(str(e.message), self._api_key)
                raise RuntimeError(f"Groq authentication error: {clean_msg}")
            except NotFoundError as e:
                clean_msg = sanitize_error_message(str(e.message), self._api_key)
                raise RuntimeError(f"Groq model unavailable: {clean_msg}")
            except RateLimitError as e:
                if attempt < retries:
                    await asyncio.sleep(1.5 * (attempt + 1))
                    continue
                clean_msg = sanitize_error_message(str(e.message), self._api_key)
                raise RuntimeError(f"Groq rate limit exceeded: {clean_msg}")
            except (APITimeoutError, httpx.RequestError) as e:
                if attempt < retries:
                    await asyncio.sleep(1.0 * (attempt + 1))
                    continue
                clean_msg = sanitize_error_message(str(e), self._api_key)
                raise RuntimeError(f"Groq service timeout / network error: {clean_msg}")
            except APIError as e:
                clean_msg = sanitize_error_message(e.message, self._api_key)
                raise RuntimeError(f"Groq API error: {clean_msg}")

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> AsyncIterator[str]:
        self._ensure_client()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else ""
                if delta:
                    yield delta
        except AuthenticationError as e:
            clean_msg = sanitize_error_message(str(e.message), self._api_key)
            raise RuntimeError(f"Groq authentication error: {clean_msg}")
        except RateLimitError as e:
            clean_msg = sanitize_error_message(str(e.message), self._api_key)
            raise RuntimeError(f"Groq rate limit exceeded: {clean_msg}")
        except APIError as e:
            clean_msg = sanitize_error_message(e.message, self._api_key)
            raise RuntimeError(f"Groq streaming API error: {clean_msg}")

