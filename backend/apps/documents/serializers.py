"""
ClauseLens – Document serializers.
"""
from rest_framework import serializers
from django.conf import settings
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Full document representation returned to the frontend."""
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'document_name', 'document_type', 'file_url',
            'policy_url', 'status', 'uploaded_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for PDF file upload."""
    file = serializers.FileField()
    document_name = serializers.CharField(max_length=500, required=False)

    def validate_file(self, file):
        # Validate MIME type
        content_type = getattr(file, 'content_type', '')
        if content_type not in settings.ALLOWED_DOCUMENT_TYPES:
            raise serializers.ValidationError(
                f'Unsupported file type "{content_type}". Only PDF files are accepted.'
            )
        # Validate file size
        max_bytes = settings.MAX_UPLOAD_SIZE_BYTES
        if file.size > max_bytes:
            raise serializers.ValidationError(
                f'File too large. Maximum allowed size is {settings.MAX_UPLOAD_SIZE_MB} MB.'
            )
        return file


class DocumentURLSerializer(serializers.Serializer):
    """Serializer for submitting a policy URL."""
    policy_url = serializers.URLField(max_length=2048)
    document_name = serializers.CharField(max_length=500, required=False)
