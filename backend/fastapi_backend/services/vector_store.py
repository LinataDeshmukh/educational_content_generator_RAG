"""Pinecone vector store integration."""

import logging
import time
from typing import Optional

from llama_index.core import Document as LlamaDocument
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from fastapi_backend.config import settings
from fastapi_backend.models.document import DocumentChunk
from fastapi_backend.utils.errors import VectorStoreError

# Suppress verbose Pinecone logs
logging.getLogger("pinecone_plugin_interface").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing vector store operations with Pinecone."""

    def __init__(self):
        """Initialize the vector store service."""
        self.pinecone_client: Optional[Pinecone] = None
        self.vector_store: Optional[PineconeVectorStore] = None
        self.pinecone_index = None
        self.index_name = None
        self._initialize_pinecone()

    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone client and vector store."""
        try:
            index_name = settings.pinecone_index_name
            self.index_name = index_name
            
            # Initialize client
            self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
            
            # Check if index exists
            index_exists = self.pinecone_client.has_index(index_name)
            
            # Create if needed
            if not index_exists:
                logger.info(f"Creating Pinecone index '{index_name}'...")
                self._create_index(index_name)
            
            # Connect
            self._connect_to_index(index_name)
            logger.info(f"Pinecone ready: {index_name}")

        except Exception as e:
            logger.error(f"Pinecone init failed: {e}")
            raise VectorStoreError(f"Failed to initialize Pinecone: {e}") from e

    def _create_index(self, index_name: str) -> None:
        """Create a new Pinecone serverless index."""
        env = settings.pinecone_environment.lower().strip()
        cloud = "gcp" if "gcp" in env else "aws"
        region = env if env in ["us-east-1", "us-west-2", "eu-west-1"] else "us-east-1"
        
        self.pinecone_client.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region),
        )
        
        # Wait for ready
        for _ in range(30):
            desc = self.pinecone_client.describe_index(index_name)
            if hasattr(desc.status, 'ready') and desc.status.ready:
                break
            time.sleep(2)

    def _connect_to_index(self, index_name: str) -> None:
        """Connect to the Pinecone index."""
        desc = self.pinecone_client.describe_index(index_name)
        host = desc.host
        
        index = self.pinecone_client.Index(index_name, host=host)
        
        # Store references
        self.pinecone_index = index
        self.vector_store = PineconeVectorStore(pinecone_index=index)

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
        if not self.pinecone_index:
            raise VectorStoreError("Pinecone index not initialized")

        try:
            self.pinecone_index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Cleared namespace: {namespace}")
        except Exception as e:
            error_msg = f"Failed to clear namespace {namespace}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise VectorStoreError(error_msg) from e
