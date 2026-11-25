"""
ClauseLens – Document service layer.
Handles business logic for document creation and triggering NLP processing.
"""
import logging
from django.utils import timezone
from .models import Document
from integrations.nlp_client import get_nlp_client

logger = logging.getLogger('clauselens')


class DocumentService:
    """Central service for all document-related operations."""

    @staticmethod
    def create_from_file(user, file, document_name=None):
        """Create a Document record for a PDF upload and queue NLP processing."""
        name = document_name or file.name
        doc = Document.objects.create(
            user=user,
            document_name=name,
            document_type=Document.DocumentType.PDF,
            file=file,
            status=Document.Status.UPLOADED,
        )
        DocumentService._queue_nlp_processing(doc)
        return doc

    @staticmethod
    def create_from_url(user, url, document_name=None):
        """Create a Document record for a URL submission and queue NLP processing."""
        name = document_name or url[:100]
        doc = Document.objects.create(
            user=user,
            document_name=name,
            document_type=Document.DocumentType.URL,
            policy_url=url,
            status=Document.Status.UPLOADED,
        )
        DocumentService._queue_nlp_processing(doc)
        return doc

    @staticmethod
    def _queue_nlp_processing(doc):
        """
        Trigger asynchronous NLP analysis via Celery.
        Import here to avoid circular imports.
        """
        try:
            from apps.analysis.tasks import process_document_nlp
            process_document_nlp.delay(doc.id)
            doc.status = Document.Status.PROCESSING
            doc.save(update_fields=['status', 'updated_at'])
            logger.info('Queued NLP processing for document %s', doc.id)
        except Exception as exc:
            logger.warning(
                'Failed to queue NLP processing for document %s: %s. '
                'Document remains in UPLOADED state.',
                doc.id, exc
            )
