"""
Integration tests for the complete NLP pipeline and change processor.
"""
from __future__ import annotations

import pytest
from app.services.document_processor import DocumentProcessor
from app.services.change_processor import ChangeProcessor, ChangeType, ClauseChange


PIPELINE_TEST_DOCUMENT = """
1. Data Collection

We collect your name, email address, phone number, and device identifiers
when you register and use our services. We also use cookies and tracking pixels.

2. Data Sharing with Third Parties

We may share your personal information with third-party service providers,
advertising partners, and business affiliates for operational and marketing purposes.

3. Arbitration and Jurisdiction

All disputes shall be resolved by binding arbitration. You waive your right
to participate in class action lawsuits. Arbitration is governed by California law.

4. Liability Limitation

The company disclaims all warranties and shall not be liable for any consequential,
incidental, or indirect damages arising from your use of our services.
"""


class TestDocumentPipeline:
    def setup_method(self):
        self.processor = DocumentProcessor()

    def test_process_text_returns_result(self):
        result = self.processor.process_text(PIPELINE_TEST_DOCUMENT)
        assert result.success is True
        assert result.total_clauses > 0
        assert len(result.clauses) > 0

    def test_all_clauses_have_category(self):
        result = self.processor.process_text(PIPELINE_TEST_DOCUMENT)
        for clause in result.clauses:
            assert "category" in clause
            assert clause["category"] != ""

    def test_all_clauses_have_severity_prior(self):
        result = self.processor.process_text(PIPELINE_TEST_DOCUMENT)
        for clause in result.clauses:
            assert "severity_prior" in clause
            assert 0.0 <= clause["severity_prior"] <= 1.0

    def test_all_clauses_have_original_text(self):
        result = self.processor.process_text(PIPELINE_TEST_DOCUMENT)
        for clause in result.clauses:
            assert "original_text" in clause
            assert len(clause["original_text"]) > 0

    def test_metrics_recorded(self):
        result = self.processor.process_text(PIPELINE_TEST_DOCUMENT)
        assert result.metrics.total_time_s > 0
        assert result.metrics.segmentation_time_s >= 0

    def test_empty_text_fails_gracefully(self):
        result = self.processor.process_text("")
        assert result.success is False

    def test_processing_status_in_output(self):
        result = self.processor.process_text(PIPELINE_TEST_DOCUMENT)
        assert result.processing_status in ("completed", "partial", "failed")

    def test_data_collection_classified_correctly(self):
        result = self.processor.process_text(PIPELINE_TEST_DOCUMENT)
        categories = [c["category"] for c in result.clauses]
        assert "Data Collection" in categories

    def test_no_embeddings_option(self):
        result = self.processor.process_text(
            PIPELINE_TEST_DOCUMENT, include_embeddings=False
        )
        assert result.success is True
        for clause in result.clauses:
            assert clause["embedding"] == []

    def test_no_summaries_option(self):
        result = self.processor.process_text(
            PIPELINE_TEST_DOCUMENT, include_summaries=False
        )
        assert result.success is True


class TestChangeProcessorIntegration:
    def setup_method(self):
        self.cp = ChangeProcessor()

    def test_process_added_clause(self):
        changes = [
            ClauseChange(
                clause_number=1,
                clause_title="Data Collection",
                clause_text="We collect your name and email address.",
                change_type=ChangeType.ADDED,
            )
        ]
        result = self.cp.process_changes(changes)
        assert result.success is True
        assert result.added_processed == 1
        assert result.clauses[0]["change_type"] == "added"
        assert result.clauses[0]["reprocessed"] is True

    def test_unchanged_clause_reuses_cache(self):
        cached = {
            "clause_number": 1, "clause_title": "Old Title",
            "original_text": "Old text.", "category": "Data Collection",
            "category_id": 1, "classification_confidence": 0.9,
            "classification_method": "rule_based", "secondary_categories": [],
            "severity_prior": 0.5, "embedding": [0.1, 0.2],
            "embedding_model": "test", "embedding_dimension": 2,
            "simple_explanation": "Old explanation.", "summarization_model": "mock",
            "summarization_provider": "mock", "is_mock_summary": True,
            "processing_status": "completed", "errors": [],
        }
        changes = [
            ClauseChange(1, "Old Title", "Old text.", ChangeType.UNCHANGED, cached)
        ]
        result = self.cp.process_changes(changes)
        assert result.unchanged_reused == 1
        assert result.clauses[0]["reprocessed"] is False

    def test_removed_clause_preserved(self):
        cached = {
            "clause_number": 1, "clause_title": "Old", "original_text": "text",
            "category": "Other", "category_id": 11, "classification_confidence": 0.1,
            "classification_method": "rule_based", "secondary_categories": [],
            "severity_prior": 0.1, "embedding": [], "embedding_model": "",
            "embedding_dimension": 0, "simple_explanation": "",
            "summarization_model": "", "summarization_provider": "",
            "is_mock_summary": False, "processing_status": "completed", "errors": [],
        }
        changes = [ClauseChange(1, "Old", "text", ChangeType.REMOVED, cached)]
        result = self.cp.process_changes(changes)
        assert result.removed_count == 1

    def test_mixed_changes(self):
        changes = [
            ClauseChange(1, "New", "We now collect your location data.", ChangeType.ADDED),
            ClauseChange(2, "Updated", "Updated data sharing with partners.", ChangeType.MODIFIED),
        ]
        result = self.cp.process_changes(changes)
        assert result.added_processed == 1
        assert result.modified_processed == 1
