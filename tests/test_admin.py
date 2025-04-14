import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from complaints.admin import ComplaintAdmin
from complaints.models import Complaint

@pytest.fixture
def admin_site():
    return AdminSite()

@pytest.fixture
def admin_user():
    User = get_user_model()
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )

@pytest.mark.django_db
class TestAdminPanel:
    def test_complaint_admin_list_display(self, admin_site, admin_user):
        complaint_admin = ComplaintAdmin(Complaint, admin_site)
        assert 'title' in complaint_admin.list_display
        assert 'status' in complaint_admin.list_display
        assert 'created_at' in complaint_admin.list_display

    def test_admin_login(self, client, admin_user):
        response = client.post('/admin/login/', {
            'username': 'admin',
            'password': 'admin123'
        })
        assert response.status_code == 302  # Redirect after successful login