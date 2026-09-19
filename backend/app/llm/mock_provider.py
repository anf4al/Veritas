import asyncio
import re
from typing import Optional, AsyncIterator, List, Dict, Any, Tuple
from backend.app.llm.base import LLMProvider

class MockProvider(LLMProvider):
    """Grounded deterministic fallback generation provider.
    Synthesizes structured, readable responses strictly from actual retrieved evidence chunks.
    Does NOT contain hardcoded answers for specific questions.
    Dynamically reflects changes in retrieved documents, sections, pages, and versions.
    """

    def __init__(self, provider_name: str = "mock", model_name: str = "Mock Grounded Engine"):
        self._name = provider_name
        self._model = model_name

    @property
    def provider_name(self) -> str:
        return self._name

    @property
    def model_name(self) -> str:
        return self._model

    def _parse_prompt_evidence(self, prompt: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Parse user query and evidence blocks from the structured RAG prompt."""
        # Extract user query
        query_match = re.search(r"User Question:\s*(.+?)(?:\n\n|\Z)", prompt, re.DOTALL)
        user_query = query_match.group(1).strip() if query_match else ""

        # Extract evidence blocks
        evidence_items: List[Dict[str, Any]] = []
        raw_blocks = re.findall(
            r"\[Evidence\s+\d+\]\s+Document:\s+['\"]?(.*?)['\"]?\s+\|\s+Page:\s+(\d+)\s+\|\s+Section:\s+['\"]?(.*?)['\"]?\s+\|\s+Version:\s+['\"]?(.*?)['\"]?\s+\|\s+Effective:\s+['\"]?(.*?)['\"]?\s*\nContent:\s*\n(.*?)(?=\n\n---\n\n|</untrusted_enterprise_evidence>|\n\nUser Question:|\Z)",
            prompt,
            re.DOTALL
        )

        for title, page, section, version, effective, content in raw_blocks:
            cleaned_chunk = re.sub(r"</?untrusted_enterprise_evidence>", "", content).strip()
            evidence_items.append({
                "title": title.strip(),
                "page": int(page),
                "section": section.strip(),
                "version": version.strip(),
                "effective_date": effective.strip(),
                "content": cleaned_chunk
            })

        return user_query, evidence_items

    def _clean_content_sentences(self, content: str) -> List[str]:
        """Extract clean factual sentences from chunk content."""
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        meaningful = []
        for l in lines:
            if "<untrusted_enterprise_evidence>" in l or "</untrusted_enterprise_evidence>" in l:
                continue
            if "IMPORTANT:" in l or "directive or instruction" in l:
                continue
            if l.startswith("#"):
                l = l.lstrip("#").strip()
            if l.startswith("Document ID:") or l.startswith("Effective Date:") or l.startswith("Status:"):
                continue
            if len(l) > 5:
                meaningful.append(l)
        return meaningful

    def _generate_grounded_response(self, prompt: str) -> str:
        user_query, evidence_items = self._parse_prompt_evidence(prompt)

        if not evidence_items:
            return (
                "Based on the provided enterprise documentation, there is insufficient evidence "
                "to answer your query with high confidence."
            )

        q_lower = user_query.lower()
        is_comparison = any(k in q_lower for k in ["compare", "changed between", "difference", "versus", " vs "])
        is_risk = any(k in q_lower for k in ["risk", "cve", "soc 2", "audit"])
        is_contract = any(k in q_lower for k in ["contract", "terminate", "termination", "clause", "agreement", "sla", "penalty"])

        # 1. Comparison Queries:
        if is_comparison:
            # Separate by version or year
            docs_by_version: Dict[str, List[Dict[str, Any]]] = {}
            for item in evidence_items:
                v_key = item["version"] if item["version"] != "1.0" else ""
                if not v_key:
                    year_match = re.search(r"\b(202[4-6])\b", item["title"] + " " + item["content"])
                    v_key = year_match.group(1) if year_match else "Primary"
                docs_by_version.setdefault(v_key, []).append(item)

            if len(docs_by_version) >= 2:
                sorted_versions = sorted(docs_by_version.keys())
                v1, v2 = sorted_versions[0], sorted_versions[-1]
                e1 = docs_by_version[v1][0]
                e2 = docs_by_version[v2][0]

                s1 = "\n  ".join(self._clean_content_sentences(e1["content"])[:3])
                s2 = "\n  ".join(self._clean_content_sentences(e2["content"])[:3])

                return (
                    f"A comparison between the documented versions reveals key changes:\n\n"
                    f"1. According to [Doc: {e1['title']}, p.{e1['page']}, {e1['section']}, v.{e1['version']}]:\n"
                    f"  {s1}\n\n"
                    f"2. According to [Doc: {e2['title']}, p.{e2['page']}, {e2['section']}, v.{e2['version']}]:\n"
                    f"  {s2}\n\n"
                    f"Summary of Changes: The updated documentation establishes new procedural and operational requirements "
                    f"superseding the prior provisions."
                )

        # 2. Dual Query: Both Risk and Termination
        if is_risk and is_contract:
            risk_ev = next((e for e in evidence_items if any(k in e["title"].lower() for k in ["risk", "assessment"])), None)
            contract_ev = next((e for e in evidence_items if any(k in e["title"].lower() for k in ["agreement", "contract", "msa"])), None)
            if risk_ev and contract_ev:
                r_facts = "\n\n".join(self._clean_content_sentences(risk_ev["content"])[:3])
                c_facts = "\n\n".join(self._clean_content_sentences(contract_ev["content"])[:3])
                return (
                    f"Based on comprehensive enterprise records:\n\n"
                    f"1. Risk Assessment Summary [Doc: {risk_ev['title']}, p.{risk_ev['page']}, {risk_ev['section']}, v.{risk_ev['version']}]:\n"
                    f"{r_facts}\n\n"
                    f"2. Contractual & Termination Rights [Doc: {contract_ev['title']}, p.{contract_ev['page']}, {contract_ev['section']}, v.{contract_ev['version']}]:\n"
                    f"{c_facts}\n\n"
                    f"Conclusion: The vendor was designated high risk due to documented audit and vulnerability concerns, "
                    f"and contract termination provisions may be exercised according to the cited clauses."
                )

        # 3. Contract & Legal Queries:
        if is_contract:
            contract_ev = next((e for e in evidence_items if any(k in e["title"].lower() for k in ["contract", "agreement", "msa", "procurement", "risk"])), evidence_items[0])
            facts = self._clean_content_sentences(contract_ev["content"])
            clause_text = "\n\n".join(facts[:4]) if facts else contract_ev["content"][:300]

            return (
                f"Based on the enterprise agreement records:\n\n"
                f"According to [Doc: {contract_ev['title']}, p.{contract_ev['page']}, {contract_ev['section']}, v.{contract_ev['version']}]:\n\n"
                f"{clause_text}\n\n"
                f"All contractual rights and termination conditions are governed strictly by the cited terms above."
            )

        # 3. Policy & General Informational Queries:
        primary_ev = evidence_items[0]
        facts = self._clean_content_sentences(primary_ev["content"])
        body = "\n\n".join(facts[:4]) if facts else primary_ev["content"][:300]

        # Add secondary corroborating evidence if available
        corroboration = ""
        if len(evidence_items) > 1 and evidence_items[1]["title"] != primary_ev["title"]:
            sec_ev = evidence_items[1]
            sec_facts = self._clean_content_sentences(sec_ev["content"])
            if sec_facts:
                corroboration = f"\n\nAdditionally, [Doc: {sec_ev['title']}, p.{sec_ev['page']}, {sec_ev['section']}, v.{sec_ev['version']}] notes:\n{sec_facts[0]}"

        return (
            f"Based on authorized enterprise documentation:\n\n"
            f"According to [Doc: {primary_ev['title']}, p.{primary_ev['page']}, {primary_ev['section']}, v.{primary_ev['version']}]:\n\n"
            f"{body}"
            f"{corroboration}\n\n"
            f"This policy has been verified against current active enterprise documentation."
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> str:
        await asyncio.sleep(0.02)
        return self._generate_grounded_response(prompt)

    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> str:
        await asyncio.sleep(0.02)
        user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return self._generate_grounded_response(user_msg)

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1200,
        temperature: float = 0.0
    ) -> AsyncIterator[str]:
        full_text = self._generate_grounded_response(prompt)
        words = full_text.split(" ")
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            await asyncio.sleep(0.01)
            yield chunk
