import re
import math
from typing import List, Dict, Any
import numpy as np

def extract_tokens(text: str) -> List[str]:
    """Extract lowercase alphanumeric tokens."""
    return re.findall(r"\b[a-z0-9]+\b", text.lower())

def compute_lexical_overlap(query_tokens: List[str], doc_tokens: List[str]) -> float:
    """Jaccard-like keyword overlap coefficient."""
    if not query_tokens or not doc_tokens:
        return 0.0
    q_set = set(query_tokens)
    d_set = set(doc_tokens)
    intersection = q_set.intersection(d_set)
    return len(intersection) / len(q_set)

def compute_bm25_lite(query_tokens: List[str], doc_tokens: List[str], avg_doc_len: float = 150.0) -> float:
    """Lite BM25 term frequency match."""
    if not query_tokens or not doc_tokens:
        return 0.0
    k1 = 1.5
    b = 0.75
    doc_len = len(doc_tokens)
    score = 0.0
    doc_counts: Dict[str, int] = {}
    for t in doc_tokens:
        doc_counts[t] = doc_counts.get(t, 0) + 1

    for q in query_tokens:
        tf = doc_counts.get(q, 0)
        if tf > 0:
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_len / avg_doc_len))
            score += numerator / denominator
    return score / (len(query_tokens) + 1e-5)

def compute_version_recency_score(version: str, effective_date: str = "", query: str = "") -> float:
    """Score currentness: 2026/v3.0 -> 1.0, 2025/v2.0 -> 0.6, 2024/v1.0 -> 0.3."""
    q_lower = query.lower()
    txt = f"{version} {effective_date}".lower()
    
    # Version comparison intent
    if any(k in q_lower for k in ["compare", "changed between", "difference", "versus", " vs "]):
        if any(y in txt for y in ["2025", "2026", "2.0", "3.0"]):
            return 1.0
        return 0.5

    # Prior / previous version intent
    if any(k in q_lower for k in ["previous", "prior", "former", "old", "superseded", "2025", "earlier", "past"]):
        if "2025" in q_lower and "2026" not in q_lower:
            if "2025" in txt or "2.0" in txt:
                return 1.0
            elif "2026" in txt or "3.0" in txt:
                return 0.2
        elif any(k in q_lower for k in ["previous", "prior", "former", "old", "superseded", "earlier", "past"]):
            if "2025" in txt or "2.0" in txt or "superseded" in txt:
                return 1.0
            elif "2026" in txt or "3.0" in txt:
                return 0.2

    # Explicit current / latest intent
    if any(k in q_lower for k in ["current", "latest", "now", "active", "present", "today"]):
        if "2026" in txt or "3.0" in txt or "current" in txt:
            return 1.0
        elif "2025" in txt or "2.0" in txt:
            return 0.15
        elif "2024" in txt or "1.0" in txt or "outdated" in txt or "superseded" in txt:
            return 0.05
        return 0.3

    # Default: favor current / latest
    if "2026" in txt or "3.0" in txt or "current" in txt:
        return 1.0
    elif "2025" in txt or "2.0" in txt:
        return 0.4
    elif "2024" in txt or "1.0" in txt or "outdated" in txt or "superseded" in txt:
        return 0.2
    return 0.4

def compute_metadata_match(query: str, title: str, department: str, doc_type: str) -> float:
    """Check if query mentions title, department, or document type."""
    q_lower = query.lower()
    match_score = 0.0
    if department.lower() in q_lower:
        match_score += 0.4
    if doc_type.lower() in q_lower:
        match_score += 0.3
    # Check title words overlap
    title_words = [w for w in title.lower().split() if len(w) > 3]
    if any(w in q_lower for w in title_words):
        match_score += 0.3
    return min(1.0, match_score)

def calculate_rerank_features(
    query: str,
    chunk_text: str,
    cosine_sim: float,
    title: str = "",
    department: str = "",
    doc_type: str = "",
    version: str = "1.0",
    effective_date: str = "",
    page: int = 1
) -> List[float]:
    """Calculate the 10 feature values for XGBoost reranker:
    0: cosine_similarity
    1: lexical_overlap
    2: bm25_lite
    3: metadata_match
    4: version_recency
    5: chunk_length_norm (log-scale normalized)
    6: exact_title_mention (binary)
    7: department_in_query (binary)
    8: page_penalty (reciprocal of page)
    9: query_length_norm
    """
    from backend.app.retrieval.query_expander import expand_query_for_retrieval

    expanded_query = expand_query_for_retrieval(query)
    q_tokens = extract_tokens(expanded_query)
    d_tokens = extract_tokens(chunk_text)

    lex_overlap = compute_lexical_overlap(q_tokens, d_tokens)
    bm25 = compute_bm25_lite(q_tokens, d_tokens)
    meta_match = compute_metadata_match(expanded_query, title, department, doc_type)
    recency = compute_version_recency_score(version, effective_date, query)

    chunk_len_norm = min(1.0, math.log(len(d_tokens) + 1) / 7.0)
    title_words = [w for w in title.lower().split() if len(w) > 3]
    title_mention = 1.0 if any(w in expanded_query.lower() for w in title_words) else 0.0
    dept_mention = 1.0 if department.lower() in expanded_query.lower() else 0.0
    page_pen = 1.0 / math.sqrt(max(1, page))
    q_len_norm = min(1.0, len(q_tokens) / 20.0)

    return [
        float(cosine_sim),
        float(lex_overlap),
        float(bm25),
        float(meta_match),
        float(recency),
        float(chunk_len_norm),
        float(title_mention),
        float(dept_mention),
        float(page_pen),
        float(q_len_norm)
    ]

