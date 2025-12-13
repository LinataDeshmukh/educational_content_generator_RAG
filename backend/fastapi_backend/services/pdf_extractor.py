"""PDF extraction service using PyMuPDF."""

import logging
from typing import Optional

import fitz  # PyMuPDF

from fastapi_backend.models.document import ExtractedDocument
from fastapi_backend.utils.errors import PDFExtractionError

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Service for extracting text from PDF files."""

    MAX_PAGES = 300

    def __init__(self):
        """Initialize the PDF extractor."""
        pass

    def extract_from_bytes(
        self, pdf_bytes: bytes, filename: Optional[str] = None
    ) -> ExtractedDocument:
        """Extract text from PDF bytes."""
        try:
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_count = len(pdf_document)

            if page_count > self.MAX_PAGES:
                raise PDFExtractionError(
                    f"PDF has {page_count} pages, maximum allowed is {self.MAX_PAGES}"
                )

            full_text_parts = []
            pages_with_text = 0
            total_chars = 0

            for page_num in range(page_count):
                page = pdf_document[page_num]
                text = page.get_text()
                text_stripped = text.strip()

                if text_stripped:
                    pages_with_text += 1
                    total_chars += len(text_stripped)

                full_text_parts.append(text)

            full_text = "\n\n".join(full_text_parts)
            full_text_stripped = full_text.strip()

            if not full_text_stripped or len(full_text_stripped) < 10:
                pdf_document.close()
                error_msg = (
                    f"No extractable text found in PDF. "
                    f"This PDF appears to be image-based (scanned). "
                    f"Pages: {page_count}, Pages with text: {pages_with_text}"
                )
                if filename:
                    error_msg = f"{filename}: {error_msg}"
                raise PDFExtractionError(error_msg)

            metadata = pdf_document.metadata
            if filename:
                metadata["filename"] = filename
            metadata["pages_with_text"] = pages_with_text
            metadata["total_chars_extracted"] = total_chars

            pdf_document.close()

            logger.info(f"Extracted {page_count} pages ({pages_with_text} with text)")

            return ExtractedDocument(
                text=full_text,
                page_count=page_count,
                chunks=[],
                metadata=metadata,
            )

        except fitz.FileDataError as e:
            raise PDFExtractionError(f"Invalid or corrupted PDF file: {str(e)}")
        except Exception as e:
            error_msg = f"Error extracting PDF: {str(e)}"
            if filename:
                error_msg += f" (file: {filename})"
            logger.error(error_msg, exc_info=True)
            raise PDFExtractionError(error_msg) from e

    def extract_from_file(self, file_path: str) -> ExtractedDocument:
        """Extract text from PDF file."""
        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
            return self.extract_from_bytes(pdf_bytes, filename=file_path)
        except FileNotFoundError:
            raise PDFExtractionError(f"PDF file not found: {file_path}")
        except Exception as e:
            raise PDFExtractionError(f"Error reading PDF file {file_path}: {str(e)}") from e

