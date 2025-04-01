from django.urls import path
from . import views

urlpatterns = [
    path('', views.complaint_list, name='complaint_list'),  # List complaints
    path('<int:pk>/', views.complaint_detail, name='complaint_detail'),  # View specific complaint
    path('create/', views.complaint_create, name='complaint_create'),  # Create a new complaint
    path('<int:pk>/edit/', views.complaint_edit, name='complaint_edit'),  # Edit a complaint
    path('<int:pk>/delete/', views.complaint_delete, name='complaint_delete'),  # Delete a complaint
    path('<int:pk>/status/', views.complaint_status, name='complaint_status'),  # Update status
    path('history/', views.complaint_history, name='complaint_history'),  # View user's complaint history
    path('search/', views.complaint_search, name='complaint_search'),  # Search complaints
    path('filter/', views.complaint_filter, name='complaint_filter'),  # Filter complaints
    path('<int:pk>/download/', views.complaint_download, name='complaint_download'),  # Download proof
]
