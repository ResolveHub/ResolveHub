from django.db import models
from auth_app.models import User
from django.utils import timezone

class Complaint(models.Model):
    user = models.ForeignKey('auth_app.User', on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=255)
    description = models.TextField()
    proof = models.FileField(upload_to='proofs/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    complaint_type = models.CharField(
    max_length=50,
    choices=[
        ('accommodation', 'Accommodation'),
        ('mess', 'Mess & Food'),
        ('maintenance', 'Maintenance'),
        ('safety', 'Safety & Security'),
        ('technical', 'Technical (Wi-Fi, Electricity, etc.)'),
        ('billing', 'Billing & Payments'),
        ('noise', 'Noise & Disturbance'),
        ('staff', 'Staff Behavior'),
        ('general', 'General'),
    ],
    default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
# Create your models here.
