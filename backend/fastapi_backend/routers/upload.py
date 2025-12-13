"""PDF upload router."""

import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from fastapi_backend.dependencies import (
    get_chunker,
    get_pdf_extractor,
    get_rag_service,
)
from fastapi_backend.models.document import ExtractedDocument
from fastapi_backend.models.schemas import ErrorResponse, UploadResponse
from fastapi_backend.services.pdf_extractor import PDFExtractor
from fastapi_backend.services.rag_service import RAGService
from fastapi_backend.utils.chunking import HybridChunker
from fastapi_backend.utils.errors import PDFExtractionError, RAGServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def upload_pdf(
    files: List[UploadFile] = File(..., description="PDF files to upload"),
    pdf_extractor: PDFExtractor = Depends(get_pdf_extractor),
    chunker: HybridChunker = Depends(get_chunker),
    rag_service: RAGService = Depends(get_rag_service),
) -> UploadResponse:
    """
    Upload and index one or more PDF files.

    Args:
        files: List of PDF files to upload (up to 300 pages total)
        pdf_extractor: PDF extraction service
        chunker: Document chunking service
        rag_service: RAG service for indexing

    Returns:
        UploadResponse with document ID and metadata

    Raises:
        HTTPException: If upload or processing fails
    """
    try:
        logger.info(f"Received upload request with {len(files) if files else 0} files")

        if not files or len(files) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one file must be uploaded",
            )

        # Validate all files are PDFs
        invalid_files = []
        for file in files:
            if not file.filename or not file.filename.lower().endswith(".pdf"):
                invalid_files.append(file.filename or "Unknown file")

        if invalid_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only PDF files are allowed. Invalid files: {', '.join(invalid_files)}",
            )

        # Extract and validate page counts for all files
        extracted_docs = []
        total_pages = 0
        file_info = []

        for file in files:
            file_content = await file.read()

            if len(file_content) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} is empty",
                )

            try:
                extracted_doc = pdf_extractor.extract_from_bytes(
                    file_content, filename=file.filename
                )
            except PDFExtractionError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PDF extraction failed for {file.filename}: {str(e)}",
                )

            total_pages += extracted_doc.page_count

            if total_pages > PDFExtractor.MAX_PAGES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Total pages ({total_pages}) exceeds the maximum limit of {PDFExtractor.MAX_PAGES} pages.",
                )

            extracted_docs.append(extracted_doc)
            file_info.append({
                "filename": file.filename,
                "pages": extracted_doc.page_count
            })

        # Combine all documents into one
        combined_text_parts = []
        file_names = ", ".join([f["filename"] for f in file_info])
        combined_metadata = {
            "files": file_info, 
            "total_files": len(files),
            "filename": file_names,  # Add filename to metadata for easy retrieval
        }

        for i, doc in enumerate(extracted_docs):
            file_header = f"\n\n=== FILE {i+1}: {file_info[i]['filename']} ===\n\n"
            combined_text_parts.append(file_header + doc.text)
            if doc.metadata:
                combined_metadata[f"file_{i+1}_metadata"] = doc.metadata

        combined_doc = ExtractedDocument(
            text="\n\n".join(combined_text_parts),
            page_count=total_pages,
            chunks=[],
            metadata=combined_metadata,
        )

        # Chunk the combined document
        chunks = chunker.chunk_document(combined_doc)

        if not chunks:
            text_length = len(combined_doc.text.strip()) if combined_doc.text else 0
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No content could be extracted from the PDFs. "
                       f"Total text length: {text_length} characters. "
                       f"Please ensure your PDFs contain extractable text.",
            )

        # Generate document ID
        document_id = str(uuid.uuid4())

        logger.info(f"Indexing {len(chunks)} chunks with namespace '{document_id}'")

        # Index documents in vector store
        try:
            rag_service.index_documents(chunks, namespace=document_id)
        except RAGServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to index document: {str(e)}",
            )

        logger.info(f"Successfully indexed {len(files)} file(s): {file_names}")

        return UploadResponse(
            document_id=document_id,
            page_count=total_pages,
            chunks_created=len(chunks),
            message=f"Successfully uploaded and indexed {len(files)} file(s) ({file_names})",
            filename=file_names,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during PDF upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )

