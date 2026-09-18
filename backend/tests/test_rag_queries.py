import pytest
import numpy as np
from unittest.mock import patch

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.company import Company
from backend.app.retrieval.tenant_store import TenantKnowledgeStore
from backend.app.retrieval.query_expander import expand_query_for_retrieval
from backend.app.retrieval.embeddings import SentenceTransformerEmbeddingProvider
from backend.app.reranking.model import get_reranker
from backend.app.agents.orchestrator import AgentOrchestrator, evaluate_evidence_sufficiency

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def asterion_context(db_session):
    company = db_session.query(Company).filter(Company.slug == "asterion").first()
    assert company is not None, "Asterion company must exist"
    user = db_session.query(User).filter(User.username == "admin@veritas.demo").first()
    assert user is not None, "Admin user must exist"
    return {"tenant_id": company.id, "user": user}

def test_query_expansion_terms():
    """Verify bidirectional domain query expansion."""
    wfh_exp = expand_query_for_retrieval("What is the current WFH policy?")
    assert "Work From Home" in wfh_exp

    work_exp = expand_query_for_retrieval("What is the current Work From Home policy?")
    assert "WFH" in work_exp

    holiday_exp = expand_query_for_retrieval("How many holidays does one get?")
    assert "annual leave" in holiday_exp.lower() or "statutory" in holiday_exp.lower()

    pto_exp = expand_query_for_retrieval("How does PTO carry forward work?")
    assert "paid time off" in pto_exp.lower() or "annual leave" in pto_exp.lower()

def test_wfh_policy_current_retrieval(asterion_context):
    """'What is the current WFH policy?' retrieves Work From Home Policy 2026 as top result."""
    tenant_id = asterion_context["tenant_id"]
    user = asterion_context["user"]
    store = TenantKnowledgeStore(tenant_id=tenant_id)
    reranker = get_reranker()

    candidates = store.search_authorized(
        query="What is the current WFH policy?",
        user_role=user.role,
        top_k=20
    )
    assert len(candidates) > 0

    reranked = reranker.rerank(query="What is the current WFH policy?", candidates=candidates, top_k=5)
    top_doc = reranked[0][0]
    assert "Work From Home Policy 2026" in top_doc.title

def test_wfh_acronym_equivalence(asterion_context):
    """'What is the current Work From Home policy?' retrieves the same top result."""
    tenant_id = asterion_context["tenant_id"]
    user = asterion_context["user"]
    store = TenantKnowledgeStore(tenant_id=tenant_id)
    reranker = get_reranker()

    candidates = store.search_authorized(
        query="What is the current Work From Home policy?",
        user_role=user.role,
        top_k=20
    )
    assert len(candidates) > 0

    reranked = reranker.rerank(query="What is the current Work From Home policy?", candidates=candidates, top_k=5)
    top_doc = reranked[0][0]
    assert "Work From Home Policy 2026" in top_doc.title

def test_holidays_query_retrieval(asterion_context):
    """'How many holidays does one get?' retrieves Leave Policy 2026 or Employee Handbook 2026."""
    tenant_id = asterion_context["tenant_id"]
    user = asterion_context["user"]
    store = TenantKnowledgeStore(tenant_id=tenant_id)
    reranker = get_reranker()

    candidates = store.search_authorized(
        query="How many holidays does one get?",
        user_role=user.role,
        top_k=20
    )
    assert len(candidates) > 0

    reranked = reranker.rerank(query="How many holidays does one get?", candidates=candidates, top_k=5)
    top_titles = [c[0].title for c in reranked]
    assert any("Employee Handbook 2026" in t or "Leave Policy 2026" in t for t in top_titles)

