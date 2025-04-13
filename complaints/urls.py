from django.urls import path
from . import views
from .views import complaint_type_choices
from .views import complaints_under_you

urlpatterns = [
    # Complaint List / Create / Delete / Update
    path('api/complaints/', views.ComplaintListView.as_view(), name='complaint-list'),
    path('api/complaints/create/', views.create_complaint, name='create_complaint'),
    path('api/complaints/<int:pk>/delete/', views.ComplaintDeleteView.as_view(), name='complaint-delete'),
    path('api/complaints/<int:pk>/update/', views.ComplaintUpdateView.as_view(), name='complaint-update'),

    # User-specific complaints
    path('api/complaints/mine/', views.MyComplaintsView.as_view(), name='my-complaints'),
    path('api/complaints/upvoted/', views.UpvotedComplaintsView.as_view(), name='upvoted-complaints'),

    # Upvotes
    path('api/complaints/upvote/', views.upvote_complaint, name='upvote_complaint'),
    path('api/complaints/remove-upvote/', views.remove_upvote, name='remove_upvote'),

    # Assigned Complaints (Authority-specific)
    path('api/complaints/under-you/', complaints_under_you, name='complaints-under-you'),

    path('complaint-types/', complaint_type_choices, name='complaint-types'),
    path('api/search/', views.search_complaints, name='search-complaints'),
    path('api/generate-report/', views.generate_complaint_report, name='generate-complaint-report'),

    # Add this new path for individual complaint reports
    path('api/report/<int:pk>/', views.generate_complaint_report, name='generate-single-report'),
    path('api/complaints/<int:pk>/details/', views.ComplaintDetailView.as_view(), name='complaint-detail'),
]