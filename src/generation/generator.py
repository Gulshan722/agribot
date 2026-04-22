# src/generation/generator.py
from typing import List, Dict, Any
from groq import Groq
from src.generation.prompt_builder import build_prompt, format_answer_with_citations
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

_client = None

def get_client() -> Groq:
    global _client
    if _client is None:
        if not config.GROQ_API_KEY or config.GROQ_API_KEY == "":
            raise ValueError(
                "Groq API key not set. Add GROQ_API_KEY=gsk_... to your .env file"
            )
        _client = Groq(api_key=config.GROQ_API_KEY)
        logger.info("Groq client initialized")
    return _client


def generate_answer(
    query: str,
    chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Given a farmer's question and retrieved chunks,
    generate a grounded answer with inline citations using Groq.
    """
    logger.info(f"Generating answer for: '{query}'")
    logger.info(f"Using {len(chunks)} context chunks")

    messages = build_prompt(query, chunks)

    client = get_client()
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=1000,
    )

    raw_answer = response.choices[0].message.content.strip()
    result = format_answer_with_citations(raw_answer, chunks)

    logger.info(f"Answer generated. Citations used: {result['num_sources']}")
    return result