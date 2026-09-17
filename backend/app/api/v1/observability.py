from typing import List
from fastapi import APIRouter, Depends
from backend.app.auth.dependencies import require_permission
from backend.app.auth.permissions import Permission
from backend.app.models.user import User
from backend.app.schemas.observability import TraceOut, MetricsOut
from backend.app.observability.tracer import get_tracer
from backend.app.observability.metrics import get_metrics_collector

router = APIRouter(prefix="/observability", tags=["Observability & Telemetry"])

@router.get("/traces", response_model=List[TraceOut])
def get_traces(
    limit: int = 50,
    current_user: User = Depends(require_permission(Permission.OBSERVABILITY_READ))
):
    """Retrieve recent end-to-end request traces with span timings."""
    tracer = get_tracer()
    return tracer.get_recent_traces(limit=limit)

@router.get("/metrics", response_model=MetricsOut)
def get_metrics(
    current_user: User = Depends(require_permission(Permission.OBSERVABILITY_READ))
):
    """Retrieve real-time platform metrics (p95 latency, component breakdowns, tool counts)."""
    collector = get_metrics_collector()
    return collector.get_metrics()
