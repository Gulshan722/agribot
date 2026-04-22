# eval/generate_eval_dataset.py
"""
Auto-generate a golden evaluation dataset from your agricultural documents.
Run once to create data/eval/golden_dataset.json
"""
import json
import random
from pathlib import Path
from groq import Groq
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 20 realistic farming questions covering all 3 documents
SEED_QUESTIONS = [
    "how to manage drought stress in wheat crops",
    "what fertilizer should I use for rice paddy",
    "how to improve soil health for farming",
    "organic methods to control pests on vegetables",
    "when to apply nitrogen fertilizer to crops",
    "how to reduce soil erosion on farmland",
    "what are climate smart agriculture practices",
    "how to manage waterlogging in fields",
    "best practices for integrated pest management",
    "how to improve crop yield in dry conditions",
    "what is urea deep placement technique",
    "how to build soil organic matter",
    "signs of nutrient deficiency in crops",
    "how to manage crop residues after harvest",
    "what is conservation agriculture",
    "how to reduce greenhouse gas emissions from farming",
    "best irrigation methods for small farmers",
    "how to identify and control fungal diseases in crops",
    "what cover crops improve soil fertility",
    "how does crop rotation help soil health",
]


def generate_expected_answer(question: str, client: Groq) -> dict:
    """Use Groq to generate a reference answer for a question."""
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{
            "role": "user",
            "content": f"""You are an expert agricultural scientist.
Give a clear, factual, 2-3 sentence answer to this farming question.
Be specific and practical.

Question: {question}

Answer:"""
        }],
        temperature=0.1,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def build_dataset():
    logger.info("Generating evaluation dataset...")
    client = Groq(api_key=config.GROQ_API_KEY)

    dataset = []
    for i, question in enumerate(SEED_QUESTIONS):
        logger.info(f"  [{i+1}/{len(SEED_QUESTIONS)}] {question}")
        try:
            expected = generate_expected_answer(question, client)
            dataset.append({
                "id": f"eval_{i+1:03d}",
                "question": question,
                "expected_answer": expected,
                "category": categorize(question)
            })
        except Exception as e:
            logger.error(f"Failed for '{question}': {e}")

    # Save
    out_path = Path("data/eval/golden_dataset.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(dataset, f, indent=2)

    logger.info(f"Saved {len(dataset)} Q&A pairs to {out_path}")
    return dataset


def categorize(question: str) -> str:
    q = question.lower()
    if any(w in q for w in ["pest", "disease", "fungal", "control"]):
        return "pest_management"
    elif any(w in q for w in ["soil", "organic", "erosion", "fertility"]):
        return "soil_management"
    elif any(w in q for w in ["fertilizer", "nitrogen", "nutrient", "urea"]):
        return "fertilizer"
    elif any(w in q for w in ["water", "irrigation", "drought", "waterlog"]):
        return "water_management"
    elif any(w in q for w in ["climate", "emission", "greenhouse"]):
        return "climate_smart"
    return "general"


if __name__ == "__main__":
    build_dataset()