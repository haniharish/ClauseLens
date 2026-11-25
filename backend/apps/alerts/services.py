"""
ClauseLens – Alert service.
Implements: A(c',u) = R(c',u) × D(c') × M(c')
"""
import logging
from django.conf import settings
from django.db import transaction

from apps.monitoring.models import PolicyChange
from apps.personalization.models import PersonalizedRisk
from .models import Notification

logger = logging.getLogger('clauselens')

DIRECTION_WEIGHTS = {
    'less_favorable': 1.0,
    'unclear': 0.8,
    'neutral': 0.3,
    'more_favorable': 0.1,
}


def _severity_from_score(score: float) -> str:
    if score >= 0.67:
        return Notification.Severity.HIGH
    if score >= 0.34:
        return Notification.Severity.MEDIUM
    return Notification.Severity.LOW


class AlertService:
    """
    For every PolicyChange on a document, find all users monitoring that
    document, fetch their personalized relevance score for the affected clause,
    compute A = R × D × M, and create a Notification if A ≥ threshold.
    """

    @staticmethod
    @transaction.atomic
    def generate_for_document(document_id: int):
        """
        Main entry point called by the Celery task after a version update.
        """
        threshold = getattr(settings, 'ALERT_THRESHOLD', 0.5)

        changes = PolicyChange.objects.filter(
            document_id=document_id,
        ).exclude(change_type='unchanged').select_related('new_clause', 'old_clause')

        if not changes.exists():
            logger.info('No changes to alert on for document %d', document_id)
            return

        # Find all users monitoring this document
        from apps.monitoring.models import MonitoredPolicy
        monitoring_records = MonitoredPolicy.objects.filter(
            document_id=document_id,
            monitoring_status='active',
        ).select_related('user')

        notifications_created = 0

        for change in changes:
            clause = change.new_clause or change.old_clause
            d_weight = DIRECTION_WEIGHTS.get(change.change_direction, 0.8)
            m = change.magnitude

            for monitoring in monitoring_records:
                user = monitoring.user

                # R – personalised relevance
                try:
                    pr = PersonalizedRisk.objects.get(user=user, clause=clause)
                    r = pr.relevance_score
                except PersonalizedRisk.DoesNotExist:
                    r = clause.severity if clause else 0.5  # fallback

                alert_score = round(r * d_weight * m, 4)

                # Update stored alert_score on the change record
                PolicyChange.objects.filter(pk=change.pk).update(alert_score=alert_score)

                if alert_score < threshold:
                    continue  # Below threshold – skip

                severity = _severity_from_score(alert_score)
                clause_title = clause.clause_title if clause else 'Policy clause'

                direction_label = {
                    'less_favorable': 'now less favourable',
                    'more_favorable': 'now more favourable',
                    'neutral': 'has changed (neutral impact)',
                    'unclear': 'has changed (impact unclear)',
                }.get(change.change_direction, 'has changed')

                try:
                    Notification.objects.create(
                        user=user,
                        document_id=document_id,
                        policy_change=change,
                        title=f'Policy Update: {clause_title}',
                        message=(
                            f'A clause "{clause_title}" in a policy you monitor '
                            f'is {direction_label}. '
                            f'Alert score: {alert_score:.2f}.'
                        ),
                        severity=severity,
                    )
                    notifications_created += 1
                except Exception as exc:
                    # unique_together may raise if notification already exists
                    logger.debug('Notification already exists or error: %s', exc)

        logger.info(
            'Alert generation complete for document %d: %d notifications created',
            document_id, notifications_created,
        )
