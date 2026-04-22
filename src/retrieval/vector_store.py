# src/retrieval/vector_store.py
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue
)
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Embedding dimension for BAAI/bge-large-en-v1.5
VECTOR_DIM = 1024


def get_client() -> QdrantClient:
    return QdrantClient(url=config.QDRANT_URL)


def create_collection(recreate: bool = False):
    """Create the Qdrant collection if it doesn't exist."""
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]

    if config.QDRANT_COLLECTION in existing:
        if recreate:
            client.delete_collection(config.QDRANT_COLLECTION)
            logger.info(f"Deleted existing collection: {config.QDRANT_COLLECTION}")
        else:
            logger.info(f"Collection already exists: {config.QDRANT_COLLECTION}")
            return

    client.create_collection(
        collection_name=config.QDRANT_COLLECTION,
        vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
    )
    logger.info(f"Created collection: {config.QDRANT_COLLECTION} (dim={VECTOR_DIM})")


def upsert_chunks(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    id_offset: int = 0          # ← add this parameter
):
    """Upload chunks + their vectors to Qdrant."""
    client = get_client()

    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        points.append(PointStruct(
            id=i + id_offset,   # ← use offset here
            vector=vector,
            payload={
                "chunk_id": chunk["chunk_id"],
                "content": chunk["content"],
                **chunk["metadata"]
            }
        ))

    batch_size = 100
    for start in range(0, len(points), batch_size):
        batch = points[start:start + batch_size]
        client.upsert(collection_name=config.QDRANT_COLLECTION, points=batch)
        logger.info(f"Upserted points {start + id_offset} to {start + id_offset + len(batch)}")

    logger.info(f"Total points upserted: {len(points)}")

def vector_search(
    query_vector: List[float],
    top_k: int = None,
    filter_source: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search Qdrant for the most similar chunks to query_vector.
    """
    client = get_client()
    top_k = top_k or config.TOP_K_RETRIEVAL

    search_filter = None
    if filter_source:
        search_filter = Filter(
            must=[FieldCondition(key="source", match=MatchValue(value=filter_source))]
        )

    results = client.query_points(
        collection_name=config.QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        query_filter=search_filter,
        with_payload=True
    ).points

    return [
        {
            "content": r.payload.get("content", ""),
            "score": r.score,
            "metadata": {k: v for k, v in r.payload.items() if k != "content"}
        }
        for r in results
    ]


def get_collection_info() -> Dict[str, Any]:
    """Return basic stats about the collection."""
    client = get_client()
    info = client.get_collection(config.QDRANT_COLLECTION)
    # vectors_count was renamed in newer qdrant-client versions
    count = (
        info.vectors_count
        if hasattr(info, "vectors_count")
        else info.points_count
    )
    return {
        "name": config.QDRANT_COLLECTION,
        "total_vectors": count,
        "status": str(info.status)
    }