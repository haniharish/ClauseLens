"""
ClauseLens — Input Validators
"""
from __future__ import annotations

import os
from pathlib import Path

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_pdf_file(file_path: str | Path) -> tuple[bool, str]:
    """
    Validate that a file path points to a readable PDF within size limits.
    Returns (is_valid, error_message).
    """
    settings = get_settings()
    path = Path(file_path)

    if not path.exists():
        return False, f"File not found: {file_path}"

    if not path.is_file():
        return False, f"Path is not a file: {file_path}"

    if path.suffix.lower() != ".pdf":
        return False, f"File must be a PDF, got: {path.suffix}"

    file_size = path.stat().st_size
    if file_size > settings.max_document_size_bytes:
        return False, (
            f"File size {file_size / (1024**2):.1f} MB exceeds "
            f"limit of {settings.max_document_size_mb} MB"
        )

    if file_size == 0:
        return False, "File is empty."

    return True, ""


def validate_pdf_bytes(data: bytes, filename: str = "upload.pdf") -> tuple[bool, str]:
    """
    Validate raw PDF bytes.
    """
    settings = get_settings()

    if not data:
        return False, "No file data received."

    if len(data) > settings.max_document_size_bytes:
        return False, (
            f"Upload size {len(data) / (1024**2):.1f} MB exceeds "
            f"limit of {settings.max_document_size_mb} MB"
        )

    # Minimal PDF magic-byte check
    if not data.startswith(b"%PDF"):
        return False, f"File '{filename}' does not appear to be a valid PDF (missing PDF header)."

    return True, ""


def validate_text_input(text: str, min_length: int = 10) -> tuple[bool, str]:
    """Validate that a text string is non-empty and meaningful."""
    if not text or not text.strip():
        return False, "Input text is empty."
    if len(text.strip()) < min_length:
        return False, f"Input text is too short (minimum {min_length} characters)."
    return True, ""
