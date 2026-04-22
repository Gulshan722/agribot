# src/ingestion/pipeline.py
import json
import hashlib
from pathlib import Path
from src.ingestion.loader import load_all_documents
from src.ingestion.chunker import chunk_documents, save_chunks
from src.ingestion.embedder import embed_texts
from src.retrieval.vector_store import create_collection, upsert_chunks, get_collection_info
from src.retrieval.bm25_store import build_bm25_index
from src.utils.logger import get_logger

logger = get_logger(__name__)

REGISTRY_PATH = "data/processed/ingested_files.json"


def load_registry() -> dict:
    """Track which files have already been ingested."""
    if Path(REGISTRY_PATH).exists():
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    return {}


def save_registry(registry: dict):
    Path(REGISTRY_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


def file_hash(filepath: str) -> str:
    """MD5 hash of file — detects if a file changed since last ingestion."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def get_new_files(data_dir: str = "data/raw") -> list:
    """Return only files not yet ingested or changed since last ingestion."""
    registry = load_registry()
    new_files = []

    for filepath in sorted(Path(data_dir).iterdir()):
        if filepath.suffix.lower() not in [".pdf", ".txt", ".md"]:
            continue
        current_hash = file_hash(str(filepath))
        if registry.get(filepath.name) != current_hash:
            new_files.append(filepath)
            logger.info(f"New/changed file detected: {filepath.name}")
        else:
            logger.info(f"Already ingested, skipping: {filepath.name}")

    return new_files


def run_ingestion_pipeline(
    recreate_collection: bool = False,
    incremental: bool = True
):
    logger.info("=" * 55)
    logger.info("AgriBot Ingestion Pipeline Starting")
    logger.info("=" * 55)

    # Decide which files to process
    if incremental and not recreate_collection:
        new_files = get_new_files()
        if not new_files:
            logger.info("No new files found. Knowledge base is up to date!")
            return
        logger.info(f"Processing {len(new_files)} new file(s)...")
        # Load only new files
        from src.ingestion.loader import load_pdf, load_text
        docs = []
        for fp in new_files:
            loaders = {".pdf": load_pdf, ".txt": load_text, ".md": load_text}
            fn = loaders.get(fp.suffix.lower())
            if fn:
                docs.extend(fn(fp))
    else:
        # Full re-ingestion
        logger.info("Full re-ingestion of all documents...")
        docs = load_all_documents()

    if not docs:
        logger.error("No documents to process.")
        return

    # Step 2: Chunk
    logger.info(f"Step 1 — Chunking {len(docs)} pages...")
    new_chunks = chunk_documents(docs)

    # Merge with existing chunks if incremental
    existing_chunks = []
    chunks_path = Path("data/processed/chunks.json")
    if incremental and chunks_path.exists() and not recreate_collection:
        with open(chunks_path) as f:
            existing_chunks = json.load(f)
        logger.info(f"Loaded {len(existing_chunks)} existing chunks")

    all_chunks = existing_chunks + new_chunks
    save_chunks(all_chunks)
    logger.info(f"Total chunks: {len(all_chunks)} ({len(new_chunks)} new)")

    # Step 3: Embed only new chunks
    logger.info(f"Step 2 — Embedding {len(new_chunks)} new chunks...")
    texts = [chunk["content"] for chunk in new_chunks]
    embeddings = embed_texts(texts, batch_size=32)

    # Step 4: Store in Qdrant
    logger.info("Step 3 — Storing in Qdrant...")
    create_collection(recreate=recreate_collection)

    # Offset IDs so new chunks don't overwrite existing ones
    offset = len(existing_chunks)
    upsert_chunks(new_chunks, embeddings, id_offset=offset)

    info = get_collection_info()
    logger.info(f"Qdrant total vectors: {info['total_vectors']}")

    # Step 5: Rebuild BM25 on ALL chunks
    logger.info("Step 4 — Rebuilding BM25 index on full corpus...")
    build_bm25_index(all_chunks)

    # Update registry — mark these files as done
    registry = load_registry()
    for filepath in Path("data/raw").iterdir():
        if filepath.suffix.lower() in [".pdf", ".txt", ".md"]:
            registry[filepath.name] = file_hash(str(filepath))
    save_registry(registry)

    logger.info("=" * 55)
    logger.info("Ingestion complete!")
    logger.info(f"  New pages processed : {len(docs)}")
    logger.info(f"  New chunks created  : {len(new_chunks)}")
    logger.info(f"  Total in knowledge base: {len(all_chunks)} chunks")
    logger.info(f"  Qdrant vectors      : {info['total_vectors']}")
    logger.info("=" * 55)


if __name__ == "__main__":
    import sys
    recreate = "--recreate" in sys.argv
    run_ingestion_pipeline(recreate_collection=recreate, incremental=True)