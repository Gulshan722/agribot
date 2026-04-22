# src/generation/faithfulness.py
from typing import List, Dict, Any
from groq import Groq
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def check_faithfulness(
    answer: str,
    chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Verify the answer is fully supported by retrieved context.
    Flags hallucinations before they reach the farmer.
    """
    context = "\n\n".join([
        f"[{i+1}] {c['content'][:300]}"
        for i, c in enumerate(chunks)
    ])

    prompt = f"""You are a strict fact-checker for an agricultural AI system.

CONTEXT (retrieved from verified documents):
{context}

ANSWER TO CHECK:
{answer}

Task: Check if every factual claim in the ANSWER is supported by the CONTEXT.

Respond in this exact format:
FAITHFUL: yes/no
SCORE: 0.0 to 1.0
ISSUES: (list any unsupported claims, or "none" if fully faithful)"""

    client = Groq(api_key=config.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=300,
    )

    raw = response.choices[0].message.content.strip()
    logger.info(f"Faithfulness check:\n{raw}")

    lines = {}
    for line in raw.split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            lines[key.strip()] = val.strip()

    score = float(lines.get("SCORE", "0.5"))
    faithful = lines.get("FAITHFUL", "no").lower() == "yes"
    issues = lines.get("ISSUES", "unknown")

    return {
        "faithful": faithful,
        "score": score,
        "issues": issues,
        "flagged": score < 0.7
    }