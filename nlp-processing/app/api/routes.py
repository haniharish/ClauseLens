"""
ClauseLens — API Routes
All FastAPI endpoint definitions for the NLP service.
"""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.schemas import (
    ClassificationOut,
    ClassifyRequest,
    ClassifyResponse,
    EmbedRequest,
    EmbedResponse,
    EmbeddingOut,
    ErrorResponse,
    ExtractResponse,
    HealthResponse,
    ProcessChangesRequest,
    ProcessChangesResponse,
    ProcessDocumentResponse,
    ProcessingMetricsOut,
    SegmentRequest,
    SegmentResponse,
    SegmentedClause,
    SummarizationOut,
    SummarizeRequest,
    SummarizeResponse,
    ClauseExplanationOut,
)
from app.classification.clause_classifier import classify_clause, classify_clauses
from app.classification.severity_priors import get_severity
from app.config import get_settings
from app.embeddings.embedding_generator import embed_clauses
from app.extraction.document_loader import load_from_bytes
from app.segmentation.clause_segmenter import segment_document
from app.services.change_processor import (
    ChangeProcessor,
    ChangeType,
    ClauseChange,
)
from app.services.document_processor import get_processor
from app.summarization.summarizer import get_summarizer
from app.utils.logger import get_logger
from app.utils.validators import validate_pdf_bytes

logger = get_logger(__name__)

router = APIRouter(prefix="/api/nlp", tags=["NLP Processing"])


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@router.get("/health/", response_model=HealthResponse, summary="Health check")
async def health_check():
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        environment=settings.environment,
        models={
            "embedding_model": settings.embedding_model,
            "classification_method": settings.classification_method,
            "llm_provider": settings.llm_provider,
            "llm_model": settings.llm_model,
            "lightweight_mode": settings.lightweight_mode,
        },
    )


# ---------------------------------------------------------------------------
# PDF Extraction
# ---------------------------------------------------------------------------

@router.post("/extract/", response_model=ExtractResponse, summary="Extract text from PDF")
async def extract_text(file: UploadFile = File(...)):
    """
    Accept a PDF file and return the extracted text with page information.
    """
    contents = await file.read()
    is_valid, err = validate_pdf_bytes(contents, file.filename or "upload.pdf")
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    result = load_from_bytes(contents, file.filename or "document.pdf")

    return ExtractResponse(
        document_name=result.document_name,
        total_pages=result.total_pages,
        extracted_text=result.extracted_text,
        status=result.status,
        error_message=result.error_message,
        is_scanned=result.is_scanned,
        ocr_attempted=result.ocr_attempted,
    )


# ---------------------------------------------------------------------------
# Clause Segmentation
# ---------------------------------------------------------------------------

@router.post("/segment/", response_model=SegmentResponse, summary="Segment text into clauses")
async def segment_text(request: SegmentRequest):
    """
    Accept document text and return individual clauses.
    """
    clauses = segment_document(request.text)
    return SegmentResponse(
        document_name=request.document_name,
        total_clauses=len(clauses),
        clauses=[
            SegmentedClause(
                clause_number=c.clause_number,
                clause_title=c.clause_title,
                clause_text=c.clause_text,
            )
            for c in clauses
        ],
    )


# ---------------------------------------------------------------------------
# Clause Classification
# ---------------------------------------------------------------------------

@router.post("/classify/", response_model=ClassifyResponse, summary="Classify clauses")
async def classify_clauses_endpoint(request: ClassifyRequest):
    """
    Accept a list of clauses and return their categories with confidence scores.
    """
    texts = [c.clause_text for c in request.clauses]
    results = classify_clauses(texts)

    classifications = []
    for clause, result in zip(request.clauses, results):
        classifications.append(ClassificationOut(
            clause_number=clause.clause_number,
            clause_title=clause.clause_title,
            category=result.category,
            category_id=result.category_id,
            confidence=result.confidence,
            method=result.method,
            secondary_categories=result.secondary_categories,
            severity_prior=get_severity(result.category),
        ))

    return ClassifyResponse(
        total_clauses=len(classifications),
        classifications=classifications,
    )


# ---------------------------------------------------------------------------
# Embedding Generation
# ---------------------------------------------------------------------------

