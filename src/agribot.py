# src/agribot.py
"""
Main AgriBot pipeline — combines retrieval + generation.
This is the single function your API and frontend will call.
"""
from typing import Dict, Any
from src.retrieval.search import search
from src.generation.generator import generate_answer
from src.generation.faithfulness import check_faithfulness
from src.utils.logger import get_logger

logger = get_logger(__name__)


def ask(query: str, run_faithfulness_check: bool = True) -> Dict[str, Any]:
    """
    Full AgriBot pipeline:
    
    Farmer's question
      → Hybrid retrieval (BM25 + vector + RRF)
      → Cross-encoder reranking
      → Grounded LLM answer with citations
      → Faithfulness verification
      → Final response with sources
    """
    logger.info(f"AgriBot received query: '{query}'")

    # Step 1: Retrieve best chunks
    chunks = search(query)
    if not chunks:
        return {
            "query": query,
            "answer": "I could not find relevant information in my knowledge base.",
            "citations": [],
            "faithfulness": None,
            "flagged": False
        }

    # Step 2: Generate grounded answer
    result = generate_answer(query, chunks)

    # Step 3: Faithfulness check (optional, costs one extra LLM call)
    faithfulness = None
    if run_faithfulness_check:
        faithfulness = check_faithfulness(result["answer"], chunks)
        if faithfulness["flagged"]:
            logger.warning(
                f"Answer flagged for low faithfulness! "
                f"Score: {faithfulness['score']} | Issues: {faithfulness['issues']}"
            )

    return {
        "query": query,
        "answer": result["answer"],
        "citations": result["citations"],
        "faithfulness": faithfulness,
        "flagged": faithfulness["flagged"] if faithfulness else False,
        "chunks_used": len(chunks)
    }