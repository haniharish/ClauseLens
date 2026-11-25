"""
Tests for clause classification (app/classification/).
"""
from __future__ import annotations

import pytest
from app.classification.clause_classifier import RuleBasedClassifier, classify_clause
from app.classification.taxonomy import CATEGORIES, CATEGORY_NAMES, OTHER_CATEGORY
from app.classification.severity_priors import SEVERITY_PRIORS, get_severity


class TestTaxonomy:
    def test_has_eleven_categories(self):
        assert len(CATEGORIES) == 11

    def test_category_names_match_research(self):
        expected = {
            "Data Collection",
            "Data Sharing with Third Parties",
            "Data Retention",
            "Arbitration and Jurisdiction",
            "Liability Limitation",
            "Unilateral Change of Terms",
            "Auto-renewal and Fees",
            "Content License",
            "Account Termination",
            "Children and Age",
            "Other",
        }
        actual = set(CATEGORY_NAMES)
        assert actual == expected

    def test_all_categories_have_ids(self):
        for cat in CATEGORIES:
            assert isinstance(cat.id, int)
            assert cat.id >= 1

    def test_other_category_exists(self):
        assert OTHER_CATEGORY.name == "Other"


class TestSeverityPriors:
    def test_all_categories_have_priors(self):
        for cat in CATEGORIES:
            assert cat.name in SEVERITY_PRIORS, f"Missing prior for {cat.name}"

    def test_priors_in_valid_range(self):
        for name, score in SEVERITY_PRIORS.items():
            assert 0.0 <= score <= 1.0, f"Invalid prior for {name}: {score}"

    def test_arbitration_highest(self):
        assert SEVERITY_PRIORS["Arbitration and Jurisdiction"] == 0.90

    def test_other_lowest(self):
        assert SEVERITY_PRIORS["Other"] == 0.10

    def test_get_severity_function(self):
        assert get_severity("Liability Limitation") == 0.85

    def test_get_severity_unknown_returns_default(self):
        result = get_severity("NonExistentCategory")
        assert result == 0.10


class TestRuleBasedClassifier:
    def setup_method(self):
        self.clf = RuleBasedClassifier()

    def test_data_collection_clause(self, sample_data_collection_clause):
        result = self.clf.classify(sample_data_collection_clause)
        assert result.category == "Data Collection"
        assert result.confidence > 0

    def test_arbitration_clause(self, sample_arbitration_clause):
        result = self.clf.classify(sample_arbitration_clause)
        assert result.category == "Arbitration and Jurisdiction"

    def test_liability_clause(self, sample_liability_clause):
        result = self.clf.classify(sample_liability_clause)
        assert result.category == "Liability Limitation"

    def test_children_clause(self, sample_children_clause):
        result = self.clf.classify(sample_children_clause)
        assert result.category == "Children and Age"

    def test_data_sharing_clause(self):
        text = "We share your personal data with our advertising partners and third-party vendors."
        result = self.clf.classify(text)
        assert result.category == "Data Sharing with Third Parties"

    def test_auto_renewal_clause(self):
        text = "Your subscription automatically renews unless cancelled before the billing date."
        result = self.clf.classify(text)
        assert result.category == "Auto-renewal and Fees"

    def test_unrecognised_returns_other(self):
        text = "The weather is nice today and we enjoy sunny afternoons."
        result = self.clf.classify(text)
        assert result.category == "Other"

    def test_result_has_confidence(self):
        result = self.clf.classify("We collect your personal data.")
        assert 0.0 <= result.confidence <= 1.0

    def test_result_has_method(self):
        result = self.clf.classify("We collect your personal data.")
        assert result.method == "rule_based"

    def test_all_scores_returned(self):
        result = self.clf.classify("We collect your personal data.")
        assert isinstance(result.all_scores, dict)
        assert len(result.all_scores) > 0

    def test_empty_text(self):
        result = self.clf.classify("")
        assert result.category == "Other"

    def test_module_function(self):
        result = classify_clause("Your data may be shared with third parties.")
        assert result.category != ""
