import json
import numpy as np
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from backend.app.core.config import settings

@dataclass
class VectorPayload:
    chunk_id: str
    document_id: str
    tenant_id: str
    text: str
    title: str
    document_type: str
    department: str
    version: str
    effective_date: Optional[str]
    confidentiality: str
    page: int
    section: Optional[str]
    vector: List[float]
    metadata_json: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VectorSearchResult:
    chunk_id: str
    document_id: str
    tenant_id: str
    text: str
    title: str
    document_type: str
    department: str
    version: str
    effective_date: Optional[str]
    confidentiality: str
    page: int
    section: Optional[str]
    score: float
    metadata_json: Dict[str, Any] = field(default_factory=dict)

class VectorStore:
    """Tenant-aware vector store interface."""
    def add_payloads(self, payloads: List[VectorPayload]):
        raise NotImplementedError

    def search(
        self,
        query_vector: List[float],
        tenant_id: str,
        top_k: int = 40,
        filter_func: Optional[Callable[[VectorPayload], bool]] = None
    ) -> List[VectorSearchResult]:
        raise NotImplementedError

    def delete_document(self, document_id: str):
        raise NotImplementedError

    def count(self, tenant_id: Optional[str] = None) -> int:
        raise NotImplementedError

class LocalVectorStore(VectorStore):
    """In-memory and locally persistent tenant-partitioned vector store."""
    def __init__(self):
        # Store indexed by tenant_id -> list of VectorPayload
        self._tenants: Dict[str, List[VectorPayload]] = {}
        # Precomputed matrices for fast vectorized dot product
        self._matrices: Dict[str, np.ndarray] = {}

    def add_payloads(self, payloads: List[VectorPayload]):
        for p in payloads:
            if p.tenant_id not in self._tenants:
                self._tenants[p.tenant_id] = []
            # Check if chunk already exists
            existing_idx = next((i for i, item in enumerate(self._tenants[p.tenant_id]) if item.chunk_id == p.chunk_id), None)
            if existing_idx is not None:
                self._tenants[p.tenant_id][existing_idx] = p
            else:
                self._tenants[p.tenant_id].append(p)

        # Invalidate matrices for updated tenants
        updated_tenants = {p.tenant_id for p in payloads}
        for tid in updated_tenants:
            self._rebuild_matrix(tid)

    def _rebuild_matrix(self, tenant_id: str):
        payloads = self._tenants.get(tenant_id, [])
        if not payloads:
            self._matrices.pop(tenant_id, None)
            return
        mat = np.array([p.vector for p in payloads], dtype=np.float32)
        # Ensure unit normalization for cosine similarity
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._matrices[tenant_id] = mat / norms

    def _ensure_hydrated(self, tenant_id: str):
        if tenant_id not in self._tenants or not self._tenants[tenant_id]:
            try:
                from backend.app.core.database import SessionLocal
                from backend.app.models.document import Document, Chunk
                from backend.app.retrieval.embeddings import get_embedding_provider

                db = SessionLocal()
                chunks = db.query(Chunk).join(Document).filter(Chunk.company_id == tenant_id).all()
                if chunks:
                    emb_provider = get_embedding_provider()
                    texts = [c.text for c in chunks]
                    embs = emb_provider.embed_batch(texts)

                    payloads = []
                    for idx, c in enumerate(chunks):
                        payloads.append(VectorPayload(
                            chunk_id=c.id,
                            document_id=c.document_id,
                            tenant_id=c.company_id,
                            text=c.text,
                            title=c.document.title,
                            document_type=c.document.document_type,
                            department=c.document.department,
                            version=c.document.version,
                            effective_date=c.document.effective_date,
                            confidentiality=c.document.confidentiality,
                            page=c.page or 1,
                            section=c.section or "General",
                            vector=embs[idx] if idx < len(embs) else [],
                            metadata_json=c.metadata_json or {}
                        ))
                    self.add_payloads(payloads)
                db.close()
            except Exception:
                pass

    def search(
        self,
        query_vector: List[float],
        tenant_id: str,
        top_k: int = 40,
        filter_func: Optional[Callable[[VectorPayload], bool]] = None
    ) -> List[VectorSearchResult]:
        """Search vectors strictly isolated to tenant_id with optional permission filter."""
        self._ensure_hydrated(tenant_id)
        payloads = self._tenants.get(tenant_id, [])
        if not payloads or tenant_id not in self._matrices:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        mat = self._matrices[tenant_id]
        # Fast dot product similarity
        scores = np.dot(mat, q_vec)

        # Sort indices descending
        sorted_indices = np.argsort(-scores)

        results: List[VectorSearchResult] = []
        for idx in sorted_indices:
            payload = payloads[idx]
            score = float(scores[idx])

            # Apply permission / metadata filter function
            if filter_func is not None and not filter_func(payload):
                continue

            results.append(VectorSearchResult(
                chunk_id=payload.chunk_id,
                document_id=payload.document_id,
                tenant_id=payload.tenant_id,
                text=payload.text,
                title=payload.title,
                document_type=payload.document_type,
                department=payload.department,
                version=payload.version,
                effective_date=payload.effective_date,
                confidentiality=payload.confidentiality,
                page=payload.page,
                section=payload.section,
                score=score,
                metadata_json=payload.metadata_json
            ))

            if len(results) >= top_k:
                break

        return results

    def delete_document(self, document_id: str):
        for tid in list(self._tenants.keys()):
            self._tenants[tid] = [p for p in self._tenants[tid] if p.document_id != document_id]
            self._rebuild_matrix(tid)

    def count(self, tenant_id: Optional[str] = None) -> int:
        if tenant_id:
            return len(self._tenants.get(tenant_id, []))
        return sum(len(items) for items in self._tenants.values())

    def clear(self):
        self._tenants.clear()
        self._matrices.clear()

# Global vector store singleton
_vector_store_instance = LocalVectorStore()

def get_vector_store() -> LocalVectorStore:
    return _vector_store_instance
