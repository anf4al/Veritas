import pytest
import asyncio
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.company import Company
from backend.app.retrieval.entity import (
    extract_query_entities,
    entity_present_in_text,
    compute_entity_presence_score,
    normalize_entity_text
)
from backend.app.agents.orchestrator import AgentOrchestrator, evaluate_evidence_sufficiency
from backend.app.retrieval.tenant_store import TenantKnowledgeStore
from backend.app.reranking.model import get_reranker

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

@pytest.fixture(scope="module")
def meridian_context(db_session):
    company = db_session.query(Company).filter(Company.slug == "meridian").first()
    assert company is not None, "Meridian company must exist"
    user = db_session.query(User).filter(User.username == "compliance@meridian.demo").first()
    assert user is not None, "Meridian user must exist"
    return {"tenant_id": company.id, "user": user}

def test_entity_extraction_normalization():
    """Requirement 7: Entity matching handles capitalization, hyphens, and ignores common words."""
    # Multi-word and capitalization
    e1 = extract_query_entities("Why was Vendor Atlas classified as high risk?")
    assert "Vendor Atlas" in e1

    e2 = extract_query_entities("does our contract with vendor atlas allow termination?")
    assert any("atlas" in e.lower() for e in e2)

    # Hyphenation
    assert entity_present_in_text("Vendor Atlas", "This is the Vendor-Atlas agreement.")
    assert entity_present_in_text("Vendor-Atlas", "Agreement with Vendor Atlas Inc.")

    # Stopwords and generic words should not be extracted
    e3 = extract_query_entities("What is the current WFH policy?")
    assert "current" not in e3
    assert "policy" not in e3
    assert "what" not in e3

def test_evidence_sufficiency_multi_signal():
    """Requirement 8: Multi-signal sufficiency gate rejects entity absence despite high semantic similarity."""
    # High semantic similarity (0.45) but named entity 'Vendor Atlas' is missing
    mismatched_evidence = [
        {
            "title": "Vendor Selection and Due Diligence Matrix",
            "section": "Due Diligence Guidelines",
            "text": "All third-party vendors must undergo annual compliance evaluation.",
            "similarity_score": 0.45,
            "rerank_score": 0.05
        }
    ]
    status, reason = evaluate_evidence_sufficiency(
        "Why was Vendor Atlas classified as high risk?",
        mismatched_evidence
    )
    assert status == "INSUFFICIENT"
    assert "Vendor Atlas" in reason

    # Strong evidence when entity is present
    matched_evidence = [
        {
            "title": "Vendor Atlas Risk Assessment 2026",
            "section": "Risk Assessment Summary",
            "text": "Vendor Atlas was classified as high risk due to repeated SLA failures.",
            "similarity_score": 0.72,
            "rerank_score": 0.91
        }
    ]
    status, reason = evaluate_evidence_sufficiency(
        "Why was Vendor Atlas classified as high risk?",
        matched_evidence
    )
    assert status == "SUFFICIENT"

@pytest.mark.asyncio
async def test_vendor_atlas_absent_in_meridian(db_session, meridian_context):
    """Requirement 1 & 3: In Meridian (where Vendor Atlas doesn't exist), return insufficient evidence
    and DO NOT synthesize from generic Meridian vendor documents.
    """
    orchestrator = AgentOrchestrator(
        db=db_session,
        user=meridian_context["user"],
        tenant_id=meridian_context["tenant_id"]
    )
    res = await orchestrator.run_query("Why was Vendor Atlas classified as high risk, and does our contract allow termination?")
    assert res.insufficient_evidence is True
    # Verify no Meridian document is cited as answering the question
    for cite in res.citations:
        assert "Vendor Atlas" in cite.title

@pytest.mark.asyncio
async def test_vendor_atlas_present_in_asterion(db_session, asterion_context):
    """Requirement 2: In Asterion (where Vendor Atlas records exist), retrieve correct evidence."""
    orchestrator = AgentOrchestrator(
        db=db_session,
        user=asterion_context["user"],
        tenant_id=asterion_context["tenant_id"]
    )
    res = await orchestrator.run_query("Does our contract with Vendor Atlas allow termination?")
    assert not res.insufficient_evidence
    cited_titles = [c.title for c in res.citations]
    assert any("Vendor Atlas Master Services Agreement" in t for t in cited_titles)

def test_wfh_current_policy_version(asterion_context):
    """Requirement 4: Current WFH policy retrieves the 2026 active version."""
    store = TenantKnowledgeStore(tenant_id=asterion_context["tenant_id"])
    reranker = get_reranker()
    candidates = store.search_authorized(
        query="What is the current WFH policy?",
        user_role=asterion_context["user"].role,
        top_k=15
    )
    reranked = reranker.rerank("What is the current WFH policy?", candidates, top_k=3)
    top_doc = reranked[0][0]
    assert "2026" in top_doc.title
    assert "Work From Home Policy 2026" in top_doc.title

@pytest.mark.asyncio
async def test_wfh_comparison_both_versions(db_session, asterion_context):
    """Requirement 5: Comparing 2025 and 2026 WFH policies retrieves both versions."""
    orchestrator = AgentOrchestrator(
        db=db_session,
        user=asterion_context["user"],
        tenant_id=asterion_context["tenant_id"]
    )
    res = await orchestrator.run_query("What changed between the 2025 and 2026 WFH policies?")
    assert not res.insufficient_evidence
    evidence_titles = [e.title for e in res.evidence]
    has_2025 = any("2025" in t for t in evidence_titles)
    has_2026 = any("2026" in t for t in evidence_titles)
    assert has_2025 and has_2026

def test_annual_leave_policy(asterion_context):
    """Requirement 6: Annual leave query retrieves correct leave policy documentation."""
    store = TenantKnowledgeStore(tenant_id=asterion_context["tenant_id"])
    reranker = get_reranker()
    candidates = store.search_authorized(
        query="How many days of annual leave do employees get?",
        user_role=asterion_context["user"].role,
        top_k=15
    )
    reranked = reranker.rerank("How many days of annual leave do employees get?", candidates, top_k=3)
    top_titles = [c[0].title for c in reranked]
    assert any("Leave Policy 2026" in t or "Employee Handbook 2026" in t for t in top_titles)

@pytest.mark.asyncio
async def test_citation_page_numbers(db_session, asterion_context):
    """Requirement 16: Citations identify valid page numbers and document metadata."""
    orchestrator = AgentOrchestrator(
        db=db_session,
        user=asterion_context["user"],
        tenant_id=asterion_context["tenant_id"]
    )
    res = await orchestrator.run_query("What is the current WFH policy?")
    assert not res.insufficient_evidence
    assert len(res.citations) > 0
    for cite in res.citations:
        assert cite.page is not None
        assert cite.page >= 1
        assert cite.title != ""

