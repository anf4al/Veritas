import re
from typing import List, Set, Optional

# Words that should never be considered standalone named entities
COMMON_STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "at",
    "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "can", "will", "just", "should",
    "now", "what", "which", "who", "whom", "this", "that", "these", "those",
    "am", "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "having", "do", "does", "did", "doing", "would", "could", "ought",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
    "how", "why", "many", "much", "our", "their", "your", "my", "its"
}

# Generic domain nouns that occur frequently across all enterprise documentation
# and should not be treated as unique named entities by themselves
GENERIC_DOMAIN_TERMS: Set[str] = {
    "policy", "policies", "contract", "contracts", "agreement", "agreements",
    "procedure", "procedures", "standard", "standards", "guideline", "guidelines",
    "clause", "clauses", "term", "terms", "condition", "conditions", "section",
    "article", "report", "document", "documents", "record", "records",
    "review", "assessment", "plan", "sop", "overview", "definition", "definitions",
    "current", "previous", "prior", "latest", "new", "old", "active", "superseded",
    "allow", "allows", "permitted", "permits", "prohibited", "prohibits", "require",
    "requires", "required", "change", "changed", "changes", "difference", "differences",
    "termination", "terminate", "risk", "risks", "high", "low", "medium",
    "annual", "leave", "holiday", "holidays", "days", "employee", "employees",
    "staff", "worker", "workers", "management", "company", "organization"
}

# Known enterprise names and vendor proper nouns
KNOWN_ENTERPRISE_ENTITIES: List[str] = [
    "Vendor Atlas",
    "Atlas",
    "Asterion Technologies",
    "Asterion",
    "Northstar Manufacturing",
    "Northstar",
    "Meridian Healthcare Services",
    "Meridian Healthcare",
    "Meridian",
    "Apex Logistics",
    "Apex",
]

def normalize_entity_text(text: str) -> str:
    """Normalize text for entity matching: lowercase, hyphens/underscores to spaces, strip punctuation."""
    if not text:
        return ""
    # Replace hyphens, underscores, slashes with spaces
    cleaned = re.sub(r"[-_/]", " ", text.lower())
    # Remove remaining punctuation except alphanumeric and space
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    # Collapse multiple spaces
    return re.sub(r"\s+", " ", cleaned).strip()

def extract_query_entities(query: str) -> List[str]:
    """Extract meaningful named entities from user queries.
    Identifies:
    1. Known enterprise and vendor entities (e.g. 'Vendor Atlas', 'Apex Logistics')
    2. Capitalized multi-word proper nouns in the original query (e.g. 'Vendor Atlas')
    3. Document ID codes (e.g. 'AST-HR-POL-2026-004')
    4. Quoted terms (e.g. '"Vendor Atlas"')
    Excludes ordinary domain terms like 'current', 'policy', 'termination', etc.
    """
    if not query:
        return []

    entities: List[str] = []
    normalized_q = normalize_entity_text(query)

    # 1. Check known entities first
    for known in KNOWN_ENTERPRISE_ENTITIES:
        norm_known = normalize_entity_text(known)
        # Use word boundary check
        pattern = r"\b" + re.escape(norm_known) + r"\b"
        if re.search(pattern, normalized_q):
            if known not in entities and not any(known in existing for existing in entities):
                entities.append(known)

    # 2. Check document IDs (e.g. AST-HR-POL-2026-004)
    doc_id_matches = re.findall(r"\b[A-Z]{2,4}-[A-Z]{2,4}-[A-Z0-9\-_]+\b", query)
    for did in doc_id_matches:
        if did not in entities:
            entities.append(did)

    # 3. Quoted substrings (e.g. "Vendor Atlas")
    quoted = re.findall(r'["\']([^"\']{2,40})["\']', query)
    for q_item in quoted:
        norm_item = normalize_entity_text(q_item)
        tokens = norm_item.split()
        # If it's not purely stopwords or generic domain terms
        if any(t not in COMMON_STOPWORDS and t not in GENERIC_DOMAIN_TERMS for t in tokens):
            if q_item not in entities:
                entities.append(q_item)

    # 4. Capitalized multi-word sequences in the original query (excluding sentence start if single word)
    cap_sequences = re.findall(r"\b[A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)+\b", query)
    for cap in cap_sequences:
        norm_cap = normalize_entity_text(cap)
        cap_tokens = norm_cap.split()
        # Filter out sequences composed entirely of generic words
        meaningful = [t for t in cap_tokens if t not in COMMON_STOPWORDS and t not in GENERIC_DOMAIN_TERMS]
        if meaningful and cap not in entities:
            # Check that it's not a substring of an already extracted entity
            if not any(cap.lower() == e.lower() for e in entities):
                entities.append(cap)

    # Deduplicate while preserving multi-word preference (e.g. prefer 'Vendor Atlas' over just 'Atlas')
    final_entities: List[str] = []
    # Sort by length descending so longer phrases take precedence
    entities.sort(key=lambda s: len(s), reverse=True)
    for e in entities:
        norm_e = normalize_entity_text(e)
        if not norm_e:
            continue
        # Don't add a single word if a multi-word entity already contains it (e.g. don't add 'Atlas' if 'Vendor Atlas' is added)
        is_sub = False
        for fe in final_entities:
            norm_fe = normalize_entity_text(fe)
            if norm_e in norm_fe.split():
                is_sub = True
                break
        if not is_sub:
            final_entities.append(e)

    return final_entities

def entity_present_in_text(entity: str, text: str) -> bool:
    """Check if normalized entity appears in normalized text."""
    if not entity or not text:
        return False
    norm_entity = normalize_entity_text(entity)
    norm_text = normalize_entity_text(text)
    
    if not norm_entity:
        return False
        
    pattern = r"\b" + re.escape(norm_entity) + r"\b"
    if re.search(pattern, norm_text):
        return True
        
    # For multi-word entities, also check if all core tokens are present
    tokens = [t for t in norm_entity.split() if t not in COMMON_STOPWORDS and t not in GENERIC_DOMAIN_TERMS]
    if len(tokens) >= 2:
        return all(r"\b" + re.escape(t) + r"\b" in norm_text or re.search(r"\b" + re.escape(t) + r"\b", norm_text) for t in tokens)
        
    return False

def compute_entity_presence_score(
    entities: List[str],
    chunk_text: str,
    title: str = "",
    section: str = ""
) -> float:
    """Score entity presence (0.0 to 1.0).
    If no specific entities were extracted from query, returns 1.0 (neutral/not penalized).
    If entities were extracted, returns the fraction of entities found in chunk text/title/section.
    """
    if not entities:
        return 1.0

    combined_text = f"{title} {section} {chunk_text}"
    matches = sum(1 for e in entities if entity_present_in_text(e, combined_text))
    return float(matches / len(entities))

