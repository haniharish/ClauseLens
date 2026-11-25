"""
Tests – Analysis results, clauses, personalized risks, monitoring, dashboard.
"""
import pytest
from apps.documents.models import Document
from apps.analysis.models import Clause, AnalysisResult
from apps.personalization.models import PersonalizedRisk
from apps.monitoring.models import MonitoredPolicy, PolicyChange


def _create_document(user):
    return Document.objects.create(
        user=user,
        document_name='Test Policy',
        document_type=Document.DocumentType.URL,
        policy_url='https://example.com/policy',
        status=Document.Status.COMPLETED,
    )


def _create_clause(doc, severity=0.8):
    return Clause.objects.create(
        document=doc,
        clause_title='Data Sharing',
        original_text='We share your data.',
        category=Clause.Category.DATA_SHARING,
        severity=severity,
        simple_explanation='Your data is shared.',
    )


def _create_analysis(doc):
    return AnalysisResult.objects.create(
        document=doc,
        total_clauses=1,
        high_risk_count=1,
        medium_risk_count=0,
        low_risk_count=0,
        overall_risk_score=0.8,
        analysis_status=AnalysisResult.AnalysisStatus.COMPLETED,
    )


@pytest.mark.django_db
class TestClauseRetrieval:

    def test_get_clauses_for_document(self, auth_client, user):
        doc = _create_document(user)
        _create_clause(doc)
        response = auth_client.get(f'/api/analysis/documents/{doc.id}/clauses/')
        assert response.status_code == 200
        assert response.data['data']['count'] >= 1

    def test_cannot_get_clauses_of_other_user(self, auth_client, another_user):
        doc = _create_document(another_user)
        _create_clause(doc)
        response = auth_client.get(f'/api/analysis/documents/{doc.id}/clauses/')
        assert response.status_code == 403


@pytest.mark.django_db
class TestAnalysisResult:

    def test_get_analysis_result(self, auth_client, user):
        doc = _create_document(user)
        _create_analysis(doc)
        response = auth_client.get(f'/api/analysis/documents/{doc.id}/result/')
        assert response.status_code == 200
        assert response.data['data']['overall_risk_score'] == 0.8

    def test_analysis_not_found(self, auth_client, user):
        doc = _create_document(user)
        response = auth_client.get(f'/api/analysis/documents/{doc.id}/result/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestPersonalizedRisk:

    def test_get_personalized_risks(self, auth_client, user):
        doc = _create_document(user)
        clause = _create_clause(doc)
        PersonalizedRisk.objects.create(
            user=user,
            clause=clause,
            relevance_score=0.75,
            risk_level='High',
            why_it_matters='This matters because...',
        )
        response = auth_client.get(f'/api/personalization/documents/{doc.id}/risks/')
        assert response.status_code == 200
        assert response.data['data']['count'] >= 1


@pytest.mark.django_db
class TestPolicyMonitoring:

    def test_add_monitoring(self, auth_client):
        response = auth_client.post('/api/monitoring/', {
            'policy_url': 'https://example.com/privacy',
            'policy_name': 'Example Privacy Policy',
            'check_interval_hours': 24,
        }, format='json')
        assert response.status_code == 201
        assert response.data['data']['policy_name'] == 'Example Privacy Policy'

    def test_list_monitoring(self, auth_client):
        auth_client.post('/api/monitoring/', {
            'policy_url': 'https://example.com/terms',
            'policy_name': 'Example Terms',
            'check_interval_hours': 24,
        }, format='json')
        response = auth_client.get('/api/monitoring/')
        assert response.status_code == 200
        assert response.data['data']['count'] >= 1

    def test_pause_monitoring(self, auth_client):
        create_resp = auth_client.post('/api/monitoring/', {
            'policy_url': 'https://example.com/policy',
            'policy_name': 'Policy',
            'check_interval_hours': 24,
        }, format='json')
        m_id = create_resp.data['data']['id']
        response = auth_client.patch(f'/api/monitoring/{m_id}/', {
            'monitoring_status': 'paused',
        }, format='json')
        assert response.status_code == 200
        assert response.data['data']['monitoring_status'] == 'paused'


@pytest.mark.django_db
class TestDashboard:

    def test_dashboard_returns_data(self, auth_client, user):
        doc = _create_document(user)
        _create_analysis(doc)
        response = auth_client.get('/api/dashboard/')
        assert response.status_code == 200
        data = response.data['data']
        assert 'documents_analyzed' in data
        assert 'risk_distribution' in data
        assert 'recent_documents' in data

    def test_dashboard_requires_auth(self, api_client):
        response = api_client.get('/api/dashboard/')
        assert response.status_code == 401


@pytest.mark.django_db
class TestNotifications:

    def test_list_notifications(self, auth_client, user):
        from apps.alerts.models import Notification
        doc = _create_document(user)
        Notification.objects.create(
            user=user,
            document=doc,
            title='Test Alert',
            message='A change was detected.',
            severity='high',
        )
        response = auth_client.get('/api/notifications/')
        assert response.status_code == 200
        assert response.data['data']['count'] >= 1

    def test_mark_notification_read(self, auth_client, user):
        from apps.alerts.models import Notification
        doc = _create_document(user)
        n = Notification.objects.create(
            user=user,
            document=doc,
            title='Alert',
            message='Change detected.',
            severity='medium',
        )
        response = auth_client.patch(f'/api/notifications/{n.id}/read/')
        assert response.status_code == 200
        n.refresh_from_db()
        assert n.is_read is True

    def test_mark_all_read(self, auth_client, user):
        from apps.alerts.models import Notification
        doc = _create_document(user)
        for i in range(3):
            Notification.objects.create(
                user=user,
                document=doc,
                title=f'Alert {i}',
                message='Change detected.',
                severity='low',
            )
        response = auth_client.patch('/api/notifications/read-all/')
        assert response.status_code == 200
        assert response.data['data']['marked_read'] == 3
