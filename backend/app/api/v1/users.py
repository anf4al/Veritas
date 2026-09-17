from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_password_hash
from backend.app.auth.dependencies import get_current_user, require_permission
from backend.app.auth.permissions import Permission, get_role_permissions
from backend.app.models.user import User, UserCompany
from backend.app.models.company import Company
from backend.app.schemas.auth import UserOut, UserCreate
from backend.app.schemas.company import CompanyOut

router = APIRouter(prefix="/users", tags=["Users & Access Control"])

@router.get("", response_model=List[UserOut])
def list_users(
    current_user: User = Depends(require_permission(Permission.USER_READ)),
    db: Session = Depends(get_db)
):
    """List system users and their assigned roles and companies."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    results = []

    for u in users:
        memberships = db.query(UserCompany).filter(UserCompany.user_id == u.id).all()
        comp_ids = [m.company_id for m in memberships]
        comps = db.query(Company).filter(Company.id.in_(comp_ids)).all() if comp_ids else []

        company_outs = [
            CompanyOut(
                id=c.id,
                name=c.name,
                slug=c.slug,
                description=c.description,
                status=c.status,
                created_at=c.created_at
            ) for c in comps
        ]

        results.append(UserOut(
            id=u.id,
            username=u.username,
            display_name=u.display_name,
            role=u.role,
            status=u.status,
            permissions=get_role_permissions(u.role),
            companies=company_outs
        ))
    return results

@router.post("", response_model=UserOut)
def create_user(
    req: UserCreate,
    current_user: User = Depends(require_permission(Permission.USER_MANAGE)),
    db: Session = Depends(get_db)
):
    """Create a new enterprise user account with assigned company memberships."""
    existing = db.query(User).filter(User.username == req.username.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.")

    new_user = User(
        username=req.username.strip().lower(),
        password_hash=get_password_hash(req.password),
        display_name=req.display_name,
        role=req.role
    )
    db.add(new_user)
    db.flush()

    for cid in req.company_ids:
        uc = UserCompany(user_id=new_user.id, company_id=cid)
        db.add(uc)

    db.commit()
    db.refresh(new_user)

    comps = db.query(Company).filter(Company.id.in_(req.company_ids)).all() if req.company_ids else []
    company_outs = [
        CompanyOut(
            id=c.id,
            name=c.name,
            slug=c.slug,
            description=c.description,
            status=c.status,
            created_at=c.created_at
        ) for c in comps
    ]

    return UserOut(
        id=new_user.id,
        username=new_user.username,
        display_name=new_user.display_name,
        role=new_user.role,
        status=new_user.status,
        permissions=get_role_permissions(new_user.role),
        companies=company_outs
    )
