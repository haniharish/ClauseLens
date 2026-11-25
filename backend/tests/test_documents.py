"""
Tests – Document upload and management.
"""
import io
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.documents.models import Document


def make_pdf_file(name='test.pdf', size=1024):
    """Create a minimal in-memory 'PDF' file for testing."""
    content = b'%PDF-1.4 fake pdf content ' + b'x' * size
    return SimpleUploadedFile(name, content, content_type='application/pdf')


@pytest.mark.django_db
class TestDocumentUpload:

    def test_upload_pdf(self, auth_client, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        pdf = make_pdf_file()
        response = auth_client.post(
            '/api/documents/upload/',
            {'file': pdf, 'document_name': 'Test Policy'},
            format='multipart',
        )
        assert response.status_code == 201
        assert response.data['success'] is True
        assert response.data['data']['document_name'] == 'Test Policy'

    def test_upload_non_pdf(self, auth_client):
        txt_file = SimpleUploadedFile('doc.txt', b'hello', content_type='text/plain')
        response = auth_client.post(
            '/api/documents/upload/',
            {'file': txt_file},
            format='multipart',
        )
        assert response.status_code == 400
        assert response.data['success'] is False

    def test_upload_requires_auth(self, api_client):
        pdf = make_pdf_file()
        response = api_client.post(
            '/api/documents/upload/',
            {'file': pdf},
            format='multipart',
        )
        assert response.status_code == 401

    def test_submit_url(self, auth_client):
        response = auth_client.post('/api/documents/url/', {
            'policy_url': 'https://example.com/privacy-policy',
            'document_name': 'Example Privacy Policy',
        }, format='json')
        assert response.status_code == 201
        assert response.data['data']['document_type'] == 'url'


@pytest.mark.django_db
class TestDocumentList:

    def test_list_own_documents(self, auth_client, user, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        pdf = make_pdf_file()
        auth_client.post('/api/documents/upload/', {'file': pdf}, format='multipart')
        response = auth_client.get('/api/documents/')
        assert response.status_code == 200
        assert response.data['data']['count'] >= 1

    def test_cannot_see_other_users_documents(self, auth_client, another_auth_client, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        pdf = make_pdf_file()
        another_auth_client.post('/api/documents/upload/', {'file': pdf}, format='multipart')
        response = auth_client.get('/api/documents/')
        assert response.status_code == 200
        # Main user should not see another user's documents
        assert response.data['data']['count'] == 0


@pytest.mark.django_db
class TestDocumentDetail:

    def test_retrieve_own_document(self, auth_client, user, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        pdf = make_pdf_file()
        upload_resp = auth_client.post('/api/documents/upload/', {'file': pdf}, format='multipart')
        doc_id = upload_resp.data['data']['id']
        response = auth_client.get(f'/api/documents/{doc_id}/')
        assert response.status_code == 200

    def test_cannot_access_other_users_document(self, auth_client, another_auth_client, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        pdf = make_pdf_file()
        upload_resp = another_auth_client.post('/api/documents/upload/', {'file': pdf}, format='multipart')
        doc_id = upload_resp.data['data']['id']
        response = auth_client.get(f'/api/documents/{doc_id}/')
        assert response.status_code == 403

    def test_delete_own_document(self, auth_client, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        pdf = make_pdf_file()
        upload_resp = auth_client.post('/api/documents/upload/', {'file': pdf}, format='multipart')
        doc_id = upload_resp.data['data']['id']
        response = auth_client.delete(f'/api/documents/{doc_id}/')
        assert response.status_code == 200
        assert not Document.objects.filter(pk=doc_id).exists()
