"""Error handling middleware for FastAPI."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from fastapi_backend.models.schemas import ErrorResponse
from fastapi_backend.utils.errors import (
    ConfigurationError,
    ContentGenerationError,
    PDFExtractionError,
    RAGEduGeneratorError,
    RAGServiceError,
    VectorStoreError,
)

logger = logging.getLogger(__name__)


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the FastAPI application."""
    if isinstance(exc, PDFExtractionError):
        logger.warning(f"PDF extraction error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(error="PDF Extraction Error", detail=str(exc)).model_dump(),
        )

    if isinstance(exc, VectorStoreError):
        logger.error(f"Vector store error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(error="Vector Store Error", detail=str(exc)).model_dump(),
        )

    if isinstance(exc, RAGServiceError):
        logger.error(f"RAG service error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(error="RAG Service Error", detail=str(exc)).model_dump(),
        )

    if isinstance(exc, ContentGenerationError):
        logger.error(f"Content generation error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(error="Content Generation Error", detail=str(exc)).model_dump(),
        )

    if isinstance(exc, ConfigurationError):
        logger.error(f"Configuration error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(error="Configuration Error", detail=str(exc)).model_dump(),
        )

    if isinstance(exc, RAGEduGeneratorError):
        logger.error(f"Application error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(error="Application Error", detail=str(exc)).model_dump(),
        )

    if hasattr(exc, "errors") and hasattr(exc, "body"):
        logger.warning(f"Validation error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(error="Validation Error", detail="Invalid request data.").model_dump(),
        )

    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error="Internal Server Error", detail="An unexpected error occurred.").model_dump(),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for the FastAPI app."""
    app.add_exception_handler(Exception, exception_handler)

