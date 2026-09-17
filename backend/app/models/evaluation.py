import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="completed")
    provider = Column(String(50), nullable=False, default="openai")
    model = Column(String(100), nullable=False)
    total_questions = Column(Integer, nullable=False, default=0)
    recall_at_5 = Column(Float, nullable=False, default=0.0)
    recall_at_10 = Column(Float, nullable=False, default=0.0)
    recall_at_20 = Column(Float, nullable=False, default=0.0)
    groundedness_score = Column(Float, nullable=False, default=0.0)
    avg_latency_ms = Column(Float, nullable=False, default=0.0)
    reranker_lift = Column(Float, nullable=False, default=0.0)  # % improvement of XGBoost over ANN
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    results = relationship("EvaluationResult", back_populates="run", cascade="all, delete-orphan")

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    expected_doc_ids = Column(JSON, nullable=True, default=list)
    retrieved_chunk_ids = Column(JSON, nullable=True, default=list)
    reranked_chunk_ids = Column(JSON, nullable=True, default=list)
    hit_at_5 = Column(Integer, nullable=False, default=0)
    hit_at_10 = Column(Integer, nullable=False, default=0)
    hit_at_20 = Column(Integer, nullable=False, default=0)
    groundedness_score = Column(Float, nullable=False, default=1.0)
    latency_ms = Column(Float, nullable=False, default=0.0)
    generated_answer = Column(Text, nullable=True)
    citations = Column(JSON, nullable=True, default=list)

    # Relationships
    run = relationship("EvaluationRun", back_populates="results")
