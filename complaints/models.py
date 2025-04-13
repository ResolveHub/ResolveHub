from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from admin_panel.models import Authority
from datetime import timedelta

User = get_user_model()


User = get_user_model()

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('resolved', 'Resolved'),
    ('rejected', 'Rejected'),
]

# COMPLAINT TYPE choices
COMPLAINT_TYPE_CHOICES = [
    ('Transport', 'Transport'),
    ('Mess', 'Mess'),
    ('Maintenance', 'Maintenance'),
    ('Other', 'Other'),
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
        default='Other'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-assign lowest level authority if not assigned
        if self.assigned_authority is None:
            try:
                from admin_panel.models import Authority  # 🔄 Adjust app name if needed
                authority = Authority.objects.filter(role=self.complaint_type,
                priority=1).first()
                if authority:
                    self.assigned_authority = authority.user
            except Exception:
                pass  # Optionally log this
        super().save(*args, **kwargs)

    def escalate_if_needed(self):
        if self.status.lower() != "resolved":
            now = timezone.now()
            last_check = self.last_escalated or self.created_at
            time_diff = now - last_check

            if time_diff >= timedelta(hours=8):
                try:
                    from admin_panel.models import Authority

                    current_authority = self.assigned_authority.authority  # Assuming reverse OneToOne or FK
                    new_priority = current_authority.priority + 1

                    higher_authority = Authority.objects.filter(
                        role=self.complaint_type,
                        priority=new_priority
                    ).first()

                    if higher_authority:
                        self.assigned_authority = higher_authority.user
                        self.last_escalated = now
                        print(f"Complaint {self.id} escalated to priority {new_priority}")
                except Exception as e:
                    print(f"[Escalation Error]: {e}")


    def total_upvotes(self):
        """Returns the total number of upvotes."""
        return self.upvotes.count()

    def __str__(self):
        return f"Complaint #{self.id} - {self.title}"

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

















