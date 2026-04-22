# src/ingestion/loader.py
import os
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger(__name__)

def load_pdf(file_path: Path) -> List[Dict[str, Any]]:
    """Extract text from a PDF file, one dict per page."""
    documents = []
    try:
        reader = PdfReader(str(file_path))
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                documents.append({
                    "content": text.strip(),
                    "metadata": {
                        "source": file_path.name,
                        "source_path": str(file_path),
                        "page": page_num + 1,
                        "total_pages": len(reader.pages),
                        "file_type": "pdf",
                        "domain": "agriculture"
                    }
                })
        logger.info(f"Loaded PDF: {file_path.name} — {len(documents)} pages")
    except Exception as e:
        logger.error(f"Failed to load {file_path.name}: {e}")
    return documents


def load_text(file_path: Path) -> List[Dict[str, Any]]:
    """Load a plain text or markdown file as a single document."""
    try:
        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            return []
        logger.info(f"Loaded text file: {file_path.name}")
        return [{
            "content": text,
            "metadata": {
                "source": file_path.name,
                "source_path": str(file_path),
                "page": 1,
                "total_pages": 1,
                "file_type": file_path.suffix.lstrip("."),
                "domain": "agriculture"
            }
        }]
    except Exception as e:
        logger.error(f"Failed to load {file_path.name}: {e}")
        return []


def load_all_documents(data_dir: str = None) -> List[Dict[str, Any]]:
    """
    Load all supported files from the raw data directory.
    Supported: .pdf, .txt, .md
    """
    data_dir = Path(data_dir or config.RAW_DATA_DIR)
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return []

    all_docs = []
    supported = {".pdf": load_pdf, ".txt": load_text, ".md": load_text}

    files = list(data_dir.iterdir())
    if not files:
        logger.warning(f"No files found in {data_dir}. Add some agricultural PDFs!")
        return []

    for file_path in sorted(files):
        loader_fn = supported.get(file_path.suffix.lower())
        if loader_fn:
            docs = loader_fn(file_path)
            all_docs.extend(docs)
        else:
            logger.warning(f"Skipping unsupported file: {file_path.name}")

    logger.info(f"Total pages/sections loaded: {len(all_docs)}")
    return all_docs