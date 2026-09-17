import time
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.evaluation import EvaluationRun, EvaluationResult
from backend.app.models.user import User
from backend.app.models.company import Company
from backend.app.evaluation.dataset import SEED_EVALUATION_QUESTIONS
from backend.app.evaluation.metrics import (
    compute_recall_at_k,
    compute_reranker_lift,
    compute_groundedness_score
)
from backend.app.retrieval.tenant_store import TenantKnowledgeStore
from backend.app.reranking.model import get_reranker
from backend.app.llm.factory import get_llm_provider
from backend.app.agents.orchestrator import AgentOrchestrator
from backend.app.core.config import settings

class EvaluationRunner:
    def __init__(self, db: Session, user: User, tenant_id: str):
        self.db = db
        self.user = user
        self.tenant_id = tenant_id
        self.orchestrator = AgentOrchestrator(db=db, user=user, tenant_id=tenant_id)
        self.tenant_store = TenantKnowledgeStore(tenant_id=tenant_id)
        self.reranker = get_reranker()
        self.llm_provider = get_llm_provider()

    async def run_benchmark(self, run_name: str = "Benchmark Evaluation Run") -> EvaluationRun:
        start_run = time.time()
        company = self.db.query(Company).filter(Company.id == self.tenant_id).first()
        tenant_name = company.name if company else "Default Tenant"

        run_record = EvaluationRun(
            tenant_id=self.tenant_id,
            name=f"{run_name} ({tenant_name})",
            status="running",
            provider=self.llm_provider.provider_name,
            model=self.llm_provider.model_name,
            total_questions=len(SEED_EVALUATION_QUESTIONS)
        )
        self.db.add(run_record)
        self.db.commit()
        self.db.refresh(run_record)

        recalls_5 = []
        recalls_10 = []
        recalls_20 = []
        lifts = []
        groundedness_scores = []
        latencies = []

        for item in SEED_EVALUATION_QUESTIONS:
            q_start = time.time()
            question = item["question"]
            expected_titles = item["expected_titles"]

            # 1. Raw ANN retrieval (K=30)
            ann_candidates = self.tenant_store.search_authorized(
                query=question,
                user_role=self.user.role,
                top_k=settings.ANN_TOP_K
            )
            ann_titles = [c.title for c in ann_candidates]

            # 2. XGBoost Reranking (top 10)
            reranked_pairs = self.reranker.rerank(
                query=question,
                candidates=ann_candidates,
                top_k=10
            )
            reranked_titles = [cand.title for cand, score in reranked_pairs]

            # 3. Full answer execution
            chat_resp = await self.orchestrator.execute_query(query=question)

            # Compute metrics
            r5 = compute_recall_at_k(reranked_titles, expected_titles, 5)
            r10 = compute_recall_at_k(reranked_titles, expected_titles, 10)
            r20 = compute_recall_at_k(ann_titles, expected_titles, 20)
            lift = compute_reranker_lift(ann_titles, reranked_titles, expected_titles)
            groundedness = compute_groundedness_score(chat_resp.citations, chat_resp.answer)
            q_lat = (time.time() - q_start) * 1000.0

            recalls_5.append(r5)
            recalls_10.append(r10)
            recalls_20.append(r20)
            lifts.append(lift)
            groundedness_scores.append(groundedness)
            latencies.append(q_lat)

            # Save per-question result
            res_record = EvaluationResult(
                run_id=run_record.id,
                question=question,
                expected_doc_ids=expected_titles,
                retrieved_chunk_ids=ann_titles[:10],
                reranked_chunk_ids=reranked_titles[:10],
                hit_at_5=1 if r5 > 0.0 else 0,
                hit_at_10=1 if r10 > 0.0 else 0,
                hit_at_20=1 if r20 > 0.0 else 0,
                groundedness_score=round(groundedness, 2),
                latency_ms=round(q_lat, 2),
                generated_answer=chat_resp.answer,
                citations=[c.model_dump() for c in chat_resp.citations]
            )
            self.db.add(res_record)

        # Update run aggregates
        run_record.status = "completed"
        run_record.recall_at_5 = round(sum(recalls_5) / len(recalls_5), 4) if recalls_5 else 0.0
        run_record.recall_at_10 = round(sum(recalls_10) / len(recalls_10), 4) if recalls_10 else 0.0
        run_record.recall_at_20 = round(sum(recalls_20) / len(recalls_20), 4) if recalls_20 else 0.0
        run_record.reranker_lift = round(sum(lifts) / len(lifts), 2) if lifts else 0.0
        run_record.groundedness_score = round(sum(groundedness_scores) / len(groundedness_scores), 4) if groundedness_scores else 0.0
        run_record.avg_latency_ms = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

        self.db.commit()
        self.db.refresh(run_record)
        return run_record
