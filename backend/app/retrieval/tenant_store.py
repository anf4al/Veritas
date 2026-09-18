from typing import List, Optional, Callable
from backend.app.retrieval.vector_store import get_vector_store, VectorPayload, VectorSearchResult
from backend.app.retrieval.embeddings import get_embedding_provider
from backend.app.retrieval.query_expander import expand_query_for_retrieval
from backend.app.auth.permissions import check_document_access

class TenantKnowledgeStore:
    """Tenant-scoped Knowledge Store facade providing isolated retrieval and indexing."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.vector_store = get_vector_store()
        self.embedding_provider = get_embedding_provider()

    def search_authorized(
        self,
        query: str,
        user_role: str,
        top_k: int = 40,
        use_expansion: bool = True
    ) -> List[VectorSearchResult]:
        """Perform permission-aware vector search strictly within this tenant.
        Uses normalized/expanded query for embedding to improve semantic recall without
        altering the original prompt passed to the LLM.
        """
        search_query = expand_query_for_retrieval(query) if use_expansion else query
        query_vector = self.embedding_provider.embed_text(search_query)

        # Define document access filter callback
        def access_filter(payload: VectorPayload) -> bool:
            return check_document_access(
                role=user_role,
                doc_department=payload.department,
                doc_confidentiality=payload.confidentiality,
                doc_type=payload.document_type,
                title=payload.title
            )

        return self.vector_store.search(
            query_vector=query_vector,
            tenant_id=self.tenant_id,
            top_k=top_k,
            filter_func=access_filter
        )

    def index_document_chunks(self, payloads: List[VectorPayload]):
        """Index chunks ensuring tenant_id matches."""
        for p in payloads:
            p.tenant_id = self.tenant_id
        self.vector_store.add_payloads(payloads)

    def get_chunk_count(self) -> int:
        return self.vector_store.count(tenant_id=self.tenant_id)

