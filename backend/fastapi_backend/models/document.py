"""Document data models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""

    text: str
    page_number: int
    chunk_index: int
    metadata: Optional[dict] = None


@dataclass
class ExtractedDocument:
    """Represents an extracted document from PDF."""

    text: str
    page_count: int
    chunks: list[DocumentChunk]
    metadata: Optional[dict] = None

