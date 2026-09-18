import os
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import numpy as np

from backend.app.core.database import SessionLocal
from backend.app.models.document import Document, Chunk
from backend.app.reranking.train import train_reranker_model
from backend.app.reranking.model import MODEL_PATH
from backend.app.retrieval.embeddings import get_embedding_provider
from backend.app.retrieval.query_expander import expand_query_for_retrieval

TRAINING_SPECS: List[Dict[str, Any]] = [
    # Core WFH and Leave queries
    {
        "query": "What is the current WFH policy?",
        "expected_titles": ["Work From Home Policy 2026", "Employee Handbook 2026"],
        "hard_negatives": ["Work From Home Policy 2025", "Leave Policy 2026", "Travel and Expense Policy 2026", "Reimbursement Policy 2026"],
        "department": "HR"
    },
    {
        "query": "What is the current Work From Home policy?",
        "expected_titles": ["Work From Home Policy 2026", "Employee Handbook 2026"],
        "hard_negatives": ["Work From Home Policy 2025", "Leave Policy 2026", "Travel and Expense Policy 2026", "Reimbursement Policy 2026"],
        "department": "HR"
    },
    {
        "query": "What was the previous WFH policy?",
        "expected_titles": ["Work From Home Policy 2025"],
        "hard_negatives": ["Work From Home Policy 2026", "Employee Handbook 2026", "Leave Policy 2025", "Travel and Expense Policy 2025"],
        "department": "HR"
    },
    {
        "query": "What changed between the 2025 and 2026 WFH policies?",
        "expected_titles": ["Work From Home Policy 2025", "Work From Home Policy 2026"],
        "hard_negatives": ["Leave Policy 2026", "Travel and Expense Policy 2026", "Reimbursement Policy 2025", "Reimbursement Policy 2026"],
        "department": "HR"
    },
    {
        "query": "How many holidays does one get?",
        "expected_titles": ["Employee Handbook 2026", "Leave Policy 2026"],
        "hard_negatives": ["Work From Home Policy 2026", "Work From Home Policy 2025", "Travel and Expense Policy 2026", "Reimbursement Policy 2026"],
        "department": "HR"
    },
    {
        "query": "How many days of annual leave do employees get?",
        "expected_titles": ["Leave Policy 2026", "Employee Handbook 2026"],
        "hard_negatives": ["Leave Policy 2025", "Work From Home Policy 2026", "Travel and Expense Policy 2026", "Reimbursement Policy 2026"],
        "department": "HR"
    },
    {
        "query": "How many annual leave days can an employee carry forward?",
        "expected_titles": ["Leave Policy 2026", "Employee Handbook 2026"],
        "hard_negatives": ["Leave Policy 2025", "Work From Home Policy 2026", "Reimbursement Policy 2026"],
        "department": "HR"
    },
    # Procurement and Vendor queries
    {
        "query": "What changed between the 2025 and 2026 procurement policies?",
        "expected_titles": ["Procurement Policy 2025", "Procurement Policy 2026"],
        "hard_negatives": ["Procurement Policy 2024", "Vendor Atlas Master Services Agreement", "Supplier SLA Compliance Review 2026"],
        "department": "Procurement"
    },
    {
        "query": "What is the current procurement policy?",
        "expected_titles": ["Procurement Policy 2026"],
        "hard_negatives": ["Procurement Policy 2025", "Procurement Policy 2024", "Vendor Atlas Master Services Agreement"],
        "department": "Procurement"
    },
    {
        "query": "Which suppliers violated their SLA more than twice?",
        "expected_titles": ["Vendor Performance Report Q4 2025", "Supplier SLA Compliance Review 2026"],
        "hard_negatives": ["Vendor Atlas Master Services Agreement", "Procurement Policy 2026", "Apex Logistics Service Contract"],
        "department": "Operations"
    },
    {
        "query": "Why was Vendor Atlas classified as high risk?",
        "expected_titles": ["Vendor Atlas Risk Assessment 2026", "Vendor Performance Report Q4 2025"],
        "hard_negatives": ["Apex Logistics Service Contract", "Procurement Policy 2026", "Vendor Atlas Master Services Agreement"],
        "department": "Procurement"
    },
    {
        "query": "Does the current Vendor Atlas contract permit termination for repeated SLA violations?",
        "expected_titles": ["Vendor Atlas Master Services Agreement", "Procurement Policy 2026"],
        "hard_negatives": ["Supplier SLA Compliance Review 2026", "Vendor Performance Report Q4 2025"],
        "department": "Legal"
    },
    # Security and Compliance queries
    {
        "query": "Which information-security procedures changed between 2025 and 2026?",
        "expected_titles": ["Information Security Policy 2025", "Information Security Policy 2026"],
        "hard_negatives": ["Information Security Policy 2024", "Incident Response Plan 2026", "Data Retention Policy 2026"],
        "department": "Security"
    },
    {
        "query": "What is the current information security policy?",
        "expected_titles": ["Information Security Policy 2026"],
        "hard_negatives": ["Information Security Policy 2025", "Data Retention Policy 2026", "Incident Response Plan 2026"],
        "department": "Security"
    },
    {
        "query": "Which contracts expire within 90 days?",
        "expected_titles": ["Vendor Atlas Master Services Agreement", "Apex Logistics Service Contract"],
        "hard_negatives": ["Procurement Policy 2026", "Supplier SLA Compliance Review 2026"],
        "department": "Legal"
    },
    {
        "query": "Which policies mention data retention?",
        "expected_titles": ["Data Retention Policy 2026", "Information Security Policy 2026", "Compliance and Audit Policy 2026"],
        "hard_negatives": ["Employee Handbook 2026", "Leave Policy 2026", "Work From Home Policy 2026"],
        "department": "Compliance"
    },
    {
        "query": "Compare the current reimbursement policy with the previous version.",
        "expected_titles": ["Reimbursement Policy 2025", "Reimbursement Policy 2026"],
        "hard_negatives": ["Reimbursement Policy 2024", "Travel and Expense Policy 2026", "Leave Policy 2026"],
        "department": "HR"
    },
    {
        "query": "What is the previous reimbursement policy?",
        "expected_titles": ["Reimbursement Policy 2025"],
        "hard_negatives": ["Reimbursement Policy 2026", "Travel and Expense Policy 2025"],
        "department": "HR"
    }
]

