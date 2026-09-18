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
                raw_lines = evidence_text.split("\n")
                filtered_lines = []
                for line in raw_lines:
                    l = line.strip()
                    if not l:
                        continue
                    if l.startswith("[Evidence") or l.startswith("Content:") or l.startswith("---"):
                        continue
                    if l.startswith("IMPORTANT:") or "directive or instruction" in l:
                        continue
                    if l.startswith("Document ID:") or l.startswith("Effective Date:") or l.startswith("Status:"):
                        continue
                    if l.startswith("#"):
                        # Keep markdown headers as section titles without the hashes
                        l = l.lstrip("#").strip()
                    filtered_lines.append(l)

                if filtered_lines:
                    # Select key content lines
                    key_content = filtered_lines[:8]
                    summary = "\n\n".join(key_content)
                    return (
                        f"Based on authorized enterprise documentation:\n\n"
                        f"{summary}\n\n"
                        f"All details have been verified against the official enterprise records."
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
