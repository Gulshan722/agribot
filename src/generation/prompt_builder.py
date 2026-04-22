# src/generation/prompt_builder.py
from typing import List, Dict, Any

def build_prompt(query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Build the message list for the LLM.
    Each chunk becomes a numbered context block with source info.
    The system prompt instructs strict grounding — no hallucination.
    """

    # Build numbered context blocks
    context_blocks = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["metadata"].get("source", "unknown")
        page   = chunk["metadata"].get("page", "?")
        context_blocks.append(
            f"[{i}] (Source: {source}, Page {page})\n{chunk['content'].strip()}"
        )

    context_text = "\n\n".join(context_blocks)

    system_prompt = """You are AgriBot, an expert agricultural assistant helping farmers, \
agricultural officers, and farming students in South Asia.

STRICT RULES:
1. Answer ONLY using the provided context below. Do not use outside knowledge.
2. Every factual claim MUST have an inline citation like [1], [2], or [1,3].
3. If the context does not contain enough information, say:
   "I don't have enough information in my knowledge base to answer this confidently. \
Please consult your local agricultural extension officer."
4. Keep answers practical, clear, and actionable for farmers.
5. Use simple language — avoid overly technical jargon.
6. End every answer with a "Sources:" section listing the cited references.

CONTEXT:
{context}"""

    return [
        {
            "role": "system",
            "content": system_prompt.format(context=context_text)
        },
        {
            "role": "user",
            "content": query
        }
    ]


def format_answer_with_citations(
    answer: str,
    chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Parse the LLM answer and attach full source metadata
    for each citation reference found in the text.
    """
    import re

    # Find all citation numbers used e.g. [1], [2,3], [1,2,4]
    raw_citations = re.findall(r'\[(\d+(?:,\s*\d+)*)\]', answer)
    cited_indices = set()
    for match in raw_citations:
        for num in match.split(','):
            cited_indices.add(int(num.strip()))

    # Build citation metadata for each referenced chunk
    citations = []
    for idx in sorted(cited_indices):
        chunk_idx = idx - 1  # convert 1-based to 0-based
        if 0 <= chunk_idx < len(chunks):
            chunk = chunks[chunk_idx]
            citations.append({
                "number": idx,
                "source": chunk["metadata"].get("source", "unknown"),
                "page": chunk["metadata"].get("page", "?"),
                "chunk_id": chunk["metadata"].get("chunk_id", ""),
                "preview": chunk["content"][:150] + "..."
            })

    return {
        "answer": answer,
        "citations": citations,
        "num_sources": len(citations)
    }