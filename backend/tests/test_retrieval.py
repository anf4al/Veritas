import pytest
from backend.app.core.database import SessionLocal
from backend.app.models.company import Company
from backend.app.retrieval.tenant_store import TenantKnowledgeStore
from backend.app.reranking.model import get_reranker

def test_tenant_retrieval_and_reranking():
    db = SessionLocal()
    asterion = db.query(Company).filter(Company.slug == "asterion").first()
    assert asterion is not None

    tenant_store = TenantKnowledgeStore(tenant_id=asterion.id)
    candidates = tenant_store.search_authorized(
        query="What is the current WFH policy?",
        user_role="EMPLOYEE",
        top_k=20
    )
    assert len(candidates) > 0

    # Ensure all retrieved candidates belong to Asterion
    for c in candidates:
        assert c.tenant_id == asterion.id

    # Test reranking
    reranker = get_reranker()
    reranked = reranker.rerank("What is the current WFH policy?", candidates, top_k=5)
    assert len(reranked) > 0
    top_chunk, score = reranked[0]
    assert score > 0.0
    assert top_chunk.tenant_id == asterion.id
    db.close()

