"""Pydantic schemas for Veritas API."""
from backend.app.schemas.auth import (
    Token,
    TokenData,
    LoginRequest,
    UserOut,
    UserCreate,
    DemoAccountOut
)
from backend.app.schemas.company import (
    CompanyOut,
    CompanyCreate,
    CompanySwitchRequest
)
from backend.app.schemas.document import (
    DocumentOut,
    ChunkOut,
    IngestResponse,
    DocumentFilter
)
from backend.app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    Citation,
    EvidenceChunk
)
from backend.app.schemas.observability import (
    TraceOut,
    SpanOut,
    MetricsOut,
    ProviderStatusOut
)
from backend.app.schemas.evaluation import (
    EvaluationRunOut,
    EvaluationRunCreate,
    EvaluationComparisonOut
)

__all__ = [
    "Token",
    "TokenData",
    "LoginRequest",
    "UserOut",
    "UserCreate",
    "DemoAccountOut",
    "CompanyOut",
    "CompanyCreate",
    "CompanySwitchRequest",
    "DocumentOut",
    "ChunkOut",
    "IngestResponse",
    "DocumentFilter",
    "ChatRequest",
    "ChatResponse",
    "Citation",
    "EvidenceChunk",
    "TraceOut",
    "SpanOut",
    "MetricsOut",
    "ProviderStatusOut",
    "EvaluationRunOut",
    "EvaluationRunCreate",
    "EvaluationComparisonOut"
]

