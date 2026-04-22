# src/retrieval/search.py
from typing import List, Dict, Any
from src.retrieval.hybrid import hybrid_search
from src.retrieval.reranker import rerank
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def search(query: str) -> List[Dict[str, Any]]:
    """
    Full retrieval pipeline for a farmer's question:
    
    Query
      → Hybrid search (vector + BM25 + RRF fusion)   [top 30]
      → Cross-encoder reranking                       [top 5]
      → Return final chunks with metadata + scores
    """
    logger.info(f"Query: '{query}'")

    # Step 1: Hybrid retrieval — cast a wide net
    candidates = hybrid_search(query, top_k=config.TOP_K_RETRIEVAL)

    # Step 2: Rerank — pick the best from the net
    final_results = rerank(query, candidates, top_k=config.TOP_K_RERANK)

    return final_results


def format_results_for_display(results: List[Dict[str, Any]]) -> str:
    """Pretty print results for terminal testing."""
    lines = []
    for i, doc in enumerate(results, 1):
        source = doc["metadata"].get("source", "unknown")
        page   = doc["metadata"].get("page", "?")
        found  = ", ".join(doc.get("found_by", ["?"]))
        rrf    = doc.get("rrf_score", 0)
        rank   = doc.get("rerank_score", 0)

        lines.append(f"\n{'='*60}")
        lines.append(f"Result #{i}")
        lines.append(f"Source  : {source}  (page {page})")
        lines.append(f"Found by: {found}")
        lines.append(f"RRF score   : {rrf:.6f}")
        lines.append(f"Rerank score: {rank:.4f}")
        lines.append(f"{'─'*60}")
        lines.append(doc["content"][:400])
        if len(doc["content"]) > 400:
            lines.append("... [truncated]")

    return "\n".join(lines)