"""Chat/Q&A router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pinecone import Pinecone

from fastapi_backend.config import settings
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

    Args:
        request: Chat request with question and document_id
        rag_service: RAG service for querying

    Returns:
        ChatResponse with answer and sources

    Raises:
        HTTPException: If query fails
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

        # Validate document_id exists
        try:
            pc = Pinecone(api_key=settings.pinecone_api_key)
            index = pc.Index(settings.pinecone_index_name)
            stats = index.describe_index_stats()
            namespace_stats = stats.get("namespaces", {})

            if request.document_id in namespace_stats:
                vector_count = namespace_stats[request.document_id].get("vector_count", 0)
                logger.info(f"Document '{request.document_id}' has {vector_count} vectors")
            else:
                logger.warning(f"Document ID '{request.document_id}' not found in index")
        except Exception as e:
            logger.warning(f"Could not validate document_id: {e}")

        # Check if user is asking about uploaded materials
        question_lower = request.question.lower().strip()
        material_phrases = [
            "what materials", "what documents", "what files", "what pdfs",
            "what have i uploaded", "what did i upload", "list my files",
            "list my documents", "show my files", "show my documents",
        ]

        if any(phrase in question_lower for phrase in material_phrases):
            filename_display = request.filename or "No filename provided"
            return ChatResponse(
                answer=f"You have uploaded: **{filename_display}**\n\nAsk questions about this document.",
                sources=[],
                from_document=False,
                message="Information about uploaded materials",
                filename=request.filename,
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