def test_annual_leave_query_retrieval(asterion_context):
    """'How many days of annual leave do employees get?' retrieves Leave Policy 2026."""
    tenant_id = asterion_context["tenant_id"]
    user = asterion_context["user"]
    store = TenantKnowledgeStore(tenant_id=tenant_id)
    reranker = get_reranker()

    candidates = store.search_authorized(
        query="How many days of annual leave do employees get?",
        user_role=user.role,
        top_k=20
    )
    assert len(candidates) > 0

    reranked = reranker.rerank(query="How many days of annual leave do employees get?", candidates=candidates, top_k=5)
    top_titles = [c[0].title for c in reranked]
    assert any("Leave Policy 2026" in t for t in top_titles)

def test_previous_wfh_policy_retrieval(asterion_context):
    """'What was the previous WFH policy?' retrieves Work From Home Policy 2025 as top result."""
    tenant_id = asterion_context["tenant_id"]
    user = asterion_context["user"]
    store = TenantKnowledgeStore(tenant_id=tenant_id)
    reranker = get_reranker()

    candidates = store.search_authorized(
        query="What was the previous WFH policy?",
        user_role=user.role,
        top_k=20
    )
    assert len(candidates) > 0

    reranked = reranker.rerank(query="What was the previous WFH policy?", candidates=candidates, top_k=5)
    top_doc = reranked[0][0]
    assert "Work From Home Policy 2025" in top_doc.title

@pytest.mark.asyncio
async def test_wfh_policy_comparison(db_session, asterion_context):
    """'What changed between the 2025 and 2026 WFH policies?' retrieves both 2025 and 2026 policies."""
    orchestrator = AgentOrchestrator(
        db=db_session,
        user=asterion_context["user"],
        tenant_id=asterion_context["tenant_id"]
    )
    response = await orchestrator.run_query("What changed between the 2025 and 2026 WFH policies?")
    assert not response.insufficient_evidence

    evidence_titles = [e.title for e in response.evidence]
    has_2025 = any("2025" in t for t in evidence_titles)
    has_2026 = any("2026" in t for t in evidence_titles)
    assert has_2025 and has_2026, f"Expected both 2025 and 2026 policies, got: {evidence_titles}"

def test_missing_embedding_provider_error():
    """Missing sentence-transformers raises explicit RuntimeError (not silent degradation)."""
    with patch.dict("sys.modules", {"sentence_transformers": None}):
        with pytest.raises(RuntimeError) as exc_info:
            SentenceTransformerEmbeddingProvider()
        assert "sentence-transformers" in str(exc_info.value)

def test_evidence_sufficiency_evaluation():
    """Evidence sufficiency logic correctly handles strong, weak, and insufficient cases."""
    # 1. Empty evidence
    status, reason = evaluate_evidence_sufficiency("What is the WFH policy?", [])
    assert status == "INSUFFICIENT"

    # 2. Strong single chunk (high similarity)
    strong_evidence = [
        {"title": "Work From Home Policy 2026", "similarity_score": 0.75, "rerank_score": 0.88, "version": "3.0"}
    ]
    status, reason = evaluate_evidence_sufficiency("What is the current WFH policy?", strong_evidence)
    assert status == "SUFFICIENT"

    # 3. Irrelevant / below threshold chunks
    irrelevant_evidence = [
        {"title": "Vendor Atlas MSA", "similarity_score": 0.08, "rerank_score": 0.05, "version": "1.0"},
        {"title": "Procurement 2024", "similarity_score": 0.10, "rerank_score": 0.07, "version": "1.0"}
    ]
    status, reason = evaluate_evidence_sufficiency("What is the current WFH policy?", irrelevant_evidence)
    assert status == "INSUFFICIENT"

    # 4. Comparison query with both versions
    comparison_evidence = [
        {"title": "Work From Home Policy 2025", "similarity_score": 0.65, "rerank_score": 0.70, "version": "2.0"},
        {"title": "Work From Home Policy 2026", "similarity_score": 0.68, "rerank_score": 0.72, "version": "3.0"}
    ]
    status, reason = evaluate_evidence_sufficiency("What changed between the 2025 and 2026 WFH policies?", comparison_evidence)
    assert status == "SUFFICIENT"

