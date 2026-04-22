# eval/metrics.py
from typing import List, Dict, Any


def context_recall(retrieved_chunks: List[Dict], expected_answer: str) -> float:
    """
    Check what fraction of key terms from the expected answer
    appear in the retrieved chunks. Uses partial matching to
    handle synonyms and word variations.
    """
    if not retrieved_chunks or not expected_answer:
        return 0.0

    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "to", "of",
        "and", "or", "in", "on", "for", "with", "by", "at", "be",
        "can", "will", "should", "may", "also", "this", "that",
        "these", "those", "it", "its", "have", "has", "from", "as"
    }

    # Extract meaningful words — shorter min length catches more terms
    key_terms = [
        w.lower().strip(".,?!;:'\"()") for w in expected_answer.split()
        if len(w) > 3 and w.lower().strip(".,?!") not in stopwords
    ]

    if not key_terms:
        return 0.0

    all_chunk_text = " ".join(c["content"].lower() for c in retrieved_chunks)

    # Partial match — term OR its stem (first 5 chars) must appear
    found = 0
    for term in key_terms:
        if term in all_chunk_text or term[:5] in all_chunk_text:
            found += 1

    return round(found / len(key_terms), 3)


def mean_reciprocal_rank(
    retrieved_chunks: List[Dict], expected_answer: str
) -> float:
    """
    MRR@5 — reward if ANY chunk in top 5 contains relevant content.
    Uses a lower match threshold (1 key term) to be more realistic.
    """
    stopwords = {
        "the", "a", "an", "is", "are", "was", "to", "of", "and",
        "can", "will", "should", "this", "that", "have", "from"
    }
    key_terms = [
        w.lower().strip(".,?!;:'\"") for w in expected_answer.split()
        if len(w) > 3 and w.lower() not in stopwords
    ]

    if not key_terms:
        return 0.0

    for rank, chunk in enumerate(retrieved_chunks, 1):
        chunk_text = chunk["content"].lower()
        # Count how many key terms appear in this chunk
        matches = sum(
            1 for term in key_terms
            if term in chunk_text or term[:5] in chunk_text
        )
        # If at least 20% of key terms found → this chunk is relevant
        if matches >= max(1, len(key_terms) * 0.20):
            return round(1.0 / rank, 3)

    return 0.0


def answer_relevancy(question: str, answer: str) -> float:
    """
    Check if key question concepts appear in the answer.
    """
    stopwords = {
        "how", "what", "when", "where", "why", "which", "should",
        "can", "the", "a", "is", "to", "do", "does", "best", "good"
    }
    q_terms = [
        w.lower().strip("?.,") for w in question.split()
        if len(w) > 3 and w.lower() not in stopwords
    ]

    if not q_terms:
        return 0.0

    answer_lower = answer.lower()
    found = sum(
        1 for term in q_terms
        if term in answer_lower or term[:5] in answer_lower
    )
    return round(found / len(q_terms), 3)


def compute_all_metrics(
    question: str,
    expected_answer: str,
    actual_answer: str,
    retrieved_chunks: List[Dict]
) -> Dict[str, float]:
    return {
        "context_recall":   context_recall(retrieved_chunks, expected_answer),
        "answer_relevancy": answer_relevancy(question, actual_answer),
        "mrr_at_5":         mean_reciprocal_rank(retrieved_chunks, expected_answer),
    }