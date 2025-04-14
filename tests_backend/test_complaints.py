import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from complaints.models import Complaint, Upvote  # Adjust the import paths based on your project structure
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

@pytest.fixture
@pytest.mark.django_db
def user():
    User = get_user_model()  # Fetch the correct user model
    # Create a user and ensure a unique email is used for testing
    user, created = User.objects.get_or_create(
        username='testuser',
        email='testuser@example.com',
        defaults={'password': 'password123'}
    )
    if not created:  # If the user already exists, update their password
        user.set_password('password123')
        user.save()
    return user

from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
@pytest.mark.django_db
def authenticated_client_with_token(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return client


@pytest.fixture
@pytest.mark.django_db
def complaint(user):
    # Create a test complaint
    return Complaint.objects.create(
        user=user,
        title="Test Complaint",
        description="This is a test complaint.",
        status="Pending"
    )

# Test Cases



@pytest.mark.django_db
def test_create_complaints(authenticated_client_with_token, complaint, user):
    url = reverse('complaint-list')  # Adjust the endpoint accordingly
    response = authenticated_client_with_token.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_upvote_complaint(authenticated_client_with_token, complaint, user):
    url = reverse('upvote_complaint')  # Adjust the endpoint accordingly
    data = {'complaint_id': complaint.id}
    
    response = authenticated_client_with_token.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_remove_upvote(authenticated_client_with_token, complaint, user):
    # Create initial upvote
    Upvote.objects.create(user=user, complaint=complaint)
    
    url = reverse('remove_upvote')  # Adjust the endpoint accordingly
    data = {'complaint_id': complaint.id}
    
    response = authenticated_client_with_token.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK



