from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # path('upvote/<int:complaint_id>/', views.upvote_complaint, name='upvote_complaint'),
]
