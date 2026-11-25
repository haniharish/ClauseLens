"""
ClauseLens — PDF Text Extractor
Uses PyMuPDF (fitz) to extract text from PDF documents.
Handles normal PDFs, scanned PDFs (OCR fallback), empty pages, and corrupted files.
"""
from __future__ import annotations

import io
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from app.utils.logger import get_logger
from app.utils.validators import validate_pdf_bytes, validate_pdf_file

logger = get_logger(__name__)


@dataclass
class PageResult:
    page_number: int          # 1-indexed
    text: str
    is_empty: bool
    char_count: int


@dataclass
class ExtractionResult:
    document_name: str
    total_pages: int
    extracted_text: str       # Full concatenated clean text
    pages: list[PageResult]
    status: str               # "success" | "scanned" | "error"
    error_message: str = ""
    is_scanned: bool = False
    ocr_attempted: bool = False


# ---------------------------------------------------------------------------
# Core extractor
# ---------------------------------------------------------------------------

class PDFExtractor:
    """
    Extracts text from PDF documents using PyMuPDF.
    Falls back to OCR (pytesseract) for scanned PDFs when available.
    """

    # Heuristic: if extracted text per page is below this many chars on
    # average, assume the PDF is scanned.
    SCANNED_THRESHOLD_CHARS_PER_PAGE = 50

    def extract_from_bytes(
        self,
        pdf_bytes: bytes,
        document_name: str = "document.pdf",
        attempt_ocr: bool = True,
    ) -> ExtractionResult:
        """
        Extract text from raw PDF bytes.

        Parameters
        ----------
        pdf_bytes : bytes
            Raw content of the PDF file.
        document_name : str
            Friendly name used in the result.
        attempt_ocr : bool
            If True and PDF appears scanned, attempt OCR via pytesseract.

        Returns
        -------
        ExtractionResult
        """
        is_valid, err = validate_pdf_bytes(pdf_bytes, document_name)
        if not is_valid:
            logger.warning("pdf_validation_failed", document=document_name, error=err)
            return ExtractionResult(
                document_name=document_name,
                total_pages=0,
                extracted_text="",
                pages=[],
                status="error",
                error_message=err,
            )

        try:
            import pymupdf as fitz  # PyMuPDF
        except ImportError:
            try:
                import fitz  # fallback for older PyMuPDF
            except ImportError:
                return ExtractionResult(
                    document_name=document_name,
                    total_pages=0,
                    extracted_text="",
                    pages=[],
                    status="error",
                    error_message="PyMuPDF is not installed. Run: pip install PyMuPDF",
                )

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as exc:
            logger.error("pdf_open_failed", document=document_name, exc=str(exc))
            return ExtractionResult(
                document_name=document_name,
                total_pages=0,
                extracted_text="",
                pages=[],
                status="error",
                error_message=f"Cannot open PDF: {exc}",
            )

        pages: list[PageResult] = []
        full_text_parts: list[str] = []
        has_images = False

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text")  # type: ignore[attr-defined]
            if not has_images and len(page.get_images()) > 0:
                has_images = True
            stripped = page_text.strip()
            is_empty = len(stripped) == 0

            page_result = PageResult(
                page_number=page_idx + 1,
                text=page_text,
                is_empty=is_empty,
                char_count=len(stripped),
            )
            pages.append(page_result)

            if not is_empty:
                full_text_parts.append(f"[Page {page_idx + 1}]\n{page_text}")

        doc.close()

        total_chars = sum(p.char_count for p in pages)
        avg_chars = total_chars / max(len(pages), 1)
        # Treat as scanned if there is virtually no selectable text (0 chars)
        # or very little text (< threshold) combined with embedded page images.
        is_scanned = (total_chars == 0) or (
            has_images and avg_chars < self.SCANNED_THRESHOLD_CHARS_PER_PAGE
        )

        if is_scanned:
            logger.warning(
                "scanned_pdf_detected",
                document=document_name,
                avg_chars_per_page=avg_chars,
            )
            if attempt_ocr:
                return self._attempt_ocr(pdf_bytes, document_name, pages)
            else:
                return ExtractionResult(
                    document_name=document_name,
                    total_pages=len(pages),
                    extracted_text="",
                    pages=pages,
                    status="scanned",
                    error_message=(
                        "This PDF appears to be scanned with no selectable text. "
                        "OCR was not attempted. Enable OCR or provide a text-based PDF."
                    ),
                    is_scanned=True,
                )

        extracted_text = "\n\n".join(full_text_parts)
        logger.info(
            "pdf_extracted",
            document=document_name,
            pages=len(pages),
            total_chars=total_chars,
        )

        return ExtractionResult(
            document_name=document_name,
            total_pages=len(pages),
            extracted_text=extracted_text,
            pages=pages,
            status="success",
        )

    def extract_from_file(
        self,
        file_path: str | Path,
        attempt_ocr: bool = True,
    ) -> ExtractionResult:
        """Extract text from a PDF file on disk."""
        path = Path(file_path)
        is_valid, err = validate_pdf_file(path)
        if not is_valid:
            return ExtractionResult(
                document_name=path.name,
                total_pages=0,
                extracted_text="",
                pages=[],
                status="error",
                error_message=err,
            )
        pdf_bytes = path.read_bytes()
        return self.extract_from_bytes(pdf_bytes, path.name, attempt_ocr=attempt_ocr)

    # ------------------------------------------------------------------
    # OCR fallback
    # ------------------------------------------------------------------

    def _attempt_ocr(
        self,
        pdf_bytes: bytes,
        document_name: str,
        original_pages: list[PageResult],
    ) -> ExtractionResult:
        """
        Attempt OCR extraction using pytesseract and PyMuPDF's pixmap rendering.
        Requires pytesseract and Tesseract binary to be installed.
        """
        try:
            import pytesseract
            from PIL import Image
            import pymupdf as fitz
        except ImportError as exc:
            logger.warning("ocr_dependencies_missing", exc=str(exc))
            return ExtractionResult(
                document_name=document_name,
                total_pages=len(original_pages),
                extracted_text="",
                pages=original_pages,
                status="scanned",
                error_message=(
                    "PDF appears to be scanned. OCR dependencies (pytesseract / Pillow) "
                    "are not installed. Install them and ensure Tesseract is on PATH."
                ),
                is_scanned=True,
                ocr_attempted=False,
            )

        logger.info("ocr_started", document=document_name)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        ocr_pages: list[PageResult] = []
        full_text_parts: list[str] = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            # Render at 300 DPI for good OCR quality
            mat = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)  # type: ignore[attr-defined]
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))

            try:
                ocr_text = pytesseract.image_to_string(img)
            except Exception as exc:
                ocr_text = ""
                logger.warning("ocr_page_failed", page=page_idx + 1, exc=str(exc))

            stripped = ocr_text.strip()
            ocr_pages.append(PageResult(
                page_number=page_idx + 1,
                text=ocr_text,
                is_empty=len(stripped) == 0,
                char_count=len(stripped),
            ))
            if stripped:
                full_text_parts.append(f"[Page {page_idx + 1}]\n{ocr_text}")

        doc.close()
        extracted_text = "\n\n".join(full_text_parts)
        logger.info(
            "ocr_completed",
            document=document_name,
            pages=len(ocr_pages),
            total_chars=sum(p.char_count for p in ocr_pages),
        )

        return ExtractionResult(
            document_name=document_name,
            total_pages=len(ocr_pages),
            extracted_text=extracted_text,
            pages=ocr_pages,
            status="success",
            is_scanned=True,
            ocr_attempted=True,
        )


# ---------------------------------------------------------------------------
# Module-level convenience instance
# ---------------------------------------------------------------------------
_extractor = PDFExtractor()


def extract_pdf(
    pdf_bytes: bytes,
    document_name: str = "document.pdf",
    attempt_ocr: bool = True,
) -> ExtractionResult:
    """Module-level shortcut for extraction from bytes."""
    return _extractor.extract_from_bytes(pdf_bytes, document_name, attempt_ocr)


def extract_pdf_file(file_path: str | Path, attempt_ocr: bool = True) -> ExtractionResult:
    """Module-level shortcut for extraction from file path."""
    return _extractor.extract_from_file(file_path, attempt_ocr)
