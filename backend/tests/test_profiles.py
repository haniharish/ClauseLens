"""
Tests – User profile CRUD.
"""
import pytest


@pytest.mark.django_db
class TestProfile:

    def test_create_profile(self, auth_client):
        response = auth_client.post('/api/profile/', {
            'age_group': '18_64',
            'intended_use': ['student', 'personal'],
            'jurisdiction': 'india',
        }, format='json')
        assert response.status_code == 201
        assert response.data['success'] is True
        data = response.data['data']
        assert 'student' in data['intended_use']

    def test_get_profile(self, auth_client):
        # Create first
        auth_client.post('/api/profile/', {
            'age_group': '18_64',
            'intended_use': ['student'],
            'jurisdiction': 'eu',
        }, format='json')
        response = auth_client.get('/api/profile/')
        assert response.status_code == 200
        assert response.data['data']['jurisdiction'] == 'eu'

    def test_update_profile(self, auth_client):
        auth_client.post('/api/profile/', {
            'age_group': '18_64',
            'intended_use': ['student'],
            'jurisdiction': 'india',
        }, format='json')
        response = auth_client.patch('/api/profile/', {
            'jurisdiction': 'usa',
        }, format='json')
        assert response.status_code == 200
        assert response.data['data']['jurisdiction'] == 'usa'

    def test_get_profile_not_found(self, auth_client):
        response = auth_client.get('/api/profile/')
        assert response.status_code == 404

    def test_profile_requires_auth(self, api_client):
        response = api_client.get('/api/profile/')
        assert response.status_code == 401

    def test_invalid_intended_use(self, auth_client):
        response = auth_client.post('/api/profile/', {
            'age_group': '18_64',
            'intended_use': ['invalid_choice'],
            'jurisdiction': 'india',
        }, format='json')
        assert response.status_code == 400
