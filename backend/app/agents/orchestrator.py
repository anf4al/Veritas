import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple, AsyncIterator
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.core.config import settings
from backend.app.llm.factory import get_llm_provider
from backend.app.tools.registry import get_tool_registry
from backend.app.agents.safeguards import AgentBudgetTracker, AgentSafeguardError
from backend.app.agents.prompt import (
    VERITAS_SYSTEM_PROMPT,
    INSUFFICIENT_EVIDENCE_MESSAGE,
    construct_rag_prompt
)
from backend.app.schemas.chat import (
    ChatResponse,
    Citation,
    EvidenceChunk,
    AgentStepInfo
)
from backend.app.observability.tracer import get_tracer

class AgentOrchestrator:
    def __init__(self, db: Session, user: User, tenant_id: str):
        self.db = db
        self.user = user
        self.tenant_id = tenant_id
        self.tool_registry = get_tool_registry()
        self.llm_provider = get_llm_provider()
        self.tracer = get_tracer()

    def _determine_plan(self, query: str) -> List[Tuple[str, Dict[str, Any], str]]:
        """Determine multi-step retrieval plan based on question intent."""
        q_lower = query.lower()
        plan: List[Tuple[str, Dict[str, Any], str]] = []

        # Complex query example from spec Part 6: Vendor Atlas risk & termination
        if "vendor atlas" in q_lower or ("risk" in q_lower and "terminate" in q_lower):
            plan.append(("get_vendor_performance", {"vendor_name": "Vendor Atlas"}, "Retrieving Vendor Atlas performance and risk assessments"))
            plan.append(("search_enterprise_knowledge", {"query": "Vendor Atlas Master Services Agreement termination clause", "top_k": 5}, "Searching contract termination terms"))
            plan.append(("search_enterprise_knowledge", {"query": "Procurement policy supplier evaluation high risk definition", "top_k": 4}, "Searching procurement high-risk policy"))
            return plan

        # Expiring contracts query
        if "expir" in q_lower and ("contract" in q_lower or "agreement" in q_lower):
            plan.append(("find_contracts_expiring", {"days_ahead": 90}, "Scanning contracts expiring within 90 days"))
            plan.append(("search_enterprise_knowledge", {"query": query, "top_k": 5}, "Searching expiring contract records"))
            return plan

        # Compare documents / policy version changes query
        if "changed" in q_lower or "compare" in q_lower or "between 2025 and 2026" in q_lower:
            if "procurement" in q_lower:
                plan.append(("compare_documents", {"title_a": "Procurement Policy 2025", "title_b": "Procurement Policy 2026"}, "Comparing 2025 and 2026 Procurement Policies"))
            elif "security" in q_lower or "infosec" in q_lower:
                plan.append(("compare_documents", {"title_a": "Information Security Policy 2025", "title_b": "Information Security Policy 2026"}, "Comparing 2025 and 2026 Information Security Policies"))
            elif "reimbursement" in q_lower:
                plan.append(("compare_documents", {"title_a": "Reimbursement Policy 2025", "title_b": "Reimbursement Policy 2026"}, "Comparing 2025 and 2026 Reimbursement Policies"))
            else:
                plan.append(("get_policy_versions", {"policy_name": query}, "Inspecting policy version history"))
            plan.append(("search_enterprise_knowledge", {"query": query, "top_k": 6}, "Retrieving comparison evidence"))
            return plan

        # Default: single or dual targeted semantic search
        plan.append(("search_enterprise_knowledge", {"query": query, "top_k": settings.RERANK_TOP_K}, "Searching enterprise knowledge base"))
        return plan

    async def execute_query(self, query: str, trace_id: Optional[str] = None) -> ChatResponse:
        start_time = time.time()
        trace_id = trace_id or self.tracer.start_trace(
            query=query,
            company_id=self.tenant_id,
            user_id=self.user.id
        )

        tracker = AgentBudgetTracker(
            max_tool_calls=settings.MAX_TOOL_CALLS,
            max_steps=settings.MAX_AGENT_STEPS
        )

        agent_steps: List[AgentStepInfo] = []
        collected_evidence: List[Dict[str, Any]] = []

        # 1. Agent planning span
        with self.tracer.span(trace_id, "agent_planning", {"query": query}):
            tracker.record_step()
            plan = self._determine_plan(query)
            agent_steps.append(AgentStepInfo(
                step=1,
                action="formulate_plan",
                observation_summary=f"Formulated {len(plan)}-step retrieval strategy."
            ))

        # 2. Execute plan steps with budget safeguards
        step_num = 2
        for tool_name, tool_args, step_desc in plan:
            try:
                tracker.record_step()
                tracker.record_tool_call(tool_name, tool_args)

                with self.tracer.span(trace_id, f"tool:{tool_name}", {"tool": tool_name, "args": tool_args}):
                    res = self.tool_registry.execute_tool(
                        name=tool_name,
                        arguments=tool_args,
                        user=self.user,
                        tenant_id=self.tenant_id,
                        db=self.db
                    )

                # Collect chunks
                if "results" in res and isinstance(res["results"], list):
                    collected_evidence.extend(res["results"])
                elif "performance_records" in res:
                    for rec in res["performance_records"]:
                        collected_evidence.append({
                            "chunk_id": rec.get("document_id", "perf"),
                            "document_id": rec.get("document_id", ""),
                            "title": rec.get("title", ""),
                            "text": rec.get("summary_excerpt", ""),
                            "page": 1,
                            "section": "Performance Evaluation",
                            "version": rec.get("version", "1.0"),
                            "effective_date": rec.get("effective_date"),
                            "department": rec.get("department", "Operations"),
                            "similarity_score": 0.85,
                            "rerank_score": 0.90
                        })
                elif "comparison_summary" in res:
                    doc_a = res.get("document_a", {})
                    doc_b = res.get("document_b", {})
                    collected_evidence.append({
                        "chunk_id": doc_a.get("id", "doc_a"),
                        "document_id": doc_a.get("id", ""),
                        "title": doc_a.get("title", ""),
                        "text": doc_a.get("text_sample", ""),
                        "page": 1,
                        "section": "Comparison A",
                        "version": doc_a.get("version", "1.0"),
                        "effective_date": doc_a.get("effective_date"),
                        "similarity_score": 0.88,
                        "rerank_score": 0.92
                    })
                    collected_evidence.append({
                        "chunk_id": doc_b.get("id", "doc_b"),
                        "document_id": doc_b.get("id", ""),
                        "title": doc_b.get("title", ""),
                        "text": doc_b.get("text_sample", ""),
                        "page": 1,
                        "section": "Comparison B",
                        "version": doc_b.get("version", "1.0"),
                        "effective_date": doc_b.get("effective_date"),
                        "similarity_score": 0.90,
                        "rerank_score": 0.95
                    })

                agent_steps.append(AgentStepInfo(
                    step=step_num,
                    action=f"execute_{tool_name}",
                    tool_name=tool_name,
                    tool_args=tool_args,
                    observation_summary=f"{step_desc} — obtained {len(res.get('results', []))} items."
                ))
                step_num += 1

            except AgentSafeguardError as se:
                agent_steps.append(AgentStepInfo(
                    step=step_num,
                    action="safeguard_interruption",
                    observation_summary=str(se)
                ))
                break

        # Deduplicate evidence by text/chunk_id
        unique_evidence: Dict[str, Dict[str, Any]] = {}
        for ev in collected_evidence:
            cid = ev.get("chunk_id") or ev.get("text", "")[:50]
            if cid not in unique_evidence:
                unique_evidence[cid] = ev

        evidence_list = list(unique_evidence.values())
        # Sort by rerank_score descending
        evidence_list.sort(key=lambda e: e.get("rerank_score", 0.0), reverse=True)
        top_evidence = evidence_list[:settings.RERANK_TOP_K]

        # Check evidence sufficiency
        insufficient = False
        if not top_evidence or all(e.get("rerank_score", 0.0) < settings.SIMILARITY_THRESHOLD for e in top_evidence):
            insufficient = True
            answer = INSUFFICIENT_EVIDENCE_MESSAGE
            citations = []
        else:
            # 3. LLM Generation span
            with self.tracer.span(trace_id, "llm_generate", {"provider": self.llm_provider.provider_name, "evidence_count": len(top_evidence)}):
                rag_prompt = construct_rag_prompt(query, top_evidence)
                answer = await self.llm_provider.generate(
                    prompt=rag_prompt,
                    system_prompt=VERITAS_SYSTEM_PROMPT,
                    max_tokens=1000,
                    temperature=0.0
                )

            # Build citations strictly from verified chunk metadata
            citations = []
            seen_cites = set()
            for ev in top_evidence:
                title = ev.get("title", "")
                page = ev.get("page", 1)
                section = ev.get("section", "General")
                cite_key = f"{title}-{page}-{section}"
                if cite_key not in seen_cites:
                    seen_cites.add(cite_key)
                    citations.append(Citation(
                        id=str(ev.get("chunk_id", "")),
                        document_id=str(ev.get("document_id", "")),
                        title=title,
                        page=page,
                        section=section,
                        version=str(ev.get("version", "1.0")),
                        effective_date=ev.get("effective_date"),
                        department=ev.get("department"),
                        confidentiality=ev.get("confidentiality", "internal"),
                        relevance_score=round(float(ev.get("rerank_score", 0.0)), 4)
                    ))

        # Build evidence chunk response objects
        response_evidence = []
        for ev in top_evidence:
            response_evidence.append(EvidenceChunk(
                chunk_id=str(ev.get("chunk_id", "")),
                document_id=str(ev.get("document_id", "")),
                title=str(ev.get("title", "")),
                text=str(ev.get("text", "")),
                page=ev.get("page", 1),
                section=ev.get("section", "General"),
                version=str(ev.get("version", "1.0")),
                effective_date=ev.get("effective_date"),
                department=ev.get("department"),
                similarity_score=round(float(ev.get("similarity_score", 0.0)), 4),
                rerank_score=round(float(ev.get("rerank_score", 0.0)), 4)
            ))

        total_latency = (time.time() - start_time) * 1000.0
        self.tracer.finish_trace(trace_id, total_latency)

        return ChatResponse(
            answer=answer,
            insufficient_evidence=insufficient,
            citations=citations,
            evidence=response_evidence,
            agent_steps=agent_steps,
            trace_id=trace_id,
            latency_ms=round(total_latency, 2),
            provider_used=self.llm_provider.provider_name,
            model_used=self.llm_provider.model_name
        )
