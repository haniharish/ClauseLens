"""
ClauseLens — Evaluation Utilities (Research Paper Evaluation Support)
Computes actual metrics on labeled evaluation sets. Never invents scores.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Sequence

from app.classification.taxonomy import CATEGORY_NAMES


@dataclass
class CategoryMetrics:
    category: str
    precision: float
    recall: float
    f1_score: float
    support: int


@dataclass
class ClassificationEvaluationReport:
    total_samples: int
    accuracy: float
    macro_f1: float
    weighted_f1: float
    per_category: list[CategoryMetrics] = field(default_factory=list)


def evaluate_classification(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Sequence[str] | None = None,
) -> ClassificationEvaluationReport:
    """
    Compute category-wise precision, recall, F1-score, and overall accuracy
    from ground-truth labels and predicted labels.
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length.")
    if not y_true:
        raise ValueError("Evaluation dataset cannot be empty.")

    target_labels = list(labels) if labels is not None else list(CATEGORY_NAMES)
    total = len(y_true)
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)

    per_cat: list[CategoryMetrics] = []
    f1_sum = 0.0
    weighted_f1_sum = 0.0
    active_labels = 0

    for label in target_labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        support = tp + fn

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        per_cat.append(
            CategoryMetrics(
                category=label,
                precision=round(precision, 4),
                recall=round(recall, 4),
                f1_score=round(f1, 4),
                support=support,
            )
        )

        if support > 0 or (tp + fp) > 0:
            f1_sum += f1
            weighted_f1_sum += f1 * support
            active_labels += 1

    macro_f1 = f1_sum / active_labels if active_labels > 0 else 0.0
    weighted_f1 = weighted_f1_sum / total if total > 0 else 0.0

    return ClassificationEvaluationReport(
        total_samples=total,
        accuracy=round(correct / total, 4),
        macro_f1=round(macro_f1, 4),
        weighted_f1=round(weighted_f1, 4),
        per_category=per_cat,
    )


@dataclass
class SummaryQualityCheck:
    has_disclaimer: bool
    is_non_empty: bool
    is_concise: bool
    source_overlap_ratio: float
    passed_basic_checks: bool


_DISCLAIMER_SUBSTR = "not legal advice"
_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "to", "of", "in", "for", "with", "on", "by",
    "that", "this", "is", "are", "be", "may", "can", "will", "your", "you", "we",
    "our", "their", "they", "it", "as", "at", "from", "any", "all",
})


def check_summary_faithfulness(
    source_text: str,
    summary_text: str,
    max_words: int = 120,
) -> SummaryQualityCheck:
    """
    Perform automated baseline quality and faithfulness checks on a summary.
    Intended to complement human review, not replace it.
    """
    cleaned_summary = (summary_text or "").strip()
    is_non_empty = len(cleaned_summary) > 0
    has_disclaimer = _DISCLAIMER_SUBSTR in cleaned_summary.lower()

    # Exclude disclaimer line when checking word count and lexical overlap
    body_lines = [
        line for line in cleaned_summary.splitlines()
        if _DISCLAIMER_SUBSTR not in line.lower()
    ]
    body_text = " ".join(body_lines).strip()
    words = re.findall(r"[a-zA-Z0-9]+", body_text.lower())
    is_concise = 3 <= len(words) <= max_words

    src_tokens = {
        w for w in re.findall(r"[a-zA-Z0-9]+", (source_text or "").lower())
        if w not in _STOPWORDS and len(w) > 2
    }
    sum_tokens = {
        w for w in words
        if w not in _STOPWORDS and len(w) > 2
    }

    if sum_tokens:
        overlap = len(src_tokens & sum_tokens) / len(sum_tokens)
    else:
        overlap = 0.0

    passed = is_non_empty and has_disclaimer and is_concise
    return SummaryQualityCheck(
        has_disclaimer=has_disclaimer,
        is_non_empty=is_non_empty,
        is_concise=is_concise,
        source_overlap_ratio=round(overlap, 4),
        passed_basic_checks=passed,
    )
