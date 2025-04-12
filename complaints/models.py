from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=255)
    description = models.TextField()
    proof = models.FileField(upload_to='proofs/', blank=True, null=True)
    upvotes = models.ManyToManyField(User, related_name='upvoted_complaints', blank=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ], default='pending')

    CONFIRMATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]
    user_confirmation_status = models.CharField(
        max_length=20,
        choices=CONFIRMATION_STATUS_CHOICES,
        default='pending'
    )
    COMPLAINT_TYPE_CHOICES = [
            ('accommodation', 'Accommodation'),
            ('mess', 'Mess & Food'),
            ('maintenance', 'Maintenance'),
            ('safety', 'Safety & Security'),
            ('technical', 'Technical (Wi-Fi, Electricity, etc.)'),
            ('billing', 'Billing & Payments'),
            ('noise', 'Noise & Disturbance'),
            ('staff', 'Staff Behavior'),
            ('general', 'General'),
        ]

    complaint_type = models.CharField(
            max_length=30,
            choices=COMPLAINT_TYPE_CHOICES,
            default='general'
)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def total_upvotes(self):
        return self.upvotes.count()

class Upvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'complaint')

    def __str__(self):
        return f"{self.user.email} upvoted '{self.complaint.title}'"
