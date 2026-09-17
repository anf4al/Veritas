from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class EvaluationResultOut(BaseModel):
    id: str
    question: str
    hit_at_5: int
    hit_at_10: int
    hit_at_20: int
    groundedness_score: float
    latency_ms: float
    generated_answer: Optional[str] = None
    citations: Optional[List[Dict[str, Any]]] = []

    model_config = {"from_attributes": True}

class EvaluationRunOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    status: str
    provider: str
    model: str
    total_questions: int
    recall_at_5: float
    recall_at_10: float
    recall_at_20: float
    groundedness_score: float
    avg_latency_ms: float
    reranker_lift: float
    created_at: datetime
    results: Optional[List[EvaluationResultOut]] = []

    model_config = {"from_attributes": True}

class EvaluationRunCreate(BaseModel):
    name: Optional[str] = "Benchmark Evaluation Run"
    company_id: Optional[str] = None

class EvaluationComparisonOut(BaseModel):
    run_a: EvaluationRunOut
    run_b: EvaluationRunOut
    recall_5_diff: float
    recall_10_diff: float
    recall_20_diff: float
    latency_diff_ms: float
    groundedness_diff: float

