# src/retrieval/bm25_store.py
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

BM25_INDEX_PATH = "data/processed/bm25_index.pkl"
BM25_CHUNKS_PATH = "data/processed/bm25_chunks.pkl"


def tokenize(text: str) -> List[str]:
    """Simple whitespace + lowercase tokenizer."""
    return text.lower().split()


def build_bm25_index(chunks: List[Dict[str, Any]]) -> BM25Okapi:
    """Build a BM25 index from chunks and save to disk."""
    logger.info(f"Building BM25 index from {len(chunks)} chunks...")

    corpus = [tokenize(chunk["content"]) for chunk in chunks]
    index = BM25Okapi(corpus)

    # Save index and chunk references together
    Path(BM25_INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(index, f)
    with open(BM25_CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    logger.info(f"BM25 index saved to {BM25_INDEX_PATH}")
    return index


def load_bm25_index():
    """Load a previously saved BM25 index and its chunks."""
    if not Path(BM25_INDEX_PATH).exists():
        raise FileNotFoundError(
            "BM25 index not found. Run the ingestion pipeline first."
        )
    with open(BM25_INDEX_PATH, "rb") as f:
        index = pickle.load(f)
    with open(BM25_CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)
    logger.info(f"Loaded BM25 index with {len(chunks)} chunks")
    return index, chunks


def bm25_search(
    query: str,
    top_k: int = None
) -> List[Dict[str, Any]]:
    """
    Search the BM25 index for the most relevant chunks.
    Returns top_k results with a normalised score.
    """
    top_k = top_k or config.TOP_K_RETRIEVAL
    index, chunks = load_bm25_index()

    tokens = tokenize(query)
    scores = index.get_scores(tokens)

    # Pair each chunk with its score and sort descending
    scored = sorted(
        enumerate(scores), key=lambda x: x[1], reverse=True
    )[:top_k]

    results = []
    max_score = scored[0][1] if scored and scored[0][1] > 0 else 1.0

    for idx, score in scored:
        if score <= 0:
            continue
        chunk = chunks[idx]
        results.append({
            "content": chunk["content"],
            "score": float(score / max_score),   # normalise to 0-1
            "metadata": chunk.get("metadata", {})
        })

    return results