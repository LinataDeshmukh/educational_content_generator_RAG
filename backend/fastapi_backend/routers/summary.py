"""Summary generation router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from fastapi_backend.dependencies import get_content_generator
from fastapi_backend.models.schemas import (
    ErrorResponse,
    SummaryRequest,
    SummaryResponse,
)
from fastapi_backend.services.content_generator import ContentGenerator
from fastapi_backend.utils.errors import ContentGenerationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post(
    "/",
    response_model=SummaryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_summary(
    request: SummaryRequest,
    content_generator: ContentGenerator = Depends(get_content_generator),
) -> SummaryResponse:
    """
    Generate a summary of the indexed content.

    Args:
        request: Summary generation request
        content_generator: Content generation service

    Returns:
        SummaryResponse with generated summary

    Raises:
        HTTPException: If generation fails
    """
    try:
        if request.length not in ["short", "medium", "long"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Length must be 'short', 'medium', or 'long'",
            )

        try:
            summary_data = content_generator.generate_summary(
                length=request.length,
                namespace=request.document_id,
            )
        except ContentGenerationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Summary generation failed: {str(e)}",
            )

        return SummaryResponse(summary=summary_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during summary generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

