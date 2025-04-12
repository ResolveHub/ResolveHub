from django.urls import path
from . import views
from .views import search_complaints , confirm_resolution

urlpatterns = [
    path('api/complaints/<int:pk>/delete/',views. ComplaintDeleteView.as_view()),
    path('api/complaints/mine/', views.MyComplaintsView.as_view()),
    path('api/complaints/upvoted/',views. UpvotedComplaintsView.as_view()),
    path('api/complaints/<int:pk>/update/', views.ComplaintUpdateView.as_view()),
    path('api/complaints/', views.ComplaintListView.as_view(), name='complaint-list'),
    path('api/upvote/', views.upvote_complaint, name='upvote_complaint'),
    path('create/',views. ComplaintCreateView.as_view(), name='create-complaint'),
    path('api/complaints/create/', views.create_complaint, name='create_complaint'),
    path('<int:complaint_id>/upvote/', views.upvote_complaint, name='upvote_complaint'),
    path('api/search/', search_complaints, name='search-complaints'),
     path('api/confirm_resolution/', confirm_resolution, name='confirm_resolution'),
]


