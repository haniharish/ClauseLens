"""
ClauseLens — Clause Classifier
Classifies clauses into the 11-category taxonomy using a hybrid approach:
  1. Rule-based keyword matching (fast, transparent baseline).
  2. Zero-shot classification via HuggingFace (when available & configured).
  3. Hybrid: rule-based if confident, zero-shot fallback otherwise.

Limitations (documented):
- Zero-shot models are not fine-tuned on legal text; accuracy may vary.
- Multi-label support via top-k zero-shot scores.
- When no model is available, rule-based scores are returned and labelled.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.classification.taxonomy import (
    CATEGORIES,
    CATEGORY_BY_NAME,
    CATEGORY_NAMES,
    OTHER_CATEGORY,
    ClauseCategory,
)
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    category: str
    category_id: int
    confidence: float          # 0.0 – 1.0
    method: str                # "rule_based" | "zero_shot" | "hybrid"
    all_scores: dict[str, float] = field(default_factory=dict)
    is_multi_label: bool = False
    secondary_categories: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Rule-based classifier
# ---------------------------------------------------------------------------

class RuleBasedClassifier:
    """
    Keyword-overlap classifier.
    Scores each category by counting keyword hits (normalized by keyword count).
    Returns the top-scoring category and all scores.
    """

    # Minimum keyword-match score to claim a confident classification
    # (below this, we return "Other")
    CONFIDENCE_THRESHOLD = 0.05

    def classify(self, text: str) -> ClassificationResult:
        lower = text.lower()
        scores: dict[str, float] = {}

        for cat in CATEGORIES:
            if not cat.keywords:
                scores[cat.name] = 0.0
                continue
            hits = sum(1 for kw in cat.keywords if kw in lower)
            scores[cat.name] = hits / len(cat.keywords)

        # Normalize scores to [0, 1] relative to max
        max_score = max(scores.values()) if scores else 0.0
        if max_score > 0:
            normalized = {k: v / max_score for k, v in scores.items()}
        else:
            normalized = {k: 0.0 for k in scores}

        best_cat = max(scores, key=lambda k: scores[k])
        raw_best = scores[best_cat]

        if raw_best < self.CONFIDENCE_THRESHOLD:
            return ClassificationResult(
                category="Other",
                category_id=OTHER_CATEGORY.id,
                confidence=0.1,
                method="rule_based",
                all_scores=normalized,
            )

        # Detect secondary categories (score >= 50% of best)
        secondary = [
            k for k, v in scores.items()
            if k != best_cat and v >= raw_best * 0.5 and v > 0
        ]

        return ClassificationResult(
            category=best_cat,
            category_id=CATEGORY_BY_NAME[best_cat].id,
            confidence=min(raw_best * 2, 0.95),  # heuristic confidence cap
            method="rule_based",
            all_scores=normalized,
            is_multi_label=len(secondary) > 0,
            secondary_categories=secondary,
        )


# ---------------------------------------------------------------------------
# Zero-shot classifier (HuggingFace)
# ---------------------------------------------------------------------------

class ZeroShotClassifier:
    """
    Uses a HuggingFace zero-shot classification pipeline.
    Lazy-loads the model on first use.
    """

    def __init__(self):
        self._pipeline = None
        self._model_name: Optional[str] = None

    def _get_pipeline(self):
        if self._pipeline is False:
            return None
        if self._pipeline is not None:
            return self._pipeline

        settings = get_settings()
        if settings.lightweight_mode:
            logger.info("zero_shot_skipped_lightweight_mode")
            return None

        try:
            from transformers import pipeline as hf_pipeline
            model = settings.zero_shot_model
            logger.info("loading_zero_shot_model", model=model)
            self._pipeline = hf_pipeline(
                "zero-shot-classification",
                model=model,
                device=-1,  # CPU; set to 0 for GPU
            )
            self._model_name = model
            logger.info("zero_shot_model_loaded", model=model)
        except Exception as exc:
            logger.warning("zero_shot_load_failed", exc=str(exc))
            self._pipeline = False  # Mark unavailable

        return self._pipeline if self._pipeline is not False else None

    def classify(self, text: str) -> Optional[ClassificationResult]:
        pipeline = self._get_pipeline()
        if pipeline is None:
            return None

        # Truncate text to avoid token limits
        input_text = text[:1024]

        try:
            result = pipeline(
                input_text,
                candidate_labels=CATEGORY_NAMES,
                multi_label=True,
            )
        except Exception as exc:
            logger.warning("zero_shot_inference_failed", exc=str(exc))
            return None

        labels: list[str] = result["labels"]
        scores: list[float] = result["scores"]

        all_scores = dict(zip(labels, scores))
        best = labels[0]
        best_score = scores[0]

        # Secondary categories: score >= 0.3 and not the primary
        secondary = [
            lbl for lbl, sc in zip(labels[1:], scores[1:])
            if sc >= 0.3
        ]

        cat = CATEGORY_BY_NAME.get(best, OTHER_CATEGORY)
        return ClassificationResult(
            category=best,
            category_id=cat.id,
            confidence=round(best_score, 4),
            method="zero_shot",
            all_scores={k: round(v, 4) for k, v in all_scores.items()},
            is_multi_label=len(secondary) > 0,
            secondary_categories=secondary,
        )


# ---------------------------------------------------------------------------
# Hybrid classifier (default)
# ---------------------------------------------------------------------------

class ClauseClassifier:
    """
    Hybrid classifier: uses rule-based scoring; supplements with zero-shot
    when rule-based confidence is low.
    """

    # Rule-based confidence below this triggers zero-shot fallback
    HYBRID_FALLBACK_THRESHOLD = 0.3

    def __init__(self):
        self._rule = RuleBasedClassifier()
        self._zero_shot = ZeroShotClassifier()
        settings = get_settings()
        self._method = settings.classification_method

    def classify(self, text: str) -> ClassificationResult:
        if self._method == "rule_based":
            result = self._rule.classify(text)
            return result

        if self._method == "zero_shot":
            zs = self._zero_shot.classify(text)
            if zs is not None:
                return zs
            # Fallback
            logger.warning("zero_shot_unavailable_falling_back_to_rule_based")
            return self._rule.classify(text)

        # Hybrid (default)
        rule_result = self._rule.classify(text)
        if rule_result.confidence >= self.HYBRID_FALLBACK_THRESHOLD:
            rule_result.method = "hybrid_rule"
            return rule_result

        # Low confidence — try zero-shot
        zs = self._zero_shot.classify(text)
        if zs is not None:
            zs.method = "hybrid_zero_shot"
            return zs

        rule_result.method = "hybrid_rule_fallback"
        return rule_result

    def classify_batch(self, texts: list[str]) -> list[ClassificationResult]:
        return [self.classify(t) for t in texts]


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------
_classifier: Optional[ClauseClassifier] = None


def get_classifier() -> ClauseClassifier:
    global _classifier
    if _classifier is None:
        _classifier = ClauseClassifier()
    return _classifier


def classify_clause(text: str) -> ClassificationResult:
    return get_classifier().classify(text)


def classify_clauses(texts: list[str]) -> list[ClassificationResult]:
    return get_classifier().classify_batch(texts)
