"""
Tests for clause segmentation (app/segmentation/clause_segmenter.py).
"""
from __future__ import annotations

import pytest
from app.segmentation.clause_segmenter import ClauseSegmenter, segment_document


NUMBERED_DOCUMENT = """
1. Data Collection

We collect your personal information when you use our services, including
your name, email address, and device identifiers.

2. Data Sharing

We may share your information with third-party service providers who assist
us in operating our platform.

3. Data Retention

We retain your data for up to seven years after account closure.
"""

ALLCAPS_DOCUMENT = """
DATA COLLECTION

We collect personal information including name, email, and usage data.

DATA SHARING

We share information with our business partners and service providers.
"""

FLAT_DOCUMENT = """
We collect your name and email address. We use cookies to track your activity.

We share your information with advertising partners. We do not sell your data.

You can delete your account at any time. We will remove your data within 30 days.
"""


class TestClauseSegmenter:
    def setup_method(self):
        self.segmenter = ClauseSegmenter()

    def test_numbered_headings_segmentation(self):
        """Should correctly segment numbered sections."""
        clauses = self.segmenter.segment(NUMBERED_DOCUMENT)
        assert len(clauses) >= 3
        titles = [c.clause_title.lower() for c in clauses]
        assert any("data collection" in t for t in titles)
        assert any("data sharing" in t or "sharing" in t for t in titles)

    def test_allcaps_headings_segmentation(self):
        """Should handle ALL CAPS headings."""
        clauses = self.segmenter.segment(ALLCAPS_DOCUMENT)
        assert len(clauses) >= 2

    def test_flat_document_fallback(self):
        """Should fall back to paragraph segmentation for headingless docs."""
        clauses = self.segmenter.segment(FLAT_DOCUMENT)
        assert len(clauses) >= 2

    def test_clause_numbering_sequential(self):
        """Clauses should be numbered starting from 1 sequentially."""
        clauses = self.segmenter.segment(NUMBERED_DOCUMENT)
        for i, c in enumerate(clauses, start=1):
            assert c.clause_number == i

    def test_original_text_preserved(self):
        """Original clause wording must appear in output."""
        clauses = self.segmenter.segment(NUMBERED_DOCUMENT)
        all_text = " ".join(c.clause_text for c in clauses)
        assert "third-party" in all_text or "third" in all_text

    def test_empty_text(self):
        """Should return empty list for empty input."""
        clauses = self.segmenter.segment("")
        assert clauses == []

    def test_very_short_text(self):
        """Should not crash on very short input."""
        clauses = self.segmenter.segment("Hello.")
        assert isinstance(clauses, list)

    def test_clause_order_preserved(self):
        """Clause order must match document order."""
        clauses = self.segmenter.segment(NUMBERED_DOCUMENT)
        numbers = [c.clause_number for c in clauses]
        assert numbers == sorted(numbers)

    def test_module_function(self):
        result = segment_document(NUMBERED_DOCUMENT)
        assert isinstance(result, list)
