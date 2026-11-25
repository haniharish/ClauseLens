"""
ClauseLens — Change Processor
Handles diff-only reprocessing for version updates (supports Member 6).

Processing rules:
- ADDED clauses:    classify, embed, summarize.
- MODIFIED clauses: reclassify, re-embed, re-summarize.
- UNCHANGED clauses: return cached NLP results as-is.
- REMOVED clauses:  no new NLP; preserve old data for history.

This module does NOT implement the clause-alignment algorithm.
Member 6 is responsible for detecting which clauses are added/modified/removed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional

from app.classification.clause_classifier import classify_clause
from app.embeddings.embedding_generator import embed_clause
from app.summarization.explanation_generator import build_explanation
from app.summarization.summarizer import get_summarizer
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChangeType(str, Enum):
    ADDED = "added"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"
    REMOVED = "removed"


@dataclass
class ClauseChange:
    clause_number: int
    clause_title: str
    clause_text: str
    change_type: ChangeType
    cached_nlp_result: Optional[dict] = None  # For UNCHANGED clauses


@dataclass
class ChangeProcessingResult:
    success: bool
    total_changes: int
    added_processed: int
    modified_processed: int
    unchanged_reused: int
    removed_count: int
    clauses: list[dict] = field(default_factory=list)
    error_message: str = ""


class ChangeProcessor:
    """
    Processes only the changed clauses in a document version update.
    """

    def process_changes(
        self,
        changes: list[ClauseChange],
        include_embeddings: bool = True,
        include_summaries: bool = True,
    ) -> ChangeProcessingResult:
        """
        Process a list of clause changes and return updated NLP results.

        Parameters
        ----------
        changes : list[ClauseChange]
            All clauses with their change type. For UNCHANGED clauses,
            cached_nlp_result must be provided.
        include_embeddings : bool
            Whether to generate embeddings for new/modified clauses.
        include_summaries : bool
            Whether to generate summaries for new/modified clauses.

        Returns
        -------
        ChangeProcessingResult
        """
        clauses_output: list[dict] = []
        added = modified = unchanged = removed = 0

        summarizer = get_summarizer()

        for change in changes:
            change_type = change.change_type

            if change_type == ChangeType.REMOVED:
                # Preserve old data for historical comparison (provided by Member 6)
                removed += 1
                if change.cached_nlp_result:
                    record = dict(change.cached_nlp_result)
                    record["change_type"] = ChangeType.REMOVED
                    record["reprocessed"] = False
                    clauses_output.append(record)
                continue

            if change_type == ChangeType.UNCHANGED:
                # Reuse cached result — no reprocessing
                unchanged += 1
                if change.cached_nlp_result:
                    record = dict(change.cached_nlp_result)
                    record["change_type"] = ChangeType.UNCHANGED
                    record["reprocessed"] = False
                    clauses_output.append(record)
                else:
                    logger.warning(
                        "unchanged_clause_missing_cache",
                        clause=change.clause_number,
                    )
                continue

            # ADDED or MODIFIED — requires full reprocessing
            logger.info(
                "reprocessing_clause",
                clause=change.clause_number,
                change_type=change_type,
            )

            classification = classify_clause(change.clause_text)

            embedding = None
            if include_embeddings:
                embedding = embed_clause(change.clause_text, change.clause_number)

            summarization = None
            if include_summaries:
                summarization = summarizer.summarize(
                    change.clause_text, classification.category
                )

            explanation = build_explanation(
                clause_number=change.clause_number,
                clause_title=change.clause_title,
                original_text=change.clause_text,
                classification=classification,
                embedding=embedding,
                summarization=summarization,
            )

            record = asdict(explanation)
            record["change_type"] = change_type
            record["reprocessed"] = True
            clauses_output.append(record)

            if change_type == ChangeType.ADDED:
                added += 1
            else:
                modified += 1

        logger.info(
            "change_processing_complete",
            added=added,
            modified=modified,
            unchanged=unchanged,
            removed=removed,
        )

        return ChangeProcessingResult(
            success=True,
            total_changes=len(changes),
            added_processed=added,
            modified_processed=modified,
            unchanged_reused=unchanged,
            removed_count=removed,
            clauses=clauses_output,
        )


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------
_change_processor: Optional[ChangeProcessor] = None


def get_change_processor() -> ChangeProcessor:
    global _change_processor
    if _change_processor is None:
        _change_processor = ChangeProcessor()
    return _change_processor
