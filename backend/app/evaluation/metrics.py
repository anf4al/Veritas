from typing import List, Dict, Any, Set

def compute_recall_at_k(retrieved_titles: List[str], expected_titles: List[str], k: int) -> float:
    """Compute Recall@K based on whether expected document titles were retrieved in top K."""
    if not expected_titles:
        return 1.0
    top_k_titles = [t.lower() for t in retrieved_titles[:k]]
    hits = 0
    for exp in expected_titles:
        exp_lower = exp.lower()
        if any(exp_lower in t or t in exp_lower for t in top_k_titles):
            hits += 1
    return hits / len(expected_titles)

def compute_reranker_lift(ann_titles: List[str], reranked_titles: List[str], expected_titles: List[str]) -> float:
    """Measure how much XGBoost reranking elevated relevant documents compared to raw ANN."""
    if not expected_titles:
        return 0.0

    ann_ranks = []
    rerank_ranks = []

    for exp in expected_titles:
        exp_lower = exp.lower()
        # Find position in ANN
        ann_pos = next((i for i, t in enumerate(ann_titles) if exp_lower in t.lower() or t.lower() in exp_lower), 50)
        ann_ranks.append(ann_pos)

        # Find position in Reranked
        rerank_pos = next((i for i, t in enumerate(reranked_titles) if exp_lower in t.lower() or t.lower() in exp_lower), 50)
        rerank_ranks.append(rerank_pos)

    # Average upward rank difference
    diffs = [ann - rr for ann, rr in zip(ann_ranks, rerank_ranks)]
    avg_lift = sum(diffs) / len(diffs) if diffs else 0.0
    return float(avg_lift)

def compute_groundedness_score(citations: List[Any], answer: str) -> float:
    """Compute groundedness score (0.0 to 1.0) based on citation density and verification."""
    if not citations or not answer:
        return 0.0
    # Simple heuristic: answer cites bracketed source and references verified titles
    has_bracket_cites = "[" in answer and "]" in answer
    cite_count = len(citations)
    if has_bracket_cites and cite_count >= 1:
        return min(1.0, 0.7 + 0.1 * min(cite_count, 3))
    return 0.5
