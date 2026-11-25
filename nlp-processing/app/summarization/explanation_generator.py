"""
ClauseLens — Explanation Generator
Assembles all NLP outputs into the structured clause explanation record
used by the backend and downstream modules (Member 5 personalization).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.classification.clause_classifier import ClassificationResult
from app.classification.severity_priors import get_severity
from app.embeddings.embedding_generator import EmbeddingResult
from app.summarization.summarizer import SummarizationResult


@dataclass
class ClauseExplanation:
    """
    Complete NLP output record for a single clause.
    Returned to the Django backend and available to Member 5.
    """
    clause_number: int
    clause_title: str
    original_text: str

    # Classification
    category: str
    category_id: int
    classification_confidence: float
    classification_method: str
    secondary_categories: list[str] = field(default_factory=list)

    # Risk (prior only — final personalized score computed by Member 5)
    severity_prior: float = 0.0

    # Embedding (for Member 5's similarity / relevance calculation)
    embedding: list[float] = field(default_factory=list)
    embedding_model: str = ""
    embedding_dimension: int = 0

    # Summarization
    simple_explanation: str = ""
    summarization_model: str = ""
    summarization_provider: str = ""
    is_mock_summary: bool = False

    # Status
    processing_status: str = "completed"  # "completed" | "partial" | "failed"
    errors: list[str] = field(default_factory=list)


def build_explanation(
    clause_number: int,
    clause_title: str,
    original_text: str,
    classification: Optional[ClassificationResult],
    embedding: Optional[EmbeddingResult],
    summarization: Optional[SummarizationResult],
) -> ClauseExplanation:
    """
    Assemble a ClauseExplanation from individual NLP component results.
    """
    errors: list[str] = []
    status = "completed"

    # Classification
    if classification:
        category = classification.category
        category_id = classification.category_id
        confidence = classification.confidence
        method = classification.method
        secondary = classification.secondary_categories
    else:
        category = "Other"
        category_id = 11
        confidence = 0.0
        method = "unavailable"
        secondary = []
        errors.append("Classification failed or unavailable.")
        status = "partial"

    severity = get_severity(category)

    # Embedding
    if embedding:
        emb_vec = embedding.embedding
        emb_model = embedding.model
        emb_dim = embedding.embedding_dimension
    else:
        emb_vec = []
        emb_model = ""
        emb_dim = 0
        errors.append("Embedding generation failed or unavailable.")
        status = "partial"

    # Summarization
    if summarization and summarization.success:
        explanation = summarization.simple_explanation
        sum_model = summarization.model_used
        sum_provider = summarization.provider
        is_mock = summarization.is_mock
    else:
        explanation = ""
        sum_model = ""
        sum_provider = ""
        is_mock = False
        err_msg = (summarization.error if summarization else "Summarizer not called.")
        errors.append(f"Summarization failed: {err_msg}")
        status = "partial"

    if errors and len(errors) >= 3:
        status = "failed"

    return ClauseExplanation(
        clause_number=clause_number,
        clause_title=clause_title,
        original_text=original_text,
        category=category,
        category_id=category_id,
        classification_confidence=confidence,
        classification_method=method,
        secondary_categories=secondary,
        severity_prior=severity,
        embedding=emb_vec,
        embedding_model=emb_model,
        embedding_dimension=emb_dim,
        simple_explanation=explanation,
        summarization_model=sum_model,
        summarization_provider=sum_provider,
        is_mock_summary=is_mock,
        processing_status=status,
        errors=errors,
    )
