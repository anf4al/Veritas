import math
import hashlib
from abc import ABC, abstractmethod
from typing import List
import numpy as np
from backend.app.core.config import settings

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

class DeterministicEmbeddingProvider(EmbeddingProvider):
    """Deterministic hash/projection embedding provider for instant offline execution,
    unit testing, or fallback when neural weights are downloading.
    Outputs unit-normalized vectors of dimension 384.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _embed_single(self, text: str) -> List[float]:
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()

        for idx, word in enumerate(words):
            # Deterministic hash for word to bucket indices
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            bucket1 = h % self.dimension
            bucket2 = (h >> 16) % self.dimension
            sign1 = 1.0 if (h >> 8) & 1 else -1.0
            sign2 = 1.0 if (h >> 24) & 1 else -1.0

            weight = 1.0 / math.sqrt(idx + 1)
            vec[bucket1] += sign1 * weight
            vec[bucket2] += sign2 * weight * 0.5

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_text(self, text: str) -> List[float]:
        return self._embed_single(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(t) for t in texts]

class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Neural embedding provider utilizing sentence-transformers/all-MiniLM-L6-v2."""
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._fallback = DeterministicEmbeddingProvider()

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                # Log or fallback gracefully if network/torch weight unavailable
                self._model = None
        return self._model

    def embed_text(self, text: str) -> List[float]:
        model = self._get_model()
        if model is not None:
            try:
                emb = model.encode(text, normalize_embeddings=True)
                return emb.tolist()
            except Exception:
                pass
        return self._fallback.embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        if model is not None:
            try:
                embs = model.encode(texts, normalize_embeddings=True)
                return embs.tolist()
            except Exception:
                pass
        return self._fallback.embed_batch(texts)

# Singleton embedding instance
_embedding_instance: EmbeddingProvider = None

def get_embedding_provider() -> EmbeddingProvider:
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = SentenceTransformerEmbeddingProvider(settings.EMBEDDING_MODEL_NAME)
    return _embedding_instance

