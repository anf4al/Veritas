import re
from typing import List, Tuple

# Bidirectional and domain-specific enterprise terminology expansions
TERM_EXPANSIONS: List[Tuple[re.Pattern, str, str]] = [
    # (pattern, expansion_term, check_term)
    (re.compile(r"\bwfh\b", re.IGNORECASE), "Work From Home policy", "work from home"),
    (re.compile(r"\bwork\s+from\s+home\b", re.IGNORECASE), "WFH policy", "wfh"),
    (re.compile(r"\bholidays?\b", re.IGNORECASE), "annual leave paid leave statutory holidays", "annual leave"),
    (re.compile(r"\bvacations?\b", re.IGNORECASE), "annual leave paid leave", "annual leave"),
    (re.compile(r"\bpaid\s+leave\b", re.IGNORECASE), "annual leave sick leave", "annual leave"),
    (re.compile(r"\bpto\b", re.IGNORECASE), "paid time off annual leave", "annual leave"),
    (re.compile(r"\btime\s+off\b", re.IGNORECASE), "annual leave leave policy", "annual leave"),
    (re.compile(r"\binfosec\b", re.IGNORECASE), "Information Security policy", "information security"),
    (re.compile(r"\bmsa\b", re.IGNORECASE), "Master Services Agreement contract", "master services agreement"),
    (re.compile(r"\bsla\s+breach(es)?\b", re.IGNORECASE), "SLA violations Service Level Agreement default", "sla violation"),
]

def expand_query_for_retrieval(query: str) -> str:
    """Expand user query with synonymous enterprise terms to maximize semantic and lexical recall
    during candidate generation without mutating the original user question presented to the LLM.
    """
    if not query:
        return ""

    query_clean = query.strip()
    expansions_to_add: List[str] = []

    for pattern, expansion, check_term in TERM_EXPANSIONS:
        if pattern.search(query_clean):
            # Only add if the expansion's core concept is not already in the query
            if check_term.lower() not in query_clean.lower():
                expansions_to_add.append(expansion)

    if expansions_to_add:
        # Deduplicate terms while preserving order
        unique_terms = []
        for exp in expansions_to_add:
            for term in exp.split():
                if term.lower() not in query_clean.lower() and term.lower() not in [u.lower() for u in unique_terms]:
                    unique_terms.append(term)

        if unique_terms:
            return f"{query_clean} {' '.join(unique_terms)}"

    return query_clean

