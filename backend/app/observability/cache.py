import hashlib
from typing import Dict, Any, Optional, List

class EnterpriseCache:
    """In-memory cache for query embeddings and tenant-partitioned retrieval results."""

    def __init__(self, max_items: int = 2000):
        self._embedding_cache: Dict[str, List[float]] = {}
        # tenant_id -> hash(query + user_role) -> cached_result
        self._retrieval_cache: Dict[str, Dict[str, Any]] = {}
        self.max_items = max_items

    def _hash_key(self, text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

    def get_embedding(self, text: str) -> Optional[List[float]]:
        key = self._hash_key(text)
        return self._embedding_cache.get(key)

    def set_embedding(self, text: str, vector: List[float]):
        if len(self._embedding_cache) >= self.max_items:
            self._embedding_cache.pop(next(iter(self._embedding_cache)))
        key = self._hash_key(text)
        self._embedding_cache[key] = vector

    def get_retrieval(self, tenant_id: str, query: str, user_role: str) -> Optional[Any]:
        tenant_dict = self._retrieval_cache.get(tenant_id, {})
        key = self._hash_key(f"{query}:{user_role}")
        return tenant_dict.get(key)

    def set_retrieval(self, tenant_id: str, query: str, user_role: str, result: Any):
        if tenant_id not in self._retrieval_cache:
            self._retrieval_cache[tenant_id] = {}
        tenant_dict = self._retrieval_cache[tenant_id]
        if len(tenant_dict) >= 500:
            tenant_dict.pop(next(iter(tenant_dict)))
        key = self._hash_key(f"{query}:{user_role}")
        tenant_dict[key] = result

    def invalidate_tenant(self, tenant_id: str):
        """Invalidate all cached search results for this tenant when documents change."""
        self._retrieval_cache.pop(tenant_id, None)

_cache_instance = None

def get_cache() -> EnterpriseCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = EnterpriseCache()
    return _cache_instance
