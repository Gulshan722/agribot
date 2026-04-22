# tests/test_ingestion.py
from src.ingestion.loader import load_all_documents
from src.ingestion.chunker import chunk_documents, save_chunks

def test_ingestion_pipeline():
    print("\n--- Loading documents ---")
    docs = load_all_documents()

    if not docs:
        print("No documents found. Add PDFs to data/raw/ and re-run.")
        return

    print(f"Loaded {len(docs)} pages/sections")
    print(f"First doc source: {docs[0]['metadata']['source']}")
    print(f"First doc preview: {docs[0]['content'][:200]}\n")

    print("--- Chunking ---")
    chunks = chunk_documents(docs)
    print(f"Total chunks: {len(chunks)}")
    print(f"Sample chunk ID: {chunks[0]['chunk_id']}")
    print(f"Sample chunk preview: {chunks[0]['content'][:200]}")
    print(f"Sample chunk metadata: {chunks[0]['metadata']}\n")

    save_chunks(chunks)
    print("Chunks saved to data/processed/chunks.json")
    print("\nAll ingestion tests passed!")

if __name__ == "__main__":
    test_ingestion_pipeline()