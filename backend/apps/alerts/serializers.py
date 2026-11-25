"""
ClauseLens – Notification serializers.
"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source='document.document_name', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'document', 'document_name', 'policy_change',
            'title', 'message', 'severity', 'is_read', 'created_at',
        ]
        read_only_fields = fields
