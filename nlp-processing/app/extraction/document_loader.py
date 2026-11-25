"""
ClauseLens — Document Loader
Unified interface for loading documents from multiple sources.
"""
from __future__ import annotations

from pathlib import Path

from app.extraction.pdf_extractor import ExtractionResult, PDFExtractor
from app.utils.logger import get_logger

logger = get_logger(__name__)

_extractor = PDFExtractor()


def load_from_bytes(data: bytes, filename: str = "document.pdf") -> ExtractionResult:
    """Load and extract text from raw bytes (e.g., uploaded via HTTP)."""
    return _extractor.extract_from_bytes(data, filename)


def load_from_path(path: str | Path) -> ExtractionResult:
    """Load and extract text from a file path."""
    return _extractor.extract_from_file(path)


def load_from_text(text: str, document_name: str = "inline_text") -> ExtractionResult:
    """
    Wrap plain text in an ExtractionResult so the pipeline can process it
    without a PDF. Useful for testing and direct text submission.
    """
    from app.extraction.pdf_extractor import PageResult

    return ExtractionResult(
        document_name=document_name,
        total_pages=1,
        extracted_text=text,
        pages=[
            PageResult(
                page_number=1,
                text=text,
                is_empty=len(text.strip()) == 0,
                char_count=len(text.strip()),
            )
        ],
        status="success",
    )
