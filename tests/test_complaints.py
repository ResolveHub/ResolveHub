import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from complaints.models import Complaint
from django.contrib.auth import get_user_model

@pytest.mark.django_db
class TestComplaints:
    def test_create_complaint(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('create-complaint')
        data = {
            'title': 'Test Complaint',
            'description': 'Test Description',
            'complaint_type': 'MAINTENANCE'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_upvote_complaint(self, api_client, test_user):
        complaint = Complaint.objects.create(
            title='Test',
            description='Test',
            created_by=test_user
        )
        api_client.force_authenticate(user=test_user)
        url = reverse('upvote-complaint', kwargs={'pk': complaint.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK

    def test_generate_report(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('generate-report')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'

    def test_search_complaints(self, api_client, test_user):
        # Create test complaints
        Complaint.objects.create(
            title='Network Issue',
            description='Slow internet connection',
            created_by=test_user
        )
        Complaint.objects.create(
            title='Maintenance Request',
            description='AC not working',
            created_by=test_user
        )
        
        # Authenticate user
        api_client.force_authenticate(user=test_user)
        
        # Test cases with different search terms
        test_cases = [
            ('Network', 1),  # Should find one complaint
            ('maintenance', 1),  # Case-insensitive search
            ('not working', 1),  # Search in description
            ('Issue', 1),  # Partial word match
            ('random', 0),  # No matches
            ('', 2),  # Empty search should return all
        ]
        
        for search_term, expected_count in test_cases:
            url = reverse('search-complaints')
            response = api_client.get(url, {'q': search_term})
            
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) == expected_count
            
            if expected_count > 0 and search_term:
                # Verify search term appears in either title or description
                for complaint in response.data:
                    assert (
                        search_term.lower() in complaint['title'].lower() or 
                        search_term.lower() in complaint['description'].lower()
                    )

    def test_search_complaints_authentication(self, api_client):
        # Test search without authentication
        url = reverse('search-complaints')
        response = api_client.get(url, {'q': 'test'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED