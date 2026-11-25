"""
ClauseLens – Analysis service layer.
Processes NLP responses and stores clause + analysis data.
"""
import logging
from django.db import transaction

from apps.documents.models import Document
from .models import Clause, AnalysisResult

logger = logging.getLogger('clauselens')

# Severity thresholds
HIGH_THRESHOLD = 0.67
LOW_THRESHOLD = 0.34


class AnalysisService:
    """Handles storing NLP analysis results for a document."""

    @staticmethod
    @transaction.atomic
    def store_nlp_results(document_id: int, nlp_data: dict):
        """
        Called after the NLP module returns its response.
        Saves all clauses and creates/updates the AnalysisResult.

        :param document_id: PK of the document being analysed.
        :param nlp_data: Validated NLP response dict.
        :raises Document.DoesNotExist: if the document is not found.
        """
        doc = Document.objects.get(pk=document_id)

        clauses_data = nlp_data.get('clauses', [])
        high = medium = low = 0
        total_severity = 0.0

        # Delete existing clauses (re-analysis scenario)
        Clause.objects.filter(document=doc).delete()

        clause_objects = []
        for item in clauses_data:
            sev = float(item.get('severity', 0.0))
            total_severity += sev
            if sev >= HIGH_THRESHOLD:
                high += 1
            elif sev >= LOW_THRESHOLD:
                medium += 1
            else:
                low += 1

            clause_objects.append(Clause(
                document=doc,
                clause_title=item.get('clause_title', 'Untitled Clause'),
                original_text=item.get('original_text', ''),
                category=item.get('category', Clause.Category.OTHER),
                severity=sev,
                simple_explanation=item.get('simple_explanation', ''),
            ))

        Clause.objects.bulk_create(clause_objects)

        total = len(clause_objects)
        overall_score = round(total_severity / total, 4) if total > 0 else 0.0

        result, _ = AnalysisResult.objects.update_or_create(
            document=doc,
            defaults={
                'total_clauses': total,
                'high_risk_count': high,
                'medium_risk_count': medium,
                'low_risk_count': low,
                'overall_risk_score': overall_score,
                'analysis_status': AnalysisResult.AnalysisStatus.COMPLETED,
            },
        )

        doc.status = Document.Status.COMPLETED
        doc.save(update_fields=['status', 'updated_at'])

        logger.info(
            'Stored %d clauses for document %d (high=%d, mid=%d, low=%d)',
            total, document_id, high, medium, low,
        )
        return result

    @staticmethod
    def mark_failed(document_id: int, reason: str = ''):
        """Mark a document and its analysis as failed."""
        try:
            doc = Document.objects.get(pk=document_id)
            doc.status = Document.Status.FAILED
            doc.save(update_fields=['status', 'updated_at'])
            AnalysisResult.objects.update_or_create(
                document=doc,
                defaults={'analysis_status': AnalysisResult.AnalysisStatus.FAILED},
            )
            logger.error('Analysis failed for document %d: %s', document_id, reason)
        except Document.DoesNotExist:
            logger.error('Cannot mark failure – document %d not found', document_id)
