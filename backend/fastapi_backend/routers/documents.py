"""Document management router."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from fastapi_backend.dependencies import get_vector_store_service
from fastapi_backend.models.schemas import ErrorResponse
from fastapi_backend.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get(
    "/list",
    responses={
        500: {"model": ErrorResponse},
    },
)
async def list_documents(
    vector_store: VectorStoreService = Depends(get_vector_store_service),
):
    """
    List all existing documents (namespaces) in Pinecone.

    Returns:
        List of documents with their IDs, filenames, and metadata
    """
    try:
        # Use the already-initialized Pinecone index
        index = vector_store.pinecone_index
        
        if not index:
            return {"documents": [], "total": 0}

        stats = index.describe_index_stats()
        namespaces = stats.get("namespaces", {})

        documents = []

        for namespace, ns_stats in namespaces.items():
            vector_count = ns_stats.get("vector_count", 0)

            if vector_count > 0:
                try:
                    sample_query = index.query(
                        vector=[0.0] * 1536,
                        top_k=1,
                        namespace=namespace,
                        include_metadata=True,
                    )

                    filename = None

                    if sample_query.get("matches"):
                        match = sample_query["matches"][0]
                        metadata = match.get("metadata", {}) if isinstance(match, dict) else (match.metadata or {})

                        if "filename" in metadata and metadata.get("filename"):
                            filename = metadata.get("filename")
                        elif "files" in metadata:
                            files_info = metadata.get("files", [])
                            if files_info and isinstance(files_info, list):
                                filenames = [
                                    f.get("filename", "")
                                    for f in files_info
                                    if isinstance(f, dict) and f.get("filename")
                                ]
                                if filenames:
                                    filename = ", ".join(filenames)

                    documents.append({
                        "document_id": namespace,
                        "filename": filename or f"Document {namespace[:8]}...",
                        "vector_count": vector_count,
                    })
                except Exception as e:
                    logger.warning(f"Could not get metadata for namespace {namespace}: {e}")
                    documents.append({
                        "document_id": namespace,
                        "filename": "Unknown",
                        "vector_count": vector_count,
                    })

        logger.info(f"Found {len(documents)} existing documents in Pinecone")

        return {
            "documents": documents,
            "total": len(documents),
        }

    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}",
        )
