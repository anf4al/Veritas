import asyncio
import json
from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.company import Company
from backend.app.agents.orchestrator import AgentOrchestrator
from backend.app.retrieval.tenant_store import TenantKnowledgeStore
from backend.app.reranking.model import get_reranker

TARGET_QUERIES = [
    "What is the current WFH policy?",
    "What is the current Work From Home policy?",
    "How many holidays does one get?",
    "How many days of annual leave do employees get?",
    "What was the previous WFH policy?",
    "What changed between the 2025 and 2026 WFH policies?"
]

async def verify_all():
    db = SessionLocal()
    comp = db.query(Company).filter_by(slug="asterion").first()
    user = db.query(User).filter_by(username="admin@veritas.demo").first()
    assert comp and user

    orchestrator = AgentOrchestrator(db=db, user=user, tenant_id=comp.id)
    store = TenantKnowledgeStore(tenant_id=comp.id)
    reranker = get_reranker()

    print("=" * 80)
    print("VERITAS ENTERPRISE RAG - LIVE END-TO-END VERIFICATION")
    print("=" * 80)

    for idx, query in enumerate(TARGET_QUERIES, start=1):
        print(f"\n[{idx}/6] QUERY: \"{query}\"")
        print("-" * 70)

        # 1. Direct ANN candidates
        cands = store.search_authorized(query, user.role, top_k=20)
        print(f"Candidate Count (ANN): {len(cands)}")
        print("Top 3 Retrieved (ANN Cosine):")
        for i, c in enumerate(cands[:3], 1):
            print(f"   {i}. \"{c.title}\" (v{c.version}) | Cosine Sim: {c.score:.4f}")

        # 2. Reranked
        reranked = reranker.rerank(query, cands, top_k=3)
        print("Top 3 Reranked (XGBoost):")
        for i, (c, score) in enumerate(reranked, 1):
            print(f"   {i}. \"{c.title}\" (v{c.version}) | Rerank Score: {score:.4f} | Cosine: {c.score:.4f}")

        # 3. Live Orchestrator Execution
        response = await orchestrator.execute_query(query)
        sufficiency = "INSUFFICIENT" if response.insufficient_evidence else "SUFFICIENT"
        print(f"Evidence Sufficiency Outcome: {sufficiency}")
        print(f"Latency: {response.latency_ms:.2f}ms | Provider: {response.provider_used} ({response.model_used})")
        print(f"Citations ({len(response.citations)}):")
        for cite in response.citations:
            print(f"   * [{cite.title}, p.{cite.page}, {cite.section}, v{cite.version}] (Relevance: {cite.relevance_score})")

        print("Generated Answer:")
        print("   " + "\n   ".join(response.answer.split("\n")))
        print("-" * 70)

    db.close()

if __name__ == "__main__":
    asyncio.run(verify_all())

