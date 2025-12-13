"""FastAPI application entry point."""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    logger.info("=" * 60)
    logger.info("STARTING LEARNIFY BACKEND")
    logger.info("=" * 60)
    
    # Print all registered routes
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(sorted(route.methods))
            routes.append(f"{methods:15} {route.path}")
    logger.info("REGISTERED ROUTES:")
    for r in sorted(routes):
        logger.info(f"  {r}")
    
    # Initialize Pinecone/VectorStore at startup
    try:
        from fastapi_backend.dependencies import get_vector_store_service
        logger.info("Initializing Pinecone Vector Store...")
        vector_store = get_vector_store_service()
        logger.info("✅ Pinecone Vector Store initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Pinecone: {e}", exc_info=True)
        logger.error("The application will start but uploads will fail.")
        logger.error("Please check your PINECONE_API_KEY in .env file.")
    
    logger.info("=" * 60)
    logger.info(f"Backend running at http://{settings.backend_host}:{settings.backend_port}")
    logger.info("=" * 60)
    
    yield  # App runs here
    
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Learnify API",
    description="AI-powered educational content generation",
    version="0.1.0",
    lifespan=lifespan,
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

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    return response


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
