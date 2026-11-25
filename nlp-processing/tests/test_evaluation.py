"""
Tests for evaluation utilities (app/utils/evaluator.py).
"""
from __future__ import annotations

import pytest
from app.utils.evaluator import check_summary_faithfulness, evaluate_classification


class TestClassificationEvaluator:
    def test_perfect_predictions(self):
        y_true = ["Data Collection", "Liability Limitation", "Other"]
        y_pred = ["Data Collection", "Liability Limitation", "Other"]
        report = evaluate_classification(y_true, y_pred)
        assert report.accuracy == 1.0
        assert report.macro_f1 == 1.0
        assert report.weighted_f1 == 1.0
        assert report.total_samples == 3

    def test_partial_predictions(self):
        y_true = ["Data Collection", "Data Collection", "Arbitration and Jurisdiction"]
        y_pred = ["Data Collection", "Other", "Arbitration and Jurisdiction"]
        report = evaluate_classification(y_true, y_pred)
        assert report.total_samples == 3
        assert abs(report.accuracy - (2 / 3)) < 1e-3
        dc = next(c for c in report.per_category if c.category == "Data Collection")
        assert dc.precision == 1.0
        assert dc.recall == 0.5
        assert dc.support == 2

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            evaluate_classification(["Data Collection"], [])

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            evaluate_classification([], [])


class TestSummaryFaithfulnessCheck:
    def test_valid_summary_passes(self):
        source = "The company may share personal information with third-party service providers."
        summary = (
            "The company can share your personal information with external service providers.\n"
            "⚠️ This is an AI-generated explanation for informational purposes, not legal advice."
        )
        check = check_summary_faithfulness(source, summary)
        assert check.has_disclaimer is True
        assert check.is_non_empty is True
        assert check.is_concise is True
        assert check.source_overlap_ratio > 0.3
        assert check.passed_basic_checks is True

    def test_missing_disclaimer_fails(self):
        check = check_summary_faithfulness(
            "We collect your personal data.",
            "The company collects your personal data.",
        )
        assert check.has_disclaimer is False
        assert check.passed_basic_checks is False
