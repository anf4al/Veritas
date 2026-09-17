from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.auth.dependencies import get_current_user, require_permission, verify_tenant_access
from backend.app.auth.permissions import Permission
from backend.app.models.user import User
from backend.app.models.evaluation import EvaluationRun, EvaluationResult
from backend.app.schemas.evaluation import (
    EvaluationRunOut,
    EvaluationRunCreate,
    EvaluationComparisonOut
)
from backend.app.evaluation.runner import EvaluationRunner

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Benchmarks"])

@router.post("/run", response_model=EvaluationRunOut)
async def run_evaluation(
    req: EvaluationRunCreate,
    current_user: User = Depends(require_permission(Permission.EVALUATION_RUN)),
    db: Session = Depends(get_db)
):
    """Execute evaluation benchmark on the seed dataset for active company."""
    company_id = req.company_id
    if not company_id and current_user.company_memberships:
        company_id = current_user.company_memberships[0].company_id
    elif not company_id:
        from backend.app.models.company import Company
        c = db.query(Company).first()
        company_id = c.id if c else ""

    verify_tenant_access(current_user, company_id, db)

    runner = EvaluationRunner(db=db, user=current_user, tenant_id=company_id)
    run_rec = await runner.run_benchmark(run_name=req.name or "Benchmark Evaluation Run")
    return run_rec

@router.get("/runs", response_model=List[EvaluationRunOut])
def list_evaluation_runs(
    current_user: User = Depends(require_permission(Permission.EVALUATION_READ)),
    db: Session = Depends(get_db)
):
    """List historical evaluation runs."""
    runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).all()
    return runs

@router.get("/runs/{run_id}", response_model=EvaluationRunOut)
def get_evaluation_run(
    run_id: str,
    current_user: User = Depends(require_permission(Permission.EVALUATION_READ)),
    db: Session = Depends(get_db)
):
    """Get single evaluation run with per-question results."""
    run = db.query(EvaluationRun).filter(EvaluationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation run not found.")
    return run

@router.get("/compare/{id_a}/{id_b}", response_model=EvaluationComparisonOut)
def compare_runs(
    id_a: str,
    id_b: str,
    current_user: User = Depends(require_permission(Permission.EVALUATION_READ)),
    db: Session = Depends(get_db)
):
    """Compare two evaluation runs side by side."""
    run_a = db.query(EvaluationRun).filter(EvaluationRun.id == id_a).first()
    run_b = db.query(EvaluationRun).filter(EvaluationRun.id == id_b).first()

    if not run_a or not run_b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both evaluation runs not found.")

    return EvaluationComparisonOut(
        run_a=EvaluationRunOut.model_validate(run_a),
        run_b=EvaluationRunOut.model_validate(run_b),
        recall_5_diff=round(run_b.recall_at_5 - run_a.recall_at_5, 4),
        recall_10_diff=round(run_b.recall_at_10 - run_a.recall_at_10, 4),
        recall_20_diff=round(run_b.recall_at_20 - run_a.recall_at_20, 4),
        latency_diff_ms=round(run_b.avg_latency_ms - run_a.avg_latency_ms, 2),
        groundedness_diff=round(run_b.groundedness_score - run_a.groundedness_score, 4)
    )
