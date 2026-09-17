import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from collections import deque
from backend.app.schemas.observability import TraceOut, SpanOut

class Span:
    def __init__(self, trace_id: str, name: str, attributes: Optional[Dict[str, Any]] = None):
        self.span_id = str(uuid.uuid4())[:8]
        self.trace_id = trace_id
        self.name = name
        self.attributes = attributes or {}
        self.start_time_iso = datetime.now(timezone.utc).isoformat()
        self._start_perf = time.perf_counter()
        self.end_time_iso = ""
        self.duration_ms = 0.0
        self.status = "ok"

    def finish(self, status: str = "ok"):
        self._end_perf = time.perf_counter()
        self.end_time_iso = datetime.now(timezone.utc).isoformat()
        self.duration_ms = round((self._end_perf - self._start_perf) * 1000.0, 2)
        self.status = status

    def to_schema(self) -> SpanOut:
        return SpanOut(
            span_id=self.span_id,
            trace_id=self.trace_id,
            name=self.name,
            start_time=self.start_time_iso,
            end_time=self.end_time_iso,
            duration_ms=self.duration_ms,
            status=self.status,
            attributes=self.attributes
        )

class Trace:
    def __init__(self, trace_id: str, query: str, company_id: Optional[str] = None, user_id: Optional[str] = None):
        self.trace_id = trace_id
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.company_id = company_id
        self.user_id = user_id
        self.query = query
        self.spans: List[Span] = []
        self.total_duration_ms = 0.0
        self.status = "in_progress"

    def add_span(self, span: Span):
        self.spans.append(span)

    def finish(self, total_duration_ms: float, status: str = "completed"):
        self.total_duration_ms = round(total_duration_ms, 2)
        self.status = status

    def to_schema(self) -> TraceOut:
        return TraceOut(
            trace_id=self.trace_id,
            timestamp=self.timestamp,
            company_id=self.company_id,
            user_id=self.user_id,
            query=self.query,
            total_duration_ms=self.total_duration_ms,
            status=self.status,
            spans=[s.to_schema() for s in self.spans]
        )

class VeritasTracer:
    def __init__(self, max_traces: int = 100):
        self._traces: deque[Trace] = deque(maxlen=max_traces)
        self._active_traces: Dict[str, Trace] = {}

    def start_trace(self, query: str, company_id: Optional[str] = None, user_id: Optional[str] = None) -> str:
        trace_id = f"trc-{uuid.uuid4().hex[:12]}"
        trace = Trace(trace_id=trace_id, query=query, company_id=company_id, user_id=user_id)
        self._active_traces[trace_id] = trace
        return trace_id

    @contextmanager
    def span(self, trace_id: str, name: str, attributes: Optional[Dict[str, Any]] = None):
        span_obj = Span(trace_id=trace_id, name=name, attributes=attributes)
        trace = self._active_traces.get(trace_id)
        if trace:
            trace.add_span(span_obj)

        status_flag = "ok"
        try:
            yield span_obj
        except Exception as e:
            status_flag = "error"
            span_obj.attributes["error"] = str(e)
            raise
        finally:
            span_obj.finish(status=status_flag)

    def finish_trace(self, trace_id: str, total_duration_ms: float, status: str = "completed"):
        trace = self._active_traces.pop(trace_id, None)
        if trace:
            trace.finish(total_duration_ms, status)
            self._traces.appendleft(trace)

    def get_recent_traces(self, limit: int = 50) -> List[TraceOut]:
        return [t.to_schema() for t in list(self._traces)[:limit]]

_tracer_instance = None

def get_tracer() -> VeritasTracer:
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = VeritasTracer()
    return _tracer_instance
