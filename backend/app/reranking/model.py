import os
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from backend.app.reranking.features import calculate_rerank_features
from backend.app.retrieval.vector_store import VectorSearchResult

MODEL_PATH = Path(__file__).resolve().parent / "reranker.xgb"

class XGBoostReranker:
    def __init__(self, model_file: Path = MODEL_PATH):
        self.model_file = model_file
        self._model = None
        self._load_model()

    def _load_model(self):
        if self.model_file.exists():
            try:
                import xgboost as xgb
                model = xgb.XGBClassifier()
                model.load_model(str(self.model_file))
                self._model = model
            except Exception:
                self._model = None
        else:
            self._model = None

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def rerank(
        self,
        query: str,
        candidates: List[VectorSearchResult],
        top_k: int = 8
    ) -> List[Tuple[VectorSearchResult, float]]:
        """Rerank candidate chunks by XGBoost predicted relevance probability (or deterministic fallback).
        Returns list of (candidate, rerank_score).
        """
        if not candidates:
            return []

        # Extract features for each candidate
        feature_matrix = []
        for c in candidates:
            feats = calculate_rerank_features(
                query=query,
                chunk_text=c.text,
                cosine_sim=c.score,
                title=c.title,
                department=c.department,
                doc_type=c.document_type,
                version=c.version,
                effective_date=c.effective_date or "",
                page=c.page,
                section=c.section or ""
            )
            feature_matrix.append(feats)

        X = np.array(feature_matrix, dtype=np.float32)

        if self._model is not None:
            try:
                # Predict probability of class 1 (relevant)
                probs = self._model.predict_proba(X)[:, 1]
                scores = [float(p) for p in probs]
            except Exception:
                scores = self._fallback_score(X)
        else:
            scores = self._fallback_score(X)

        # Pair candidates with scores
        scored_pairs = list(zip(candidates, scores))
        # Sort descending by rerank score
        scored_pairs.sort(key=lambda item: item[1], reverse=True)

        return scored_pairs[:top_k]

    def _fallback_score(self, X: np.ndarray) -> List[float]:
        """Deterministic weighted linear combination fallback:
        0.35 * cosine + 0.25 * bm25 + 0.15 * lexical + 0.15 * recency + 0.10 * metadata
        """
        weights = np.array([0.35, 0.15, 0.25, 0.10, 0.15, 0.05, 0.05, 0.05, 0.0, 0.0], dtype=np.float32)
        # Dot product
        raw = np.dot(X, weights)
        # Sigmoid to map to [0, 1]
        probs = 1.0 / (1.0 + np.exp(-raw * 2.0))
        return [float(p) for p in probs]

# Global reranker singleton
_reranker_instance = None

def get_reranker() -> XGBoostReranker:
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = XGBoostReranker()
    return _reranker_instance

