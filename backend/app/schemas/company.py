from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CompanyOut(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    document_count: Optional[int] = 0
    chunk_count: Optional[int] = 0

    model_config = {"from_attributes": True}

class CompanyCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class CompanySwitchRequest(BaseModel):
    company_id: str

