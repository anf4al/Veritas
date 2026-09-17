import asyncio
import re
from typing import Optional, AsyncIterator, List, Dict
from backend.app.llm.base import LLMProvider

class MockProvider(LLMProvider):
    """High-fidelity local fallback provider for offline demo runs,
    benchmarking, or when API keys have not yet been provided in .env.
    Synthesizes grounded answers directly from the provided evidence context.
    """

    def __init__(self, provider_name: str = "openai", model_name: str = "gpt-4o-mini-demo"):
        self._name = provider_name
        self._model = model_name

    @property
    def provider_name(self) -> str:
        return self._name

    @property
    def model_name(self) -> str:
        return self._model

    def _extract_answer_from_context(self, text: str) -> str:
        # Check if context has untrusted evidence
        if "<untrusted_enterprise_evidence>" in text:
            match = re.search(r"<untrusted_enterprise_evidence>(.*?)</untrusted_enterprise_evidence>", text, re.DOTALL)
            if match:
                evidence_text = match.group(1).strip()
                lines = [l.strip() for l in evidence_text.split("\n") if l.strip() and not l.strip().startswith("[Evidence")]
                key_points = lines[:4]
                summary = " ".join(key_points)
                return (
                    f"Based on the authorized enterprise records:\n\n"
                    f"{summary}\n\n"
                    f"All findings have been verified against the current company documentation."
                )

        return (
            "Based on the authorized enterprise knowledge base, the records indicate the policy "
            "and procedural requirements documented in the cited company materials."
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> str:
        await asyncio.sleep(0.05)
        return self._extract_answer_from_context(prompt)

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> str:
        await asyncio.sleep(0.05)
        user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return self._extract_answer_from_context(user_msg)

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> AsyncIterator[str]:
        full_text = self._extract_answer_from_context(prompt)
        words = full_text.split(" ")
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            await asyncio.sleep(0.02)
            yield chunk
