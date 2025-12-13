"""Dependency injection for FastAPI routes."""

from functools import lru_cache

from fastapi_backend.services.competitive_quiz_service import CompetitiveQuizService
from fastapi_backend.services.content_generator import ContentGenerator
from fastapi_backend.services.pdf_extractor import PDFExtractor
from fastapi_backend.services.rag_service import RAGService
from fastapi_backend.services.vector_store import VectorStoreService
from fastapi_backend.utils.chunking import HybridChunker


@lru_cache()
def get_vector_store_service() -> VectorStoreService:
    """Get or create VectorStoreService instance (singleton)."""
    return VectorStoreService()


@lru_cache()
def get_rag_service() -> RAGService:
    """Get or create RAGService instance (singleton)."""
    vector_store_service = get_vector_store_service()
    return RAGService(vector_store_service)


@lru_cache()
def get_content_generator() -> ContentGenerator:
    """Get or create ContentGenerator instance (singleton)."""
    rag_service = get_rag_service()
    return ContentGenerator(rag_service)


@lru_cache()
def get_competitive_quiz_service() -> CompetitiveQuizService:
    """Get or create CompetitiveQuizService instance (singleton)."""
    content_generator = get_content_generator()
    return CompetitiveQuizService(content_generator)


@lru_cache()
def get_pdf_extractor() -> PDFExtractor:
    """Get or create PDFExtractor instance (singleton)."""
    return PDFExtractor()


@lru_cache()
def get_chunker() -> HybridChunker:
    """Get or create HybridChunker instance (singleton)."""
    return HybridChunker()

