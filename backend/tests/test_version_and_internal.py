"""
Tests – Version Tracking, Internal callbacks, and Alert calculation.
"""
import pytest
from django.conf import settings
from apps.documents.models import Document
from apps.analysis.models import Clause
from apps.monitoring.models import PolicyVersion, PolicyChange, MonitoredPolicy
from apps.alerts.models import Notification
from apps.alerts.services import AlertService


def _setup_monitored_doc(user):
    doc = Document.objects.create(
        user=user,
        document_name='Monitored Privacy Policy',
        document_type=Document.DocumentType.URL,
        policy_url='https://example.com/privacy',
        status=Document.Status.COMPLETED,
    )
    monitored = MonitoredPolicy.objects.create(
        user=user,
        document=doc,
        policy_url=doc.policy_url,
        policy_name=doc.document_name,
        monitoring_status=MonitoredPolicy.MonitoringStatus.ACTIVE,
    )
    clause = Clause.objects.create(
        document=doc,
        clause_title='Data Sharing with Third Parties',
        original_text='We share your data with advertisers.',
        category=Clause.Category.DATA_SHARING,
        severity=0.85,
        simple_explanation='Advertisers receive your data.',
    )
    return doc, monitored, clause


@pytest.mark.django_db
class TestInternalEndpoints:

    def test_internal_version_update_authenticated(self, api_client, user):
        doc, _, clause = _setup_monitored_doc(user)
        payload = {
            'document_id': doc.id,
            'version_number': 2,
            'version_text': 'Updated privacy policy text...',
            'content_hash': 'abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
            'changes': [
                {
                    'clause_id': clause.id,
                    'change_type': 'modified',
                    'change_direction': 'less_favorable',
                    'magnitude': 0.8,
                }
            ],
        }
        response = api_client.post(
            '/api/internal/version-update/',
            payload,
            format='json',
            HTTP_X_INTERNAL_TOKEN=settings.INTERNAL_SERVICE_TOKEN,
        )
        assert response.status_code == 201
        assert response.data['success'] is True
        assert PolicyVersion.objects.filter(document=doc, version_number=2).exists()
        assert PolicyChange.objects.filter(document=doc, change_type='modified').exists()

    def test_internal_version_update_unauthorized(self, api_client, user):
        doc, _, _ = _setup_monitored_doc(user)
        payload = {
            'document_id': doc.id,
            'version_number': 2,
            'version_text': 'Text',
            'content_hash': 'hash',
            'changes': [],
        }
        # Without header or wrong header
        response = api_client.post('/api/internal/version-update/', payload, format='json')
        assert response.status_code == 403

    def test_internal_nlp_callback(self, api_client, user):
        doc = Document.objects.create(
            user=user,
            document_name='NLP Test Doc',
            document_type=Document.DocumentType.PDF,
            status=Document.Status.PROCESSING,
        )
        payload = {
            'document_id': doc.id,
            'total_clauses': 1,
            'clauses': [
                {
                    'clause_title': 'Arbitration Requirement',
                    'original_text': 'All disputes must be resolved through binding arbitration.',
                    'category': 'arbitration',
                    'severity': 0.9,
                    'simple_explanation': 'You cannot go to court.',
                }
            ],
        }
        response = api_client.post(
            '/api/internal/nlp-callback/',
            payload,
            format='json',
            HTTP_X_INTERNAL_TOKEN=settings.INTERNAL_SERVICE_TOKEN,
        )
        assert response.status_code == 201
        assert response.data['success'] is True
        doc.refresh_from_db()
        assert doc.status == Document.Status.COMPLETED
        assert Clause.objects.filter(document=doc, category='arbitration').exists()


@pytest.mark.django_db
class TestVersionHistoryAndCompare:

    def test_get_version_list_and_compare(self, auth_client, user):
        doc, _, clause = _setup_monitored_doc(user)
        # Create versions 1 and 2
        v1 = PolicyVersion.objects.create(
            document=doc,
            version_number=1,
            version_text='Version 1 text',
            content_hash='hash1',
        )
        v2 = PolicyVersion.objects.create(
            document=doc,
            version_number=2,
            version_text='Version 2 text',
            content_hash='hash2',
        )
        change = PolicyChange.objects.create(
            document=doc,
            old_clause=clause,
            change_type='modified',
            change_direction='less_favorable',
            magnitude=0.75,
            alert_score=0.64,
        )

        # GET /api/versions/
        resp = auth_client.get('/api/versions/')
        assert resp.status_code == 200
        assert resp.data['data']['count'] >= 2

        # GET /api/versions/{doc_id}/
        resp_doc = auth_client.get(f'/api/versions/{doc.id}/')
        assert resp_doc.status_code == 200
        assert len(resp_doc.data['data']) == 2

        # GET /api/versions/{doc_id}/compare/
        resp_compare = auth_client.get(f'/api/versions/{doc.id}/compare/')
        assert resp_compare.status_code == 200
        assert resp_compare.data['data']['new_version']['version_number'] == 2
        assert resp_compare.data['data']['old_version']['version_number'] == 1

        # GET /api/changes/{doc_id}/
        resp_changes = auth_client.get(f'/api/changes/{doc.id}/')
        assert resp_changes.status_code == 200
        assert resp_changes.data['data']['count'] >= 1


@pytest.mark.django_db
class TestAlertGenerationFormula:

    def test_alert_score_formula_and_threshold(self, user):
        """
        Verify:
          A(c',u) = R(c',u) * D(c') * M(c')
          Less Favorable D = 1.0
          Unclear D = 0.8
          Neutral D = 0.3
          More Favorable D = 0.1
        """
        doc, monitored, clause = _setup_monitored_doc(user)
        # Clause severity = 0.85 -> default R fallback = 0.85
        # Direction = less_favorable (D=1.0)
        # Magnitude = 0.8 (M=0.8)
        # Expected A = 0.85 * 1.0 * 0.8 = 0.68 >= ALERT_THRESHOLD (0.5)
        change = PolicyChange.objects.create(
            document=doc,
            new_clause=clause,
            change_type='modified',
            change_direction='less_favorable',
            magnitude=0.8,
        )

        AlertService.generate_for_document(doc.id)

        notifications = Notification.objects.filter(user=user, document=doc)
        assert notifications.exists()
        n = notifications.first()
        assert n.severity == 'high'
        change.refresh_from_db()
        assert change.alert_score == pytest.approx(0.68, 0.01)

    def test_below_threshold_skips_alert(self, user):
        doc, monitored, clause = _setup_monitored_doc(user)
        # Direction = more_favorable (D=0.1)
        # Magnitude = 0.2 (M=0.2)
        # Expected A = 0.85 * 0.1 * 0.2 = 0.017 < ALERT_THRESHOLD (0.5)
        PolicyChange.objects.create(
            document=doc,
            new_clause=clause,
            change_type='modified',
            change_direction='more_favorable',
            magnitude=0.2,
        )

        AlertService.generate_for_document(doc.id)

        notifications = Notification.objects.filter(user=user, document=doc)
        assert not notifications.exists()
