import os
from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.company import Company
from backend.app.retrieval.tenant_store import TenantKnowledgeStore
from backend.app.reranking.model import get_reranker

def run():
    db = SessionLocal()
    comp = db.query(Company).filter_by(slug="asterion").first()
    user = db.query(User).filter_by(username="admin@veritas.demo").first()
    store = TenantKnowledgeStore(tenant_id=comp.id)

    queries = [
        "What is the current WFH policy?",
        "What is the current Work From Home policy?",
        "How many holidays does one get?",
        "How many days of annual leave do employees get?",
        "What was the previous WFH policy?",
        "What changed between the 2025 and 2026 WFH policies?"
    ]

    reranker = get_reranker()
    reranker._load_model()

    for q in queries:
        cands = store.search_authorized(q, user.role, top_k=20)
        reranked = reranker.rerank(q, cands, top_k=3)
        print(f"\nQuery: '{q}' (candidates: {len(cands)})")
        for cand, score in reranked:
            print(f"   -> {cand.title} [v{cand.version}] | sim={cand.score:.4f} | rerank={score:.4f}")

    db.close()

if __name__ == "__main__":
    run()

