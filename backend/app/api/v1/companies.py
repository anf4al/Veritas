from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.auth.dependencies import get_current_user, require_permission
from backend.app.auth.permissions import Permission
from backend.app.models.user import User, UserCompany
from backend.app.models.company import Company
from backend.app.models.document import Document, Chunk
from backend.app.models.audit import AuditEvent
from backend.app.schemas.company import CompanyOut, CompanyCreate, CompanySwitchRequest
from backend.app.auth.jwt import generate_token_for_user

router = APIRouter(prefix="/companies", tags=["Companies & Tenants"])

@router.get("", response_model=List[CompanyOut])
def list_companies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List companies accessible to authenticated user."""
    if current_user.role == "PLATFORM_ADMIN":
        companies = db.query(Company).order_by(Company.name).all()
    else:
        memberships = db.query(UserCompany).filter(UserCompany.user_id == current_user.id).all()
        comp_ids = [m.company_id for m in memberships]
        companies = db.query(Company).filter(Company.id.in_(comp_ids)).order_by(Company.name).all()

    results = []
    for c in companies:
        doc_count = db.query(Document).filter(Document.company_id == c.id).count()
        chunk_count = db.query(Chunk).filter(Chunk.company_id == c.id).count()
        results.append(CompanyOut(
            id=c.id,
            name=c.name,
            slug=c.slug,
            description=c.description,
            status=c.status,
            created_at=c.created_at,
            document_count=doc_count,
            chunk_count=chunk_count
        ))
    return results

@router.post("/switch")
def switch_company(
    req: CompanySwitchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Switch active tenant context. Platform admins can switch freely; others must be members."""
    company = db.query(Company).filter(Company.id == req.company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target company not found.")

    if current_user.role != "PLATFORM_ADMIN":
        membership = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == req.company_id
        ).first()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not have permission to switch to this tenant."
            )

    # Log audit event
    audit = AuditEvent(
        company_id=company.id,
        user_id=current_user.id,
        action="company_switch",
        details={"switched_to": company.name, "company_id": company.id}
    )
    db.add(audit)
    db.commit()

    # Generate new token bound to active company
    token_str = generate_token_for_user(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        company_id=company.id
    )

    return {
        "status": "success",
        "active_company_id": company.id,
        "company_name": company.name,
        "new_token": token_str
    }

@router.post("", response_model=CompanyOut)
def create_company(
    req: CompanyCreate,
    current_user: User = Depends(require_permission(Permission.ADMIN_ALL)),
    db: Session = Depends(get_db)
):
    """Create a new company/tenant (Platform Admin only)."""
    existing = db.query(Company).filter((Company.name == req.name) | (Company.slug == req.slug)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company name or slug already exists.")

    comp = Company(name=req.name, slug=req.slug, description=req.description)
    db.add(comp)
    db.commit()
    db.refresh(comp)

    return CompanyOut(
        id=comp.id,
        name=comp.name,
        slug=comp.slug,
        description=comp.description,
        status=comp.status,
        created_at=comp.created_at,
        document_count=0,
        chunk_count=0
    )
