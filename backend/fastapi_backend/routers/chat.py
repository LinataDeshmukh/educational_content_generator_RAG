"""Chat/Q&A router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from fastapi_backend.dependencies import get_rag_service
from fastapi_backend.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from fastapi_backend.services.rag_service import RAGService
from fastapi_backend.utils.errors import RAGServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    """
    Chat with the indexed material using RAG.
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty",
            )

        if not request.document_id or not request.document_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document ID is required. Please upload a PDF first.",
            )

        # Query RAG service
        try:
            result = rag_service.query(
                question=request.question,
                similarity_top_k=5,
                namespace=request.document_id,
            )
        except RAGServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"RAG query failed: {str(e)}",
            )

        return ChatResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            from_document=result.get("from_document", True),
            message=result.get("message"),
            filename=request.filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
