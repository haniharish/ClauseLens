"""
ClauseLens – Policy monitoring models.
"""
from django.db import models
from django.conf import settings


class MonitoredPolicy(models.Model):
    """
    A policy URL that a user has asked ClauseLens to monitor for changes.
    The actual crawling/fetching is done by Member 6's version tracking module.
    """

    class MonitoringStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAUSED = 'paused', 'Paused'

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='monitored_policies',
    )
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='monitoring',
        null=True,
        blank=True,
        help_text='Associated document record (created when URL is submitted).',
    )
    policy_url = models.URLField(max_length=2048)
    policy_name = models.CharField(max_length=500)
    monitoring_status = models.CharField(
        max_length=10,
        choices=MonitoringStatus.choices,
        default=MonitoringStatus.ACTIVE,
        db_index=True,
    )
    check_interval_hours = models.PositiveIntegerField(
        default=24,
        help_text='How often (in hours) the version tracker should check for changes.',
    )
    added_at = models.DateTimeField(auto_now_add=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'monitored_policies'
        unique_together = [('user', 'policy_url')]
        ordering = ['-added_at']

    def __str__(self):
        return f'MonitoredPolicy({self.policy_name}) – {self.monitoring_status}'


class PolicyVersion(models.Model):
    """Historical snapshots of a policy (populated by the version tracking module)."""
    id = models.BigAutoField(primary_key=True)
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='versions',
    )
    version_number = models.PositiveIntegerField()
    version_text = models.TextField()
    content_hash = models.CharField(max_length=64, db_index=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'policy_versions'
        unique_together = [('document', 'version_number')]
        ordering = ['-version_number']

    def __str__(self):
        return f'PolicyVersion(doc={self.document_id}, v={self.version_number})'


class PolicyChange(models.Model):
    """
    Clause-level change between two policy versions.
    Populated by the version tracking module via the internal API.
    """

    class ChangeType(models.TextChoices):
        ADDED = 'added', 'Added'
        REMOVED = 'removed', 'Removed'
        MODIFIED = 'modified', 'Modified'
        UNCHANGED = 'unchanged', 'Unchanged'

    class ChangeDirection(models.TextChoices):
        MORE_FAVORABLE = 'more_favorable', 'More Favorable'
        NEUTRAL = 'neutral', 'Neutral'
        LESS_FAVORABLE = 'less_favorable', 'Less Favorable'
        UNCLEAR = 'unclear', 'Unclear'

    id = models.BigAutoField(primary_key=True)
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='policy_changes',
    )
    old_clause = models.ForeignKey(
        'analysis.Clause',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='old_changes',
    )
    new_clause = models.ForeignKey(
        'analysis.Clause',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='new_changes',
    )
    change_type = models.CharField(max_length=12, choices=ChangeType.choices)
    change_direction = models.CharField(max_length=15, choices=ChangeDirection.choices, default=ChangeDirection.UNCLEAR)
    magnitude = models.FloatField(
        help_text='Change magnitude 0.0–1.0 from the version tracking module.',
        default=0.0,
    )
    alert_score = models.FloatField(
        help_text='Computed alert score A(c,u) = R × D × M.',
        default=0.0,
    )
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'policy_changes'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['document', 'change_type']),
        ]

    def __str__(self):
        return f'PolicyChange(doc={self.document_id}, type={self.change_type})'
