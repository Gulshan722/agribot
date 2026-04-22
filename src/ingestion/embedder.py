# src/ingestion/embedder.py
from typing import List
from sentence_transformers import SentenceTransformer
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Load once at module level — M4 will use MPS (Apple Silicon GPU) automatically
_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
    return _model


def embed_texts(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Embed a list of strings. Returns a list of float vectors.
    Runs in batches to avoid memory issues on large corpora.
    """
    model = get_embedding_model()
    logger.info(f"Embedding {len(texts)} texts in batches of {batch_size}...")
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True   # cosine similarity works better normalized
    )
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """Embed a single query string for retrieval."""
    model = get_embedding_model()
    vector = model.encode(query, normalize_embeddings=True)
    return vector.tolist()