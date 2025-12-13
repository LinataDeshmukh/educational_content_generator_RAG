"""Custom exception classes for error handling."""


class RAGEduGeneratorError(Exception):
    """Base exception for RAG Educational Content Generator."""
    pass


class PDFExtractionError(RAGEduGeneratorError):
    """Error during PDF extraction."""
    pass


class VectorStoreError(RAGEduGeneratorError):
    """Error with vector store operations."""
    pass


class RAGServiceError(RAGEduGeneratorError):
    """Error in RAG service operations."""
    pass


class ContentGenerationError(RAGEduGeneratorError):
    """Error during content generation."""
    pass


class ConfigurationError(RAGEduGeneratorError):
    """Error in configuration."""
    pass

