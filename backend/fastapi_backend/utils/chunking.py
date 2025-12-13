"""Hybrid chunking strategy for documents."""

import logging
from typing import Optional

from llama_index.core import Document as LlamaDocument
from llama_index.core.node_parser import SentenceSplitter

from fastapi_backend.models.document import DocumentChunk, ExtractedDocument

logger = logging.getLogger(__name__)


class HybridChunker:
    """Hybrid chunking strategy: semantic chunks respecting page boundaries."""

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
        separator: str = "\n\n",
    ):
        """Initialize the hybrid chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=separator,
        )

    def chunk_document(self, document: ExtractedDocument) -> list[DocumentChunk]:
        """Chunk a document using hybrid strategy."""
        chunks: list[DocumentChunk] = []
        full_text = document.text
        page_texts = full_text.split("\n\n")

        if document.page_count > 0 and len(page_texts) >= document.page_count:
            current_chunk_index = 0
            for page_num in range(min(document.page_count, len(page_texts))):
                page_text = page_texts[page_num].strip()
                if not page_text:
                    continue

                page_metadata = {"page_number": page_num + 1}
                if page_num == 0 and document.metadata:
                    page_metadata.update(document.metadata)

                llama_doc = LlamaDocument(text=page_text, metadata=page_metadata)
                page_nodes = self.splitter.get_nodes_from_documents([llama_doc])

                for node in page_nodes:
                    chunk = DocumentChunk(
                        text=node.text,
                        page_number=page_num + 1,
                        chunk_index=current_chunk_index,
                        metadata={
                            **(node.metadata or {}),
                            "start_char_idx": node.start_char_idx,
                            "end_char_idx": node.end_char_idx,
                        },
                    )
                    chunks.append(chunk)
                    current_chunk_index += 1
        else:
            llama_doc = LlamaDocument(text=full_text, metadata=document.metadata or {})
            nodes = self.splitter.get_nodes_from_documents([llama_doc])

            for idx, node in enumerate(nodes):
                page_number = 1
                if node.metadata and "page_number" in node.metadata:
                    page_number = node.metadata["page_number"]
                elif document.page_count > 0:
                    estimated_page = int((idx / len(nodes)) * document.page_count) + 1
                    page_number = min(estimated_page, document.page_count)

                chunk = DocumentChunk(
                    text=node.text,
                    page_number=page_number,
                    chunk_index=idx,
                    metadata={
                        **(node.metadata or {}),
                        "start_char_idx": node.start_char_idx,
                        "end_char_idx": node.end_char_idx,
                    },
                )
                chunks.append(chunk)

        logger.info(f"Created {len(chunks)} chunks from {document.page_count} pages")
        return chunks

    def chunk_text(
        self, text: str, page_number: int = 1, metadata: Optional[dict] = None
    ) -> list[DocumentChunk]:
        """Chunk a text string."""
        llama_doc = LlamaDocument(
            text=text,
            metadata={"page_number": page_number, **(metadata or {})},
        )
        nodes = self.splitter.get_nodes_from_documents([llama_doc])

        chunks = []
        for idx, node in enumerate(nodes):
            chunk = DocumentChunk(
                text=node.text,
                page_number=page_number,
                chunk_index=idx,
                metadata={
                    **(node.metadata or {}),
                    "start_char_idx": node.start_char_idx,
                    "end_char_idx": node.end_char_idx,
                },
            )
            chunks.append(chunk)

        return chunks

