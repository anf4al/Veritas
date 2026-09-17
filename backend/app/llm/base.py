from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator, Dict, Any, List

class LLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider: 'openai' or 'grok'."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the model being called."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> str:
        """Generate full text completion."""
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> AsyncIterator[str]:
        """Stream generated text chunks asynchronously."""
        pass

    @abstractmethod
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> str:
        """Generate completion from chat messages list."""
        pass
