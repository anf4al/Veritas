from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class SpanOut(BaseModel):
    span_id: str
    trace_id: str
    name: str  # auth, embedding, vector_search, rerank, tool_call, llm, verification
    start_time: str
    end_time: str
    duration_ms: float
    status: str  # ok, error
    attributes: Dict[str, Any] = {}

class TraceOut(BaseModel):
    trace_id: str
    timestamp: str
    company_id: Optional[str] = None
    user_id: Optional[str] = None
    query: str
    total_duration_ms: float
    status: str
    spans: List[SpanOut] = []

class MetricsOut(BaseModel):
    request_count: int = 0
    error_count: int = 0
    p95_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    avg_retrieval_latency_ms: float = 0.0
    avg_reranking_latency_ms: float = 0.0
    avg_llm_latency_ms: float = 0.0
    total_tool_calls: int = 0
    cache_hit_rate: float = 0.0

class ProviderStatusOut(BaseModel):
    provider: str
    configured: bool
    model: str
    error: Optional[str] = None

