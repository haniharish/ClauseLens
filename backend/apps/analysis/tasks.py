"""
ClauseLens – Celery tasks for asynchronous NLP processing.
"""
import logging
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func):
            func.delay = func
            return func
        if args and callable(args[0]):
            return decorator(args[0])
        return decorator

from integrations.nlp_client import get_nlp_client
from .services import AnalysisService

logger = logging.getLogger('clauselens')


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    name='analysis.process_document_nlp',
)
def process_document_nlp(self, document_id: int):
    """
    Celery task: send document to NLP service and store the results.
    Retries up to 3 times with a 30-second delay if the NLP service is down.
    """
    logger.info('Starting NLP processing for document %d', document_id)

    # Import here to avoid circular imports
    from apps.documents.models import Document

    try:
        doc = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        logger.error('Document %d not found – aborting NLP task', document_id)
        return

    try:
        client = get_nlp_client()
        nlp_response = client.analyze_document(document_id=doc.id, document=doc)

        if not nlp_response.get('clauses'):
            logger.warning('NLP service returned no clauses for document %d', document_id)

        AnalysisService.store_nlp_results(document_id, nlp_response)

    except Exception as exc:
        logger.error('NLP processing failed for document %d: %s', document_id, exc)
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            AnalysisService.mark_failed(document_id, reason=str(exc))