@router.post("/embed/", response_model=EmbedResponse, summary="Generate embeddings")
async def generate_embeddings(request: EmbedRequest):
    """
    Accept a list of clauses and return semantic embeddings for each.
    """
    texts = [c.clause_text for c in request.clauses]
    ids = [c.clause_number for c in request.clauses]
    results = embed_clauses(texts, ids)

    settings = get_settings()
    embeddings = []
    for emb in results:
        if emb is not None:
            embeddings.append(EmbeddingOut(
                clause_id=emb.clause_id,
                model=emb.model,
                embedding_dimension=emb.embedding_dimension,
                embedding=emb.embedding,
                text_length=emb.text_length,
            ))
        else:
            embeddings.append(None)

    return EmbedResponse(
        total_clauses=len(embeddings),
        model=settings.embedding_model,
        embeddings=embeddings,
    )


# ---------------------------------------------------------------------------
# Summarization
# ---------------------------------------------------------------------------

@router.post("/summarize/", response_model=SummarizeResponse, summary="Summarize clauses")
async def summarize_clauses(request: SummarizeRequest):
    """
    Accept a list of clauses and return simple-language explanations.
    Automatically classifies clauses when category is not provided.
    Optionally accepts user_context for personalized explanation support.
    """
    summarizer = get_summarizer()
    summaries = []

    for clause in request.clauses:
        if clause.category:
            category = clause.category
            confidence = 1.0
        else:
            clf = classify_clause(clause.clause_text)
            category = clf.category
            confidence = clf.confidence

        result = summarizer.summarize(
            clause.clause_text,
            category,
            user_context=request.user_context,
        )
        summaries.append(SummarizationOut(
            clause_number=clause.clause_number,
            clause_title=clause.clause_title,
            source_text=clause.clause_text,
            category=category,
            classification_confidence=confidence,
            simple_explanation=result.simple_explanation,
            model_used=result.model_used,
            provider=result.provider,
            is_mock=result.is_mock,
            success=result.success,
            error=result.error,
        ))

    return SummarizeResponse(total_clauses=len(summaries), summaries=summaries)


# ---------------------------------------------------------------------------
# Full Document Pipeline
# ---------------------------------------------------------------------------

@router.post(
    "/process-document/",
    response_model=ProcessDocumentResponse,
    summary="Complete NLP pipeline on a PDF document",
)
async def process_document(
    file: UploadFile = File(None),
    text: str = Form(None),
    document_name: str = Form("document"),
    include_embeddings: bool = Form(True),
    include_summaries: bool = Form(True),
):
    """
    Run the complete NLP pipeline on a PDF or plain text.
    Returns extracted clauses with categories, severity priors, embeddings,
    and plain-English explanations.
    """
    processor = get_processor()

    if file is not None:
        contents = await file.read()
        is_valid, err = validate_pdf_bytes(contents, file.filename or "upload.pdf")
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
        result = processor.process_pdf(
            contents,
            file.filename or document_name,
            include_embeddings=include_embeddings,
            include_summaries=include_summaries,
        )
    elif text:
        result = processor.process_text(
            text,
            document_name,
            include_embeddings=include_embeddings,
            include_summaries=include_summaries,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either a PDF file or text input.",
        )

    return ProcessDocumentResponse(
        success=result.success,
        document_name=result.document_name,
        total_pages=result.total_pages,
        total_clauses=result.total_clauses,
        processing_status=result.processing_status,
        clauses=[ClauseExplanationOut(**c) for c in result.clauses],
        metrics=ProcessingMetricsOut(**asdict(result.metrics)),
        error_message=result.error_message,
    )


# ---------------------------------------------------------------------------
# Change Processing (for Member 6)
# ---------------------------------------------------------------------------

@router.post(
    "/process-changes/",
    response_model=ProcessChangesResponse,
    summary="Process only added/modified clauses (version update support)",
)
async def process_changes(request: ProcessChangesRequest):
    """
    Accept a diff of clause changes and reprocess only added/modified clauses.
    Unchanged clauses reuse cached NLP results. Removed clauses are preserved
    in the response for historical comparison.
    """
    changes = []
    for item in request.changes:
        changes.append(ClauseChange(
            clause_number=item.clause_number,
            clause_title=item.clause_title,
            clause_text=item.clause_text,
            change_type=ChangeType(item.change_type.value),
            cached_nlp_result=item.cached_nlp_result,
        ))

    cp = ChangeProcessor()
    result = cp.process_changes(
        changes,
        include_embeddings=request.include_embeddings,
        include_summaries=request.include_summaries,
    )

    return ProcessChangesResponse(
        success=result.success,
        total_changes=result.total_changes,
        added_processed=result.added_processed,
        modified_processed=result.modified_processed,
        unchanged_reused=result.unchanged_reused,
        removed_count=result.removed_count,
        clauses=[ClauseExplanationOut(**c) for c in result.clauses],
        error_message=result.error_message,
    )
