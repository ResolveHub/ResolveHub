
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def make_user(**kwargs):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
        }
        data.update(kwargs)
        return User.objects.create_user(**data)
    return make_user

@pytest.mark.django_db
def test_signup(api_client):
    payload = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpass123'
    }
    response = api_client.post('/auth/signup/', payload)
    assert response.status_code == 201
    assert 'id' in response.data

@pytest.mark.django_db
def test_login_success(api_client, create_user):
    user = create_user()
    response = api_client.post('/auth/login/', {
        'email': user.email,
        'password': 'testpassword123'
    })
    assert response.status_code == 200
    assert 'token' in response.data

@pytest.mark.django_db
def test_login_failure(api_client):
    response = api_client.post('/auth/login/', {
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    })
    assert response.status_code == 401

@pytest.mark.django_db
def test_forgot_password(api_client, create_user, monkeypatch):
    user = create_user(email='reset@example.com')
    
    def fake_send_mail(subject, message, from_email, recipient_list, **kwargs):
        return 1

    monkeypatch.setattr("django.core.mail.send_mail", fake_send_mail)
    
    response = api_client.post('/auth/forgot-password/', {'email': 'reset@example.com'})
    assert response.status_code == 200
    assert response.data['message'] == 'OTP sent to email'

@pytest.mark.django_db
def test_reset_password(api_client, create_user):
    user = create_user(email='reset2@example.com')
    user.otp_secret = '123456'
    user.save()

    response = api_client.post('/auth/reset-password/', {
        'email': 'reset2@example.com',
        'otp': '123456',
        'new_password': 'newsecurepass'
    })
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password('newsecurepass')
