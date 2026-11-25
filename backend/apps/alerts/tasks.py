"""
ClauseLens – Alert Celery tasks.
"""
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

import logging

logger = logging.getLogger('clauselens')


@shared_task(name='alerts.generate_alerts_for_document')
def generate_alerts_for_document(document_id: int):
    """Generate personalised alerts for all users monitoring a document."""
    from .services import AlertService
    logger.info('Generating alerts for document %d', document_id)
    AlertService.generate_for_document(document_id)
