from django.urls import path
from .views import assign_authority

urlpatterns = [
    path("assign-authority/", assign_authority, name="assign_authority"),
]
