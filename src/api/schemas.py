# src/api/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class QuestionRequest(BaseModel):
    query: str
    run_faithfulness_check: bool = True

class CitationResponse(BaseModel):
    number: int
    source: str
    page: int | str
    preview: str

class FaithfulnessResponse(BaseModel):
    faithful: bool
    score: float
    issues: str
    flagged: bool

class AnswerResponse(BaseModel):
    query: str
    answer: str
    citations: List[CitationResponse]
    faithfulness: Optional[FaithfulnessResponse]
    flagged: bool
    chunks_used: int

class HealthResponse(BaseModel):
    status: str
    qdrant: str
    bm25: str
    embedding_model: str
    llm_model: str

class FeedbackRequest(BaseModel):
    query: str
    answer: str
    rating: int          # 1-5
    comment: Optional[str] = ""