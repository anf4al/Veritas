from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Citation(BaseModel):
    id: str
    document_id: str
    title: str
    page: Optional[int] = 1
    section: Optional[str] = None
    version: Optional[str] = "1.0"
    effective_date: Optional[str] = None
    confidentiality: Optional[str] = "internal"
    department: Optional[str] = None
    relevance_score: Optional[float] = 0.0

class EvidenceChunk(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    text: str
    page: Optional[int] = 1
    section: Optional[str] = None
    version: Optional[str] = "1.0"
    effective_date: Optional[str] = None
    department: Optional[str] = None
    similarity_score: float = 0.0
    rerank_score: float = 0.0

class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str

class ChatRequest(BaseModel):
    query: str
    history: List[ChatMessage] = []
    company_id: Optional[str] = None
    stream: bool = False
    enable_agent: bool = True

class AgentStepInfo(BaseModel):
    step: int
    action: str
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    observation_summary: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    insufficient_evidence: bool = False
    citations: List[Citation] = []
    evidence: List[EvidenceChunk] = []
    agent_steps: List[AgentStepInfo] = []
    trace_id: str
    latency_ms: float
    provider_used: str
    model_used: str

