"""
Tests for AI summarization (app/summarization/).
Uses mock LLM provider — no real API calls made.
"""
from __future__ import annotations

import pytest


class TestSummarizer:
    def test_summarizer_instantiates(self):
        from app.summarization.summarizer import Summarizer
        s = Summarizer()
        assert s is not None

    def test_mock_summary_returned(self):
        """Mock provider should return a non-empty explanation."""
        from app.summarization.summarizer import Summarizer
        s = Summarizer()
        result = s.summarize("We collect your personal data.", "Data Collection")
        assert result.success is True
        assert result.simple_explanation != ""
        assert result.is_mock is True

    def test_disclaimer_always_present(self):
        """Disclaimer must appear in every summary."""
        from app.summarization.summarizer import Summarizer
        s = Summarizer()
        result = s.summarize("You waive your right to sue in court.", "Arbitration and Jurisdiction")
        assert "not legal advice" in result.simple_explanation.lower() or \
               "informational purposes" in result.simple_explanation.lower()

    def test_empty_clause_returns_failure(self):
        from app.summarization.summarizer import Summarizer
        s = Summarizer()
        result = s.summarize("", "Other")
        assert result.success is False
        assert result.error is not None

    def test_batch_summarization(self):
        from app.summarization.summarizer import Summarizer
        s = Summarizer()
        pairs = [
            ("We collect your name and email.", "Data Collection"),
            ("We share data with third parties.", "Data Sharing with Third Parties"),
        ]
        results = s.summarize_batch(pairs)
        assert len(results) == 2
        for r in results:
            assert r.success is True

    def test_prompts_built_correctly(self):
        from app.summarization.prompts import build_user_prompt
        prompt = build_user_prompt("We collect cookies.", "Data Collection")
        assert "Data Collection" in prompt
        assert "We collect cookies." in prompt


class TestExplanationGenerator:
    def test_builds_full_explanation(self):
        from app.summarization.explanation_generator import build_explanation
        from app.classification.clause_classifier import ClassificationResult
        from app.embeddings.embedding_generator import EmbeddingResult
        from app.summarization.summarizer import SummarizationResult

        clf = ClassificationResult(
            category="Data Collection",
            category_id=1,
            confidence=0.8,
            method="rule_based",
        )
        emb = EmbeddingResult(
            clause_id=1,
            model="test-model",
            embedding_dimension=3,
            embedding=[0.1, 0.2, 0.3],
            text_length=50,
        )
        summ = SummarizationResult(
            simple_explanation="This clause means the company collects your data.",
            model_used="mock",
            provider="mock",
            is_mock=True,
            success=True,
        )

        result = build_explanation(
            clause_number=1,
            clause_title="Data Collection",
            original_text="We collect your personal data.",
            classification=clf,
            embedding=emb,
            summarization=summ,
        )

        assert result.clause_number == 1
        assert result.category == "Data Collection"
        assert result.severity_prior == 0.50
        assert len(result.embedding) == 3
        assert "collects" in result.simple_explanation.lower()
        assert result.processing_status == "completed"

    def test_partial_status_on_missing_embedding(self):
        from app.summarization.explanation_generator import build_explanation
        from app.classification.clause_classifier import ClassificationResult
        from app.summarization.summarizer import SummarizationResult

        clf = ClassificationResult(
            category="Other", category_id=11, confidence=0.1, method="rule_based"
        )
        summ = SummarizationResult(
            simple_explanation="Mock explanation.",
            model_used="mock", provider="mock", is_mock=True, success=True
        )

        result = build_explanation(
            clause_number=1,
            clause_title="Test",
            original_text="Some clause.",
            classification=clf,
            embedding=None,  # missing
            summarization=summ,
        )
        assert result.processing_status == "partial"
        assert len(result.errors) > 0

    def test_external_llm_failure_handled(self, monkeypatch):
        """When external LLM fails, success=False and error is reported clearly."""
        from app.summarization.summarizer import Summarizer

        class _FailingProvider:
            def complete(self, system_prompt: str, user_prompt: str) -> str:
                raise RuntimeError("Upstream 503 Service Unavailable")

        s = Summarizer()
        s._provider = _FailingProvider()
        s._provider_name = "openai"
        s._model_name = "gpt-4o-mini"

        result = s.summarize("We collect personal information.", "Data Collection")
        assert result.success is False
        assert result.simple_explanation == ""
        assert "Upstream 503" in (result.error or "")

    def test_user_context_explanation_prompt(self):
        from app.summarization.prompts import build_context_explanation_prompt
        prompt = build_context_explanation_prompt(
            "Users under 13 require parental consent.",
            "Children and Age",
            {"age_group": "minor", "jurisdiction": "US"},
        )
        assert "age_group: minor" in prompt
        assert "jurisdiction: US" in prompt
