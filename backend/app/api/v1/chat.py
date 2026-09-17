import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.auth.dependencies import get_current_user, verify_tenant_access
from backend.app.models.user import User
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.agents.orchestrator import AgentOrchestrator
from backend.app.observability.metrics import get_metrics_collector
from backend.app.observability.tracer import get_tracer
from backend.app.models.audit import AuditEvent

router = APIRouter(prefix="/chat", tags=["Research & Chat Workspace"])

@router.post("", response_model=ChatResponse)
async def chat_query(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute enterprise RAG / agentic query for active tenant."""
    company_id = req.company_id
    if not company_id:
        # Fallback to user's first company
        if current_user.company_memberships:
            company_id = current_user.company_memberships[0].company_id
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Active company_id must be provided.")

    verify_tenant_access(current_user, company_id, db)

    orchestrator = AgentOrchestrator(db=db, user=current_user, tenant_id=company_id)
    tracer = get_tracer()
    trace_id = tracer.start_trace(
        query=req.query,
        company_id=company_id,
        user_id=current_user.id
    )

    metrics = get_metrics_collector()
    try:
        response = await orchestrator.execute_query(query=req.query, trace_id=trace_id)
        metrics.record_request(latency_ms=response.latency_ms, is_error=False)

        # Log audit
        audit = AuditEvent(
            company_id=company_id,
            user_id=current_user.id,
            action="chat_query",
            details={
                "query": req.query[:100],
                "citations_count": len(response.citations),
                "insufficient_evidence": response.insufficient_evidence
            }
        )
        db.add(audit)
        db.commit()

        return response
    except Exception as e:
        metrics.record_request(latency_ms=0.0, is_error=True)
        tracer.finish_trace(trace_id, 0.0, status="error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution error: {str(e)}"
        )

@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream cited research responses via Server-Sent Events (SSE)."""
    company_id = req.company_id
    if not company_id and current_user.company_memberships:
        company_id = current_user.company_memberships[0].company_id

    verify_tenant_access(current_user, company_id, db)

    orchestrator = AgentOrchestrator(db=db, user=current_user, tenant_id=company_id)
    resp = await orchestrator.execute_query(query=req.query)

    async def event_generator():
        # Stream evidence and steps metadata first
        yield f"event: metadata\ndata: {json.dumps({'citations': [c.model_dump() for c in resp.citations], 'agent_steps': [s.model_dump() for s in resp.agent_steps], 'trace_id': resp.trace_id})}\n\n"

        # Stream answer chunks
        words = resp.answer.split(" ")
        for i in range(0, len(words), 2):
            chunk = " ".join(words[i:i+2]) + " "
            yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"

        # Done event
        yield f"event: done\ndata: {json.dumps({'status': 'completed', 'latency_ms': resp.latency_ms})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
