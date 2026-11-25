"""
Tests for FastAPI endpoints.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def client(test_client):
    return test_client


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/api/nlp/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "models" in data

    def test_root_returns_info(self, client):
        response = client.get("/")
        assert response.status_code == 200


class TestSegmentEndpoint:
    def test_segment_valid_text(self, client, sample_privacy_policy_text):
        payload = {"text": sample_privacy_policy_text, "document_name": "test_policy"}
        response = client.post("/api/nlp/segment/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_clauses"] > 0
        assert isinstance(data["clauses"], list)

    def test_segment_too_short_text(self, client):
        payload = {"text": "Hi", "document_name": "test"}
        response = client.post("/api/nlp/segment/", json=payload)
        assert response.status_code == 422

    def test_segment_response_has_required_fields(self, client, sample_privacy_policy_text):
        payload = {"text": sample_privacy_policy_text}
        response = client.post("/api/nlp/segment/", json=payload)
        assert response.status_code == 200
        clauses = response.json()["clauses"]
        for clause in clauses:
            assert "clause_number" in clause
            assert "clause_title" in clause
            assert "clause_text" in clause


class TestClassifyEndpoint:
    def test_classify_single_clause(self, client):
        payload = {
            "clauses": [
                {
                    "clause_number": 1,
                    "clause_title": "Test",
                    "clause_text": "We collect your personal data and device identifiers.",
                }
            ]
        }
        response = client.post("/api/nlp/classify/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_clauses"] == 1
        clf = data["classifications"][0]
        assert "category" in clf
        assert "confidence" in clf
        assert "severity_prior" in clf

    def test_classify_multiple_clauses(self, client):
        payload = {
            "clauses": [
                {"clause_number": 1, "clause_title": "A", "clause_text": "We collect your name and email."},
                {"clause_number": 2, "clause_title": "B", "clause_text": "Disputes resolved by arbitration."},
            ]
        }
        response = client.post("/api/nlp/classify/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_clauses"] == 2


class TestSummarizeEndpoint:
    def test_summarize_returns_explanation(self, client):
        payload = {
            "clauses": [
                {
                    "clause_number": 1,
                    "clause_title": "Data Collection",
                    "clause_text": "We collect personal information including name and email.",
                }
            ]
        }
        response = client.post("/api/nlp/summarize/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_clauses"] == 1
        summary = data["summaries"][0]
        assert "simple_explanation" in summary
        assert "source_text" in summary
        assert summary["category"] == "Data Collection"

    def test_summarize_with_user_context(self, client):
        payload = {
            "clauses": [
                {
                    "clause_number": 1,
                    "clause_title": "Children",
                    "clause_text": "Users under 13 require verifiable parental consent.",
                }
            ],
            "user_context": {"age_group": "minor", "jurisdiction": "US"},
        }
        response = client.post("/api/nlp/summarize/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["summaries"][0]["category"] == "Children and Age"


class TestEmbedEndpoint:
    def test_embed_returns_response(self, client):
        payload = {
            "clauses": [
                {"clause_number": 1, "clause_title": "Test", "clause_text": "We collect your data."}
            ]
        }
        response = client.post("/api/nlp/embed/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_clauses"] == 1
        assert "embeddings" in data


class TestProcessDocumentEndpoint:
    def test_process_text_via_form(self, client, sample_privacy_policy_text):
        response = client.post(
            "/api/nlp/process-document/",
            data={
                "text": sample_privacy_policy_text,
                "document_name": "test_policy",
                "include_embeddings": "false",
                "include_summaries": "true",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_clauses"] > 0
        assert isinstance(data["clauses"], list)

    def test_process_no_input_returns_400(self, client):
        response = client.post("/api/nlp/process-document/", data={})
        assert response.status_code == 400

    def test_response_clause_has_all_fields(self, client, sample_privacy_policy_text):
        response = client.post(
            "/api/nlp/process-document/",
            data={"text": sample_privacy_policy_text, "include_embeddings": "false"},
        )
        assert response.status_code == 200
        clauses = response.json()["clauses"]
        for clause in clauses:
            assert "clause_number" in clause
            assert "original_text" in clause
            assert "category" in clause
            assert "severity_prior" in clause
            assert "simple_explanation" in clause


class TestProcessChangesEndpoint:
    def test_process_added_clause(self, client):
        payload = {
            "changes": [
                {
                    "clause_number": 1,
                    "clause_title": "New Policy",
                    "clause_text": "We now collect your location data for targeted advertising.",
                    "change_type": "added",
                    "cached_nlp_result": None,
                }
            ],
            "include_embeddings": False,
            "include_summaries": True,
        }
        response = client.post("/api/nlp/process-changes/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["added_processed"] == 1

    def test_invalid_change_type_returns_422(self, client):
        payload = {
            "changes": [
                {
                    "clause_number": 1,
                    "clause_title": "X",
                    "clause_text": "Some text here.",
                    "change_type": "invalid_type",
                }
            ]
        }
        response = client.post("/api/nlp/process-changes/", json=payload)
        assert response.status_code == 422


class TestExtractAndPDFProcessEndpoints:
    @staticmethod
    def _make_pdf(text: str) -> bytes:
        import pymupdf as fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), text, fontsize=11)
        data = doc.tobytes()
        doc.close()
        return data

    def test_extract_valid_pdf_upload(self, client):
        pdf_bytes = self._make_pdf("1. Data Collection\n\nWe collect your email address and usage data.")
        response = client.post(
            "/api/nlp/extract/",
            files={"file": ("policy.pdf", pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_pages"] == 1
        assert "Data Collection" in data["extracted_text"]

    def test_extract_invalid_file_returns_400(self, client):
        response = client.post(
            "/api/nlp/extract/",
            files={"file": ("not_a_pdf.pdf", b"plain text not pdf", "application/pdf")},
        )
        assert response.status_code == 400

    def test_process_document_pdf_upload(self, client):
        pdf_bytes = self._make_pdf(
            "1. Data Collection\n\nWe collect your personal data and cookies.\n\n"
            "2. Arbitration and Jurisdiction\n\nDisputes are resolved by binding arbitration."
        )
        response = client.post(
            "/api/nlp/process-document/",
            files={"file": ("policy.pdf", pdf_bytes, "application/pdf")},
            data={"include_embeddings": "false", "include_summaries": "true"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_clauses"] >= 1
