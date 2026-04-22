# src/ingestion/chunker.py
import re
import json
from pathlib import Path
from typing import List, Dict, Any
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def clean_text(text: str) -> str:
    """Remove excessive whitespace and fix common PDF extraction artifacts."""
    text = re.sub(r'\n{3,}', '\n\n', text)       # collapse 3+ newlines → 2
    text = re.sub(r'[ \t]{2,}', ' ', text)        # collapse multiple spaces
    text = re.sub(r'-\n(\w)', r'\1', text)         # fix hyphenated line breaks
    return text.strip()


def split_into_chunks(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[str]:
    """
    Split text into overlapping chunks by sentence boundaries.
    Tries to keep sentences together rather than cutting mid-sentence.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP

    # Split on sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # If adding this sentence stays within limit, keep building
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            # Save current chunk if it has content
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            # Start new chunk with overlap from end of previous chunk
            overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
            current_chunk = overlap_text + " " + sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return [c for c in chunks if len(c) > 50]  # drop tiny fragments


def chunk_documents(
    documents: List[Dict[str, Any]],
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[Dict[str, Any]]:
    """
    Take raw loaded documents and return a flat list of chunks,
    each with full metadata for citation and tracing.
    """
    all_chunks = []
    chunk_id = 0

    for doc in documents:
        raw_text = clean_text(doc["content"])
        chunks = split_into_chunks(raw_text, chunk_size, chunk_overlap)

        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"chunk_{chunk_id:05d}",
                "content": chunk_text,
                "metadata": {
                    **doc["metadata"],               # inherit source, page, etc.
                    "chunk_index": i,                # position within this page
                    "total_chunks_in_page": len(chunks),
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_text.split()),
                }
            })
            chunk_id += 1

    logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} pages/sections")
    return all_chunks


def save_chunks(chunks: List[Dict[str, Any]], output_path: str = None) -> str:
    """Save processed chunks to a JSON file for inspection and reuse."""
    output_path = output_path or f"{config.PROCESSED_DATA_DIR}/chunks.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(chunks)} chunks to {output_path}")
    return output_path