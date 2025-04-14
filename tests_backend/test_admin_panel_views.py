import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from admin_panel.models import Authority

User = get_user_model()

@pytest.mark.django_db
def test_assign_authority(client):
    # Create a user
    user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')

    # Assign authority
    response = client.post(
        reverse('assign_authority'),
        data={
            "user_id": user.id,
            "role": "Mess",
            "priority": 2
        },
        content_type="application/json"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Authority assigned successfully"
    assert data["role"] == "Mess"
    assert data["priority"] == 2

    # Check database
    authority = Authority.objects.get(user=user)
    assert authority.role == "Mess"
    assert authority.priority == 2

@pytest.mark.django_db
def test_delete_authority(client):
    # Create user and authority
    user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')    
    Authority.objects.create(user=user, role="Transport", priority=3)

    # Delete authority
    response = client.post(
        reverse('delete_authority'),
        data={"user_id": user.id},
        content_type="application/json"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Authority deleted successfully"
    assert not Authority.objects.filter(user=user).exists()

@pytest.mark.django_db
def test_assign_authority_invalid_user(client):
    response = client.post(
        reverse('assign_authority'),
        data={"user_id": 9999, "role": "Mess", "priority": 1},
        content_type="application/json"
    )
    assert response.status_code == 404
    assert response.json()["error"] == "User not found"

@pytest.mark.django_db
def test_delete_authority_invalid_user(client):
    response = client.post(
        reverse('delete_authority'),
        data={"user_id": 9999},
        content_type="application/json"
    )
    assert response.status_code == 404
    assert response.json()["error"] == "User not found"
