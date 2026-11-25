"""
ClauseLens – Notification model.
"""
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Personalised alert sent to a user when a monitored policy changes.
    Alert score: A(c',u) = R(c',u) × D(c') × M(c')
    """

    class Severity(models.TextChoices):
        HIGH = 'high', 'High'
        MEDIUM = 'medium', 'Medium'
        LOW = 'low', 'Low'

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
    )
    policy_change = models.ForeignKey(
        'monitoring.PolicyChange',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
    )
    title = models.CharField(max_length=500)
    message = models.TextField()
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.MEDIUM,
        db_index=True,
    )
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
        # Prevent duplicate notifications for the same user + change combination
        unique_together = [('user', 'policy_change')]

    def __str__(self):
        return f'Notification({self.user_id}, read={self.is_read}) – {self.title}'
