# src/retrieval/reranker.py
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

_reranker = None

def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        logger.info(f"Loading reranker: {config.RERANKER_MODEL}")
        _reranker = CrossEncoder(config.RERANKER_MODEL)
        logger.info("Reranker loaded")
    return _reranker


def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = None
) -> List[Dict[str, Any]]:
    """
    Re-score each (query, chunk) pair with a cross-encoder.
    
    Unlike bi-encoders (which embed query and doc separately),
    a cross-encoder sees BOTH together — much more accurate
    but slower, so we only run it on the top 30 candidates.
    """
    top_k = top_k or config.TOP_K_RERANK
    if not candidates:
        return []

    reranker = get_reranker()

    # Build pairs for cross-encoder
    pairs = [(query, doc["content"]) for doc in candidates]
    scores = reranker.predict(pairs)

    # Attach reranker scores
    for doc, score in zip(candidates, scores):
        doc["rerank_score"] = round(float(score), 4)

    # Sort by reranker score and return top_k
    reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

    logger.info(
        f"Reranked {len(candidates)} candidates → kept top {top_k}. "
        f"Best score: {reranked[0]['rerank_score']:.4f}"
    )

    return reranked[:top_k]