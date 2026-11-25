"""
ClauseLens — Document Processor
Orchestrates the complete NLP pipeline:
  PDF Extraction → Text Cleaning → Clause Segmentation →
  Classification → Severity → Embeddings → Summarization → Output
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Optional

from app.classification.clause_classifier import classify_clauses
from app.embeddings.embedding_generator import embed_clauses
from app.extraction.document_loader import load_from_bytes, load_from_text
from app.extraction.text_cleaner import clean_text
from app.segmentation.clause_segmenter import segment_document
from app.summarization.explanation_generator import build_explanation
from app.summarization.summarizer import get_summarizer
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessingMetrics:
    extraction_time_s: float = 0.0
    cleaning_time_s: float = 0.0
    segmentation_time_s: float = 0.0
    classification_time_s: float = 0.0
    embedding_time_s: float = 0.0
    summarization_time_s: float = 0.0
    total_time_s: float = 0.0


@dataclass
class DocumentProcessingResult:
    success: bool
    document_name: str
    total_pages: int
    total_clauses: int
    processing_status: str         # "completed" | "partial" | "failed"
    clauses: list[dict]            # List of ClauseExplanation dicts
    metrics: ProcessingMetrics = field(default_factory=ProcessingMetrics)
    error_message: str = ""


class DocumentProcessor:
    """
    Runs the full NLP pipeline on a document.
    Each NLP step is independently timed and errors are caught per-clause.
    """

    def process_pdf(
        self,
        pdf_bytes: bytes,
        document_name: str = "document.pdf",
        include_embeddings: bool = True,
        include_summaries: bool = True,
    ) -> DocumentProcessingResult:
        """Process a PDF document end-to-end."""
        start = time.perf_counter()
        metrics = ProcessingMetrics()

        # -----------------------------------------------------------
        # STEP 1 & 2: Extract text
        # -----------------------------------------------------------
        t0 = time.perf_counter()
        extraction = load_from_bytes(pdf_bytes, document_name)
        metrics.extraction_time_s = round(time.perf_counter() - t0, 6)

        if extraction.status == "error":
            return DocumentProcessingResult(
                success=False,
                document_name=document_name,
                total_pages=0,
                total_clauses=0,
                processing_status="failed",
                clauses=[],
                metrics=metrics,
                error_message=extraction.error_message,
            )

        if extraction.status == "scanned":
            return DocumentProcessingResult(
                success=False,
                document_name=document_name,
                total_pages=extraction.total_pages,
                total_clauses=0,
                processing_status="failed",
                clauses=[],
                metrics=metrics,
                error_message=extraction.error_message,
            )

        return self._process_text(
            raw_text=extraction.extracted_text,
            document_name=document_name,
            total_pages=extraction.total_pages,
            include_embeddings=include_embeddings,
            include_summaries=include_summaries,
            start_time=start,
            metrics=metrics,
        )

    def process_text(
        self,
        text: str,
        document_name: str = "inline_text",
        include_embeddings: bool = True,
        include_summaries: bool = True,
    ) -> DocumentProcessingResult:
        """Process pre-extracted plain text end-to-end."""
        return self._process_text(
            raw_text=text,
            document_name=document_name,
            total_pages=1,
            include_embeddings=include_embeddings,
            include_summaries=include_summaries,
            start_time=time.perf_counter(),
            metrics=ProcessingMetrics(),
        )

    def _process_text(
        self,
        raw_text: str,
        document_name: str,
        total_pages: int,
        include_embeddings: bool,
        include_summaries: bool,
        start_time: float,
        metrics: ProcessingMetrics,
    ) -> DocumentProcessingResult:

        # -----------------------------------------------------------
        # STEP 3: Clean text
        # -----------------------------------------------------------
        t0 = time.perf_counter()
        cleaning = clean_text(raw_text)
        cleaned = cleaning.cleaned_text
        metrics.cleaning_time_s = round(time.perf_counter() - t0, 6)

        # -----------------------------------------------------------
        # STEP 4: Segment into clauses
        # -----------------------------------------------------------
        t0 = time.perf_counter()
        clauses = segment_document(cleaned)
        metrics.segmentation_time_s = round(time.perf_counter() - t0, 6)

        if not clauses:
            logger.warning("no_clauses_segmented", document=document_name)
            return DocumentProcessingResult(
                success=False,
                document_name=document_name,
                total_pages=total_pages,
                total_clauses=0,
                processing_status="failed",
                clauses=[],
                metrics=metrics,
                error_message="No clauses could be segmented from the document.",
            )

        clause_texts = [c.clause_text for c in clauses]
        clause_ids = [c.clause_number for c in clauses]

        # -----------------------------------------------------------
        # STEP 5: Classify
        # -----------------------------------------------------------
        t0 = time.perf_counter()
        classifications = classify_clauses(clause_texts)
        metrics.classification_time_s = round(time.perf_counter() - t0, 6)

        # -----------------------------------------------------------
        # STEP 6 & 7: Embeddings
        # -----------------------------------------------------------
        embeddings_list = [None] * len(clauses)
        if include_embeddings:
            t0 = time.perf_counter()
            embeddings_list = embed_clauses(clause_texts, clause_ids)
            metrics.embedding_time_s = round(time.perf_counter() - t0, 6)

        # -----------------------------------------------------------
        # STEP 8: Summarize
        # -----------------------------------------------------------
        summaries_list = [None] * len(clauses)
        if include_summaries:
            t0 = time.perf_counter()
            summarizer = get_summarizer()
            pairs = [
                (clauses[i].clause_text, classifications[i].category)
                for i in range(len(clauses))
            ]
            summaries_list = summarizer.summarize_batch(pairs)
            metrics.summarization_time_s = round(time.perf_counter() - t0, 6)

        # -----------------------------------------------------------
        # STEP 9: Assemble output
        # -----------------------------------------------------------
        output_clauses: list[dict] = []
        for i, clause in enumerate(clauses):
            explanation = build_explanation(
                clause_number=clause.clause_number,
                clause_title=clause.clause_title,
                original_text=clause.clause_text,
                classification=classifications[i] if i < len(classifications) else None,
                embedding=embeddings_list[i] if i < len(embeddings_list) else None,
                summarization=summaries_list[i] if i < len(summaries_list) else None,
            )
            output_clauses.append(asdict(explanation))

        metrics.total_time_s = round(time.perf_counter() - start_time, 6)
        logger.info(
            "document_processing_complete",
            document=document_name,
            clauses=len(output_clauses),
            total_time=metrics.total_time_s,
        )

        return DocumentProcessingResult(
            success=True,
            document_name=document_name,
            total_pages=total_pages,
            total_clauses=len(output_clauses),
            processing_status="completed",
            clauses=output_clauses,
            metrics=metrics,
        )


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------
_processor: Optional[DocumentProcessor] = None


def get_processor() -> DocumentProcessor:
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor
