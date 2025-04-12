from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from admin_panel.models import Authority

User = get_user_model()



# class Complaint(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints')
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     proof = models.FileField(upload_to='proofs/', blank=True, null=True)
#     upvotes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='upvoted_complaints', blank=True)
    
#     status = models.CharField(max_length=50, choices=[
#         ('pending', 'Pending'),
#         ('resolved', 'Resolved'),
#         ('rejected', 'Rejected'),
#     ], default='pending')

#     assigned_authority = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='assigned_complaints'
#     )
    
#     created_at = models.DateTimeField(default=timezone.now)

#     def save(self, *args, **kwargs):
#         # Assign to authority level 1 if not already assigned
#         if self.assigned_authority is None:
#             first_level_authority = settings.AUTH_USER_MODEL.objects.filter(
#                 is_authority=True,
#                 authority_level=1
#             ).first()

#             if first_level_authority:
#                 self.assigned_authority = first_level_authority

#         super().save(*args, **kwargs)



   
#     COMPLAINT_TYPE_CHOICES = [
#             ('accommodation', 'Accommodation'),
#             ('mess', 'Mess & Food'),
#             ('maintenance', 'Maintenance'),
#             ('safety', 'Safety & Security'),
#             ('technical', 'Technical (Wi-Fi, Electricity, etc.)'),
#             ('billing', 'Billing & Payments'),
#             ('noise', 'Noise & Disturbance'),
#             ('staff', 'Staff Behavior'),
#             ('general', 'General'),
#         ]

#     complaint_type = models.CharField(
#             max_length=30,
#             choices=COMPLAINT_TYPE_CHOICES,
#             default='general'
# )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.title

#     def total_upvotes(self):
#         return self.upvotes.count()

User = get_user_model()

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('resolved', 'Resolved'),
    ('rejected', 'Rejected'),
]

# COMPLAINT TYPE choices
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


class Complaint(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='complaints'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    proof = models.FileField(upload_to='proofs/', blank=True, null=True)

    upvotes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='upvoted_complaints',
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending'
    )

    assigned_authority = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_complaints'
    )

    complaint_type = models.CharField(
        max_length=30,
        choices=COMPLAINT_TYPE_CHOICES,
        default='general'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-assign lowest level authority if not assigned
        if self.assigned_authority is None:
            from admin_panel.models import Authority  # 🔄 Adjust import based on your structure
            authority = Authority.objects.filter(priority=1).first()
            self.assigned_authority = authority.user if authority else None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Complaint #{self.id} - {self.title}"

    def total_upvotes(self):
        return self.upvotes.count()

    class Meta:
        ordering = ['-created_at']


class Upvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'complaint')

    def __str__(self):
        return f"{self.user.email} upvoted '{self.complaint.title}'"
