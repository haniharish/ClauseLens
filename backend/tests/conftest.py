"""
ClauseLens – Test fixtures (conftest.py).
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='testuser@example.com',
        username='testuser',
        full_name='Test User',
        password='TestPass1234!',
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email='other@example.com',
        username='otheruser',
        full_name='Other User',
        password='OtherPass1234!',
    )


@pytest.fixture
def auth_client(api_client, user):
    """An API client authenticated as 'user'."""
    response = api_client.post(
        '/api/auth/login/',
        {'email': 'testuser@example.com', 'password': 'TestPass1234!'},
        format='json',
    )
    token = response.data['data']['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def another_auth_client(api_client, another_user):
    """An API client authenticated as 'another_user'."""
    response = api_client.post(
        '/api/auth/login/',
        {'email': 'other@example.com', 'password': 'OtherPass1234!'},
        format='json',
    )
    token = response.data['data']['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client
