from django.urls import path
from . import views

urlpatterns = [
    # path('<int:pk>/', views.complaint_detail, name='complaint_detail'),
    # path('create/', views.complaint_create, name='complaint_create'),
    # path('<int:pk>/edit/', views.complaint_edit, name='complaint_edit'),
    # path('<int:pk>/delete/', views.complaint_delete, name='complaint_delete'),
    # path('<int:pk>/status/', views.complaint_status, name='complaint_status'),
    # path('history/', views.complaint_history, name='complaint_history'),
    # path('search/', views.complaint_search, name='complaint_search'),
    # path('filter/', views.complaint_filter, name='complaint_filter'),
    # path('<int:pk>/download/', views.complaint_download, name='complaint_download'),
    path('api/complaints/', views.ComplaintListView.as_view(), name='complaint-list'),
    path('api/upvote/', views.upvote_complaint, name='upvote_complaint'),
    path('create/',views. ComplaintCreateView.as_view(), name='create-complaint'),
    path('api/complaints/create/', views.create_complaint, name='create_complaint'),
    path('<int:complaint_id>/upvote/', views.upvote_complaint, name='upvote_complaint'),  # Correct one
]


