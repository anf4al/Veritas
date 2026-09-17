import time
from typing import List
import numpy as np
from backend.app.schemas.observability import MetricsOut

class MetricsCollector:
    def __init__(self):
        self.request_count: int = 0
        self.error_count: int = 0
        self.total_tool_calls: int = 0
        self.cache_hits: int = 0
        self.cache_lookups: int = 0

        self.latencies: List[float] = []
        self.retrieval_latencies: List[float] = []
        self.reranking_latencies: List[float] = []
        self.llm_latencies: List[float] = []

    def record_request(self, latency_ms: float, is_error: bool = False):
        self.request_count += 1
        if is_error:
            self.error_count += 1
        self.latencies.append(latency_ms)
        if len(self.latencies) > 1000:
            self.latencies.pop(0)

    def record_tool_call(self):
        self.total_tool_calls += 1

    def record_cache_event(self, hit: bool):
        self.cache_lookups += 1
        if hit:
            self.cache_hits += 1

    def record_component_latency(self, component: str, latency_ms: float):
        if component == "retrieval":
            self.retrieval_latencies.append(latency_ms)
            if len(self.retrieval_latencies) > 500:
                self.retrieval_latencies.pop(0)
        elif component == "reranking":
            self.reranking_latencies.append(latency_ms)
            if len(self.reranking_latencies) > 500:
                self.reranking_latencies.pop(0)
        elif component == "llm":
            self.llm_latencies.append(latency_ms)
            if len(self.llm_latencies) > 500:
                self.llm_latencies.pop(0)

    def get_metrics(self) -> MetricsOut:
        avg_lat = float(np.mean(self.latencies)) if self.latencies else 0.0
        p95_lat = float(np.percentile(self.latencies, 95)) if self.latencies else 0.0
        avg_ret = float(np.mean(self.retrieval_latencies)) if self.retrieval_latencies else 0.0
        avg_rer = float(np.mean(self.reranking_latencies)) if self.reranking_latencies else 0.0
        avg_llm = float(np.mean(self.llm_latencies)) if self.llm_latencies else 0.0
        hit_rate = (self.cache_hits / self.cache_lookups) if self.cache_lookups > 0 else 0.0

        return MetricsOut(
            request_count=self.request_count,
            error_count=self.error_count,
            p95_latency_ms=round(p95_lat, 2),
            avg_latency_ms=round(avg_lat, 2),
            avg_retrieval_latency_ms=round(avg_ret, 2),
            avg_reranking_latency_ms=round(avg_rer, 2),
            avg_llm_latency_ms=round(avg_llm, 2),
            total_tool_calls=self.total_tool_calls,
            cache_hit_rate=round(hit_rate, 4)
        )

_metrics_instance = None

def get_metrics_collector() -> MetricsCollector:
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance
