import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.tools.base import EnterpriseTool
from backend.app.retrieval.tenant_store import TenantKnowledgeStore
from backend.app.retrieval.query_expander import expand_query_for_retrieval
from backend.app.reranking.model import get_reranker
from backend.app.core.config import settings

logger = logging.getLogger("veritas.rag.knowledge")

class SearchEnterpriseKnowledgeTool(EnterpriseTool):
    name = "search_enterprise_knowledge"
    description = (
        "Search the organization's private knowledge base for authorized policies, "
        "contracts, guidelines, and reports using semantic vector retrieval and XGBoost reranking."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The specific factual question or search query."
            },
            "top_k": {
                "type": "integer",
                "description": "Number of evidence chunks to return (default: 6).",
                "default": 6
            }
        },
        "required": ["query"]
    }

    def execute(self, user: User, tenant_id: str, db: Session, **kwargs) -> Dict[str, Any]:
        query = kwargs.get("query", "").strip()
        top_k = kwargs.get("top_k", 6)

        if not query:
            return {"error": "Query cannot be empty.", "results": []}

        expanded_query = expand_query_for_retrieval(query)
        logger.info(f"Knowledge Search query='{query}' | expanded='{expanded_query}' | role='{user.role}'")

        tenant_store = TenantKnowledgeStore(tenant_id=tenant_id)
        # ANN retrieval (30-40 candidates)
        candidates = tenant_store.search_authorized(
            query=query,
            user_role=user.role,
            top_k=settings.ANN_TOP_K
        )

        logger.info(f"ANN candidates retrieved: {len(candidates)}")
        top_ann = [(c.title, round(c.score, 4)) for c in candidates[:5]]
        logger.info(f"Top 5 ANN candidates (title, sim): {top_ann}")

        if not candidates:
            logger.info(f"No authorized evidence found matching query: '{query}'")
            return {
                "query": query,
                "found_count": 0,
                "results": [],
                "message": "No authorized evidence found matching the query in this tenant."
            }

        # XGBoost reranking
        reranker = get_reranker()
        reranked = reranker.rerank(query=query, candidates=candidates, top_k=top_k)
        top_rerank = [(c.title, round(score, 4), round(c.score, 4)) for c, score in reranked[:5]]
        logger.info(f"Top 5 Reranked (title, rerank_score, sim_score): {top_rerank} (reranker_active={reranker.is_trained})")

        results = []
        for cand, score in reranked:
            results.append({
                "chunk_id": cand.chunk_id,
                "document_id": cand.document_id,
                "title": cand.title,
                "department": cand.department,
                "document_type": cand.document_type,
                "version": cand.version,
                "effective_date": cand.effective_date,
                "page": cand.page,
                "section": cand.section,
                "similarity_score": round(cand.score, 4),
                "rerank_score": round(score, 4),
                "text": cand.text
            })

        return {
            "query": query,
            "found_count": len(results),
            "reranker_active": reranker.is_trained,
            "results": results
        }

