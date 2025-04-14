import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from faker import Faker

fake = Faker()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.mark.django_db
class TestAuthentication:
    def test_user_registration(self, api_client):
        url = reverse('register')
        data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data

    def test_user_login(self, api_client, test_user):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data

    def test_password_reset(self, api_client, test_user):
        # Request password reset
        url = reverse('password-reset-request')
        response = api_client.post(url, {'email': test_user.email})
        assert response.status_code == status.HTTP_200_OK