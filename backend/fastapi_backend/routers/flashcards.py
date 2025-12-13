"""Flashcard generation router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from fastapi_backend.dependencies import get_content_generator
from fastapi_backend.models.schemas import (
    ErrorResponse,
    FlashcardsRequest,
    FlashcardsResponse,
)
from fastapi_backend.services.content_generator import ContentGenerator
from fastapi_backend.utils.errors import ContentGenerationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.post(
    "/",
    response_model=FlashcardsResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_flashcards(
    request: FlashcardsRequest,
    content_generator: ContentGenerator = Depends(get_content_generator),
) -> FlashcardsResponse:
    """
    Generate flashcards from the indexed content.

    Args:
        request: Flashcard generation request
        content_generator: Content generation service

    Returns:
        FlashcardsResponse with generated flashcards

    Raises:
        HTTPException: If generation fails
    """
    try:
        try:
            flashcards_data = content_generator.generate_flashcards(
                num_flashcards=request.num_flashcards,
                namespace=request.document_id,
            )
        except ContentGenerationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Flashcard generation failed: {str(e)}",
            )

        return FlashcardsResponse(flashcards=flashcards_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during flashcard generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

