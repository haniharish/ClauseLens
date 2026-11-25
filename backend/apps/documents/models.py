"""
ClauseLens – Document model.
"""
from django.db import models
from django.conf import settings


def document_upload_path(instance, filename):
    """Store uploads under media/documents/<user_id>/<filename>."""
    return f'documents/{instance.user_id}/{filename}'


class Document(models.Model):
    """
    Represents a Terms & Conditions / Privacy Policy document
    uploaded by a user (either as a file or via URL).
    """

    class DocumentType(models.TextChoices):
        PDF = 'pdf', 'PDF'
        URL = 'url', 'URL'

    class Status(models.TextChoices):
        UPLOADED = 'uploaded', 'Uploaded'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    document_name = models.CharField(max_length=500)
    document_type = models.CharField(
        max_length=10,
        choices=DocumentType.choices,
        default=DocumentType.PDF,
    )
    file = models.FileField(
        upload_to=document_upload_path,
        null=True,
        blank=True,
        help_text='Uploaded PDF file (null for URL-based documents).',
    )
    policy_url = models.URLField(
        max_length=2048,
        null=True,
        blank=True,
        help_text='Source URL (null for file uploads).',
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.UPLOADED,
        db_index=True,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['uploaded_at']),
        ]

    def __str__(self):
        return f'Document({self.id}) – {self.document_name}'
