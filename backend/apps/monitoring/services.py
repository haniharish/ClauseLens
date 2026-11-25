"""
ClauseLens – Monitoring service layer.
Handles incoming version updates from the version tracking module.
"""
import logging
from django.db import transaction
from django.conf import settings

from apps.documents.models import Document
from apps.analysis.models import Clause
from .models import PolicyVersion, PolicyChange, MonitoredPolicy
from .serializers import VersionUpdateSerializer

logger = logging.getLogger('clauselens')


class VersionUpdateService:
    """
    Receives version update data from the Version Tracking module,
    persists it, and triggers alert generation.
    """

    @staticmethod
    @transaction.atomic
    def handle_version_update(raw_data: dict):
        """
        Validate and store a version update payload.
        Returns a dict with keys: version_id, changes_saved, or error.
        """
        serializer = VersionUpdateSerializer(data=raw_data)
        if not serializer.is_valid():
            return {'error': str(serializer.errors)}

        data = serializer.validated_data

        try:
            doc = Document.objects.get(pk=data['document_id'])
        except Document.DoesNotExist:
            return {'error': f"Document {data['document_id']} not found."}

        # Save version snapshot
        version, created = PolicyVersion.objects.get_or_create(
            document=doc,
            version_number=data['version_number'],
            defaults={
                'version_text': data['version_text'],
                'content_hash': data['content_hash'],
            },
        )

        if not created:
            return {'error': 'Version already recorded.'}

        # Save per-clause changes
        changes_saved = 0
        change_records = []
        for change_data in data.get('changes', []):
            old_clause = None
            new_clause = None

            if change_data.get('clause_id'):
                try:
                    old_clause = Clause.objects.get(pk=change_data['clause_id'])
                except Clause.DoesNotExist:
                    pass

            change_records.append(PolicyChange(
                document=doc,
                old_clause=old_clause,
                new_clause=new_clause,
                change_type=change_data['change_type'],
                change_direction=change_data['change_direction'],
                magnitude=change_data['magnitude'],
            ))
            changes_saved += 1

        PolicyChange.objects.bulk_create(change_records)

        # Update monitoring record
        MonitoredPolicy.objects.filter(document=doc).update(
            last_checked_at=version.fetched_at,
        )

        logger.info(
            'Version update stored: doc=%d, version=%d, changes=%d',
            doc.id, data['version_number'], changes_saved,
        )

        # Trigger alert generation asynchronously
        try:
            from apps.alerts.tasks import generate_alerts_for_document
            generate_alerts_for_document.delay(doc.id)
        except Exception as exc:
            logger.warning('Failed to queue alert generation: %s', exc)

        return {'version_id': version.id, 'changes_saved': changes_saved}
