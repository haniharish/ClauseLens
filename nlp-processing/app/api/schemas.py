"""
ClauseLens — Pydantic Schemas
Request and response models for all API endpoints.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Shared / inner models
# ---------------------------------------------------------------------------

class ClauseInput(BaseModel):
    clause_number: int = Field(..., ge=1)
    clause_title: str = Field(default="", max_length=500)
    clause_text: str = Field(..., min_length=1)
    category: Optional[str] = None


class ClauseExplanationOut(BaseModel):
    clause_number: int
    clause_title: str
    original_text: str
    category: str
    category_id: int
    classification_confidence: float
    classification_method: str
    secondary_categories: list[str] = []
    severity_prior: float
    embedding: list[float] = []
    embedding_model: str = ""
    embedding_dimension: int = 0
    simple_explanation: str = ""
    summarization_model: str = ""
    summarization_provider: str = ""
    is_mock_summary: bool = False
    processing_status: str
    errors: list[str] = []
    change_type: Optional[str] = None
    reprocessed: Optional[bool] = None


class ProcessingMetricsOut(BaseModel):
    extraction_time_s: float = 0.0
    cleaning_time_s: float = 0.0
    segmentation_time_s: float = 0.0
    classification_time_s: float = 0.0
    embedding_time_s: float = 0.0
    summarization_time_s: float = 0.0
    total_time_s: float = 0.0


# ---------------------------------------------------------------------------
# /api/nlp/extract/
# ---------------------------------------------------------------------------

class ExtractResponse(BaseModel):
    document_name: str
    total_pages: int
    extracted_text: str
    status: str
    error_message: str = ""
    is_scanned: bool = False
    ocr_attempted: bool = False


# ---------------------------------------------------------------------------
# /api/nlp/segment/
# ---------------------------------------------------------------------------

class SegmentRequest(BaseModel):
    text: str = Field(..., min_length=10)
    document_name: str = "document"


class SegmentedClause(BaseModel):
    clause_number: int
    clause_title: str
    clause_text: str


class SegmentResponse(BaseModel):
    document_name: str
    total_clauses: int
    clauses: list[SegmentedClause]


# ---------------------------------------------------------------------------
# /api/nlp/classify/
# ---------------------------------------------------------------------------

class ClassifyRequest(BaseModel):
    clauses: list[ClauseInput]


class ClassificationOut(BaseModel):
    clause_number: int
    clause_title: str
    category: str
    category_id: int
    confidence: float
    method: str
    secondary_categories: list[str] = []
    severity_prior: float


class ClassifyResponse(BaseModel):
    total_clauses: int
    classifications: list[ClassificationOut]


# ---------------------------------------------------------------------------
# /api/nlp/embed/
# ---------------------------------------------------------------------------

class EmbedRequest(BaseModel):
    clauses: list[ClauseInput]


class EmbeddingOut(BaseModel):
    clause_id: int
    model: str
    embedding_dimension: int
    embedding: list[float]
    text_length: int


class EmbedResponse(BaseModel):
    total_clauses: int
    model: str
    embeddings: list[Optional[EmbeddingOut]]


# ---------------------------------------------------------------------------
# /api/nlp/summarize/
# ---------------------------------------------------------------------------

class SummarizeRequest(BaseModel):
    clauses: list[ClauseInput]
    user_context: Optional[dict[str, str]] = None


class SummarizationOut(BaseModel):
    clause_number: int
    clause_title: str
    source_text: str
    category: str
    classification_confidence: float = 0.0
    simple_explanation: str
    model_used: str
    provider: str
    is_mock: bool
    success: bool
    error: Optional[str] = None


class SummarizeResponse(BaseModel):
    total_clauses: int
    summaries: list[SummarizationOut]


# ---------------------------------------------------------------------------
# /api/nlp/process-document/
# ---------------------------------------------------------------------------

class ProcessDocumentResponse(BaseModel):
    success: bool
    document_name: str
    total_pages: int
    total_clauses: int
    processing_status: str
    clauses: list[ClauseExplanationOut]
    metrics: ProcessingMetricsOut
    error_message: str = ""


# ---------------------------------------------------------------------------
# /api/nlp/process-changes/
# ---------------------------------------------------------------------------

class ChangeTypeEnum(str, Enum):
    added = "added"
    modified = "modified"
    unchanged = "unchanged"
    removed = "removed"


class ClauseChangeInput(BaseModel):
    clause_number: int = Field(..., ge=1)
    clause_title: str = ""
    clause_text: str = ""
    change_type: ChangeTypeEnum
    cached_nlp_result: Optional[dict] = None


class ProcessChangesRequest(BaseModel):
    changes: list[ClauseChangeInput]
    include_embeddings: bool = True
    include_summaries: bool = True


class ProcessChangesResponse(BaseModel):
    success: bool
    total_changes: int
    added_processed: int
    modified_processed: int
    unchanged_reused: int
    removed_count: int
    clauses: list[ClauseExplanationOut]
    error_message: str = ""


# ---------------------------------------------------------------------------
# /api/nlp/health/
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    models: dict[str, Any]


# ---------------------------------------------------------------------------
# Generic error
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
