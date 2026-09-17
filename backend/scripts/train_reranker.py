import os
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.document import Document, Chunk
from backend.app.evaluation.dataset import SEED_EVALUATION_QUESTIONS
from backend.app.reranking.train import train_reranker_model
from backend.app.reranking.model import MODEL_PATH
from backend.app.retrieval.embeddings import get_embedding_provider
import numpy as np

def generate_training_data(db: Session):
    training_data = []
    emb_provider = get_embedding_provider()

    all_chunks = db.query(Chunk).join(Document).all()
    if not all_chunks:
        print("No chunks found in database. Run seed_database.py first.")
        return []

    print(f"Generating training pairs from {len(SEED_EVALUATION_QUESTIONS)} questions across chunks...")

    for q_item in SEED_EVALUATION_QUESTIONS:
        query = q_item["question"]
        expected_titles = [t.lower() for t in q_item["expected_titles"]]
        q_vec = emb_provider.embed_text(query)

        # Sample positive and negative chunks
        positives = []
        negatives = []

        for chunk in all_chunks:
            title = chunk.document.title
            is_relevant = any(exp in title.lower() or title.lower() in exp for exp in expected_titles)

            chunk_vec = emb_provider.embed_text(chunk.text[:200])
            sim = float(np.dot(q_vec, chunk_vec))

            sample = {
                "query": query,
                "chunk_text": chunk.text,
                "cosine_sim": sim,
                "title": title,
                "department": chunk.document.department,
                "doc_type": chunk.document.document_type,
                "version": chunk.document.version,
                "effective_date": chunk.document.effective_date or "",
                "page": chunk.page or 1,
                "label": 1 if is_relevant else 0
            }

            if is_relevant and len(positives) < 15:
                positives.append(sample)
            elif not is_relevant and len(negatives) < 30:
                negatives.append(sample)

        training_data.extend(positives)
        training_data.extend(negatives)

    return training_data

def train_and_evaluate():
    db = SessionLocal()
    try:
        data = generate_training_data(db)
        if not data:
            print("Failed to build training dataset.")
            return

        print(f"Total training samples: {len(data)}. Training XGBoost relevance model...")
        result = train_reranker_model(data, save_path=MODEL_PATH)
        print(f"Training Result: {result}")
    finally:
        db.close()

if __name__ == "__main__":
    train_and_evaluate()

