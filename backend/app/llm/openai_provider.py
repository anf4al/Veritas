import asyncio
from typing import Optional, AsyncIterator, List, Dict
import httpx
from openai import AsyncOpenAI, APIError, APITimeoutError
from backend.app.core.config import settings
from backend.app.llm.base import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key or settings.OPENAI_API_KEY
        self._model = model or settings.OPENAI_MODEL
        if self._api_key:
            self._client = AsyncOpenAI(api_key=self._api_key, timeout=30.0)
        else:
            self._client = None

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    def _ensure_client(self):
        if not self._client:
            raise RuntimeError("OpenAI API key is missing or not configured in .env.")

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
        # Bounded retry for transient rate limits or timeouts
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
            except (APITimeoutError, httpx.RequestError) as e:
                if attempt < retries:
                    await asyncio.sleep(1.0 * (attempt + 1))
                    continue
                raise RuntimeError(f"OpenAI service timeout: {str(e)}")
            except APIError as e:
                raise RuntimeError(f"OpenAI API error: {e.message}")

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
