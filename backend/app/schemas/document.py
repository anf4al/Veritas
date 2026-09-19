from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ChunkOut(BaseModel):
    id: str
    document_id: str
    company_id: str
    chunk_index: int
    text: str
    page: Optional[int] = 1
    section: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = {}

    model_config = {"from_attributes": True}

class DocumentOut(BaseModel):
    id: str
    company_id: str
    title: str
    filename: str
    document_type: str
    department: str
    version: str
    effective_date: Optional[str] = None
    status: str
    confidentiality: str
    source: Optional[str] = None
    storage_path: Optional[str] = None
    has_file: Optional[bool] = False
    created_at: datetime
    chunk_count: Optional[int] = 0

    model_config = {"from_attributes": True}

class IngestResponse(BaseModel):
    document_id: str
    title: str
    chunks_created: int
    status: str
    message: str

class DocumentFilter(BaseModel):
    department: Optional[str] = None
    document_type: Optional[str] = None
    confidentiality: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None

