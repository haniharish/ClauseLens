"""
Tests – User registration and login.
"""
import pytest


@pytest.mark.django_db
class TestRegistration:

    def test_register_success(self, api_client):
        response = api_client.post('/api/auth/register/', {
            'username': 'newuser',
            'full_name': 'New User',
            'email': 'newuser@example.com',
            'password': 'StrongPass1234!',
            'password_confirm': 'StrongPass1234!',
        }, format='json')
        assert response.status_code == 201
        assert response.data['success'] is True
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']

    def test_register_duplicate_email(self, api_client, user):
        response = api_client.post('/api/auth/register/', {
            'username': 'duplicate',
            'email': 'testuser@example.com',  # already exists
            'password': 'StrongPass1234!',
            'password_confirm': 'StrongPass1234!',
        }, format='json')
        assert response.status_code == 400
        assert response.data['success'] is False

    def test_register_password_mismatch(self, api_client):
        response = api_client.post('/api/auth/register/', {
            'username': 'mismatch',
            'email': 'mismatch@example.com',
            'password': 'StrongPass1234!',
            'password_confirm': 'DifferentPass!',
        }, format='json')
        assert response.status_code == 400
        assert response.data['success'] is False

    def test_register_weak_password(self, api_client):
        response = api_client.post('/api/auth/register/', {
            'username': 'weakpass',
            'email': 'weakpass@example.com',
            'password': '1234',
            'password_confirm': '1234',
        }, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogin:

    def test_login_success(self, api_client, user):
        response = api_client.post('/api/auth/login/', {
            'email': 'testuser@example.com',
            'password': 'TestPass1234!',
        }, format='json')
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'access' in response.data['data']

    def test_login_wrong_password(self, api_client, user):
        response = api_client.post('/api/auth/login/', {
            'email': 'testuser@example.com',
            'password': 'WrongPassword!',
        }, format='json')
        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_client):
        response = api_client.post('/api/auth/login/', {
            'email': 'nobody@example.com',
            'password': 'SomePass!',
        }, format='json')
        assert response.status_code == 401


@pytest.mark.django_db
class TestAuthEndpoints:

    def test_me_authenticated(self, auth_client, user):
        response = auth_client.get('/api/auth/me/')
        assert response.status_code == 200
        assert response.data['data']['email'] == user.email

    def test_me_unauthenticated(self, api_client):
        response = api_client.get('/api/auth/me/')
        assert response.status_code == 401

    def test_change_password_success(self, auth_client):
        response = auth_client.post('/api/auth/change-password/', {
            'old_password': 'TestPass1234!',
            'new_password': 'NewStrongPass5678!',
            'new_password_confirm': 'NewStrongPass5678!',
        }, format='json')
        assert response.status_code == 200
        assert response.data['success'] is True

    def test_change_password_wrong_old(self, auth_client):
        response = auth_client.post('/api/auth/change-password/', {
            'old_password': 'WrongOldPass!',
            'new_password': 'NewStrongPass5678!',
            'new_password_confirm': 'NewStrongPass5678!',
        }, format='json')
        assert response.status_code == 400
