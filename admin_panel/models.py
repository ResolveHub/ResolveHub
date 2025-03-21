from django.db import models
from django.conf import settings

class Authority(models.Model):
    ROLE_CHOICES = [
        ("Maintenance", "Maintenance"),
        ("Transport", "Transport"),
        ("Mess", "Mess"),
        ("Other", "Other"),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="User")
    priority = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.email} - {self.role} (Priority: {self.priority})"
