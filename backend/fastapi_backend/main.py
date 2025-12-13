"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_backend.config import settings
from fastapi_backend.middleware import setup_exception_handlers
from fastapi_backend.models.schemas import HealthResponse
from fastapi_backend.routers import (
    chat,
    competitive_quiz,
    documents,
    flashcards,
    quiz,
    summary,
    upload,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RAG Educational Content Generator API",
    description="API for RAG-powered educational content generation",
    version="0.1.0",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(quiz.router)
app.include_router(summary.router)
app.include_router(flashcards.router)
app.include_router(competitive_quiz.router)
app.include_router(documents.router)


@app.get("/", response_model=HealthResponse, tags=["health"])
async def root() -> HealthResponse:
    """Root endpoint with health check."""
    return HealthResponse(status="healthy", version="0.1.0")


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fastapi_backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )

