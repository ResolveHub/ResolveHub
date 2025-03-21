from django.urls import path
from .views import assign_authority,delete_authority

urlpatterns = [
    path("assign-authority/", assign_authority, name="assign_authority"),
    path('delete_authority/', delete_authority, name='delete_authority'),

]
