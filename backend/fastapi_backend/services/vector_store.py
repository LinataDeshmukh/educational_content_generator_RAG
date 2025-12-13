"""Pinecone vector store integration."""

import logging
from typing import Optional

from llama_index.core import Document as LlamaDocument
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from fastapi_backend.config import settings
from fastapi_backend.models.document import DocumentChunk
from fastapi_backend.utils.errors import VectorStoreError

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing vector store operations with Pinecone."""

    def __init__(self):
        """Initialize the vector store service."""
        self.pinecone_client: Optional[Pinecone] = None
        self.vector_store: Optional[PineconeVectorStore] = None
        self._initialize_pinecone()

    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone client and vector store."""
        try:
            self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
            index_name = settings.pinecone_index_name
            existing_indexes = [idx.name for idx in self.pinecone_client.list_indexes()]

            if index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {index_name}")
                dimension = 1536  # OpenAI embeddings
                cloud = "gcp" if "gcp" in settings.pinecone_environment.lower() else "aws"

                self.pinecone_client.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud=cloud, region=settings.pinecone_environment),
                )
                logger.info(f"Created Pinecone index: {index_name}")
            else:
                logger.info(f"Using existing Pinecone index: {index_name}")

            index = self.pinecone_client.Index(index_name)
            self.vector_store = PineconeVectorStore(pinecone_index=index)
            self.index_name = index_name
            self.pinecone_index = index

            logger.info("Pinecone vector store initialized successfully")

        except Exception as e:
            error_msg = f"Failed to initialize Pinecone: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise VectorStoreError(error_msg) from e

    def add_documents(
        self,
        chunks: list[DocumentChunk],
        namespace: Optional[str] = None,
        batch_size: int = 100,
    ) -> list[str]:
        """Add document chunks to the vector store."""
        if not self.vector_store:
            raise VectorStoreError("Vector store not initialized")

        try:
            llama_docs = []
            doc_ids = []
            for idx, chunk in enumerate(chunks):
                metadata = {
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    **(chunk.metadata or {}),
                }
                chunk_id = f"{namespace}_{idx}" if namespace else f"chunk_{idx}"
                doc_ids.append(chunk_id)

                llama_doc = LlamaDocument(
                    text=chunk.text,
                    metadata=metadata,
                    id_=chunk_id,
                )
                llama_docs.append(llama_doc)

            self.vector_store.add(llama_docs)

            logger.info(f"Added {len(chunks)} chunks to vector store")
            return doc_ids

        except Exception as e:
            error_msg = f"Failed to add documents to vector store: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise VectorStoreError(error_msg) from e

    def delete_documents(self, doc_ids: list[str], namespace: Optional[str] = None) -> None:
        """Delete documents from the vector store."""
        if not self.vector_store:
            raise VectorStoreError("Vector store not initialized")

        try:
            self.vector_store.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents from vector store")
        except Exception as e:
            error_msg = f"Failed to delete documents: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise VectorStoreError(error_msg) from e

    def get_vector_store(self) -> PineconeVectorStore:
        """Get the underlying vector store instance."""
        if not self.vector_store:
            raise VectorStoreError("Vector store not initialized")
        return self.vector_store

    def clear_namespace(self, namespace: str) -> None:
        """Clear all documents in a namespace."""
        if not self.pinecone_client:
            raise VectorStoreError("Pinecone client not initialized")

        try:
            index = self.pinecone_client.Index(settings.pinecone_index_name)
            index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Cleared namespace: {namespace}")
        except Exception as e:
            error_msg = f"Failed to clear namespace {namespace}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise VectorStoreError(error_msg) from e

