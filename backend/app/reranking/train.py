import os
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from backend.app.reranking.features import calculate_rerank_features
from backend.app.reranking.model import MODEL_PATH

def train_reranker_model(training_data: List[Dict[str, Any]], save_path: Path = MODEL_PATH) -> Dict[str, Any]:
    """Train XGBoost binary classifier on synthetic relevance pairs.
    training_data format:
    [{
       "query": "...",
       "chunk_text": "...",
       "cosine_sim": 0.8,
       "title": "...",
       "department": "...",
       "doc_type": "...",
       "version": "...",
       "effective_date": "...",
       "page": 1,
       "label": 1
    }, ...]
    """
    X_list = []
    y_list = []

    for item in training_data:
        feats = calculate_rerank_features(
            query=item["query"],
            chunk_text=item["chunk_text"],
            cosine_sim=item.get("cosine_sim", 0.5),
            title=item.get("title", ""),
            department=item.get("department", ""),
            doc_type=item.get("doc_type", ""),
            version=item.get("version", "1.0"),
            effective_date=item.get("effective_date", ""),
            page=item.get("page", 1)
        )
        X_list.append(feats)
        y_list.append(item["label"])

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)

    if len(X) < 10:
        # Not enough samples to train
        return {"status": "insufficient_data", "samples": len(X)}

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(
        n_estimators=50,
        max_depth=4,
        learning_rate=0.1,
        eval_metric="logloss",
        random_state=42
    )

    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

    val_accuracy = float(model.score(X_val, y_val))
    save_path.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(save_path))

    return {
        "status": "trained",
        "samples": len(X),
        "validation_accuracy": val_accuracy,
        "model_file": str(save_path)
    }

