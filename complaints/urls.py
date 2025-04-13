# from django.urls import path
# from . import views
# from .views import assigned_complaints_api

# urlpatterns = [
#     path('api/complaints/<int:pk>/delete/',views. ComplaintDeleteView.as_view()),
#     path('api/complaints/mine/', views.MyComplaintsView.as_view()),
#     path('api/complaints/upvoted/',views. UpvotedComplaintsView.as_view()),
#     path('api/complaints/<int:pk>/update/', views.ComplaintUpdateView.as_view()),
#     path('api/complaints/', views.ComplaintListView.as_view(), name='complaint-list'),
#     path('api/upvote/', views.upvote_complaint, name='upvote_complaint'),
#     path('create/',views. ComplaintCreateView.as_view(), name='create-complaint'),
#     path('api/complaints/create/', views.create_complaint, name='create_complaint'),
#     path('<int:complaint_id>/upvote/', views.upvote_complaint, name='upvote_complaint'),
#     path("api/assigned-complaints/", assigned_complaints_api),
#     path("api/assigned-complaints/", assigned_complaints_api, name='assigned_complaints_api'),
#     path('api/complaints/', views.ComplaintListView.as_view()),
#     path('api/complaints/upvote/', views.upvote_complaint),
#     path('api/complaints/assigned/', views.assigned_complaints_api),
#     path('api/complaints/<int:pk>/delete/', views.ComplaintDeleteView.as_view()),
    
# ]

from django.urls import path
from . import views
from .views import assigned_complaints_api
from .views import complaint_type_choices
from .views import my_assigned_complaints

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

    # Assigned Complaints (Authority-specific)
    # path('api/complaints/assigned/', views.assigned_complaints_api, name='assigned_complaints_api'),
      path('complaints/assigned/',my_assigned_complaints, name='assigned-complaints'),

     path('complaint-types/', complaint_type_choices, name='complaint-types'),
     path('api/search/', views.search_complaints, name='search-complaints'),
]




