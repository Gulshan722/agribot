# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="AgriBot API",
    description="AI-powered agricultural knowledge assistant for farmers",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI at /docs
    redoc_url="/redoc"      # ReDoc UI at /redoc
)

# Allow frontend to call this API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "name": "AgriBot",
        "description": "Ask agricultural questions, get cited answers",
        "docs": "/docs",
        "ask": "/api/v1/ask",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting AgriBot API server...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)