def generate_training_data(db: Session):
    training_data = []
    emb_provider = get_embedding_provider()

    all_chunks = db.query(Chunk).join(Document).all()
    if not all_chunks:
        print("No chunks found in database. Run seed_database.py first.")
        return []

    print(f"Generating balanced training pairs from {len(TRAINING_SPECS)} enterprise specs across {len(all_chunks)} chunks...")

    # Pre-embed chunks for fast cosine similarity calculation
    chunk_texts = [c.text for c in all_chunks]
    chunk_embs = emb_provider.embed_batch(chunk_texts)

    for spec in TRAINING_SPECS:
        query = spec["query"]
        expected_titles = [t.lower() for t in spec["expected_titles"]]
        hard_neg_titles = [t.lower() for t in spec.get("hard_negatives", [])]
        target_dept = spec.get("department", "").lower()

        search_query = expand_query_for_retrieval(query)
        q_vec = emb_provider.embed_text(search_query)

        positives = []
        hard_negatives = []
        easy_negatives = []

        for idx, chunk in enumerate(all_chunks):
            title = chunk.document.title
            title_lower = title.lower()
            dept_lower = (chunk.document.department or "").lower()

            chunk_vec = chunk_embs[idx]
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
            }

            is_positive = any(exp in title_lower or title_lower in exp for exp in expected_titles)
            is_explicit_hard_neg = any(hn in title_lower or title_lower in hn for hn in hard_neg_titles)
            is_same_dept_wrong_topic = (dept_lower == target_dept) and not is_positive

            if is_positive:
                sample["label"] = 1
                positives.append(sample)
            elif is_explicit_hard_neg or is_same_dept_wrong_topic:
                sample["label"] = 0
                hard_negatives.append(sample)
            else:
                sample["label"] = 0
                easy_negatives.append(sample)

        # Balance: take up to 15 positives, up to 15 hard negatives (prioritize highest cosine sim), up to 10 easy negatives
        positives = positives[:15]
        hard_negatives.sort(key=lambda s: s["cosine_sim"], reverse=True)
        hard_negatives = hard_negatives[:15]
        easy_negatives.sort(key=lambda s: s["cosine_sim"], reverse=True)
        easy_negatives = easy_negatives[:10]

        training_data.extend(positives)
        training_data.extend(hard_negatives)
        training_data.extend(easy_negatives)

    print(f"Generated {len(training_data)} total training samples "
          f"({sum(1 for s in training_data if s['label'] == 1)} pos, "
          f"{sum(1 for s in training_data if s['label'] == 0)} neg).")
    return training_data

def train_and_evaluate():
    db = SessionLocal()
    try:
        data = generate_training_data(db)
        if not data:
            print("Failed to build training dataset.")
            return

        print(f"Training XGBoost relevance reranker on {len(data)} samples...")
        result = train_reranker_model(data, save_path=MODEL_PATH)
        print(f"Training Result: {result}")
        return result
    finally:
        db.close()

if __name__ == "__main__":
    train_and_evaluate()
