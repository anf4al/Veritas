from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import verify_password
from backend.app.auth.jwt import generate_token_for_user
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.permissions import get_role_permissions
from backend.app.models.user import User, UserCompany
from backend.app.models.company import Company
from backend.app.models.document import Document, Chunk
from backend.app.schemas.auth import (
    Token,
    LoginRequest,
    UserOut,
    DemoAccountOut
)
from backend.app.schemas.company import CompanyOut

router = APIRouter(prefix="/auth", tags=["Authentication"])

DEMO_ACCOUNTS = [
    DemoAccountOut(
        title="Platform Administrator",
        username="admin@veritas.demo",
        role="PLATFORM_ADMIN",
        company_name="All Companies",
        access_description="Full access to users, all companies, documents, indexing, observability, and evaluation.",
        password_hint="VeritasAdmin!2026"
    ),
    DemoAccountOut(
        title="HR Manager (Asterion)",
        username="hr@asterion.demo",
        role="HR_MANAGER",
        company_name="Asterion Technologies",
        access_description="HR handbooks, leave, reimbursement, HR SOPs. Cannot access salary records or security incident reports.",
        password_hint="VeritasHR!2026"
    ),
    DemoAccountOut(
        title="Operations Manager (Asterion)",
        username="ops@asterion.demo",
        role="OPERATIONS_MANAGER",
        company_name="Asterion Technologies",
        access_description="Procurement, vendors, SLAs, ops reports, product docs. Cannot access confidential HR files.",
        password_hint="VeritasOps!2026"
    ),
    DemoAccountOut(
        title="Security / Compliance Officer (Asterion)",
        username="security@asterion.demo",
        role="SECURITY_OFFICER",
        company_name="Asterion Technologies",
        access_description="InfoSec policies, incidents, data retention, audit docs. Cannot access salary records.",
        password_hint="VeritasSec!2026"
    ),
    DemoAccountOut(
        title="Sales User (Asterion)",
        username="sales@asterion.demo",
        role="SALES",
        company_name="Asterion Technologies",
        access_description="Product documentation, approved pricing, customer-facing materials.",
        password_hint="VeritasSales!2026"
    ),
    DemoAccountOut(
        title="Standard Employee (Asterion)",
        username="employee@asterion.demo",
        role="EMPLOYEE",
        company_name="Asterion Technologies",
        access_description="General handbooks, leave, WFH, reimbursement. Cannot access restricted HR, security incidents, or contracts.",
        password_hint="VeritasEmployee!2026"
    ),
    DemoAccountOut(
        title="Northstar Administrator",
        username="admin@northstar.demo",
        role="COMPANY_ADMIN",
        company_name="Northstar Manufacturing",
        access_description="Management of documents and users strictly for Northstar Manufacturing.",
        password_hint="NorthstarAdmin!2026"
    ),
    DemoAccountOut(
        title="Meridian Compliance Officer",
        username="compliance@meridian.demo",
        role="COMPLIANCE_OFFICER",
        company_name="Meridian Healthcare Services",
        access_description="Compliance, clinical guidelines, and audit materials strictly for Meridian Healthcare.",
        password_hint="MeridianCompliance!2026"
    )
]

def build_user_out(user: User, active_company_id: str, db: Session) -> UserOut:
    permissions = get_role_permissions(user.role)

    # Get permitted companies
    if user.role == "PLATFORM_ADMIN":
        companies_db = db.query(Company).filter(Company.status == "active").all()
    else:
        memberships = db.query(UserCompany).filter(UserCompany.user_id == user.id).all()
        comp_ids = [m.company_id for m in memberships]
        companies_db = db.query(Company).filter(Company.id.in_(comp_ids), Company.status == "active").all()

    company_outs = []
    for c in companies_db:
        doc_count = db.query(Document).filter(Document.company_id == c.id).count()
        chunk_count = db.query(Chunk).filter(Chunk.company_id == c.id).count()
        company_outs.append(CompanyOut(
            id=c.id,
            name=c.name,
            slug=c.slug,
            description=c.description,
            status=c.status,
            created_at=c.created_at,
            document_count=doc_count,
            chunk_count=chunk_count
        ))

    return UserOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        role=user.role,
        status=user.status,
        permissions=permissions,
        companies=company_outs,
        active_company_id=active_company_id
    )

@router.get("/demo-accounts", response_model=List[DemoAccountOut])
def get_demo_accounts():
    """List the 8 pre-seeded demo accounts with password hints."""
    return DEMO_ACCOUNTS

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with username and password, return JWT token."""
    user = db.query(User).filter(User.username == req.username.strip().lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password. Please verify credentials."
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive."
        )

    # Resolve active company
    active_company_id = req.company_id
    if not active_company_id:
        if user.role == "PLATFORM_ADMIN":
            first_comp = db.query(Company).filter(Company.status == "active").first()
            active_company_id = first_comp.id if first_comp else ""
        else:
            first_mem = db.query(UserCompany).filter(UserCompany.user_id == user.id).first()
            if not first_mem:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User has no company memberships assigned."
                )
            active_company_id = first_mem.company_id

    # Verify company exists
    company = db.query(Company).filter(Company.id == active_company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned company not found.")

    token_str = generate_token_for_user(
        user_id=user.id,
        username=user.username,
        role=user.role,
        company_id=active_company_id
    )

    user_out = build_user_out(user, active_company_id, db)
    return Token(
        access_token=token_str,
        token_type="bearer",
        expires_in=28800,
        user=user_out
    )

@router.get("/me", response_model=UserOut)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve profile and assigned companies for authenticated user."""
    # Default active company
    first_mem = db.query(UserCompany).filter(UserCompany.user_id == current_user.id).first()
    active_id = first_mem.company_id if first_mem else ""
    if current_user.role == "PLATFORM_ADMIN" and not active_id:
        comp = db.query(Company).first()
        active_id = comp.id if comp else ""
    return build_user_out(current_user, active_id, db)
