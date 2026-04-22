# src/retrieval/hybrid.py
from typing import List, Dict, Any
from src.retrieval.vector_store import vector_search
from src.retrieval.bm25_store import bm25_search
from src.ingestion.embedder import embed_query
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Merge two ranked lists using Reciprocal Rank Fusion.
    
    Formula: score(doc) = Σ 1 / (k + rank)
    k=60 is standard — smooths out high-rank dominance.
    
    A document appearing at rank 1 in BOTH lists scores higher
    than one appearing at rank 1 in only one list.
    """
    scores: Dict[str, float] = {}
    doc_map: Dict[str, Dict[str, Any]] = {}

    # Score vector results
    for rank, doc in enumerate(vector_results, start=1):
        key = doc["content"][:100]  # use content prefix as unique key
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
        doc_map[key] = {**doc, "found_by": ["vector"]}

    # Score BM25 results — add to existing or create new
    for rank, doc in enumerate(bm25_results, start=1):
        key = doc["content"][:100]
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
        if key in doc_map:
            doc_map[key]["found_by"].append("bm25")
        else:
            doc_map[key] = {**doc, "found_by": ["bm25"]}

    # Sort by fused score descending
    sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)

    results = []
    for key in sorted_keys:
        doc = doc_map[key]
        doc["rrf_score"] = round(scores[key], 6)
        results.append(doc)

    return results


def hybrid_search(
    query: str,
    top_k: int = None
) -> List[Dict[str, Any]]:
    """
    Full hybrid search pipeline:
    1. Embed query → vector search in Qdrant
    2. Tokenize query → BM25 keyword search
    3. Fuse results with RRF
    4. Return top_k merged results
    """
    top_k = top_k or config.TOP_K_RETRIEVAL
    logger.info(f"Hybrid search for: '{query}'")

    # Run both searches in parallel (sequential for now, easy to parallelise later)
    query_vector = embed_query(query)
    vector_results = vector_search(query_vector, top_k=top_k)
    bm25_results = bm25_search(query, top_k=top_k)

    logger.info(f"  Vector results : {len(vector_results)}")
    logger.info(f"  BM25 results   : {len(bm25_results)}")

    # Fuse
    fused = reciprocal_rank_fusion(vector_results, bm25_results)
    logger.info(f"  Fused results  : {len(fused)}")

    return fused[:top_k]