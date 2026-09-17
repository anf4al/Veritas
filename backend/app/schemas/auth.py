from typing import List, Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: "UserOut"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
    company_id: Optional[str] = None

class UserOut(BaseModel):
    id: str
    username: str
    display_name: str
    role: str
    status: str
    permissions: List[str] = []
    companies: List["CompanyOut"] = []
    active_company_id: Optional[str] = None

    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str
    role: str
    company_ids: List[str] = []

class DemoAccountOut(BaseModel):
    title: str
    username: str
    role: str
    company_name: str
    access_description: str
    password_hint: str

# Rebuild models for forward refs
from backend.app.schemas.company import CompanyOut
Token.model_rebuild()
UserOut.model_rebuild()

