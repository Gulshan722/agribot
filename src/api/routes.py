# src/api/routes.py
import json
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from src.api.schemas import (
    QuestionRequest, AnswerResponse, HealthResponse,
    FeedbackRequest
)
from src.agribot import ask
from src.retrieval.vector_store import get_collection_info
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Check if all components are running correctly."""
    try:
        info = get_collection_info()
        qdrant_status = f"ok — {info['total_vectors']} vectors"
    except Exception as e:
        qdrant_status = f"error: {str(e)}"

    bm25_path = Path("data/processed/bm25_index.pkl")
    bm25_status = "ok" if bm25_path.exists() else "index not found"

    return HealthResponse(
        status="ok",
        qdrant=qdrant_status,
        bm25=bm25_status,
        embedding_model=config.EMBEDDING_MODEL,
        llm_model=config.LLM_MODEL,
    )


@router.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """
    Main endpoint — farmer asks a question, AgriBot answers with citations.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(request.query) > 500:
        raise HTTPException(status_code=400, detail="Query too long (max 500 chars)")

    logger.info(f"POST /ask — query: '{request.query}'")

    try:
        result = ask(
            query=request.query,
            run_faithfulness_check=request.run_faithfulness_check
        )
        return AnswerResponse(**result)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    """
    Save user feedback for improving the system over time.
    Stored locally in data/eval/feedback.jsonl
    """
    if not 1 <= feedback.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": feedback.query,
        "answer": feedback.answer[:200],
        "rating": feedback.rating,
        "comment": feedback.comment
    }

    feedback_path = Path("data/eval/feedback.jsonl")
    feedback_path.parent.mkdir(parents=True, exist_ok=True)
    with open(feedback_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    logger.info(f"Feedback saved — rating: {feedback.rating}/5")
    return {"status": "ok", "message": "Thank you for your feedback!"}


@router.get("/stats")
def get_stats():
    """Return basic usage stats from feedback log."""
    feedback_path = Path("data/eval/feedback.jsonl")
    if not feedback_path.exists():
        return {"total_feedback": 0, "average_rating": None}

    entries = []
    with open(feedback_path) as f:
        for line in f:
            entries.append(json.loads(line))

    if not entries:
        return {"total_feedback": 0, "average_rating": None}

    avg_rating = sum(e["rating"] for e in entries) / len(entries)
    return {
        "total_feedback": len(entries),
        "average_rating": round(avg_rating, 2),
        "recent_queries": [e["query"] for e in entries[-5:]]
    }