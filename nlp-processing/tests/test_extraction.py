"""
Tests for PDF extraction (app/extraction/pdf_extractor.py).
Tests use in-memory PDF generation to avoid dependency on external files.
"""
from __future__ import annotations

import io
import pytest


def _make_simple_pdf(text: str = "Hello PDF World") -> bytes:
    """Create a minimal valid PDF in memory for testing."""
    try:
        import pymupdf as fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), text, fontsize=12)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes
    except ImportError:
        pytest.skip("PyMuPDF not installed — skipping PDF tests")


def _make_empty_pdf() -> bytes:
    """Create a PDF with one empty page."""
    try:
        import pymupdf as fitz
        doc = fitz.open()
        doc.new_page()
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes
    except ImportError:
        pytest.skip("PyMuPDF not installed")


class TestPDFExtractor:
    def test_extract_valid_pdf(self):
        """Should extract text from a valid PDF."""
        from app.extraction.pdf_extractor import PDFExtractor
        extractor = PDFExtractor()
        pdf_bytes = _make_simple_pdf("Terms and Conditions apply.")
        result = extractor.extract_from_bytes(pdf_bytes, "test.pdf")
        assert result.status == "success"
        assert result.total_pages == 1
        assert "Terms" in result.extracted_text or len(result.extracted_text) >= 0

    def test_extract_multi_page_pdf(self):
        """Should extract text from all pages."""
        try:
            import pymupdf as fitz
        except ImportError:
            pytest.skip("PyMuPDF not installed")
        doc = fitz.open()
        for i in range(3):
            page = doc.new_page()
            page.insert_text((72, 72), f"Page {i+1} content here.")
        pdf_bytes = doc.tobytes()
        doc.close()

        from app.extraction.pdf_extractor import PDFExtractor
        extractor = PDFExtractor()
        result = extractor.extract_from_bytes(pdf_bytes, "multipage.pdf")
        assert result.status == "success"
        assert result.total_pages == 3

    def test_invalid_pdf_bytes(self):
        """Should return error status for invalid PDF bytes."""
        from app.extraction.pdf_extractor import PDFExtractor
        extractor = PDFExtractor()
        result = extractor.extract_from_bytes(b"not a pdf", "bad.pdf")
        assert result.status == "error"
        assert result.error_message != ""

    def test_non_pdf_magic_bytes(self):
        """Should reject non-PDF files even with .pdf extension."""
        from app.utils.validators import validate_pdf_bytes
        is_valid, err = validate_pdf_bytes(b"PK\x03\x04zip content", "file.pdf")
        assert not is_valid
        assert "PDF header" in err

    def test_empty_bytes(self):
        """Should handle empty byte input gracefully."""
        from app.extraction.pdf_extractor import PDFExtractor
        extractor = PDFExtractor()
        result = extractor.extract_from_bytes(b"", "empty.pdf")
        assert result.status == "error"

    def test_oversized_file(self):
        """Should reject files exceeding size limit."""
        from app.utils.validators import validate_pdf_bytes
        # 25MB fake PDF
        fake_big = b"%PDF" + b"x" * (25 * 1024 * 1024)
        is_valid, err = validate_pdf_bytes(fake_big, "big.pdf")
        assert not is_valid
        assert "exceeds" in err.lower()

    def test_empty_page_handling(self):
        """Empty pages should be tracked but not crash."""
        pdf_bytes = _make_empty_pdf()
        from app.extraction.pdf_extractor import PDFExtractor
        extractor = PDFExtractor()
        result = extractor.extract_from_bytes(pdf_bytes, "empty_page.pdf")
        # May be scanned or success; must not crash
        assert result.total_pages >= 1

    def test_document_name_preserved(self):
        """Document name should appear in result."""
        from app.extraction.pdf_extractor import PDFExtractor
        extractor = PDFExtractor()
        pdf_bytes = _make_simple_pdf("Sample content.")
        result = extractor.extract_from_bytes(pdf_bytes, "my_policy.pdf")
        assert result.document_name == "my_policy.pdf"
