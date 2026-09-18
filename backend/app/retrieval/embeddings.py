from abc import ABC, abstractmethod
from typing import List
from backend.app.core.config import settings

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Production neural embedding provider utilizing sentence-transformers/all-MiniLM-L6-v2.
    Fails explicitly with actionable error if model weights or PyTorch fail to load.
    No silent fallback to hash-based embeddings.
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize SentenceTransformer model '{self.model_name}': {e}. "
                "Ensure torch and sentence-transformers are installed in the active environment."
            ) from e

    def embed_text(self, text: str) -> List[float]:
        if self._model is None:
            self._load_model()
        try:
            emb = self._model.encode(text, normalize_embeddings=True)
            return emb.tolist()
        except Exception as e:
            raise RuntimeError(f"Error generating embedding with '{self.model_name}': {e}") from e

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self._model is None:
            self._load_model()
        try:
            embs = self._model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
            return embs.tolist()
        except Exception as e:
            raise RuntimeError(f"Error generating batch embeddings with '{self.model_name}': {e}") from e

# Singleton embedding instance
_embedding_instance: EmbeddingProvider = None

def get_embedding_provider() -> EmbeddingProvider:
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = SentenceTransformerEmbeddingProvider(settings.EMBEDDING_MODEL_NAME)
    return _embedding_instance
